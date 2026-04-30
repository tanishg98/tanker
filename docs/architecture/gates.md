# Human gates

`/cto` autopilot has **two mandatory human review gates**, both pre-qualified by review agents.

## Why

Most autopilots either go fully autonomous (and ship slop) or stop at every phase (and waste owner time). Tanker stops twice — at the points where human judgment compounds:

- **Gate 1 (PRD):** before code is written. If the PRD is wrong, the build is wrong.
- **Gate 2 (MVP):** before production deploy. If the MVP is wrong, the deploy is wrong.

Between gates, agents handle the work autonomously.

## Pre-qualification

Each gate is preceded by a review agent (`prd-reviewer`, `mvp-reviewer`) that runs an exhaustive check. The owner only sees the gate after the agent returns `PASS` or `PASS_WITH_FIXES`. On `BLOCK`, the relevant skill is re-dispatched (max 2 retries) before the gate is shown.

This means: when you see a Tanker review gate, the artifact has already passed an automated pre-check. Your time is spent on the questions only a human can answer.

## Gate 1 — PRD review

Triggered after `/prd` and `prd-reviewer` PASS. You see:

```
✋ PRD ready for review
Open: outputs/<slug>/prd/index.html
Read: outputs/<slug>/prd/prd.md

prd-reviewer verdict: PASS

Reply with:
  "approved"        — proceed to /architect
  "fix: <feedback>" — re-run /prd with this feedback
  "abort"           — stop, keep state.json for resume
```

## Gate 2 — MVP review

Triggered after the local build passes `mvp-reviewer`. Local server is running. You see:

```
✋ MVP ready for review
Open: http://localhost:3000

mvp-reviewer verdict: PASS WITH FIXES
  - HIGH: keyboard trap on /settings modal
  - MEDIUM: 404 page missing

Coverage:
  Screens: 9/9 · Features: 47/47 · Golden paths: 6/6

Reply with:
  "approved"
  "fix: <feedback>"
  "abort"
```

## Skipping gates

`--full-auto` skips both gates. Not recommended for a new product. Acceptable for repeat runs of a known-shape product, or for rapid spike-and-throw work.

## Resume across gates

If you `abort` at a gate, `state.json` retains the human gate state. `/cto --resume <slug>` returns to the same gate.
