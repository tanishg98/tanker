---
name: compound
description: Runs after a PR merge (or on demand) to extract reusable patterns from the diff, PR comments, and user corrections in the conversation. Appends new rules to project `.claude/brain.md` and surfaces global candidates for `~/.claude/CLAUDE.md`. This is Tanker's "Dreaming" loop — institutional knowledge that compounds across sessions instead of being lost.
argument-hint: "[pr <number> | last-merge | session]  — default: last-merge on current repo"
---

# /compound — Compounding Engineering Loop

You are running the **Compound** loop. Your job is to mine the most recent shipped work for durable lessons, write them into project memory, and surface the ones worth promoting to global memory.

This skill exists because every PR teaches the system something — what broke, what the user pushed back on, what shortcut bit us — and 95% of that signal is lost the moment the session ends. Compound captures it.

Inspired by the "Compounding Engineering" pattern: every merge makes the next merge cheaper.

---

## When to run

- **Automatic:** after a PR is merged on the current repo (`gh pr view --json state` returns `MERGED`).
- **Manual end-of-session:** when the user finishes a meaningful chunk of work and wants the lessons saved.
- **Catching up:** after a stretch of merges you weren't running this on, pass `pr <number>` to backfill one at a time.

Do NOT run this on every commit — that's noise. Run on merges (real shipped units of work) and on explicit end-of-session.

---

## Inputs

`/compound [scope]` where scope is:
- `last-merge` (default) — most recent merged PR on the current branch's upstream
- `pr <number>` — specific PR
- `session` — current conversation (no PR; mine the transcript)

---

## How you operate

### 1. Gather the source material

Depending on scope:

**`last-merge` / `pr <N>`:**
- `gh pr view <N> --json title,body,url,mergeCommit,reviewDecision,comments,reviews`
- `gh pr diff <N>` for the full diff
- `gh api repos/{owner}/{repo}/pulls/<N>/comments` for line-level comments
- Identify the merge commit and pull the commit message via `git show <sha>`

**`session`:**
- Re-read the current conversation. Focus on: user corrections, "no don't do that," "actually let's...", surprised reactions, and any rules of thumb the user stated.

### 2. Extract candidates

Read everything once. Then write a short list of candidate lessons. Each candidate must be:

- **Specific** — not "write better code." Specific: "always use `git status --porcelain` before removing a worktree because `git diff --quiet` misses untracked files."
- **Reusable** — applies beyond this one PR.
- **Non-obvious from the code** — if a future Claude can derive it by reading the repo, don't save it.

Classify each candidate:
- **convention** — how we do things in this project (lives in `brain.md` under Conventions)
- **pitfall** — a landmine to avoid (lives in `brain.md` under Pitfalls)
- **preference** — what the user wants (lives in `brain.md` under Preferences)
- **global** — worth promoting to `~/.claude/CLAUDE.md` because it applies across all projects (surface but do not auto-write)

### 3. De-duplicate against existing memory

Before writing, read:
- `.claude/brain.md` and `.claude/brain.private.md` (if present) in the project
- The auto-memory index at `~/.claude/projects/-Users-tanishgirotra1/memory/MEMORY.md`

If a candidate restates something already there, drop it. If it sharpens or contradicts an existing entry, prepare an **update** (not a new entry).

### 4. Present the diff before writing

Show the user a compact table of what you're about to do:

```
| action  | target               | entry (truncated)                                       |
|---------|----------------------|---------------------------------------------------------|
| add     | brain.md/Pitfalls    | git diff --quiet misses untracked — use --porcelain     |
| update  | brain.md/Conventions | (existing) bash 3.2 compat + new: gtimeout fallback...  |
| surface | global candidate     | "Stage files by name, never git add ."                  |
```

Ask: "Apply these N edits to `.claude/brain.md`? Surface M global candidates for `~/.claude/CLAUDE.md` review?"

Default to yes-on-Enter behavior — the user has already opted in by running `/compound`.

### 5. Write

- Append/update entries in `.claude/brain.md` under the right H2 section. Match the existing format exactly (date prefix, bullet style).
- For project-sensitive items: write to `.claude/brain.private.md` instead. Use private when the entry names internal customers, pricing, employee names, or stack details that should never go public.
- For global candidates: never auto-write to `~/.claude/CLAUDE.md`. Print them at the end with the suggestion "run `/remember` to promote any of these to global rules."
- Commit the brain.md change on a `chore/compound-<date>` branch only if the project repo is clean. Otherwise leave uncommitted and tell the user.

### 6. Memory ledger

Append one line to `~/.claude/projects/-Users-tanishgirotra1/memory/compound_runs.md`:

```
2026-05-17 | tanker | PR #11 | 3 added, 1 updated, 2 global candidates
```

This is the audit trail. Never read this file from inside `/compound` — it's for cross-session review only.

---

## Hard rails

- **Never write to a tracked file with sensitive content.** If the entry mentions internal company names, pricing, customer names, employee names, or unreleased products — route to `.claude/brain.private.md`, never `.claude/brain.md`. If both are tracked, fail-fast and ask where to put it.
- **Never promote to global without user approval.** Even "obvious" global rules need a human ack — `~/.claude/CLAUDE.md` is loaded into every session, every project.
- **Idempotent.** Running `/compound pr 11` twice must not double-write. Use a marker (e.g., `<!-- compound:pr-11 -->`) at the end of each entry block.
- **No invented lessons.** If the PR was a clean ship with no friction and no corrections, the right output is "0 lessons — clean ship." Do not fabricate to fill the table.

---

## What good output looks like

A typical run on a meaningful PR produces 1–4 lessons. A run on a clean trivial PR produces 0. A run that produces 10+ is probably padding — re-read and cut the weak ones.

The test for each lesson: **would my future self thank me for writing this?** If the answer is "meh, I'd remember anyway," drop it.

---

## Handoff

After writing, prompt:
> "N lessons captured. M global candidates surfaced — run `/remember` to review them. Continue session, or close out?"
