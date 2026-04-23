---
name: advisor
description: Cross-model peer review. Takes an artifact (PRD, plan, code, spec, decision memo) and runs it past a DIFFERENT model than the one that authored it. Opus drafts → Sonnet or Haiku re-reads as an independent reader. Returns structured peer review — what's wrong, what's missing, what assumptions aren't defended, what to cut. Run before committing or sharing any single-model-authored artifact.
triggers:
  - /advisor
args: "[path to artifact file, or describe the artifact to review]"
---

# Advisor — Cross-Model Peer Review

You are the dispatcher for a second pair of eyes. Your job is to send an artifact to a DIFFERENT model than the one that wrote it, then return the advisor's feedback to the user.

The goal: catch what a single author misses. One model's blind spots are another model's obvious flags.

---

## How This Works

### Phase 1 — Identify the artifact

If the user gave a file path, read it.
If the user described the artifact, ask for the file path or the full content.

Artifacts this skill works on:
- PRDs, product specs, feature lists
- Plans (createplan output, architecture docs)
- Code (functions, files, diffs)
- Decision memos, pricing proposals
- Any single-author long-form output

### Phase 2 — Pick the advisor model

Use `AskUserQuestion`:

> "Who should review this? Pick a model different from the one that wrote it."

Options (detect author model if possible; exclude it):
- **Sonnet 4.6** — balanced, fast, good at spotting PRD/spec gaps
- **Haiku 4.5** — fastest, good for small artifacts
- **Opus 4.7** — deepest reasoning, slowest (use for critical reviews or when the author was Sonnet/Haiku)

Default recommendation: if author was Opus, use Sonnet. If author was Sonnet, use Opus. If author was Haiku, use Sonnet.

### Phase 3 — Spawn the advisor

Use the `Agent` tool with:
- `subagent_type: general-purpose`
- `model: <chosen>` (override to force the different model)
- Prompt the advisor with the review frame below

**Review frame (embed in Agent prompt):**

> "You are reviewing an artifact you did NOT write. Read it as an independent reader who has no stake in its conclusions. Your job is to challenge, not to validate.
>
> Produce a structured review with these sections:
>
> **1. Fundamental disagreements** — claims in the artifact you think are wrong. Quote the claim, state your position, explain why.
>
> **2. Missing content** — things a reasonable reader would expect that aren't there. Be specific about what's missing and why it matters.
>
> **3. Unsupported assumptions** — places the artifact asserts something without evidence. List each, and say what evidence would be needed to support it.
>
> **4. Scope issues** — features/sections/arguments that feel bloated, premature, or out of place. What should be cut?
>
> **5. What the author got right** — brief. 3–5 bullets. Just enough to confirm you read it fairly.
>
> **6. Top 3 changes to make** — prioritized. If the author only fixes three things, these are the three.
>
> Be direct. No hedging. No 'this is great but…' The author explicitly asked for critical review."

Pass the FULL artifact content to the advisor, not a summary.

### Phase 4 — Return the review

Write the review to `outputs/advisor/[artifact-slug]-reviewed-by-[model]-[date].md`.

Present to user:
- 2-line summary of advisor's biggest disagreement
- Link to full review file
- Ask: "Apply advisor's top 3 changes now, or let you read the full review first?"

### Phase 5 — Handoff

If user says apply: either edit the artifact directly (if small) or hand off to `/execute` with the advisor's change list as the plan.

If user says read first: stop. They'll come back.

---

## Rules

- **Always use a different model.** Never run advisor with the same model that authored the artifact. That defeats the entire skill.
- **Full artifact, not summary.** The advisor reviews what exists, not your description of what exists.
- **No synthesis bias.** Do NOT soften the advisor's feedback. Return it verbatim. Your job is dispatch, not diplomacy.
- **Single-pass only.** One advisor, one review. If user wants a second advisor, they invoke `/advisor` again.
- **Don't run this on artifacts authored by multiple models or humans.** This skill's value is catching single-model blind spots. Multi-author artifacts need a different review (`/peer-review` or the review agent).
