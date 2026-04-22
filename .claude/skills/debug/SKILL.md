---
name: debug
description: Systematic debugging skill. Invoke when a bug exists but the cause is unknown. Traces failure from symptom to root cause using a structured elimination method — never guess-and-check.
triggers:
  - /debug
args: "[symptom description | error message | failing test | 'I don't know where to start']"
---

# Debug

You are debugging this problem systematically. No guessing. No random edits. Every hypothesis is tested against evidence before the next one is formed.

---

## Phase 1 — Understand the Symptom Precisely

Before touching any code:

1. **Restate the symptom exactly**: What is observed? What was expected? What is the delta?
2. **Reproduce it**: Can you reproduce it from a clean state? Is it consistent or intermittent?
3. **Scope it**: When did it start? After what change? What conditions are required?
4. **Identify the blast radius**: What other behavior might be affected?

Do not proceed to Phase 2 until you can state: *"When [X], the system does [Y] instead of [Z]."*

---

## Phase 2 — Locate the Failure Layer

Trace the execution path from symptom back to source. Start at the output (what you observe), not the input (where you guess the bug is).

**Execution layers to trace (top-down from symptom):**

```
UI / Output
    ↓
Data transformation / mapping
    ↓
Business logic / state management
    ↓
Data access / API call
    ↓
Input / trigger
```

At each layer, ask: *"Is the data correct at this point?"* Use the minimum number of reads to eliminate layers.

**Elimination method:**
- Read the code at the symptom layer first
- If data is wrong here, move one layer deeper
- If data is correct here, the bug is above this layer
- Continue until you find the layer where data first becomes wrong

---

## Phase 3 — Form One Hypothesis

State a single, falsifiable hypothesis:

> *"I believe the bug is in [function/line], caused by [mechanism], triggered when [condition]."*

Then find evidence that would **disprove** this hypothesis (not confirm it). If you can't find disconfirming evidence, the hypothesis stands.

---

## Phase 4 — Verify Without Changing Code

Before writing any fix:
- Trace the failing path through the code manually
- Identify the exact line where behavior diverges from expected
- Confirm what the value actually is at that line (via logs, tests, or reading the logic)

State: *"The bug is on line X: [what happens] instead of [what should happen]."*

---

## Phase 5 — Fix Surgically

Fix the smallest possible change that corrects the root cause. Do not:
- Refactor surrounding code
- Add "defensive" checks for unrelated cases
- Change behavior in code paths that aren't involved in the bug

After fixing: verify the original symptom is gone and no adjacent behavior changed.

---

## Output Format

### 🔍 Symptom
Exact restatement: when X, system does Y instead of Z.

### 🗺️ Traced Path
```
Layer: [name]
Status: correct / incorrect / unknown
Evidence: [what you read to determine this]
```
(One entry per layer examined)

### 🎯 Root Cause
```
File: [path:line]
Mechanism: [what the code does wrong]
Trigger: [the exact condition that causes it]
```

### 🔧 Fix
```
Before: [code]
After:  [code]
Rationale: [one sentence — why this is the right fix, not a workaround]
```

### ✅ Verification
How to confirm the fix works and nothing regressed.

---

## Rules

- **One hypothesis at a time.** Don't maintain two competing theories — eliminate one first.
- **Read before writing.** Never change code without reading and understanding the exact line that's wrong.
- **Don't fix symptoms.** A try-catch around the crash is not a fix. Find what caused the throw.
- **Note the trigger, not just the location.** A bug location without its trigger is useless — you need to know what condition activates it.
