---
name: retro
description: Weekly engineering retrospective for a project. Reads git history, the project brain, and asks what shipped, what broke, and what slowed things down. Produces a structured report and writes key learnings back to .claude/brain.md. Run at the end of a sprint or week of work.
triggers:
  - /retro
args: "[optional: 'week' (default, last 7 days) | 'sprint' | 'month' | specific date range 'YYYY-MM-DD:YYYY-MM-DD']"
---

# Retro

You are running a team retrospective — except the team is one person and their AI. The goal is not to celebrate or complain. It is to **extract signal from the past week and feed it forward**.

A retro that doesn't change behavior next week is a waste of time. Every retro ends with specific changes: to the project brain, to a skill, or to a way of working.

---

## When to Run This

- End of a week or sprint
- After a hard week (something broke in production, something took way longer than expected)
- When starting a new sprint (run retro on the last one first)
- Monthly for active projects

---

## Phase 1 — Gather Context

Before asking any questions, read the available data:

### Git history
```bash
git log --since="7 days ago" --oneline --author=$(git config user.email)
# or for the specified range
git log --since="[start]" --until="[end]" --oneline
```

Also read:
```bash
git diff --stat HEAD~7 HEAD 2>/dev/null || git log --oneline | tail -20
```

### Project brain
Check if `.claude/brain.md` exists. If it does, read it — especially Pitfalls (were any hit this week?) and Open Questions (were any resolved?).

### Recent skill/rule changes
```bash
git log --since="7 days ago" --oneline -- .claude/
```

---

## Phase 2 — Four Questions

Ask these four questions using `AskUserQuestion`, one at a time. Don't combine them. Wait for a real answer.

**Q1 — What shipped?**
> "What did you actually ship or complete this week — features, fixes, infrastructure?"

Accept bullet lists. Ask for specifics if the answer is "a bunch of stuff."

**Q2 — What broke or was harder than expected?**
> "What took longer than expected, broke in production, or required more back-and-forth than it should have?"

This is the most important question. Dig in if the answer is vague.

**Q3 — Where was time lost?**
> "Where did you lose time this week — debugging something that should have been obvious, unclear requirements, waiting on something, Claude going in circles?"

**Q4 — What would you do differently?**
> "If you ran this week again, what's the one change that would make the biggest difference?"

---

## Phase 3 — Generate the Retro Report

Synthesize everything into a structured report.

```markdown
# Retro — [Project Name] — [Date Range]

## What Shipped
[Bullet list from git log + Q1 — be specific]

## What Went Well
[1-3 things to repeat — derived from the "what shipped" answer and git history]

## What Broke / Slowed Things Down
[Derived from Q2 and Q3 — pattern-match across the week, not just one incident]

## Root Causes
[For each "what broke" item: why did it really happen? Technical? Unclear spec? Missing skill? Bad assumption?]

## One Change for Next Week
[From Q4 — one specific, actionable change. "Be more careful" is not a change. "Run /autoresearch-review before merging to catch async race conditions" is a change.]

## Metrics
- Commits: [N]
- Files changed: [N] (+[X] -[Y] lines)
- Skills/agents used: [list from .claude/ history]
- Pitfalls hit from brain.md: [list, or "none"]
```

---

## Phase 4 — Update the Project Brain

After the report, identify what should be added to `.claude/brain.md`:

- New **Pitfalls** (things that broke that should be flagged for future)
- Resolved **Open Questions** (remove from open, promote to Decision)
- New **Conventions** (ways of working that crystallized this week)
- New **Preferences** (things the user corrected — add them)

Write the updates using `/learn` logic (append/update `.claude/brain.md`).

Report what was added:
```
Brain updated:
  + Pitfall: [description]
  + Decision: [description]
  ~ Removed open question: [description] (resolved)
```

---

## Output Format

1. Retro report (Phase 3) — full markdown block
2. Brain updates (Phase 4) — short list of what was added/changed
3. End with:

> **Retro complete.** Brain updated with [N] new entries. Next week: [one change from Q4].

---

## Rules

- **The retro must produce at least one change.** If nothing goes into the brain, the retro was too shallow. Push harder on Q2 and Q3.
- **Pattern over incident.** One bug is an incident. The same class of bug three times is a pattern — name the pattern, not the instances.
- **Root cause, not blame.** "Claude suggested the wrong approach" is not a root cause. "The skill didn't check for the existing pattern before proposing a new one" is.
- **Keep the report short.** Longer retros are read less. A 4-section report that's precise beats a 10-section report that's thorough.
- **The 'one change' must be specific and actionable.** Vague resolutions decay by Thursday. A specific skill invocation or rule change persists.
