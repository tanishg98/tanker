#!/usr/bin/env bash
# dispatch.sh — fan out N task briefs to parallel headless `claude -p` workers
# in isolated git worktrees. Wraps each with `timeout`, runs the verifier,
# optionally opens a PR, and writes a summary.json.
#
# Usage:
#   dispatch.sh <task-dir> <repo-path> [--parallel N] [--timeout S] [--pr]
#
# Env:
#   SWARM_BASE_BRANCH   — fork base (default: origin/main)
#   SWARM_OUT_ROOT      — log root (default: <repo>/outputs/swarm-runs)

set -uo pipefail

TASK_DIR="${1:?task-dir required}"
REPO="${2:?repo path required}"
shift 2

PARALLEL=5
TIMEOUT=1800
OPEN_PR=0
ONLY=""
DRY_RUN=0

while (( "$#" )); do
  case "$1" in
    --parallel) PARALLEL="$2"; shift 2;;
    --timeout)  TIMEOUT="$2"; shift 2;;
    --pr)       OPEN_PR=1; shift;;
    --only)     ONLY="$2"; shift 2;;
    --dry-run)  DRY_RUN=1; shift;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

BASE_BRANCH="${SWARM_BASE_BRANCH:-origin/main}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${SWARM_OUT_ROOT:-$REPO/outputs/swarm-runs}"
OUT="$OUT_ROOT/$TS"
mkdir -p "$OUT"

echo "swarm: $TS"
echo "  repo:     $REPO"
echo "  base:     $BASE_BRANCH"
echo "  task dir: $TASK_DIR"
echo "  parallel: $PARALLEL"
echo "  timeout:  ${TIMEOUT}s"
echo "  open PR:  $OPEN_PR"
echo "  logs:     $OUT"
echo ""

# Pre-flight: repo state
cd "$REPO" || exit 2
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "fatal: $REPO is not a git repo" >&2; exit 2
fi
git fetch origin --quiet || echo "warn: git fetch failed (offline?)" >&2

# Discover tasks (bash 3.2-portable: no mapfile)
TASK_FILES=()
while IFS= read -r line; do
  [ -n "$line" ] && TASK_FILES+=("$line")
