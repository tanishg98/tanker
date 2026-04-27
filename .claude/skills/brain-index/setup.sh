#!/usr/bin/env bash
# Sets up an isolated Python venv at ~/.claude/brain-index/venv with chromadb.
# Idempotent — safe to re-run.
set -euo pipefail

VENV="$HOME/.claude/brain-index/venv"
DATA_DIR="$HOME/.claude/brain-index/data"

mkdir -p "$DATA_DIR"

if [ ! -x "$VENV/bin/python" ]; then
  echo "[brain-index] creating venv at $VENV"
  # Pick the most stable Python available. Skip 3.14+ which often has broken
  # ensurepip in early releases. chromadb requires >=3.9.
  PY=""
  for cand in python3.12 python3.11 python3.10 python3.13 /usr/bin/python3 python3; do
    if command -v "$cand" >/dev/null 2>&1; then
      VER=$("$cand" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
      MAJOR=${VER%.*}
      MINOR=${VER#*.}
      # Accept 3.9 through 3.13. Skip 3.14+ (bleeding edge, ensurepip bugs).
      if [ "$MAJOR" = "3" ] && [ "$MINOR" -ge 9 ] && [ "$MINOR" -le 13 ]; then
        PY="$cand"
        echo "[brain-index] using $cand (Python $VER)"
        break
      fi
    fi
  done

  if [ -z "$PY" ]; then
    echo "[brain-index] ERROR: no compatible Python found (need 3.9–3.13)"
    echo "[brain-index] install one with: brew install python@3.12"
    exit 1
  fi

  "$PY" -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

# Install only if missing — avoids re-downloading 200MB on every run
if ! python -c "import chromadb" 2>/dev/null; then
  echo "[brain-index] installing chromadb (one-time, ~200MB)..."
  pip install --quiet --upgrade pip
  pip install --quiet "chromadb>=0.5,<0.6" "pyyaml>=6"
fi

if ! python -c "import yaml" 2>/dev/null; then
  pip install --quiet "pyyaml>=6"
fi

echo "[brain-index] ready · venv=$VENV · data=$DATA_DIR"
