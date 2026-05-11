---
id: short-kebab-id
goal: One sentence describing the outcome. The agent succeeds when this is true.
files:
  - path/to/file/the/agent/will/likely/touch.ext
  - another/likely/file.ext
verify: |
  # Shell command(s) that exit 0 iff the task succeeded.
  # Runs from the worktree root after the agent finishes.
  # Examples:
  #   bun run typecheck && bun run test:unit
  #   pytest tests/test_foo.py
  #   test -f docs/new-page.md && grep -q "Expected heading" docs/new-page.md
  echo "REPLACE WITH REAL VERIFIER" && false
constraints:
  - Do not modify files outside the `files` list unless strictly necessary.
  - Match the surrounding code style.
  - Do not add new dependencies.
---

# Task: <human-readable title>

## Context
Two or three sentences explaining the WHY. What is the user trying to achieve at the project level, and how does this task contribute? An agent reading this in isolation should understand the point of the work.

## What to do
A specific, ordered list of changes. Avoid hand-waving.

1. Open `path/to/file.ext`.
2. Locate the function `foo()`.
3. Replace the body with the implementation described below.
4. Update the call sites in `path/to/other.ext`.

## Implementation notes
Anything non-obvious: edge cases, gotchas, references to existing patterns in the codebase the agent should match.

## Out of scope
List anything the agent might be tempted to "improve" but should not touch. This is critical — vague task specs lead to drive-by refactors that break the verifier.
