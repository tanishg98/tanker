---
name: learn
description: Project brain skill. Writes, reads, and maintains a .claude/brain.md file in the current project — storing conventions, decisions, pitfalls, and preferences that accumulate across sessions. Run at the end of any meaningful work session, or whenever something important is learned. Also reads the brain at the start of /explore and /retro.
triggers:
  - /learn
args: "[optional: 'show' to read the current brain | 'add [category]: [what to record]' | leave blank to run a guided end-of-session capture]"
---

# Learn

You are building the project brain — a structured memory file that persists knowledge across sessions so the next session doesn't start from zero.

This is not a log. It is a **living document** that gets more useful over time. Old entries get updated. Resolved pitfalls get removed. Preferences sharpen as the project evolves.

---

## Brain File Location

Every project that uses `/learn` gets a brain file at:
```
[project root]/.claude/brain.md
```

This file is read automatically by `/explore` and `/retro`. It is the first file Claude should read when resuming work on a project.

---

## When to Run This

- **End of a work session** — capture what was learned before context is lost
- **After a bug fix** — add the root cause to Pitfalls so it's not rediscovered
- **After a key decision** — add to Decisions so the next session knows why
- **After the user corrects Claude's approach** — add to Preferences immediately
- **When `/retro` surfaces a pattern** — add it to the brain so it persists

---

## Phase 1 — Determine Mode

### Mode A: `show`
If args contain "show" or "read", read `.claude/brain.md` and display it formatted. Report "No brain file exists yet" if it doesn't exist.

### Mode B: `add [category]: [entry]`
If args contain "add", parse the category and entry, then add it to the correct section of the brain file. Create the file if it doesn't exist.

### Mode C: Guided end-of-session capture (default, no args)
Ask the user a sequence of questions to extract learnings from the current session. Use `AskUserQuestion`.

---

## Phase 2 — Guided Capture (Mode C)

Ask these questions one at a time. Skip any where the answer would be "nothing" — don't force entries.

**Q1:** "What patterns or conventions did we establish or discover in this session?"
*(Examples: naming conventions, file structure choices, how something is organized in this codebase)*

**Q2:** "What decisions did we make that the next session should know about — and why were they made?"
*(Examples: chose X over Y because Z, deferred X because of constraint Y)*

**Q3:** "What broke, what was confusing, or what took longer than expected — and why?"
*(This becomes a Pitfall — so the same mistake isn't made again)*

**Q4:** "What does this project's owner want you to do differently or consistently going forward?"
*(Specific preferences: how they want output formatted, approaches to avoid, tools they prefer)*

After collecting answers (skip non-answers), write them to `.claude/brain.md`.

---

## Phase 3 — Write the Brain File

The brain file uses this structure. Create it if it doesn't exist; append to existing sections if it does.

```markdown
# Project Brain — [Project Name]

> Auto-maintained by /learn. Read this before starting any session on this project.
> Last updated: [date]

---

## Conventions
*How this project does things: naming, file structure, patterns, tech choices.*

- [entry]

---

## Decisions
*Why key choices were made. Prevents re-litigating settled questions.*

- **[Decision]:** [what was decided] — *Reason: [why]*

---

## Pitfalls
*What broke, what was confusing, what not to repeat.*

- **[Issue]:** [what happened] — *Root cause: [why]* — *Fix: [what resolved it]*

---

## Preferences
*How the project owner wants things done. These override defaults.*

- [preference entry]

---

## Open Questions
*Unresolved decisions or unknowns that need a decision.*

- [ ] [question]
```

**Writing rules:**
- Update "Last updated" date on every write
- If an entry in Pitfalls has been resolved and the fix is stable, move it to Decisions ("we learned X, now we always do Y")
- If a Preference contradicts a skill's default behavior, that Preference wins
- Keep entries terse — one line per entry where possible
- Remove entries that are no longer true (refactored away, reversed decisions)

---

## Phase 4 — Confirm and Report

After writing, confirm:

```
Brain updated at .claude/brain.md

Added:
  Conventions: [X new entries]
  Decisions:   [X new entries]
  Pitfalls:    [X new entries]
  Preferences: [X new entries]
```

If the brain file didn't exist before this session: "Brain created. This file will be read automatically at the start of future /explore and /retro sessions."

---

## Integration Points

### In `/explore`
Before exploring the codebase, check if `.claude/brain.md` exists. If it does, read it first and incorporate its contents into the exploration context — especially Conventions (shapes what you look for) and Pitfalls (flags known problem areas).

### In `/retro`
Read the brain before running the retrospective. The retro's learnings should be written back to the brain using `/learn add ...`.

### In `/reflect`
When a corrective improvement is made to a skill or rule file, add the lesson to Preferences so it's not just in the rule file but also in the project's brain.

---

## Output Format for `show` Mode

```markdown
## Project Brain — [name]
*Last updated: [date]*

### Conventions ([N entries])
[list]

### Decisions ([N entries])
[list]

### Pitfalls ([N entries])
[list]

### Preferences ([N entries])
[list]

### Open Questions ([N entries])
[list]
```

End with:
> Use `/learn add [category]: [entry]` to add a single entry, or run `/learn` again at end of session.

---

## Rules

- **One brain per project.** Always write to `[project root]/.claude/brain.md`, not a global file.
- **Update, don't append blindly.** If an entry would duplicate or contradict an existing one, update the existing one.
- **Preferences override skill defaults.** If the brain says "always use tabs for this project," that overrides any tool that defaults to spaces.
- **Pitfalls are temporary.** Once something is fixed and the fix is stable, the pitfall becomes a Decision or Convention and the pitfall entry is removed.
- **This is not a journal.** Don't record what you did — record what future-you needs to know. "Implemented the auth flow" is not a brain entry. "Auth uses session tokens stored in httpOnly cookies, not localStorage — changed after security review" is.
