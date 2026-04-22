---
name: context-save
description: Session checkpoint skill. Commits all in-progress work with a WIP prefix and writes a structured context file to .claude/context.md — capturing where you are, what's next, and what decisions were made. Run before ending a session on unfinished work so the next session can resume without re-reading the whole conversation.
triggers:
  - /context-save
args: "[optional: brief description of where you're stopping]"
---

# Context Save

You are creating a session checkpoint. When this session ends, all context — what was being worked on, what decisions were made, what's blocked, what's next — lives only in the conversation history. This skill commits the work and writes a handoff note so the next session can pick up without losing ground.

Think of this as leaving a note for future-you on a whiteboard: not everything, just what matters.

---

## When to Run This

- Before ending a session on in-progress work (anything not merged)
- Before a long break (overnight, weekend)
- After hitting a block that requires more thought
- When the session has gotten long and context compression might lose important decisions

---

## Phase 1 — Commit In-Progress Work

Check git status:
```bash
git status
git diff --stat
```

If there are uncommitted changes:

Stage and commit with WIP prefix:
```bash
git add -A
git commit -m "WIP: [branch/feature name] — [brief state: e.g., 'auth middleware partial, tests pending']"
```

WIP commit rules:
- Prefix always: `WIP: ` 
- Never ship a WIP commit to main — it's a checkpoint, not a release
- Include enough in the message that `git log --oneline` tells the story

If there's nothing to commit (clean working tree):
- Note: "Working tree is clean — no uncommitted changes to checkpoint."

---

## Phase 2 — Write the Context File

Write `.claude/context.md` in the project root (overwrite if it exists):

```markdown
# Session Context — [Project Name]

**Saved:** [ISO date and time]
**Branch:** [current branch]
**Last commit:** [hash] [message]

---

## What's Being Built

[1-3 sentences: what feature/fix is in progress, what it's for]

---

## Current State

**Completed in this session:**
- [bullet: what was finished]
- [bullet]

**In progress / incomplete:**
- [bullet: what was started but not finished]
- [bullet: what's partially done and what specifically remains]

**Blocked on:**
- [bullet: what's blocking progress, if anything]

---

## Key Decisions Made

| Decision | What | Why |
|----------|------|-----|
| [topic] | [what was decided] | [why — the constraint or reasoning] |

---

## Next Steps (in order)

1. [First thing to do when resuming]
2. [Second thing]
3. [Third thing]

---

## Files in Play

[List the key files that are being modified or that are relevant to resume from — file paths only, no descriptions needed]

---

## Notes

[Anything that would be confusing without context — gotchas, half-finished thoughts, decisions still open]
```

Fill in only sections that have real content. An empty "Blocked on" section should be omitted.

---

## Phase 3 — Confirm

Report:
```
✓ WIP commit: [hash] [message]  (or: "No uncommitted changes")
✓ Context saved: .claude/context.md
  Branch: [branch]
  Next steps: [first item]
```

End with:
> **Checkpoint saved.** Resume with `/context-restore` to pick up where you left off.

---

## Rules

- **WIP commits are not PRs.** Don't push them to remote unless the user asks — they're local checkpoints.
- **context.md is always current.** Every `/context-save` overwrites it — it reflects the most recent checkpoint, not a history.
- **Next Steps must be actionable.** "Continue working" is not a next step. "Implement the `validateToken` function in `src/auth/middleware.ts`" is.
- **Don't checkpoint clean state.** If nothing is in progress and there are no uncommitted changes, there's nothing to save. Say so.
