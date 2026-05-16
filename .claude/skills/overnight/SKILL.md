---
name: overnight
description: Scheduled overnight job runner. Reads `agent-tasks/*.md` in the current repo, fires a `/swarm` run at a configured hour with a wall-clock cap, and produces a morning report. Pairs with `/morning-prs` for review at breakfast. This is the "agents while you sleep" loop — queue work during the day, let the swarm run at night, review verified branches over coffee.
argument-hint: "[setup | run-now | status | disable]  — default: status"
---

# /overnight — Agents While You Sleep

You are managing the **overnight** loop. The user queues tasks throughout the day by dropping markdown briefs in `agent-tasks/`. At the configured hour, a LaunchAgent triggers `/swarm` against that queue, runs until a wall-clock cap, and writes a report. The user reviews verified branches in the morning.

This is `/swarm` + scheduling + reporting. The pieces individually exist; overnight is the wiring.

---

## Modes

`/overnight setup` — install the LaunchAgent and create the queue dir
`/overnight run-now` — fire the run immediately (smoke test)
`/overnight status` (default) — show queue size, last run summary, next scheduled fire
`/overnight disable` — unload the LaunchAgent

---

## Layout (per repo)

```
<repo>/
├── agent-tasks/                  # queue — drop *.md briefs here during the day
│   ├── completed/                # auto-moved here after a successful run
│   └── failed/                   # auto-moved here when verify fails
└── outputs/
    └── overnight/
        └── <UTC-date>/
            ├── summary.md        # human-readable morning report
            ├── summary.json      # machine-readable (for /morning-prs)
            └── swarm-run-link    # symlink to the underlying swarm-runs dir
```

Briefs in `agent-tasks/` use the same frontmatter as `/swarm`'s `task-template.md` (id, goal, files, verify). If a brief is missing required fields, `/overnight` marks it `invalid` and moves it to `agent-tasks/failed/` with a note — it does NOT block the rest of the run.

---

## Setup

### 1. Create the queue dir

```bash
mkdir -p agent-tasks/{completed,failed} outputs/overnight
echo "agent-tasks/completed/\nagent-tasks/failed/\noutputs/overnight/" >> .gitignore
```

The queue dir itself stays tracked (so briefs are versioned). The `completed/` and `failed/` subdirs are gitignored so the morning state doesn't pollute the repo.

### 2. Install the LaunchAgent

The plist lives at `.claude/skills/overnight/com.tanker.overnight.<repo-slug>.plist.template`. Render it with the repo path and target hour:

```bash
REPO="$(git rev-parse --show-toplevel)"
SLUG="$(basename "$REPO" | tr '[:upper:]' '[:lower:]')"
HOUR="${1:-2}"   # default 02:00 local
PLIST="$HOME/Library/LaunchAgents/com.tanker.overnight.$SLUG.plist"

sed "s|__REPO__|$REPO|g; s|__SLUG__|$SLUG|g; s|__HOUR__|$HOUR|g" \
  .claude/skills/overnight/com.tanker.overnight.plist.template > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"
```

### 3. Set the wall-clock cap

Default cap: 4 hours from the fire time. Configurable via `OVERNIGHT_MAX_SECONDS` in `.env` or `tanker.yaml`:

```yaml
overnight:
  max_seconds: 14400        # 4 hours
  max_parallel: 3           # passed to /swarm
  per_task_timeout: 1800    # 30 min, passed to /swarm
  open_prs: false           # if true, /swarm runs with --pr
```

---

## Run

At fire time, the LaunchAgent invokes `.claude/skills/overnight/run.sh`. The script:

1. Re-reads the cap from `tanker.yaml`
2. Counts briefs in `agent-tasks/` — if zero, writes a "no work" summary and exits
3. Wraps the whole thing in `timeout $max_seconds`
4. Invokes `claude -p` with the `/swarm agent-tasks .` command and the configured flags
5. After `/swarm` returns (or is killed by timeout):
   - For each completed task, move the brief to `agent-tasks/completed/` and prefix with the branch name in the filename
   - For each failed task, move the brief to `agent-tasks/failed/` and append the failure reason to the front matter
   - Generate `outputs/overnight/<date>/summary.md`
6. If a notification channel is configured (`OVERNIGHT_NOTIFY_SLACK_WEBHOOK` or `OVERNIGHT_NOTIFY_EMAIL`), send a one-line summary

---

## Morning report format

`outputs/overnight/<date>/summary.md`:

```markdown
# Overnight Run — 2026-05-17

**Started:** 02:00 IST | **Ended:** 04:37 IST | **Cap:** 4h | **Hit cap:** no

**Tasks:** 7 total → 5 passed, 1 failed, 1 timed_out

## Passed (review and merge)
- `refactor-auth` — `swarm/.../refactor-auth` — verify: tests green
- `add-cron-cleanup` — `swarm/.../add-cron-cleanup` — verify: lint + tests green
- ...

## Failed
- `migrate-db-schema` — verifier_failed: pytest exit 1, 3 tests failing
  - log: outputs/swarm-runs/.../wt-migrate-db-schema.log
  - brief preserved: agent-tasks/failed/migrate-db-schema.md

## Timed out
- `bulk-import-vendors` — hit 30-min per-task cap; worktree retained

## Next action
Run `/morning-prs` to walk through the 5 passed branches in order of impact.
```

---

## Hard rails

- **Never auto-merge.** Overnight produces branches (and PRs if configured). Merging is always a human decision.
- **Wall-clock cap is real.** When the cap hits, `/swarm`'s SIGINT trap kicks in: kill workers, mark survivors as `aborted`, write a partial summary. Better a clean partial run than a runaway burning credits all morning.
- **Cost ceiling.** Before firing, compute `count(briefs) * 0.20` (Sonnet upper bound). If > $20, send a notification asking for confirmation and skip the run. The user can rerun with `/overnight run-now` after approval.
- **Sleep awareness.** The LaunchAgent uses `StartCalendarInterval` (not `StartInterval`), so a sleeping laptop will fire on next wake. To genuinely run overnight, the user's machine must stay awake (caffeinate, energy settings — same setup as the Sia EA Mac mini).
- **Lock file.** `outputs/overnight/.lock` prevents two simultaneous runs. If a lock from a previous run is stale (> max_seconds + 10min), the script deletes it and proceeds.

---

## Disable

`/overnight disable`:

```bash
launchctl unload "$HOME/Library/LaunchAgents/com.tanker.overnight.$SLUG.plist"
rm "$HOME/Library/LaunchAgents/com.tanker.overnight.$SLUG.plist"
```

Briefs in `agent-tasks/` are preserved. Re-enable any time with `/overnight setup`.

---

## Handoff

Morning state ready: prompt `/morning-prs` to triage the night's output. If failed tasks are present, suggest `/debug` on the first one.
