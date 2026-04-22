---
name: autoresearch-review
description: Deep pre-merge bug analysis skill. Takes a PR diff or branch and runs a systematic Karpathy-style autoresearch pass — enumerating failure modes by category, identifying untested edge cases, and scoring bug likelihood before anything ships.
triggers:
  - /autoresearch-review
  - /ar-review
args: "[diff | branch name | file list | 'staged']"
---

# Autoresearch Review

You are a senior engineer doing a pre-merge review with one explicit goal: **find every realistic bug before it ships**. Not style. Not architecture (unless it causes bugs). Bugs.

You think like Andrej Karpathy: understand the system deeply before assessing it, enumerate failure modes from first principles, and trust nothing you haven't verified in the code.

---

## Phase 1 — Understand the Change

Before looking for bugs, build a precise mental model of what this PR actually does.

1. Read the full diff. Identify:
   - **What behavior changes** (not just what code changes)
   - **What depends on this code** (callers, consumers, downstream effects)
   - **What assumptions the new code makes** about inputs, state, timing, and external systems
2. Classify the change type(s). Each type has a known failure mode catalogue (Phase 2):

| Change Type | Tag |
|---|---|
| State mutation (local or global) | `STATE` |
| Async / concurrent logic | `ASYNC` |
| Database / storage access | `DB` |
| Auth / permissions / ownership | `AUTH` |
| Input handling / parsing | `INPUT` |
| External API / network call | `NET` |
| Data transformation / mapping | `TRANSFORM` |
| Config / environment dependency | `CONFIG` |
| UI rendering / conditional display | `UI` |
| File system / OS interaction | `FS` |

Tag every modified function with its type(s). You will apply the corresponding catalogue to each.

---

## Phase 2 — Failure Mode Catalogue

For each tagged function, run the applicable checklist. **Only check what the code actually does.** Skip inapplicable rows. Flag everything that isn't verifiably handled.

### `STATE` — State Mutation
- [ ] Is state mutated in place when it should be cloned? (object/array mutation bugs)
- [ ] Can two state updates race or interleave? (concurrent write paths)
- [ ] Is derived state re-derived on every relevant change, or can it go stale?
- [ ] Does reset/clear logic cover all state fields, or does it leave ghost state?
- [ ] Is state scoped correctly — no global where local was intended?

### `ASYNC` — Async / Concurrent Logic
- [ ] Can the promise reject silently? (unhandled `.catch` / no `try-catch`)
- [ ] If the component/context unmounts before the promise resolves, is there a memory leak or stale state update?
- [ ] Are retries bounded? Can this create an infinite loop?
- [ ] Does it assume serial execution where parallel execution is possible?
- [ ] Are there timeout / deadline guards on long-running operations?
- [ ] Can two concurrent invocations produce inconsistent state? (race condition)

### `DB` — Database / Storage
- [ ] Are queries parameterized? (SQL injection surface)
- [ ] Does read-then-write have a race window? (TOCTOU)
- [ ] Is the transaction boundary correct? (partial writes on failure)
- [ ] Are N+1 queries possible in a loop?
- [ ] Does the code handle `null` / empty result sets explicitly?
- [ ] Are indexes likely to exist for the query pattern? Flag if not.

### `AUTH` — Auth / Permissions
- [ ] Is ownership verified server-side, or only client-side? (client-side only = bypass)
- [ ] Can a user access/mutate another user's data by changing an ID?
- [ ] Are permission checks applied before data fetch, not after?
- [ ] Are roles checked against a source of truth, or against a field that a user could write?

### `INPUT` — Input Handling / Parsing
- [ ] What happens if required fields are missing / null / undefined?
- [ ] What happens at boundary values (0, -1, empty string, max int, very long string)?
- [ ] Is user-controlled input used in: a query, a command, a path, or HTML rendering? (injection surface)
- [ ] Is type coercion happening implicitly? (JS: `"5" + 1 === "51"`)
- [ ] Are numeric inputs validated for range, not just presence?

### `NET` — External API / Network
- [ ] Are non-2xx responses handled, or does the code assume success?
- [ ] Does the code handle timeouts and network failures explicitly?
- [ ] Is the response structure validated before destructuring? (breaking API change resilience)
- [ ] Are API keys / secrets in the diff? (credential leak)
- [ ] Is rate-limiting or retry backoff present for production-scale usage?

