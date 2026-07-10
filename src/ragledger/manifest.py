"""Reproducibility manifest generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ragledger.snapshots import load_snapshot


def build_manifest(
    corpus_ref: str,
    eval_set: str = "",
    prompt_version: str = "",
    retriever_top_k: int = 5,
) -> dict[str, Any]:
    snapshot = load_snapshot(corpus_ref)
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "corpus": snapshot["corpus"],
        "corpus_version": snapshot["version"],
        "corpus_hash": snapshot["corpus_hash"],
        "document_count": snapshot["document_count"],
        "chunk_count": snapshot["chunk_count"],
        "chunking": {"strategy": "paragraph", "max_chars": 900},
        "embedding": {"provider": "not_captured", "model": "not_captured"},
        "retriever": {"top_k": retriever_top_k},
        "prompt_version": prompt_version,
        "eval_set": eval_set,
    }


def write_manifest(manifest: dict[str, Any], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return output
