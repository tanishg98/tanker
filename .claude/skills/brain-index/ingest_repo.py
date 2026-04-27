#!/usr/bin/env python3
"""
Ingests a GitHub repository's signal files (README, manifests, key source files)
into the 'refs' ChromaDB collection so /cto and github-scout can pull from your
curated reference library via semantic retrieval.

Shallow-clones to a tmp dir, extracts the high-signal subset, indexes, cleans up.

Usage:
  python ingest_repo.py https://github.com/owner/name --why "Why this repo matters" --tags ui,frontend
"""
from __future__ import annotations
import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DATA_DIR = Path.home() / ".claude" / "brain-index" / "data"
COLLECTION = "refs"

# Only these files / globs get indexed — keeps signal high
SIGNAL_FILES = {
    "README.md",
    "README.MD",
    "readme.md",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Dockerfile",
    "fly.toml",
    "vercel.json",
    "railway.json",
    "schema.prisma",
    "next.config.js",
    "next.config.mjs",
    "tsconfig.json",
}
SIGNAL_DIRS = {"docs", "supabase/migrations", "prisma"}  # also pull any *.md from docs/
MAX_FILE_BYTES = 80_000  # skip huge files — they're rarely the signal


def shallow_clone(url: str, dest: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", "--single-branch", url, str(dest)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def extract_signal(repo_dir: Path) -> list[tuple[str, str]]:
    """Returns list of (relative_path, file_text) — only signal-bearing files."""
    out: list[tuple[str, str]] = []

    # Top-level signal files
    for name in SIGNAL_FILES:
        p = repo_dir / name
        if p.exists() and p.is_file() and p.stat().st_size <= MAX_FILE_BYTES:
            try:
                out.append((name, p.read_text(encoding="utf-8", errors="ignore")))
            except Exception:
                pass

    # Signal dirs (recursive *.md only)
    for d in SIGNAL_DIRS:
        dp = repo_dir / d
        if dp.exists() and dp.is_dir():
            for f in dp.rglob("*.md"):
                if f.stat().st_size <= MAX_FILE_BYTES:
                    try:
                        out.append(
                            (str(f.relative_to(repo_dir)), f.read_text(encoding="utf-8", errors="ignore"))
                        )
                    except Exception:
                        pass

    return out


def chunk(text: str, max_chars: int = 1200) -> list[str]:
    if len(text) <= max_chars:
        return [text.strip()]
    return [
        text[i : i + max_chars].strip()
        for i in range(0, len(text), max_chars - 200)
        if text[i : i + max_chars].strip()
    ]


def ingest(url: str, why: str, tags: list[str]) -> int:
    import chromadb

    repo_slug = url.rstrip("/").split("/")[-2] + "/" + url.rstrip("/").split("/")[-1]

    with tempfile.TemporaryDirectory(prefix="tanker-ref-") as tmp:
        tmp_path = Path(tmp)
        try:
            shallow_clone(url, tmp_path)
        except subprocess.CalledProcessError as e:
            print(
                f"[ingest] clone failed for {url}: {e.stderr.decode(errors='ignore')}",
                file=sys.stderr,
            )
            return 1

        files = extract_signal(tmp_path)
        if not files:
            print(f"[ingest] no signal files found in {repo_slug}", file=sys.stderr)
            return 1

        client = chromadb.PersistentClient(path=str(DATA_DIR))
        coll = client.get_or_create_collection(
            name=COLLECTION, metadata={"hnsw:space": "cosine"}
        )

        n_chunks = 0
        for rel_path, text in files:
            for piece in chunk(text):
                doc_id = hashlib.sha256(
                    f"{repo_slug}::{rel_path}::{piece}".encode("utf-8")
                ).hexdigest()
                coll.upsert(
                    ids=[doc_id],
                    documents=[piece],
                    metadatas=[
                        {
                            "repo": repo_slug,
                            "url": url,
                            "path": rel_path,
                            "why": why,
                            "tags": ",".join(tags),
                            "source": url,
                        }
                    ],
                )
                n_chunks += 1

        print(f"[ingest] {repo_slug} · {len(files)} files · {n_chunks} chunks")
        return 0


def remove_repo(url: str) -> None:
    import chromadb

    repo_slug = url.rstrip("/").split("/")[-2] + "/" + url.rstrip("/").split("/")[-1]
    client = chromadb.PersistentClient(path=str(DATA_DIR))
    try:
        coll = client.get_collection(COLLECTION)
    except Exception:
        return
    coll.delete(where={"repo": repo_slug})
    print(f"[ingest] removed all chunks for {repo_slug}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("url", help="GitHub repo URL")
    p.add_argument("--why", default="", help="Why this repo matters (1 line)")
    p.add_argument("--tags", default="", help="Comma-separated tags")
    p.add_argument("--remove", action="store_true", help="Remove this repo from the refs index")
    args = p.parse_args()

    if args.remove:
        remove_repo(args.url)
        sys.exit(0)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    sys.exit(ingest(args.url, args.why, tags))


if __name__ == "__main__":
    main()
