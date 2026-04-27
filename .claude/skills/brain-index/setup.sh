#!/usr/bin/env bash
# Sets up an isolated Python venv at ~/.claude/brain-index/venv with chromadb.
# Idempotent — safe to re-run.
set -euo pipefail

VENV="$HOME/.claude/brain-index/venv"
DATA_DIR="$HOME/.claude/brain-index/data"

mkdir -p "$DATA_DIR"

if [ ! -x "$VENV/bin/python" ]; then
  echo "[brain-index] creating venv at $VENV"
  python3 -m venv "$VENV"
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
