#!/usr/bin/env bash
# Tanker — one-line installer.
# Usage:   curl -fsSL https://raw.githubusercontent.com/tanishg98/tanker/main/install.sh | bash
# Or:      bash install.sh
set -euo pipefail

REPO="https://github.com/tanishg98/tanker"
TARGET_DIR="${1:-$PWD}"
TANKER_HOME="${HOME}/.claude"
VAULT_PATH="${TANKER_HOME}/vault/credentials.json"
BRAIN_INDEX_DIR="${TANKER_HOME}/brain-index"

color() { printf "\033[%sm%s\033[0m" "$1" "$2"; }
green() { color "32" "$1"; }
yellow() { color "33" "$1"; }
red() { color "31" "$1"; }
bold() { color "1" "$1"; }

step() { echo -e "$(bold "[$1]") $2"; }
ok()   { echo -e "  $(green "✓") $1"; }
warn() { echo -e "  $(yellow "⚠") $1"; }
err()  { echo -e "  $(red "✗") $1"; exit 1; }

step "1/5" "Checking prerequisites"

command -v git >/dev/null 2>&1 || err "git not found. Install git first."
command -v jq  >/dev/null 2>&1 || warn "jq not found. Install for full vault support: brew install jq"
command -v gh  >/dev/null 2>&1 || warn "gh CLI not found. Install for /cto autopilot: brew install gh"
command -v python3 >/dev/null 2>&1 || warn "python3 not found. Install for brain-index + /analyst."
ok "git: $(git --version | awk '{print $3}')"

step "2/5" "Installing Tanker .claude/ into ${TARGET_DIR}"

if [[ -d "${TARGET_DIR}/.claude" ]]; then
  warn ".claude/ already exists — backing up to .claude.bak.$(date +%s)"
  mv "${TARGET_DIR}/.claude" "${TARGET_DIR}/.claude.bak.$(date +%s)"
fi

# If running in-repo (you ran install.sh after cloning) — copy local
if [[ -d "$(dirname "$0")/.claude" && "$(realpath "$(dirname "$0")/.claude")" != "$(realpath "${TARGET_DIR}")/.claude" ]]; then
  cp -R "$(dirname "$0")/.claude" "${TARGET_DIR}/.claude"
  ok "Copied .claude/ from local Tanker repo"
else
  # Otherwise, clone fresh into a tmp dir and copy
  TMP=$(mktemp -d)
  git clone --depth 1 "${REPO}" "${TMP}/tanker" >/dev/null 2>&1
  cp -R "${TMP}/tanker/.claude" "${TARGET_DIR}/.claude"
  rm -rf "${TMP}"
  ok "Cloned and installed .claude/ from ${REPO}"
fi

step "3/5" "Setting up Tanker home (${TANKER_HOME})"

mkdir -p "${TANKER_HOME}/vault" "${TANKER_HOME}/references" "${BRAIN_INDEX_DIR}"
chmod 700 "${TANKER_HOME}/vault"
if [[ ! -f "${VAULT_PATH}" ]]; then
  echo '{}' > "${VAULT_PATH}"
  chmod 600 "${VAULT_PATH}"
  ok "Vault created at ${VAULT_PATH} (0600)"
else
  ok "Vault already exists at ${VAULT_PATH}"
fi

if [[ ! -f "${TANKER_HOME}/references/repos.yaml" ]]; then
  cat > "${TANKER_HOME}/references/repos.yaml" <<'EOF'
# Tanker reference library — curated GitHub repos that shape /cto's output toward your taste.
# Add via /cto-add-ref or edit directly.
references: []
EOF
  ok "Reference library scaffolded at ${TANKER_HOME}/references/repos.yaml"
fi

step "4/5" "Optional: brain-index for semantic retrieval over Obsidian vault"

OBSIDIAN_VAULT="${HOME}/Desktop/Obsidian/Brain"
if [[ -d "${OBSIDIAN_VAULT}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    if [[ ! -d "${BRAIN_INDEX_DIR}/venv" ]]; then
      echo "  Setting up brain-index venv (~3 min, ~200MB)..."
      python3 -m venv "${BRAIN_INDEX_DIR}/venv"
      "${BRAIN_INDEX_DIR}/venv/bin/pip" install -q --upgrade pip
      "${BRAIN_INDEX_DIR}/venv/bin/pip" install -q chromadb sentence-transformers
      ok "brain-index venv ready"
    else
      ok "brain-index venv already exists"
    fi
    warn "Run \`python ${TARGET_DIR}/.claude/skills/brain-index/index.py\` once to embed your vault (~5 min for 1000 notes)."
  else
    warn "python3 missing — skipping brain-index. Install python3 + rerun installer to enable."
  fi
else
  warn "No Obsidian vault at ${OBSIDIAN_VAULT} — skipping brain-index. /cto falls back to keyword grep."
fi

step "5/5" "Done"

cat <<EOF

$(green "✓ Tanker installed at ${TARGET_DIR}/.claude/")

$(bold "Next steps:")
  1. Add credentials to your vault as needed:
     /vault-add github vercel supabase anthropic

  2. (Optional) Curate your reference library:
     /cto-add-ref add https://github.com/<owner>/<repo> --why "..." --tags ...

  3. Try a build:
     /cto "build me a todo app with auth"

  Docs:    https://github.com/tanishg98/tanker#readme
  Issues:  https://github.com/tanishg98/tanker/issues

EOF
