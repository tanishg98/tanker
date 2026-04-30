# Brain index

Tanker's `brain-index` skill embeds your local Obsidian vault + curated GitHub references into a local ChromaDB collection. `/cto` Phase 1 retrieves from this index instead of grep — so the orchestrator pulls from your accumulated knowledge, not generic GitHub search.

## Setup

```bash
bash .claude/skills/brain-index/setup.sh    # ~3 min, ~200MB
~/.claude/brain-index/venv/bin/python \
  .claude/skills/brain-index/index.py        # ~5 min for 1000 notes
```

## What gets indexed

| Collection | Source | Purpose |
|---|---|---|
| `brain` | `~/Desktop/Obsidian/Brain/**/*.md` | Owner's accumulated thinking — projects, decisions, people, processes |
| `refs` | `~/.claude/references/repos.yaml` | Curated GitHub repos that shape `/cto`'s output toward your taste |

## Curate references

```bash
/cto-add-ref add https://github.com/<owner>/<repo> \
  --why "Production-grade Next.js + Supabase auth pattern" \
  --tags nextjs,supabase,auth
```

This adds the repo to `~/.claude/references/repos.yaml`, fetches its signal files (README, manifests, schemas, docs), and embeds them into the `refs` collection.

## Privacy

- All embeddings run locally via `all-MiniLM-L6-v2` (default ChromaDB model, ~80MB).
- Vault contents never leave the machine.
- Curated repo content is fetched once over HTTPS, then embedded locally.

## Refresh

```bash
~/.claude/brain-index/venv/bin/python .claude/skills/brain-index/index.py
```

Incremental — only re-embeds chunks whose content changed.

## Auto-refresh

Recommended: a Stop-hook that runs the indexer nightly. See `~/Desktop/Obsidian/Brain/CLAUDE.md` Stop-hook section for the pattern.
