#!/usr/bin/env bash
# Stop-hook: when the session ends with a non-trivial diff in the repo, auto-spawn the review agent.
# Wired via .claude/settings.json hooks.Stop entry.
#
# Safe by design:
#   - Read-only diff check (git status --porcelain)
#   - Skips on empty diff, on agent-tasks/ only changes, on .claude/git-state.md only changes
#   - Spawns `claude -p` with --permission-mode plan (review can't write)
#   - Writes report to outputs/auto-review/<ts>.md; never edits files itself
#   - Loop control: max 3 auto-iterations per session via a counter file
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$REPO_ROOT"

TS="$(date -u +%Y-%m-%d-%H%M%S)"
OUT_DIR="outputs/auto-review"
mkdir -p "$OUT_DIR"

COUNTER="$OUT_DIR/.session-counter"
MAX_ITER="${TANKER_AUTOREVIEW_MAX:-3}"

# Initialize / increment counter
CURRENT=0
[[ -f "$COUNTER" ]] && CURRENT=$(cat "$COUNTER" 2>/dev/null || echo 0)
if (( CURRENT >= MAX_ITER )); then
  echo "[auto-review] iteration cap ($MAX_ITER) hit — skipping" >&2
  exit 0
fi

# Diff check — ignore noise files
DIFF=$(git status --porcelain | grep -v -E '\.claude/git-state\.md$|^.. agent-tasks/' || true)
if [[ -z "$DIFF" ]]; then
  # Clean session, reset counter
  rm -f "$COUNTER"
  exit 0
fi

# Count actual code changes
CHANGED_LINES=$(git diff --shortstat 2>/dev/null | awk '{s+=$1} END{print s+0}')
if (( CHANGED_LINES < 5 )); then
  # Trivial diff, skip
  exit 0
fi

echo $((CURRENT + 1)) > "$COUNTER"

REPORT="$OUT_DIR/$TS.md"
LOG="$OUT_DIR/$TS.log"

# Spawn the review agent in plan mode — it can read everything but write nothing
claude -p "Spawn the review agent against the current uncommitted diff in this repo. Use the diff from \`git diff\` (and \`git status\` for untracked). Score PASS / CONDITIONAL / FAIL. If FAIL, list the 3 most important fixes. Be concise." \
  --permission-mode plan \
  --allowedTools Read,Glob,Grep,Bash \
  > "$REPORT" 2> "$LOG" &
PID=$!

# Cap review wall time at 5 min
( sleep 300 && kill -TERM $PID 2>/dev/null ) &
WATCHDOG=$!
wait $PID
REVIEW_EXIT=$?
kill -TERM $WATCHDOG 2>/dev/null

if (( REVIEW_EXIT != 0 )); then
  echo "[auto-review] review agent exit $REVIEW_EXIT — see $LOG" >&2
fi

# Print one-line verdict to stderr so it shows in the user's terminal
VERDICT=$(grep -m1 -oE 'PASS|CONDITIONAL|FAIL' "$REPORT" 2>/dev/null || echo 'UNKNOWN')
echo "[auto-review] $VERDICT — full report: $REPORT" >&2

exit 0