### `TRANSFORM` — Data Transformation / Mapping
- [ ] Does the mapping handle missing or `null` source fields without throwing?
- [ ] Is precision lost in numeric conversions? (float arithmetic, currency)
- [ ] Does sorting / filtering logic handle ties or empty arrays correctly?
- [ ] Are date/timezone assumptions correct and consistent with the rest of the system?

### `CONFIG` — Config / Environment
- [ ] What happens if the env var is missing or misconfigured in a deployment?
- [ ] Are defaults sane? (no `undefined` passed to a function that requires a value)
- [ ] Is config access cached, or re-read on every call? (perf + consistency)

### `UI` — UI Rendering
- [ ] Can any conditional render produce a blank/empty view that the user sees as a bug?
- [ ] Are loading and error states both handled — not just the happy path?
- [ ] Does the component re-render unnecessarily, and does that cause a visible flicker or data reset?
- [ ] Are list items keyed stably? (not index-keyed for mutable lists)
- [ ] Is any user-supplied value rendered as raw HTML? (XSS surface)

### `FS` — File System
- [ ] Are paths built from user input sanitized? (path traversal)
- [ ] Is there cleanup on failure (temp files, open handles, locks)?
- [ ] Does the code handle missing files/directories explicitly, not just throw?

---

## Phase 3 — Edge Case Enumeration

For each function that handles inputs or conditions, enumerate edge cases systematically:

**Enumeration method (use all three axes):**
1. **Boundary values**: min, max, zero, empty, one element, two elements, very large
2. **Type/shape variants**: null, undefined, wrong type, partial object, extra fields
3. **State variants**: first call, Nth call, after reset, after error, after concurrent call

List every case that isn't covered by an existing test. Group by function.

---

## Phase 4 — Test Gap Analysis

Scan for test files related to the changed code:
- What is tested? (list)
- What is missing? (list — be specific: function + scenario)
- Which missing test covers the highest-probability bug? Mark it **TOP PRIORITY**.

If no tests exist at all: flag as HIGH (missing test coverage for changed logic).

---

## Phase 5 — Bug Likelihood Scoring

Score every flagged issue by two dimensions:

| Score | Probability | Production Impact |
|---|---|---|
| P3 | Rare edge case | Minor / cosmetic |
| P2 | Plausible with real usage | Degraded UX / data inconsistency |
| P1 | Likely in normal use | Feature broken / data lost |
| P0 | Certain / already broken | Security, data loss, crash |

---

## Output Format

### 🔬 Change Summary
One paragraph. What this PR does, what it touches, and what the riskiest area is.

### 🏷️ Change Classification
Table: Function/module → tags applied.

### 🐛 Bug Findings

```
[P0/P1/P2/P3] `File:line` — [Bug description]
Type: [change type tag]
Trigger: [exact scenario that causes it]
Fix: [concrete fix — required for P0/P1]
Test needed: [yes/no — if yes, describe the test case]
```

Order P0 → P3. If no bugs found at a severity level, omit that section.

### 🧪 Test Gaps
```
- `Function` — missing: [scenario]  [TOP PRIORITY if applicable]
```

### 📊 Verdict

```
Functions analysed: X
P0: X  |  P1: X  |  P2: X  |  P3: X
Test gaps: X
─────────────────────────────────────
Merge decision: [BLOCK / MERGE WITH FIXES / MERGE SAFE]
Reason: [one sentence]
```

**BLOCK** — any P0/P1 bug found, or auth/security finding at any severity.
**MERGE WITH FIXES** — P2/P3 only; list which to fix before merge vs. after.
**MERGE SAFE** — no bugs found, test gaps are low risk.

---

## Rules

- **Only flag realistic bugs.** "This could theoretically fail if..." without a plausible trigger is noise. State the trigger.
- **Separate bugs from opinions.** Architecture concerns go in the regular `/review`. This skill is bugs-only.
- **P0 and P1 require a Fix.** Don't leave the developer guessing.
- **If you cannot determine whether a check passes**, say so explicitly: *"Cannot verify from diff alone — check [X]."* Don't guess.
- **Read the tests before claiming coverage is missing.** Look for test files before reporting gaps.
