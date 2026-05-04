---
name: remember
description: Injects a concise memory block into the project's CLAUDE.md so it auto-loads in every new CLI session. Solves the "fresh session blank slate" problem — run this at end of any session where important context was established. Also reads brain.md and context.md to brief you at the start of a session if the global CLAUDE.md rule hasn't already done so.
triggers:
  - /remember
args: "[optional: 'inject' to write to CLAUDE.md | 'status' to show what memory exists | leave blank to do both]"
---

# Remember

Every new Claude Code CLI session starts blank. The only things that survive are files Claude is told to read at startup — primarily CLAUDE.md. This skill bridges the gap: it writes the project brain into CLAUDE.md so the next session starts informed, not cold.

---

## How Memory Survives CLI Sessions

```
End of session:           /remember inject
                               ↓
                    Writes summary → CLAUDE.md
                               ↓
Next session starts:    CLAUDE.md auto-loads
                               ↓
                    Claude reads brain + context
                               ↓
                    Session starts with full context
```

The global `~/.claude/CLAUDE.md` tells Claude to read `.claude/brain.md` and `.claude/context.md` automatically. This skill makes sure those files exist and are up to date — and injects a summary into the project CLAUDE.md as a belt-and-suspenders backup.

---

## Phase 1 — Determine Mode

**`status`** — Show what memory currently exists without changing anything.

**`inject`** — Write the memory block into CLAUDE.md.

**Default (no args)** — Run status first, then inject.

---

## Phase 2 — Gather Memory Sources

Read all available memory:

```bash
# Project brain
cat .claude/brain.md 2>/dev/null

# Session context
cat .claude/context.md 2>/dev/null

# Recent git activity (last 5 commits)
git log --oneline -5 2>/dev/null

# Check if project CLAUDE.md exists
cat CLAUDE.md 2>/dev/null || cat .claude/CLAUDE.md 2>/dev/null
```

---

## Phase 3 — Status Report

Show what exists:

```
Memory status for: [project name / current directory]

  brain.md:     [exists — N conventions, N decisions, N pitfalls, N preferences]
                [or: not found — run /learn to create it]
  context.md:   [exists — last saved [date], working on: [what]]
                [or: not found — run /context-save to create it]
  CLAUDE.md:    [exists with memory block / exists without memory block / not found]

  Last 5 commits:
    [git log output]
```

---

## Phase 4 — Inject Memory Block into CLAUDE.md

Generate a concise memory block from brain.md + context.md. Keep it **under 40 lines** — long enough to be useful, short enough not to dominate the file.

### Memory block format

```markdown
## Active Project Memory
<!-- tanker:remember — auto-updated, do not edit manually -->
<!-- Last updated: [ISO date] -->

### What this project is
[1-2 sentence description derived from brain.md or git history]

### Conventions (apply always)
[bullet list — max 5 most important from brain.md Conventions section]

### Active work
[From context.md: what's in progress, what's next — or "No active context" if context.md absent]

### Pitfalls (known landmines)
[bullet list — max 5 most critical from brain.md Pitfalls section]

### Preferences (owner's explicit instructions)
[bullet list — max 5 from brain.md Preferences section]
<!-- end tanker:remember -->
```

### Where to write it

**If `CLAUDE.md` exists** in the project root: append/update the `## Active Project Memory` section. Replace the block between `<!-- tanker:remember -->` and `<!-- end tanker:remember -->` if it already exists.

**If `CLAUDE.md` does not exist** in the project root: create it with just the memory block. Don't invent other content.

**Never overwrite** content outside the `<!-- tanker:remember -->` markers.

---

## Phase 5 — Confirm

```
Memory injected into CLAUDE.md

  Conventions: [N items]
  Pitfalls:    [N items]
  Preferences: [N items]
  Active work: [one-line summary or "none"]
  Block size:  [N lines]

Next session will auto-load this context.
Run /remember inject again after any /learn session to keep it current.
```

---

## Session Start Mode (no CLAUDE.md instruction ran yet)

If the global CLAUDE.md memory instruction didn't fire (e.g., running in a project without the global config), `/remember` can also serve as a manual session-start briefing:

Read brain.md + context.md and produce:

```
Session briefing for: [project]

  Project: [what it is — 1 sentence]
  Conventions: [top 3]
  Last working on: [from context.md or git log]
  Next steps: [from context.md if available]
  Active pitfalls: [top 2]

Ready. What would you like to work on?
```

---

## Rules

- **The memory block must be under 40 lines.** It's a summary, not a copy of brain.md. If brain.md has 20 pitfalls, pick the 5 most critical.
- **Never touch content outside the markers.** The `<!-- tanker:remember -->` delimiters define the safe zone. Everything outside them is untouched.
- **Prefer recency.** If brain.md has 10 conventions, surface the ones added most recently first — they're most likely to be relevant.
- **Run after every /learn session.** brain.md is the source of truth; CLAUDE.md is the cache. Keep the cache current.
- **If neither brain.md nor context.md exists**, say so and suggest running `/learn` to create them rather than writing an empty block.
