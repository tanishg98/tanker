---
name: test-gen
description: Generates targeted tests for untested code paths. Invoke after /autoresearch-review surfaces test gaps, or directly on any function/module. Writes the minimum tests needed to catch the highest-probability bugs — not ceremonial coverage padding.
triggers:
  - /test-gen
args: "[file path | function name | 'gaps from autoresearch-review' | diff]"
---

# Test Gen

You are writing targeted tests to catch real bugs — not to inflate coverage numbers. Every test you write must be traceable to a specific failure mode that could exist in this code.

---

## Phase 0 — Framework Detection

Before writing a single test, identify the test framework in use.

**Check in this order:**
1. Config files: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `setup.cfg`, `pyproject.toml`, `.mocharc.*`, `karma.conf.*`
2. `package.json` — look at `scripts.test` and `devDependencies`
3. Existing test files — check imports (`import { describe } from 'vitest'`, `import pytest`, etc.)
4. Directory names: `__tests__/`, `spec/`, `tests/`

**If a framework is found:** State it at the top of your output — e.g. *"Framework: Vitest (detected from vitest.config.ts)"* — then continue.

**If no framework is found:**
- List the frameworks appropriate for this tech stack (e.g. for a Node/TS project: Jest or Vitest; for Python: pytest)
- Recommend one with a one-line justification
- **Stop here.** Do not write tests without a framework in place. Output:

```
⚠️ No test framework detected.

Recommended: [framework] — [one-line reason]

Set it up first, then re-run /test-gen.

Setup steps:
[3–5 concrete commands to install and configure it]
```

---

## Phase 1 — Read Before Writing

1. Read the function(s) to be tested in full. Understand:
   - What it does (inputs → outputs → side effects)
   - What it assumes about its inputs
   - What it calls (dependencies to mock or use real)
2. Read any existing tests for this code. Do not duplicate what's already tested.
3. Identify the project's test framework and patterns (Jest, Vitest, pytest, etc.) — match them exactly.

---

## Phase 2 — Enumerate Test Cases

For each function, generate test cases across three axes:

**Axis 1 — Happy path** (what the tests probably already cover)
- Standard input → expected output
- Skip if already tested

**Axis 2 — Boundary / edge cases** (where bugs live)
- Empty / null / undefined inputs
- Single element vs. collection
- Zero, negative, maximum values
- First call, Nth call, call after reset

**Axis 3 — Failure modes** (what `/autoresearch-review` or logic analysis flagged)
- Each flagged scenario gets exactly one test
- Name the test after the scenario: `"returns null when userId is missing"` not `"test case 3"`

Rank all cases by bug probability. Write highest-probability tests first.

---

## Phase 3 — Write the Tests

Follow these rules:

**Structure (AAA — required)**
```
// Arrange — set up state, inputs, mocks
// Act     — call the function
// Assert  — verify output and side effects
```

**Naming**
- Format: `[function] [scenario] [expected outcome]`
- Example: `getUser returns null when userId is undefined`
- No "should" — say what it does, not what it should do

**Mocks**
- Mock at the boundary (external APIs, DB, file system) — not in the middle of business logic
- Use the project's existing mock patterns exactly
- Verify mock calls when the side effect is the point of the test

**Assertions**
- Assert the specific value, not just that something exists
- For error cases: assert both that an error is thrown AND the error type/message
- Don't assert implementation details (which internal function was called) — assert behavior

**One concern per test.** A test that checks three things is three tests.

---

## Output Format

### 📋 Test Plan
```
Function: [name]
File: [path]
Existing tests: [count / "none"]
New tests to write: [count]
Skipped (already covered): [list]
```

### 🧪 Generated Tests

Provide complete, runnable test code. Include:
- Required imports at the top
- Any shared setup (beforeEach, fixtures)
- Each test with AAA comments on first occurrence

Group tests by function. Order: boundary cases first, then failure modes, then happy path (if not already covered).

### 📊 Coverage Impact
```
Functions covered: X/X in scope
Key risks now tested: [list the P0/P1 scenarios from autoresearch-review that are now covered]
Remaining gaps: [any cases intentionally not written and why]
```

---

## Rules

- **Read existing tests first.** Never duplicate a test that already exists.
- **Match the project's test style exactly.** If the project uses `describe` blocks, use them. If it uses `it`, use `it`.
- **No ceremonial tests.** A test that passes trivially and catches nothing is worse than no test — it creates false confidence.
- **Bug-probability first.** If you can only write 3 tests, write the 3 most likely to catch a real production bug.
- **Don't test the framework.** Don't test that `parseInt("5") === 5`. Test your code's logic.
