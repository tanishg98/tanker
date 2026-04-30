# Install

## One-line install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/tanishg98/tanker/main/install.sh)
```

The installer:

1. Checks prerequisites (`git`, `jq`, `gh`, `python3`).
2. Copies `.claude/` into the current directory (or backs up an existing one).
3. Sets up `~/.claude/vault/` (0700) and `~/.claude/vault/credentials.json` (0600).
4. Scaffolds `~/.claude/references/repos.yaml` for your curated reference library.
5. (Optional) Sets up the brain-index venv if `~/Desktop/Obsidian/Brain/` exists.

## Manual install

```bash
git clone https://github.com/tanishg98/tanker
cp -r tanker/.claude your-project/.claude
mkdir -p ~/.claude/vault ~/.claude/references
chmod 700 ~/.claude/vault
echo '{}' > ~/.claude/vault/credentials.json
chmod 600 ~/.claude/vault/credentials.json
```

## Prerequisites

| Tool | Required for | Install |
|---|---|---|
| Claude Code | running skills | https://docs.claude.com/claude-code |
| `git` | repo operations | system |
| `gh` CLI | `gh-provisioner`, `/ship` | `brew install gh` |
| `jq` | vault read/write | `brew install jq` |
| `python3` | brain-index, `/analyst` | system |

## Verify install

```bash
ls .claude/skills/cto/SKILL.md   # → exists
cat ~/.claude/vault/credentials.json   # → {}
stat -f '%A' ~/.claude/vault/credentials.json   # → 600
```

In Claude Code, type `/` — you should see `/cto`, `/grill`, `/architect`, etc.

## Next

→ [First /cto run](./first-cto.md)
