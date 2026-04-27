#!/usr/bin/env python3
"""
Indexes the Obsidian vault at ~/Desktop/Obsidian/Brain/ into a local ChromaDB
collection at ~/.claude/brain-index/data/. Embeddings stay on this machine.

Incremental: chunks are keyed by sha256(content) so re-running only re-embeds
chunks whose text changed.

Usage:
  python index.py                          # full vault, default location
  python index.py --vault /path/to/vault   # custom path
  python index.py --collection refs        # different collection (used by ingest_repo.py)
  python index.py --reset                  # drop and rebuild collection
"""
from __future__ import annotations
import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Iterator

DEFAULT_VAULT = Path.home() / "Desktop" / "Obsidian" / "Brain"
DATA_DIR = Path.home() / ".claude" / "brain-index" / "data"
DEFAULT_COLLECTION = "brain"

# Files to skip — tmp, hidden, binary
SKIP_DIRS = {".obsidian", ".git", ".trash", "node_modules", "__pycache__"}
MD_EXTS = {".md", ".markdown"}


def chunk_markdown(text: str, max_chars: int = 1200) -> list[tuple[str, str]]:
    """Split markdown by H2 headings; fall back to fixed windows for sections >max_chars.
    Returns list of (heading, chunk_text)."""
    chunks: list[tuple[str, str]] = []
    sections = re.split(r"\n(?=##\s)", text)
    for sec in sections:
        if not sec.strip():
            continue
        m = re.match(r"^##\s+(.+)$", sec.split("\n", 1)[0])
        heading = m.group(1).strip() if m else "(intro)"
        if len(sec) <= max_chars:
            chunks.append((heading, sec.strip()))
        else:
            # Sliding window for long sections
            for i in range(0, len(sec), max_chars - 200):
                chunks.append((heading, sec[i : i + max_chars].strip()))
    return [c for c in chunks if c[1]]


def iter_markdown_files(vault: Path) -> Iterator[Path]:
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in MD_EXTS and p.stat().st_size > 0:
                yield p


def index_vault(vault: Path, collection_name: str, reset: bool = False) -> None:
    import chromadb  # lazy import — setup.sh ensures it exists

    client = chromadb.PersistentClient(path=str(DATA_DIR))

    if reset:
        try:
            client.delete_collection(collection_name)
            print(f"[brain-index] reset collection '{collection_name}'")
        except Exception:
            pass

    coll = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    n_files = 0
    n_chunks_total = 0
    n_chunks_new = 0
    seen_ids: set[str] = set()

    for path in iter_markdown_files(vault):
        n_files += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[brain-index] skip {path}: {e}", file=sys.stderr)
            continue

        rel_path = str(path.relative_to(vault))
        for heading, chunk in chunk_markdown(text):
            n_chunks_total += 1
            doc_id = hashlib.sha256(
                f"{rel_path}::{heading}::{chunk}".encode("utf-8")
            ).hexdigest()
            seen_ids.add(doc_id)

            existing = coll.get(ids=[doc_id], include=[])
            if existing["ids"]:
                continue  # unchanged content — skip re-embedding

            n_chunks_new += 1
            coll.upsert(
                ids=[doc_id],
                documents=[chunk],
                metadatas=[
                    {
                        "path": rel_path,
                        "heading": heading,
                        "vault": str(vault),
                    }
                ],
            )

    # Garbage-collect chunks that no longer exist in the vault
    all_ids_resp = coll.get(include=[])
    stale = [i for i in all_ids_resp["ids"] if i not in seen_ids]
    if stale:
        coll.delete(ids=stale)

    print(
        f"[brain-index] {collection_name}: "
        f"{n_files} files · {n_chunks_total} chunks · "
        f"{n_chunks_new} new/updated · {len(stale)} removed"
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    p.add_argument("--collection", default=DEFAULT_COLLECTION)
    p.add_argument("--reset", action="store_true")
    args = p.parse_args()

    if not args.vault.exists():
        print(f"[brain-index] vault not found: {args.vault}", file=sys.stderr)
        sys.exit(1)

    index_vault(args.vault, args.collection, args.reset)


if __name__ == "__main__":
    main()
