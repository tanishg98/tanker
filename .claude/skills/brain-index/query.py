#!/usr/bin/env python3
"""
Semantic-retrieval interface over the local brain index.

Usage:
  python query.py "merchant analytics" --top 10
  python query.py "ecommerce dashboard" --collection brain --top 5 --json
  python query.py "auth patterns"      --collection refs  --top 5

Output (default): markdown — quick to drop into context for /cto.
Output (--json): JSON list of {path, heading, score, text}.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path.home() / ".claude" / "brain-index" / "data"


def query(text: str, collection_name: str, top: int) -> list[dict]:
    import chromadb

    client = chromadb.PersistentClient(path=str(DATA_DIR))
    try:
        coll = client.get_collection(collection_name)
    except Exception:
        return []

    res = coll.query(
        query_texts=[text],
        n_results=top,
        include=["documents", "metadatas", "distances"],
    )
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
            }
        )
    return out


def render_markdown(query_text: str, results: list[dict]) -> str:
    if not results:
        return f"# Brain query — no results for: {query_text}\n"
    lines = [f"# Brain query — {query_text}", ""]
    for i, r in enumerate(results, 1):
        lines.append(
            f"## {i}. {r['heading']}  ·  `{r['path']}`  ·  score {r['score']}"
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
    args = p.parse_args()

    results = query(args.query, args.collection, args.top)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(render_markdown(args.query, results))


if __name__ == "__main__":
    main()
