---
name: createplan
description: Creates a structured implementation plan document. Invoke after /explore Q&A is complete and all ambiguities are resolved. Produces a markdown plan with steps, subtasks, key decisions, and risks.
---

Based on everything discussed during `/explore` and our Q&A, produce a plan document.

The plan is a shared artefact — it's how we track what's being built, in what order, and why. It is **not** the time to write code. Clarity and brevity matter more than completeness.

---

## SOP — Constraints / Reference / Output Format

**Constraints:**
- Every step must have: `id`, `title`, `verify`, `est_minutes`, `depends_on` (list of step ids), `risk` (P0/P1/P2). No step without a verify check.
- A step is "done" only when its verify passes. "I think it works" is not done.
- Risk-first ordering: P0-risk steps run before P1, P1 before P2 — even if it means doing the hard thing first. Discovering a problem in step 1 is cheaper than step 8.
- A spike step (unresolved decision) must come before any step it could change.
- No step longer than 60 minutes of work. Break it down further.

**Reference:**
- Output shape: linear list of typed tasks with explicit verify + dependencies. Risk-first ordering (P0 before P1 before P2).
- Each step is small enough to verify in one pass — break further if a step exceeds 60 minutes of estimated work.

**Output Format:**
1. `outputs/<slug>/plan.md` — narrative for humans.
2. `outputs/<slug>/plan.json` — machine-readable. Schema:

```json
{
  "$schema": ".claude/schemas/plan.schema.json",
  "version": "1.0",
  "feature": "...",
  "total_est_minutes": 240,
  "steps": [
    {
      "id": "P-01",
      "title": "Add migration for orders.shipping_method",
      "subtasks": ["..."],
      "verify": "psql -c '\\d orders' shows shipping_method column",
      "est_minutes": 15,
      "depends_on": [],
      "risk": "P0",
      "files_touched": ["supabase/migrations/<ts>_orders_shipping_method.sql"]
    }
  ],
  "decisions": [
    { "id": "D-01", "decision": "...", "alternatives_rejected": [], "why": "..." }
  ],
  "risks": [
    { "id": "R-01", "risk": "...", "mitigation": "...", "step_ids": ["P-01"] }
  ],
  "open_questions": []
}
```

**`open_questions` must be empty.** Resolve before producing the plan.

---

---

## Step 0 — Dependency & Risk Analysis (do this before writing the plan)

Before ordering any steps, answer three questions explicitly:

**1. What depends on what?**
List the dependency chain between planned pieces of work. A step that another step relies on must come first. Common patterns:
- DB schema before any code that reads/writes it
- Auth layer before any route that requires ownership checks
- Shared types/interfaces before both producer and consumer
- External API integration before any feature that calls it

If two steps have no dependency relationship, they can be done in any order — note that explicitly.

**2. Where are the unknowns?**
Any question from `/explore` that wasn't fully resolved is an unknown. Unknowns that could change the implementation become their own first step: a **spike step** — a short investigation that produces a decision, not working code. Don't bury an unresolved question in Step 3; surface it as Step 1.

**3. What are the high-risk steps?**
High-risk = steps touching auth, DB schema changes, external integrations, or areas flagged as fragile during exploration. These should come early — not because they're easy, but because discovering a problem in Step 1 is cheaper than discovering it in Step 5.

Order the steps by: unresolved spikes first → high-risk/foundational next → lower-risk/dependent last.

---

## Confidence Check (do this after drafting the plan)

Before presenting the plan, run this check on every step:

> "If I started implementing this step right now, would I need to come back and ask a clarifying question?"

If yes: either resolve the question in the plan itself (add a decision under Key Decisions), or convert the ambiguous part into a spike subtask at the top of that step.

A plan with 3 well-understood steps is better than 7 steps with hidden assumptions.

---

## What to produce

A markdown plan document using the template below. Fill every section — don't skip any, don't add sections that aren't in the template.

**Step sizing:** Each step should be roughly one session's worth of work — focused enough to complete and verify in one sitting, large enough to deliver something meaningful. If a step feels too big, split it. If two steps feel inseparable, merge them.

**Scope discipline:** Only include what was explicitly discussed and agreed during exploration. If something seems obviously useful but wasn't discussed, put it in "Out of Scope" — not in the tasks.

---

## Template

```markdown
# [Feature Name] — Implementation Plan

**Status:** `0% complete` — update this manually as steps finish.

---

## What we're building
One or two sentences. What does this add or fix, and why does it matter?

---

## Out of Scope
Things we are explicitly NOT building in this plan. List them so there's no ambiguity later.
- ...

---

## Key Decisions
Architectural and implementation choices locked in during exploration. For each, note what was chosen, what was considered and rejected, and why.

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| ... | ... | ... | ... |

---

## Steps

### 🟥 Step 1: [Name]
**Goal:** One sentence — what does completing this step achieve?
**Files touched:** `src/path/to/file.ts`, `supabase/migrations/...`

- 🟥 Subtask A
- 🟥 Subtask B
- 🟥 Subtask C

---

### 🟥 Step 2: [Name]
**Goal:** ...
**Files touched:** ...

- 🟥 Subtask A
- 🟥 Subtask B

---

## Risks & Watch-outs
Anything flagged during exploration that could cause problems. Keep this visible — don't bury it.
- ...
```

---

## Status key

| Emoji | Meaning |
|-------|---------|
| 🟥 | To do |
| 🟨 | In progress |
| 🟩 | Done |

Update step and subtask emojis as work progresses. Update the top-line status percentage when a step completes.

---

Once the plan is reviewed and agreed, move to `/execute`.
