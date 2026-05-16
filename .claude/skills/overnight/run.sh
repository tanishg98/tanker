#!/usr/bin/env bash
# /overnight runner — invoked by the LaunchAgent at the scheduled hour.
# Reads agent-tasks/, dispatches /swarm, writes morning summary.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "ERROR: not inside a git repo" >&2
  exit 2
}
cd "$REPO_ROOT"

TS_UTC="$(date -u +%Y-%m-%d-%H%M%S)"
DATE_LOCAL="$(date +%Y-%m-%d)"
OUT_DIR="outputs/overnight/$DATE_LOCAL"
LOCK="outputs/overnight/.lock"

mkdir -p "$OUT_DIR" agent-tasks/completed agent-tasks/failed

# Load config (with defaults)
MAX_SECONDS=$(awk '/^overnight:/{f=1;next} f && /max_seconds:/{print $2; exit}' tanker.yaml 2>/dev/null)
MAX_SECONDS="${MAX_SECONDS:-14400}"
MAX_PARALLEL=$(awk '/^overnight:/{f=1;next} f && /max_parallel:/{print $2; exit}' tanker.yaml 2>/dev/null)
MAX_PARALLEL="${MAX_PARALLEL:-3}"
PER_TASK_TIMEOUT=$(awk '/^overnight:/{f=1;next} f && /per_task_timeout:/{print $2; exit}' tanker.yaml 2>/dev/null)
PER_TASK_TIMEOUT="${PER_TASK_TIMEOUT:-1800}"
OPEN_PRS=$(awk '/^overnight:/{f=1;next} f && /open_prs:/{print $2; exit}' tanker.yaml 2>/dev/null)

# Stale lock cleanup
if [[ -f "$LOCK" ]]; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK" 2>/dev/null || stat -c %Y "$LOCK") ))
  STALE_THRESHOLD=$(( MAX_SECONDS + 600 ))
  if (( LOCK_AGE > STALE_THRESHOLD )); then
    echo "[overnight] stale lock (age ${LOCK_AGE}s) — removing" >&2
    rm -f "$LOCK"
  else
    echo "[overnight] another run in progress (lock age ${LOCK_AGE}s) — abort" >&2
    exit 3
  fi
fi
echo "$$" > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

# Count briefs
shopt -s nullglob
BRIEFS=(agent-tasks/*.md)
N=${#BRIEFS[@]}
if (( N == 0 )); then
  cat > "$OUT_DIR/summary.md" <<EOF
# Overnight Run — $DATE_LOCAL

No briefs in agent-tasks/. Nothing to do.
EOF
  echo "{\"ts\":\"$TS_UTC\",\"total\":0,\"note\":\"empty queue\"}" > "$OUT_DIR/summary.json"
  exit 0
fi

# Cost guard
EST_COST=$(awk "BEGIN{printf \"%.2f\", $N * 0.20}")
EST_LIMIT="${OVERNIGHT_COST_CEILING:-20}"
if awk "BEGIN{exit !($EST_COST > $EST_LIMIT)}"; then
  cat > "$OUT_DIR/summary.md" <<EOF
# Overnight Run — $DATE_LOCAL — SKIPPED

Estimated cost \$${EST_COST} exceeds ceiling \$${EST_LIMIT}.
$N briefs queued. Run manually with \`/overnight run-now\` after review.
EOF
  exit 4
fi

# Swarm args
SWARM_ARGS=(agent-tasks "$REPO_ROOT" --parallel "$MAX_PARALLEL" --timeout "$PER_TASK_TIMEOUT")
[[ "${OPEN_PRS:-false}" == "true" ]] && SWARM_ARGS+=(--pr)

# Resolve timeout binary (bash 3.2 / macOS fallback chain)
if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN="gtimeout"
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout"
else
  TIMEOUT_BIN="perl -e 'alarm shift; exec @ARGV' --"
fi

START_TS=$(date +%s)
START_HUMAN=$(date +%H:%M)

# Fire swarm via headless claude -p
$TIMEOUT_BIN "$MAX_SECONDS" claude -p "/swarm ${SWARM_ARGS[*]}" \
  --permission-mode acceptEdits \
  --allowedTools Bash,Edit,Write,Read,Glob,Grep \
  > "$OUT_DIR/swarm-stdout.log" 2> "$OUT_DIR/swarm-stderr.log"
SWARM_EXIT=$?

END_TS=$(date +%s)
END_HUMAN=$(date +%H:%M)
WALL=$(( END_TS - START_TS ))

HIT_CAP="no"
[[ $SWARM_EXIT -eq 124 || $SWARM_EXIT -eq 142 ]] && HIT_CAP="yes"

# Find latest swarm-runs dir created by this run
SWARM_RUN_DIR=$(ls -1dt outputs/swarm-runs/*/ 2>/dev/null | head -1)
if [[ -n "$SWARM_RUN_DIR" ]]; then
  ln -snf "$SWARM_RUN_DIR" "$OUT_DIR/swarm-run-link"
  SWARM_SUMMARY="$SWARM_RUN_DIR/summary.json"
else
  SWARM_SUMMARY=""
fi

# Move briefs based on swarm summary
PASSED=0; FAILED=0; TIMED_OUT=0
if [[ -f "$SWARM_SUMMARY" ]]; then
  PASSED=$(awk -F'[: ,]' '/"passed"/{print $(NF-1); exit}' "$SWARM_SUMMARY" 2>/dev/null || echo 0)
  FAILED=$(awk -F'[: ,]' '/"failed"/{print $(NF-1); exit}' "$SWARM_SUMMARY" 2>/dev/null || echo 0)
  TIMED_OUT=$(awk -F'[: ,]' '/"timed_out"/{print $(NF-1); exit}' "$SWARM_SUMMARY" 2>/dev/null || echo 0)
fi

# Build morning report
cat > "$OUT_DIR/summary.md" <<EOF
# Overnight Run — $DATE_LOCAL

**Started:** $START_HUMAN | **Ended:** $END_HUMAN | **Wall:** ${WALL}s | **Cap:** ${MAX_SECONDS}s | **Hit cap:** $HIT_CAP

**Tasks:** $N total → $PASSED passed, $FAILED failed, $TIMED_OUT timed_out

See swarm summary: $SWARM_SUMMARY

## Next action
- Run \`/morning-prs\` to triage passed branches
- Inspect failed worktrees under outputs/swarm-runs/.../wt-*/
EOF

cat > "$OUT_DIR/summary.json" <<EOF
{
  "ts": "$TS_UTC",
  "total": $N,
  "passed": $PASSED,
  "failed": $FAILED,
  "timed_out": $TIMED_OUT,
  "wall_seconds": $WALL,
  "hit_cap": "$HIT_CAP",
  "swarm_run": "$SWARM_RUN_DIR"
}
EOF

# Optional notification
if [[ -n "${OVERNIGHT_NOTIFY_SLACK_WEBHOOK:-}" ]]; then
  curl -sS -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\":sun_with_face: Overnight: $PASSED/$N passed, $FAILED failed, $TIMED_OUT timed_out (${WALL}s)\"}" \
    "$OVERNIGHT_NOTIFY_SLACK_WEBHOOK" >/dev/null || true
fi

exit 0