done < <(ls "$TASK_DIR"/*.md 2>/dev/null | sort)
if [ ${#TASK_FILES[@]} -eq 0 ]; then
  echo "fatal: no *.md files in $TASK_DIR" >&2; exit 2
fi

# Filter by --only if given
if [ -n "$ONLY" ]; then
  IFS=',' read -ra WHITELIST <<< "$ONLY"
  FILTERED=()
  for f in "${TASK_FILES[@]}"; do
    id="$(awk '/^id:/ {print $2; exit}' "$f")"
    for w in "${WHITELIST[@]}"; do
      [ "$id" = "$w" ] && FILTERED+=("$f")
    done
  done
  TASK_FILES=("${FILTERED[@]}")
fi

# Validate frontmatter
for f in "${TASK_FILES[@]}"; do
  for key in id goal files verify; do
    if ! grep -q "^$key:" "$f"; then
      echo "fatal: $f missing required frontmatter key: $key" >&2; exit 2
    fi
  done
done

# --dry-run: print run table and exit
if [ "$DRY_RUN" = "1" ]; then
  echo "dry-run: would dispatch ${#TASK_FILES[@]} task(s) with parallel=$PARALLEL, timeout=${TIMEOUT}s"
  echo ""
  printf "  %-30s  %s\n" "id" "file"
  printf "  %-30s  %s\n" "------------------------------" "----"
  for f in "${TASK_FILES[@]}"; do
    id="$(awk '/^id:/ {print $2; exit}' "$f")"
    printf "  %-30s  %s\n" "$id" "$(basename "$f")"
  done
  echo ""
  echo "dry-run complete — no workers spawned."
  exit 0
fi

run_one() {
  local task_file="$1"
  local id; id="$(awk '/^id:/ {print $2; exit}' "$task_file")"
  local short_id="${id//[^a-zA-Z0-9_-]/-}"
  local branch="swarm/$TS/$short_id"
  local wt="$OUT/wt-$short_id"
  local log="$OUT/wt-$short_id.log"
  local status_file="$OUT/wt-$short_id.status"

  {
    echo "[$id] starting at $(date -u +%H:%M:%SZ)"
    echo "[$id] worktree: $wt"
    echo "[$id] branch:   $branch"

    # Worktree — serialized via lockfile to avoid .git/config lock races
    # when many workers call `git worktree add` simultaneously.
    local lockfile="$OUT/.worktree-add.lock"
    local wt_rc=1
    (
      # macOS doesn't have flock; fall back to a simple mkdir-based mutex
      if command -v flock >/dev/null 2>&1; then
        flock 200
        git worktree add -b "$branch" "$wt" "$BASE_BRANCH"
      else
        # mkdir-based mutex (atomic on POSIX)
        local mutex="$OUT/.worktree-add.mutex"
        while ! mkdir "$mutex" 2>/dev/null; do sleep 0.2; done
        git worktree add -b "$branch" "$wt" "$BASE_BRANCH"
        local rc=$?
        rmdir "$mutex"
        exit $rc
      fi
    ) 200>"$lockfile"
    wt_rc=$?

    if [ $wt_rc -ne 0 ]; then
      echo "[$id] git worktree add failed (rc=$wt_rc)" >&2
      echo "worktree_failed" > "$status_file"
      return
    fi

    # Run Claude — strip YAML frontmatter so claude -p doesn't parse `---`
    # as an option. The agent only needs the human-readable brief.
    local prompt
    prompt="$(awk 'BEGIN{fm=0; printed=0} /^---$/{fm++; next} fm>=2{print; printed=1} END{if(!printed) exit}' "$task_file")"
    # Fallback: if no frontmatter detected, use the raw file
    if [ -z "$prompt" ]; then
      prompt="$(cat "$task_file")"
    fi

    # acceptEdits permission mode + restricted tool set
    local cmd=(claude -p "$prompt"
      --permission-mode acceptEdits
      --allowedTools Bash Edit Write Read Glob Grep
    )

    # Run with timeout. macOS has `gtimeout` or none; use perl as portable fallback.
    if command -v gtimeout >/dev/null 2>&1; then
      WRAPPER=(gtimeout "$TIMEOUT")
    elif command -v timeout >/dev/null 2>&1; then
      WRAPPER=(timeout "$TIMEOUT")
    else
      WRAPPER=(perl -e "alarm shift; exec @ARGV" "$TIMEOUT")
    fi

    pushd "$wt" >/dev/null || { echo "agent_dir_missing" > "$status_file"; return; }

    "${WRAPPER[@]}" "${cmd[@]}"
    local agent_rc=$?
    popd >/dev/null

    if [ $agent_rc -ne 0 ]; then
      echo "[$id] agent exited rc=$agent_rc"
      echo "agent_failed_rc_$agent_rc" > "$status_file"
      return
    fi

    # Verifier
    local verify_script
    verify_script="$(awk '/^verify: \|/{flag=1; next} /^[a-z]+:/{flag=0} flag' "$task_file")"
    if [ -z "$verify_script" ]; then
      echo "[$id] no verifier — marking pass-without-verify"
      echo "no_verifier" > "$status_file"
    else
      pushd "$wt" >/dev/null
      bash -c "$verify_script"
      local verify_rc=$?
      popd >/dev/null
      if [ $verify_rc -ne 0 ]; then
        echo "[$id] verifier failed rc=$verify_rc"
        echo "verifier_failed" > "$status_file"
        return
      fi
    fi

    # Commit anything dirty (agent should have committed but be defensive).
    # `git diff --quiet` misses UNTRACKED files — use `git status --porcelain`
    # instead, otherwise new files get discarded when the worktree is removed.
    pushd "$wt" >/dev/null
    if [ -n "$(git status --porcelain)" ]; then
      git add -A
      git -c user.email=swarm@local -c user.name="Swarm Worker" commit -m "swarm($id): changes from agent" || true
    fi

    # Push if --pr
    if [ "$OPEN_PR" = "1" ]; then
      git push -u origin "$branch" 2>&1 || echo "[$id] push failed"
      if command -v gh >/dev/null 2>&1; then
        local title; title="$(awk -F': ' '/^pr_title:/{print $2}' "$task_file")"
        [ -z "$title" ] && title="swarm($id): $(awk -F': ' '/^goal:/{print $2; exit}' "$task_file" | cut -c1-60)"
        # Strip YAML frontmatter from PR body so it renders cleanly on GitHub
        local pr_body_file="$wt/.swarm-pr-body.md"
        awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$task_file" > "$pr_body_file"
        [ ! -s "$pr_body_file" ] && cp "$task_file" "$pr_body_file"
        gh pr create --base "${BASE_BRANCH#origin/}" --head "$branch" --title "$title" --body-file "$pr_body_file" 2>&1 || echo "[$id] pr create failed"
        rm -f "$pr_body_file"
      fi
    fi
    popd >/dev/null

    echo "passed" > "$status_file"

    # On success, remove worktree (keeps branch)
    git worktree remove --force "$wt" 2>&1 || true
    echo "[$id] done at $(date -u +%H:%M:%SZ)"
  } > "$log" 2>&1
}

export -f run_one
export OUT TS BASE_BRANCH OPEN_PR TIMEOUT

# Dispatch with parallelism via xargs -P
printf '%s\n' "${TASK_FILES[@]}" | xargs -n1 -P "$PARALLEL" bash -c 'run_one "$0"'

# Build summary.json
echo "[" > "$OUT/summary.json"
first=1
for f in "${TASK_FILES[@]}"; do
  id="$(awk '/^id:/ {print $2; exit}' "$f")"
  short_id="${id//[^a-zA-Z0-9_-]/-}"
  status="unknown"
  [ -f "$OUT/wt-$short_id.status" ] && status="$(cat "$OUT/wt-$short_id.status")"
  branch="swarm/$TS/$short_id"
  goal="$(awk -F': ' '/^goal:/{print $2; exit}' "$f" | sed 's/"/\\"/g')"
  [ $first -eq 1 ] && first=0 || echo "," >> "$OUT/summary.json"
  cat >> "$OUT/summary.json" <<JSON
  { "id": "$id", "status": "$status", "branch": "$branch", "goal": "$goal", "log": "$OUT/wt-$short_id.log" }
JSON
done
echo "]" >> "$OUT/summary.json"

# Console summary
echo ""
echo "=========================================="
echo "swarm complete: $TS"
total=${#TASK_FILES[@]}
passed=$(grep -l '^passed$' "$OUT"/*.status 2>/dev/null | wc -l | tr -d ' ')
failed=$((total - passed))
echo "  total:  $total"
echo "  passed: $passed"
echo "  failed: $failed"
echo ""
echo "per-task:"
for f in "${TASK_FILES[@]}"; do
  id="$(awk '/^id:/ {print $2; exit}' "$f")"
  short_id="${id//[^a-zA-Z0-9_-]/-}"
  status="?"
  [ -f "$OUT/wt-$short_id.status" ] && status="$(cat "$OUT/wt-$short_id.status")"
  printf "  %-30s %s\n" "$id" "$status"
done
echo ""
echo "logs at: $OUT"
