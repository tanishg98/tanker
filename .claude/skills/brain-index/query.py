#!/usr/bin/env python3
"""
Semantic-retrieval interface over the local brain index.

Usage:
  python query.py "merchant analytics" --top 10
  python query.py "ecommerce dashboard" --collection brain --top 5 --json
  python query.py "auth patterns"      --collection refs  --top 5

Per-agent memory slice (steal #7 from MetaGPT):
  python query.py "request handler error patterns" --domain backend --top 6
  python query.py "design references"              --domain frontend --top 6
  python query.py "schema migration patterns"      --domain data --top 6
  python query.py "decisions on auth"              --surface decisions --top 4

Filters can stack:
  python query.py "rate limit" --domain backend --surface wiki --top 6

Output (default): markdown — quick to drop into context for /cto.
Output (--json): JSON list of {path, heading, score, text, surface, domains}.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path.home() / ".claude" / "brain-index" / "data"

VALID_DOMAINS = {"frontend", "backend", "data", "infra", "product", "content"}
VALID_SURFACES = {
    "identity", "people", "decisions", "meetings", "daily",
    "projects", "playbook", "wiki", "raw",
}


def build_where(domain: str | None, surface: str | None) -> dict | None:
    """Translate CLI filters into a ChromaDB `where` clause.

    `domains` is stored as a comma-separated string so we use $contains.
    `surface` is a single string so we use $eq.
    Multiple clauses combine with $and.
    """
    clauses: list[dict] = []
    if domain:
        if domain not in VALID_DOMAINS:
            print(f"[brain-index] warning: unknown domain '{domain}' (valid: {sorted(VALID_DOMAINS)})", file=sys.stderr)
        clauses.append({"domains": {"$contains": domain}})
    if surface:
        if surface not in VALID_SURFACES:
            print(f"[brain-index] warning: unknown surface '{surface}' (valid: {sorted(VALID_SURFACES)})", file=sys.stderr)
        clauses.append({"surface": {"$eq": surface}})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def query(text: str, collection_name: str, top: int, where: dict | None = None) -> list[dict]:
    import chromadb

    client = chromadb.PersistentClient(path=str(DATA_DIR))
    try:
        coll = client.get_collection(collection_name)
    except Exception:
        return []

    kwargs = {
        "query_texts": [text],
        "n_results": top,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    res = coll.query(**kwargs)

    out = []
    for doc, meta, dist in zip(
        res["documents"][0] if res["documents"] else [],
        res["metadatas"][0] if res["metadatas"] else [],
        res["distances"][0] if res["distances"] else [],
    ):
        out.append(
            {
                "path": meta.get("path"),
                "heading": meta.get("heading"),
                "score": round(1 - dist, 3),  # cosine distance → similarity
                "text": doc,
                "source": meta.get("vault") or meta.get("repo") or meta.get("source"),
                "surface": meta.get("surface") or "",
                "domains": meta.get("domains") or "",
            }
        )
    return out


def render_markdown(query_text: str, results: list[dict], filter_summary: str = "") -> str:
    if not results:
        return f"# Brain query — no results for: {query_text} {filter_summary}\n"
    lines = [f"# Brain query — {query_text} {filter_summary}".strip(), ""]
    for i, r in enumerate(results, 1):
        tags = []
        if r.get("surface"):
            tags.append(f"surface:{r['surface']}")
        if r.get("domains"):
            tags.append(f"domains:{r['domains']}")
        tag_suffix = f"  ·  {' '.join(tags)}" if tags else ""
        lines.append(
            f"## {i}. {r['heading']}  ·  `{r['path']}`  ·  score {r['score']}{tag_suffix}"
        )
        lines.append("")
        lines.append(r["text"][:600] + ("…" if len(r["text"]) > 600 else ""))
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("query", help="Natural-language query")
    p.add_argument("--collection", default="brain")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--domain", default=None,
                   help="Restrict to chunks tagged with this domain (frontend/backend/data/infra/product/content). "
                        "Used by /cto subagents for memory-slice retrieval.")
    p.add_argument("--surface", default=None,
                   help="Restrict to chunks under this vault surface (identity/people/decisions/meetings/daily/projects/playbook/wiki/raw).")
    args = p.parse_args()

    where = build_where(args.domain, args.surface)
    results = query(args.query, args.collection, args.top, where=where)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        filter_bits = []
        if args.domain:
            filter_bits.append(f"domain={args.domain}")
        if args.surface:
            filter_bits.append(f"surface={args.surface}")
        filter_summary = f"({', '.join(filter_bits)})" if filter_bits else ""
        print(render_markdown(args.query, results, filter_summary))


if __name__ == "__main__":
    main()
