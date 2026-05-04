---
name: ship
description: Complete release workflow — from working code to open PR. Syncs with main, runs tests, stages changes, pushes to remote, and opens a structured pull request. Run after /execute and /autoresearch-review when you're ready to ship. Replaces the ad-hoc "git push and hope" pattern.
triggers:
  - /ship
args: "[optional: PR title | 'draft' to open as draft PR | leave blank for guided mode]"
---

# Ship

You are the release engineer. Your job is to take working code from the current branch and prepare it for merge — cleanly, completely, and without surprising anyone on the other side.

This is not a shortcut. It is a checklist that runs fast because it is automated.

---

## Pre-Flight Check

Before doing anything, answer these:

1. **Are we on a feature branch?** Check with `git branch --show-current`. If on `main` or `master`, stop and warn: "You are on the main branch. Create a feature branch first."

2. **Is there a pre-merge gate?** If `.claude/agents/pre-merge.md` exists, it should have been run before `/ship`. If the user hasn't run it, warn: "Run `pre-merge` agent before shipping — it catches bugs that pass CI. Skip only if this is a hotfix or trivial change."

3. **Does a test framework exist?** Check for `package.json` with test scripts, `pytest.ini`, `go.mod`, etc. If found, run tests. If they fail, stop — do not ship failing code.

---

## Phase 1 — Sync with Main

```bash
git fetch origin
git status
```

Check: is the current branch behind `origin/main`? If yes:

```bash
git merge origin/main --no-edit
```

If there are merge conflicts:
- List the conflicting files
- Do NOT auto-resolve conflicts — stop and report them
- Ask the user to resolve, then run `/ship` again

---

## Phase 2 — Run Tests

Detect and run the test suite:

```bash
# Node/JS
npm test          # or: yarn test, npx vitest run, npx jest --ci

# Python
python -m pytest  # or: uv run pytest

# Go
go test ./...
```

If tests fail:
- Show the failure output
- Stop — do not proceed to commit or push
- Say: "Tests are failing. Fix them before shipping."

If no test framework is found:
- Note: "No test suite found. Shipping without test verification. Consider adding tests with `/test-gen`."
- Continue

---

## Phase 3 — Stage and Review

```bash
git status
git diff --stat
```

Show the user a summary of what will be committed:
- Files changed (with counts: +X lines, -Y lines)
- New files added
- Files deleted

Ask: "This is what will ship. Anything to exclude?" (Give the user a chance to unstage specific files before committing.)

Stage all tracked changes:
```bash
git add -A
```

If there are untracked files that look like they should be included (non-build, non-node_modules, non-.env), flag them and ask if they should be included.

---

## Phase 4 — Commit

Write a clean commit message:
- First line: imperative mood, under 72 chars, describes what changed not why
- Body (optional): 2-3 lines of context for non-obvious changes
- No "WIP", no "fix", no "changes"

```bash
git commit -m "$(cat <<'EOF'
[concise description of what was built/fixed]

[optional: why this approach, key decisions, anything reviewers should know]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Phase 5 — Push

```bash
git push -u origin [branch-name]
```

If push is rejected (non-fast-forward):
- Run `git pull --rebase origin [branch-name]`
- If rebase has conflicts, stop and report them

---

## Phase 6 — Open Pull Request

Use `gh pr create` to open a structured PR.

Gather context first:
```bash
git log main..HEAD --oneline          # all commits on this branch
git diff main...HEAD --stat           # files changed vs main
```

Write the PR description:

```bash
gh pr create --title "[title]" --body "$(cat <<'EOF'
## What changed
[2-4 bullet points describing what was built or fixed — user-facing, not implementation details]

## Why
[1-3 sentences on the motivation — what problem this solves or what it enables]

## How to test
- [ ] [specific thing to test]
- [ ] [another specific thing]
- [ ] [edge case to verify]

## Notes for reviewers
[optional: anything non-obvious about the approach, known limitations, follow-up work]

---
🤖 Built with [tanker](https://github.com/tanishg98/tanker)
EOF
)"
```

If args include "draft", add `--draft` flag.

---

## Output Format

Report after each phase:

```
✓ On branch: feature/[name]
✓ Tests: [passed X/X | skipped (no framework)]
✓ Changes: [N files, +X -Y lines]
✓ Committed: [commit hash] [message]
✓ Pushed: origin/[branch]
✓ PR opened: [PR URL]
```

End with:
> **Shipped.** PR is open at [URL]. Run `pre-merge` agent if not already done, then get a review.

---

## Rules

- **Never ship on main.** Stop and warn if the current branch is the default branch.
- **Never push with `--force` unless the user explicitly asks.** If force-push is needed, explain why and confirm first.
- **Never commit `.env` files, credentials, or build artifacts.** If they appear in `git status`, flag them and exclude.
- **Don't invent a PR title.** If one isn't provided, derive it from the branch name and commit messages — don't make up marketing copy.
- **Tests are a hard gate.** Failing tests mean no commit, no push, no PR. A warning and skip is only acceptable when no test framework exists.
- **One commit per `/ship`.** Squash is the user's decision, not Claude's.
