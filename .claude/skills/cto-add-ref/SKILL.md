---
name: cto-add-ref
description: Curates the owner's reference library at ~/.claude/references/repos.yaml. Each entry is a GitHub repo you find inspiring — patterns to copy, products to study, stacks to learn from. The skill ingests the repo's signal files (README, manifests, schemas, docs) into the local 'refs' ChromaDB collection so /cto and github-scout pull from YOUR curated taste, not generic GitHub search. Idempotent — re-running on an existing entry is safe.
triggers:
  - /cto-add-ref
  - /cto-list-refs
  - /cto-remove-ref
args: "[add <github-url> | list | remove <github-url>] [--why \"reason\"] [--tags tag1,tag2]"
---

# cto-add-ref

You are managing the reference library. This is the curated set of GitHub repos that shape `/cto`'s output toward the owner's taste — instead of relying on generic GitHub search and training-time priors.

The library has two layers:
1. **Manifest:** `~/.claude/references/repos.yaml` — human-readable list of repos + reasons + tags
2. **Index:** `~/.claude/brain-index/data/` `refs` collection — semantic-search over each repo's signal files

When the owner adds a repo, both layers get updated. When `/cto` runs, it queries the `refs` collection against the brief and surfaces matching reference patterns to `/architect` and `/prd`.

---

## Phase 0 — Setup

```bash
bash .claude/skills/brain-index/setup.sh   # ensures venv + chromadb
mkdir -p ~/.claude/references
test -f ~/.claude/references/repos.yaml || cat > ~/.claude/references/repos.yaml <<'EOF'
# Curated reference repos for /cto. Add what inspires you.
# Format below. Run /cto-add-ref to append + ingest, or edit by hand.
references: []
EOF
```

---

## Phase 1 — Parse intent

Parse args into one of:
- `add <url> [--why "..."] [--tags a,b,c]`
- `list`
- `remove <url>`

If args are missing, ask once for clarification then proceed.

---

## Phase 2 — Add

```bash
URL="$1"
WHY="$2"   # from --why
TAGS="$3"  # from --tags, comma-separated

# 1. Append to YAML manifest (idempotent — skip if URL already present)
~/.claude/brain-index/venv/bin/python - <<PY
import yaml, sys
from pathlib import Path
p = Path.home() / ".claude" / "references" / "repos.yaml"
data = yaml.safe_load(p.read_text()) or {"references": []}
if any(r.get("url") == "$URL" for r in data["references"]):
    print("[refs] already in manifest")
    sys.exit(0)
data["references"].append({
    "url": "$URL",
    "why": "$WHY",
    "tags": [t.strip() for t in "$TAGS".split(",") if t.strip()],
})
p.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True))
print(f"[refs] added {repr('$URL')}")
PY

# 2. Ingest into refs collection
source ~/.claude/brain-index/venv/bin/activate
python .claude/skills/brain-index/ingest_repo.py "$URL" --why "$WHY" --tags "$TAGS"
```

Report: repo slug, files ingested, chunks added.

---

## Phase 3 — List

```bash
~/.claude/brain-index/venv/bin/python - <<PY
import yaml
from pathlib import Path
data = yaml.safe_load((Path.home()/".claude"/"references"/"repos.yaml").read_text()) or {}
refs = data.get("references", [])
print(f"# Reference library ({len(refs)} repos)\n")
for r in refs:
    tags = " ".join(f"#{t}" for t in (r.get("tags") or []))
    print(f"- **{r['url']}**  {tags}")
    if r.get("why"):
        print(f"    *{r['why']}*")
PY
```

---

## Phase 4 — Remove

```bash
URL="$1"

# 1. Remove from YAML
~/.claude/brain-index/venv/bin/python - <<PY
import yaml
from pathlib import Path
p = Path.home() / ".claude" / "references" / "repos.yaml"
data = yaml.safe_load(p.read_text()) or {"references": []}
before = len(data["references"])
data["references"] = [r for r in data["references"] if r.get("url") != "$URL"]
p.write_text(yaml.safe_dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True))
print(f"[refs] removed {before - len(data['references'])} entry from manifest")
PY

# 2. Drop chunks from refs collection
source ~/.claude/brain-index/venv/bin/activate
python .claude/skills/brain-index/ingest_repo.py "$URL" --remove
```

---

## YAML format reference

The user can also edit `~/.claude/references/repos.yaml` directly. Format:

```yaml
references:
  - url: https://github.com/vercel/next.js
    why: "Canonical Next.js patterns — App Router, Server Actions, edge runtime"
    tags: [nextjs, frontend, ssr]

  - url: https://github.com/supabase/supabase
    why: "How a great BaaS sets up auth + RLS + realtime"
    tags: [supabase, postgres, auth, rls]

  - url: https://github.com/peecai/peec
    why: "GEO suite competitor — close to Visibl, study their UX"
    tags: [geo, competitor, ui-ref]

  - url: https://github.com/anthropics/anthropic-cookbook
    why: "Reference patterns for prompt caching + tool use + advisor pattern"
    tags: [claude-api, cookbook, patterns]
```

After hand-editing, run `/cto-add-ref add <url>` for any new entries to trigger ingestion (or `/brain-index` to re-ingest everything).

---

## Rules

- **Manifest and index must stay in sync.** Add → both updated. Remove → both updated. Hand-edit YAML → user must re-ingest.
- **No private creds in YAML.** This file is in `~/.claude/`, not the repo, but still: only public GitHub URLs.
- **One URL per entry.** No globs, no orgs.
- **The `why` field matters.** It's stored in the chunk metadata so retrieval can surface "why this repo matters for the current brief."

---

## Handoff

> **Reference library updated.** `/cto` will surface matching patterns from these repos via semantic search on its next run.
