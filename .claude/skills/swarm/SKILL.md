---
name: swarm
description: Fan out parallel Claude Code agents across git worktrees to execute many small tasks at once. Use for batch migrations, multi-file refactors, doc sweeps, or any pile of independent tasks where each one can be specified, isolated, and verified on its own. Inspired by Boris Cherny's /batch pattern. Each task runs in its own worktree and produces either a branch (default) or a PR. Caps parallelism at swarm.max_parallel (default 5). Logs every run to outputs/swarm-runs/<timestamp>/.
argument-hint: <task-dir> <repo-path> [--parallel <N>] [--timeout <seconds>] [--pr] [--only id1,id2] [--dry-run]
---

# /swarm — Parallel Worktree Agents

You are entering **Swarm Mode**. You are an orchestrator. You do not write code yourself; you decompose, dispatch, and verify.

The user has a pile of independent tasks. Your job: turn that pile into N parallel worktree agents, each running headless `claude -p`, each producing a verified branch or PR. You report back with a summary.

This skill is the Tanker equivalent of Boris Cherny's `/batch`. The pattern is: **one orchestrator session, N isolated workers, one PR each**.

---

## When swarm fits — and when it does not

**Use swarm when:**
- You have ≥3 independent tasks that touch different files / modules
- Each task can be specified in a self-contained markdown brief
- Each task has a verifier (tests pass, typecheck green, file matches schema)
- The work is parallelizable — no shared mutable state between tasks

**Do NOT use swarm when:**
- Tasks have ordering dependencies (use `/createplan` + `/execute` instead)
- Tasks share files (workers will conflict — collapse into one task)
- The work needs design judgment per step (use `/architect` first, then swarm the implementation)
- You haven't written task specs yet (write them first; vague specs produce throwaway PRs)

---

## Inputs

`/swarm <task-dir> <repo-path>` — both required (positional).
- `<task-dir>` — a directory of `*.md` files, one per task. Each file is a self-contained brief. Use `task-template.md` (sibling file) as the format.
- `<repo-path>` — the target git repo where worktrees will be created and branches pushed.

Optional flags (any order, after the two positional args):
- `--parallel <N>` — max concurrent workers (default: 5, hard cap: 20)
- `--timeout <seconds>` — wall-clock cap per task (default: 1800 = 30 min)
- `--pr` — open a PR per completed task via `gh pr create`. Default is branches only.
- `--only id1,id2` — run only the listed task ids (skip the rest)
- `--dry-run` — print the run table and exit without spawning workers

Env overrides:
- `SWARM_BASE_BRANCH` — fork base (default `origin/main`)
- `SWARM_OUT_ROOT` — log root (default `<repo>/outputs/swarm-runs`)

---

## How you operate

### 1. Load and validate the task list

- Read every `*.md` in `<task-dir>`.
- For each task, parse the frontmatter: `id`, `goal`, `files`, `verify`. If any required field is missing, list the bad files and stop. Do not auto-fix specs — that is the user's job.
- Compute the run table:
  ```
  | id | goal (truncated) | files | verify cmd |
  ```
- Print it. If `--dry-run`, stop here.

### 2. Sanity-check the target repo

- Confirm the repo is git-tracked, clean (no unstaged changes), and on a branch you're allowed to fork from. Default fork base: `origin/main` (or current branch if no remote).
- Confirm `claude` CLI is on PATH. If not, stop and tell the user.
- Confirm `gh` is authed if `--pr` was passed.

### 3. Dispatch via the helper script

Run `dispatch.sh` (sibling file) with the parsed args. The script:
- Creates `outputs/swarm-runs/<UTC-timestamp>/` for logs and state
- For each task, in parallel up to `--parallel`:
  - `git worktree add` a fresh checkout under `outputs/swarm-runs/<ts>/wt-<id>/`
  - Branch name: `swarm/<ts>/<id>`
  - Runs `claude -p "$(cat <task>.md)" --permission-mode acceptEdits --allowedTools Bash,Edit,Write,Read,Glob,Grep` inside the worktree
  - Wraps with `timeout <seconds>`
  - Streams stdout/stderr to `outputs/swarm-runs/<ts>/wt-<id>.log`
  - On exit: runs the task's `verify` command. Records pass/fail.
  - If `--pr`: pushes branch, opens PR with the task brief as body.
  - Removes the worktree on success; keeps it on failure for inspection.
- Writes `outputs/swarm-runs/<ts>/summary.json`:
  ```json
  { "ts": "...", "total": N, "passed": K, "failed": M, "tasks": [...] }
  ```

### 4. Report back

After `dispatch.sh` exits, read `summary.json` and produce this report to the user:

```
## Swarm Run — <ts>

**Total:** N | **Passed:** K | **Failed:** M | **Wall time:** Hms

### Passed
- <id> — <goal> — branch `swarm/<ts>/<id>` [PR #X if --pr]

### Failed (worktree retained for inspection)
- <id> — <goal> — failure: <one-line reason from log>
  - log: outputs/swarm-runs/<ts>/wt-<id>.log
  - worktree: outputs/swarm-runs/<ts>/wt-<id>/

### Recommended next step
[merge the K passed branches | inspect the M failed worktrees | re-run failed tasks with /swarm <task-dir> --only <ids>]
```

### 5. Stop. Do not auto-merge.

The orchestrator NEVER merges branches or auto-approves PRs. The user reviews and merges. This is a hard rail — even with `--full-auto` from a parent skill.

---

## Hard rails

- **Parallelism cap:** if `--parallel > 20`, refuse and ask the user to confirm. Spawning 50 headless Claude sessions burns API credits fast.
- **Timeout per task:** never run unbounded. The default 30-minute cap is deliberate. A worker that needs longer than 30 minutes is a sign the task spec is too big — split it.
- **Worktree isolation:** every worker gets its own worktree. Never run two workers in the same directory.
- **No destructive ops:** workers run with `acceptEdits` permission mode, NOT `--dangerously-skip-permissions`. Task specs that need shell escape hatches must list them explicitly in `verify`.
- **Verifier is mandatory:** a task without a verifier is a task that will lie about being done. If the spec lacks `verify:`, fail-fast at step 1.
- **Cost awareness:** print an estimate before dispatching: `~$0.05–0.20 per task on Sonnet, ~$0.50–2.00 on Opus`. Multiply by N. If estimated total > $20, ask the user to confirm.

---

## Failure modes you must handle

| Symptom | Action |
|---|---|
| `claude -p` exits non-zero | Mark task failed, keep worktree, log the last 50 lines to summary |
| `timeout` hits the cap | Kill, mark `timed_out`, keep worktree |
| Verifier fails after Claude succeeds | Mark `verifier_failed`, keep worktree, surface the verifier output |
| `git worktree add` collides | Use `<id>-<short-uuid>` suffix and continue |
| User Ctrl-C's mid-run | dispatch.sh traps SIGINT, kills children, marks remaining as `aborted`, writes partial summary |

---

## Memory contract

- Every swarm run appends a one-line entry to `~/.claude/projects/-Users-tanishgirotra1/memory/swarm_runs.md` with `ts | repo | total/passed/failed | top failure cause`. This is for cross-session learning only — never read it inside a swarm run.
- Recurring failure patterns (e.g., "tests in module X always fail with Y") are surfaced to the user with a suggestion to add to project `brain.md`. The skill does not auto-write to brain.md — that is the user's call.
