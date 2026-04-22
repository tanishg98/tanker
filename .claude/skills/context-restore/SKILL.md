---
name: context-restore
description: Session recovery skill. Reads .claude/context.md and recent git history to reconstruct where the previous session left off. Run at the start of a new session on in-progress work to avoid re-reading the full conversation history.
triggers:
  - /context-restore
args: "[no args needed]"
---

# Context Restore

You are reconstructing the state of a previous session from its checkpoint. The goal is to get back to productive work in under 60 seconds — without re-reading the conversation, without re-exploring the codebase, without asking what was being worked on.

---

## When to Run This

- At the start of any session where work was left incomplete
- After a long break on a project
- When resuming after using `/context-save`

---

## Phase 1 — Read the Context File

Check for `.claude/context.md`:

```bash
cat .claude/context.md 2>/dev/null || echo "NO_CONTEXT_FILE"
```

If the file doesn't exist:
- "No context file found. Try reading recent git log: `git log --oneline -10`"
- Proceed to Phase 2 (reconstruct from git)

If the file exists, read and hold it for Phase 3.

---

## Phase 2 — Read Recent Git History

```bash
git log --oneline -10
git status
git diff --stat
```

Also check for WIP commits:
```bash
git log --oneline --grep="WIP:" -5
```

---

## Phase 3 — Reconstruct and Present

Combine the context file + git history into a clear session briefing. Format:

```markdown
## Session Resumed — [Project Name]

**Branch:** [current branch]
**Last saved:** [date from context.md, or "unknown"]
**Last commit:** [hash] [message]

---

### What Was Being Built
[From context.md "What's Being Built" section]

### Where It Was Left
**Done:** [bullet list from "Completed in this session"]
**In progress:** [bullet list from "In progress / incomplete"]
**Blocked:** [from "Blocked on" — or omit if nothing]

### Key Decisions (from last session)
[Table from context.md, or omit if empty]

### Next Steps
[Numbered list from context.md — this is the action queue]

### Files to Look At First
[List from context.md "Files in Play"]
```

If context.md is missing and only git history is available, reconstruct best-effort from commit messages and current git status.

---

## Phase 4 — Offer to Start

After presenting the briefing, ask:

> "Ready to pick up? Say 'yes' to start with Step 1, or tell me where you want to start."

If the user says yes:
- Begin the first next step immediately
- Read the relevant files before writing anything (standard explore-before-execute practice)

---

## Output Format

The briefing (Phase 3), followed by the offer to start (Phase 4). Keep the briefing tight — the goal is a fast handoff, not a full re-read.

---

## Rules

- **Don't ask what they were working on.** Read it. The context file exists for this reason.
- **Start with the next step, not a summary.** The summary is for orientation. The goal is to get back to work.
- **If context.md is stale** (context says branch X but we're on branch Y), flag it: "Context file is from branch X but we're on Y — this may be outdated."
- **Don't re-explore the codebase unless the context is missing.** `/context-restore` is a fast handoff, not a fresh `/explore`.
