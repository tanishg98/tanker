---
name: reflect
description: Self-improvement skill. Auto-invoked when a step is blocked, something goes wrong during implementation, or the user gives corrective feedback ("no, don't do that", "that was wrong", "instead do X", "stop doing Y"). Traces the failure to the responsible skill/agent/rule file, proposes a surgical improvement, and applies it after approval. Also invoke manually with /reflect to capture a learning from the current session.
allowed-tools: Read, Edit, Glob, Grep
---

You are in **Reflection Mode**. Something went wrong, or the user has given corrective feedback. Your job is to improve the config files so this doesn't happen again.

Do not defend the current config. Do not explain why it was written that way. Just figure out what to fix and fix it.

---

## Step 0 — Check Prior Failures

Before diagnosing, read `.claude/reflect-log.md` if it exists.

Scan the log for entries that describe a similar failure — same skill, same symptom, or same class of problem.

**If this failure has been logged before:**
- Note the previous entry (date, file, what was fixed)
- Check the current config file to confirm whether that fix was actually applied
- If the fix is **missing from the file**: it was agreed but never applied, or was reverted. Re-apply it immediately — skip to Step 4, no need to re-diagnose
- If the fix is **present but the failure recurred**: the fix was insufficient or addressed the wrong root cause. Go through the full flow, but go one level deeper than last time

**If this is a new failure:** proceed to Step 1.

---

## Step 1 — Name what went wrong

Write one sentence that describes the specific failure or feedback. Be concrete:

- "The execute skill didn't stop when it hit a file that didn't exist — it improvised instead."
- "The explore agent listed files that don't exist yet."
- "User corrected: don't summarise what you just did at the end of every response."
- "Step 2 went off-plan because the skill didn't make the constraint explicit enough."

If there are multiple issues, handle them one at a time.

---

## Step 2 — Trace to the root config

Ask: which skill, agent, or rule file should have prevented this — or caused it?

Check these locations:
- `.claude/agents/` — failures during explore or review
- `.claude/skills/` — failures during a specific workflow
- `.claude/rules/` — always-on standards that weren't followed

Read the relevant file. Find the specific section that:
- Was **missing** — no instruction covered this case
- Was **wrong** — gave the wrong instruction
- Was **ambiguous** — could reasonably be interpreted multiple ways
- Was **too weak** — said "prefer X" when it should say "always X" or "never Y"

If the failure wasn't caused by any config file (e.g. it was an external API error, a missing dependency, or a one-off user decision), say so clearly and stop. Not every failure means the config was wrong.

---

## Step 3 — Propose a targeted improvement

Show a clear before/after for the specific section to change. Keep it minimal — change only what's needed to prevent this specific failure.

Use this format:

```
**File:** `.claude/skills/execute/SKILL.md`
**Section:** [section name or brief description]

**Before:**
[current text — exact quote]

**After:**
[improved text]

**Why:** [one sentence — what failure this prevents]
```

If the issue requires adding a new instruction rather than modifying an existing one, show the addition in the same format with "Before: *(nothing)*".

If the improvement belongs in a new rule file under `.claude/rules/`, propose that instead.

---

## Step 4 — Get approval, then apply

Ask: *"Apply this change?"*

Wait for explicit confirmation before editing any file. Once approved:
1. Apply the edit using the Edit tool
2. Confirm the change was applied

---

## Step 5 — Log the improvement

Append a one-line entry to `.claude/reflect-log.md` (create the file if it doesn't exist):

```markdown
- **[YYYY-MM-DD]** `[file]` — [what was wrong → what was fixed]
```

Example:
```markdown
- **2026-03-14** `.claude/skills/execute/SKILL.md` — skill didn't enforce stopping when a referenced file was missing → added explicit rule to stop and report rather than improvise
```

---

## Rules

- **One issue, one fix.** Don't use a single failure as an excuse to rewrite a whole file. Surgical edits only.
- **Smallest change that prevents the specific failure.** Don't gold-plate.
- **Don't invent problems.** Only improve for what actually went wrong, not what might go wrong.
- **If the config was right**, say so. Attribute the failure correctly — don't blame the config for execution errors.
- **Don't change tone or style** of the target file unless that was the problem. Match the existing voice.
