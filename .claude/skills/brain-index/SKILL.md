---
name: brain-index
description: Indexes the local Obsidian vault at ~/Desktop/Obsidian/Brain/ into a local ChromaDB collection so /cto, /prd, /architect, and github-scout can do semantic retrieval (not keyword grep) against the owner's accumulated knowledge. Embeddings are computed locally via the default `all-MiniLM-L6-v2` model — vault contents never leave the machine. Incremental: only re-embeds chunks whose content changed. Run on demand or via the nightly Stop-hook.
triggers:
  - /brain-index
  - /brain-query
args: "[index | query \"<text>\"] [--top N] [--reset] [--vault PATH] [--collection brain|refs] [--domain frontend|backend|data|infra|product|content] [--surface identity|people|decisions|meetings|daily|projects|playbook|wiki|raw]"
---

# brain-index

You are operating the local brain index. The Obsidian vault is the owner's accumulated knowledge — opinions, decisions, meeting notes, project history, taste. The brain-index makes it semantically queryable so the orchestrator can pull *relevant context* on every run, not just files matching a keyword.

The data plane is a local ChromaDB at `~/.claude/brain-index/data/`. The compute plane is a local venv at `~/.claude/brain-index/venv/`. Nothing leaves the machine.

---

## Phase 0 — Setup (idempotent)

```bash
bash .claude/skills/brain-index/setup.sh
```

This creates the venv on first run (~200MB download) and is a no-op afterward.

---

## Phase 1 — Pick the operation

Two operations: **index** (refresh the vector DB from vault) and **query** (semantic retrieval).

### Per-agent memory slice

Each chunk written by `index.py` carries two metadata fields the query side filters on:

- **`surface`** — top-level vault folder. Maps to `identity / people / decisions / meetings / daily / projects / playbook / wiki / raw`. Use `--surface decisions` to retrieve only from the Decisions/ folder.
- **`domains`** — comma-separated set inferred from heading + body keywords. Values: `frontend / backend / data / infra / product / content`. Use `--domain backend` to retrieve only chunks that mention backend keywords.

Filters stack via `$and`. Example: `--domain backend --surface wiki` returns wiki chunks tagged backend.

This is what `/cto` Phase 5 uses to give each engineering subagent its own slice of memory — backend agent sees backend context, frontend agent sees frontend context. Avoids cross-domain noise.

### Index

```bash
source ~/.claude/brain-index/venv/bin/activate
python .claude/skills/brain-index/index.py
```

Default vault: `~/Desktop/Obsidian/Brain/`. Override with `--vault /custom/path`. Default collection: `brain`. Use `--reset` to drop and rebuild the collection (rare; only after a major vault reorg).

Incremental indexing: chunks are keyed by sha256 of their text, so re-running only re-embeds what changed. A 1000-note vault refreshes in ~5 seconds after the first build.

### Query

```bash
source ~/.claude/brain-index/venv/bin/activate
python .claude/skills/brain-index/query.py "<query text>" --top 10
```

Flags:
- `--collection brain` (default) or `--collection refs` (curated GitHub references)
- `--top N` — number of results (default 10)
- `--json` — JSON output instead of markdown

Markdown output is designed to drop directly into context for `/cto` Phase 1.

---

## Phase 2 — Wire into /cto

`/cto` Phase 1 (context load) calls this for **semantic retrieval** before generating any artifact:

```bash
# Inside /cto context-load phase
QUERY="<keywords + concepts from brief>"
python .claude/skills/brain-index/query.py "$QUERY" --top 8 --collection brain > outputs/<slug>/context-brain.md
python .claude/skills/brain-index/query.py "$QUERY" --top 5 --collection refs  > outputs/<slug>/context-refs.md
```

Both files are appended to the context bundle that `/prd`, `/architect`, and `/createplan` read.

---

## Phase 3 — Auto-refresh

Two patterns for keeping the index current:

**Pattern A — Stop hook** (recommended): add to `.claude/settings.json` so the index refreshes when the session ends:

```json
{
  "hooks": {
    "Stop": [
      { "type": "shell", "command": "bash ~/.claude/brain-index/refresh.sh >/dev/null 2>&1 &" }
    ]
  }
}
```

(Backgrounded so it never blocks the prompt return.)

**Pattern B — LaunchAgent / cron** (overnight): run `python index.py` nightly at 3am. See `~/.claude/brain-index/launchd/` if you want the plist scaffolding.

---

## What gets indexed

- Every `*.md` and `*.markdown` file under `~/Desktop/Obsidian/Brain/`
- Skipped: `.obsidian/`, `.git/`, `.trash/`, `node_modules/`, `__pycache__/`, hidden dirs
- Chunks: split by H2 headings; sliding window for sections >1200 chars

---

## What does NOT get indexed

- Anything outside the vault root
- PDFs, images, audio (chunk model is text-only)
- Files >80KB (rarely high-signal)

If you want PDF/audio coverage, that's a future skill — the embedding model would change.

---

## Privacy posture

- All data is local. The chromadb default model is `all-MiniLM-L6-v2` (~80MB, runs on CPU).
- No API calls. No telemetry. Zero network during embed or query.
- Verify by running the indexer offline (turn off wifi after first install).

---

## Handoff

> **Indexed.** N files, M chunks. Run `/brain-query "<text>"` to test, or `/cto` will auto-pull relevant context on its next run.
