---
name: verify
description: Outcomes-style rubric grader. Given an artifact (file, branch, PR, report) and a rubric (`.claude/rubrics/<name>.yaml`), produces a score, a pass/fail verdict, and a specific list of fixes if it fails. Used standalone or as a gate inside `/cto`, `/swarm`, and `/overnight`. Closes the gap exposed by the Anthropic Outcomes feature: "hope the agent produced good output" → "grade it against a rubric and iterate."
argument-hint: "<artifact-path-or-PR-#> <rubric-name>  [--fix]  [--max-iter 3]"
---

# /verify — Rubric-Graded Verification

You are running **Verify**. You take an artifact and a rubric, you grade the artifact against the rubric line by line, and you report a verdict plus specific fixes.

This is Tanker's answer to "Outcomes" in the Claude Managed Agents API: explicit success criteria, machine-graded, with an iterate-to-green option.

---

## Why this exists

Review agents return vibes ("looks good"). Rubrics return scores. Vibes don't compose — you can't gate a pipeline on "looks good." Scores do — you can gate on `score >= 0.85 AND no_critical_failures`.

Existing Tanker review surface:
- `review` agent — generalist quality check, qualitative
- `pre-merge` agent — pre-PR gate, qualitative
- `mvp-reviewer`, `prd-reviewer`, `site-eval` — domain-specific qualitative gates
- `/autoresearch-review` — Karpathy-style bug analysis

`/verify` adds the missing axis: **structured, rubric-graded, iterable**. The qualitative agents stay; verify is for the cases where you want a deterministic pass/fail.

---

## Rubric format

Rubrics live in `.claude/rubrics/<name>.yaml`. Schema:

```yaml
name: prd-quality
description: Grades a PRD against Tanker's exhaustiveness standard
applies_to: "outputs/*/prd.md"        # optional glob, for auto-pick

# Each criterion is graded 0.0 - 1.0 by Claude. Critical criteria failing -> FAIL regardless of total.
criteria:
  - id: features_enumerated
    weight: 0.15
    critical: false
    check: "Every user-visible feature is listed with name, user value, acceptance criteria."

  - id: screens_x_states
    weight: 0.15
    critical: false
    check: "Each screen has all states enumerated: empty, loading, error, success, edge cases."

  - id: html_mocks_present
    weight: 0.10
    critical: true
    check: "At least one HTML mock exists per primary screen. Mocks are linked or embedded."

  - id: no_ai_slop
    weight: 0.10
    critical: true
    check: "No purple/violet gradient. No 'unlock the power of' copy. No icon-in-circle 3-col feature grids."

  - id: success_metrics
    weight: 0.10
    critical: false
    check: "Success metrics are quantitative and time-bounded, not 'users love it'."

# Verdict thresholds
pass_threshold: 0.85
conditional_threshold: 0.70
# < 0.70 OR any critical failing -> FAIL
```

Rubric library to seed (commit these in `.claude/rubrics/`):
- `prd-quality.yaml`
- `static-site.yaml` (mirrors `static-site-standards.md` rules)
- `pr-readiness.yaml` (lint + tests + diff size + commit message style)
- `mvp-shippable.yaml` (functional + deployed + smoke tested + monitoring on)
- `brain-md-entry.yaml` (specific, reusable, non-obvious — same gates as `/compound`)

---

## How you operate

### 1. Resolve inputs

- `<artifact>` may be: a file path, a directory, a branch (`branch:feat/x`), or `pr:<number>`. Resolve to concrete content.
- `<rubric-name>` may be: a name (looked up in `.claude/rubrics/<name>.yaml`) or a full path. If omitted and the artifact matches a rubric's `applies_to` glob, auto-pick.

### 2. Grade

For each criterion in the rubric:
- Read the relevant slice of the artifact (don't try to fit the whole thing in one shot — use Grep/Read targeted at what the `check:` describes)
- Score 0.0–1.0 with a one-sentence justification
- If `critical: true` and score < 0.7, flag as a critical failure

Compute `total = sum(weight * score) / sum(weight)`.

Verdict:
- `PASS` if `total >= pass_threshold` AND no critical failures
- `CONDITIONAL` if `total >= conditional_threshold` AND no critical failures
- `FAIL` otherwise

### 3. Report

```
## /verify — <rubric-name> on <artifact>

**Verdict: PASS** (score 0.91)

| criterion | weight | score | note |
|---|---|---|---|
| features_enumerated | 0.15 | 1.0 | All 12 features have user value + AC |
| screens_x_states | 0.15 | 0.8 | error state missing on settings screen |
| html_mocks_present | 0.10 | 1.0 | 4 mocks present |
| no_ai_slop | 0.10 | 1.0 | clean |
| success_metrics | 0.10 | 0.9 | "<2s p95 load" is quantitative |

### Fixes (if any) — sorted by impact
1. Add error state to settings screen (+0.03 total)
```

For FAIL, replace the "Fixes" section with a numbered list of the smallest set of changes that would flip the verdict to PASS.

### 4. --fix loop (optional)

If `--fix` was passed and verdict is FAIL or CONDITIONAL:
- Generate a fix brief listing exactly the changes needed
- Spawn `/execute` against the fix brief (in the same context, not a subagent)
- Re-run `/verify` on the modified artifact
- Loop up to `--max-iter` (default 3)
- Stop on PASS, on max iterations, or when score does not improve between iterations (avoids oscillation)

This is the article's "iterate to green" loop. Off by default — opt in with `--fix`.

### 5. Memory ledger

Append one line to `outputs/verify/log.jsonl`:
```json
{"ts":"2026-05-17T10:30:00Z","artifact":"outputs/x/prd.md","rubric":"prd-quality","verdict":"PASS","score":0.91,"iterations":1}
```

---

## Composition with other skills

- `/cto` Gate 1 (PRD approval) — gate on `/verify <prd-path> prd-quality` returning PASS before pinging the human
- `/cto` Gate 2 (MVP approval) — gate on `/verify <preview-url> mvp-shippable` returning PASS
- `/swarm` task `verify:` field — can call `/verify` instead of (or alongside) a shell command
- `/overnight` — pre-bedtime sanity check: `/verify HEAD pr-readiness` on every queued brief
- Stop-hook auto-review — instead of free-form review, run `/verify HEAD pr-readiness`

---

## Hard rails

- **Never auto-pass a critical failure.** A rubric that marks `no_ai_slop: critical` means even 0.99 elsewhere returns FAIL if slop is present.
- **No invented criteria.** Grade only what's in the rubric. If you think a criterion is missing, propose it as a new rubric entry — don't silently grade against it.
- **No fix-loop without `--fix`.** Default behavior is grade-and-report. The user opts in to mutation.
- **No fix-loop on FAIL with critical failures unless the fix is mechanical.** Critical failures usually need a design conversation, not a patch. Surface to the user.
- **Rubrics live in the repo.** This makes the standard versioned and reviewable. Never grade against an in-line rubric defined in the prompt — that's vibes with extra steps.

---

## Handoff

- PASS → "Verify passed. Run `/ship` to open the PR?" or hand back to the calling skill
- CONDITIONAL → "Conditional pass — N improvements would push to PASS. Apply? (`/verify ... --fix`)"
- FAIL → "Failed. Top fix: <one line>. Re-run after fixing, or run with `--fix` to attempt automated repair."
