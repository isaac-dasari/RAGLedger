"""Snapshot creation and loading."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ragledger.documents import inspect_document, iter_document_paths
from ragledger.hashing import sha256_text
from ragledger.models import DocumentRecord, Snapshot
from ragledger.paths import SNAPSHOT_DIR
from ragledger.registry import get_corpus


def create_snapshot(corpus_name: str) -> Snapshot:
    corpus = get_corpus(corpus_name)
    root = Path(corpus.path)
    documents = [inspect_document(root, path) for path in iter_document_paths(root)]
    version = next_snapshot_version(corpus_name)
    corpus_hash = compute_corpus_hash(documents)
    snapshot = Snapshot(
        corpus=corpus_name,
        version=version,
        created_at=datetime.now(timezone.utc).isoformat(),
        corpus_hash=corpus_hash,
        document_count=len(documents),
        chunk_count=sum(len(document.chunks) for document in documents),
        documents=documents,
    )
    save_snapshot(snapshot)
    return snapshot


def next_snapshot_version(corpus_name: str) -> str:
    existing = list_snapshots(corpus_name)
    return f"v{len(existing) + 1}"


def save_snapshot(snapshot: Snapshot) -> Path:
    path = snapshot_path(snapshot.corpus, snapshot.version)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
    return path


def list_snapshots(corpus_name: str) -> list[str]:
    directory = SNAPSHOT_DIR / corpus_name
    if not directory.exists():
        return []
    return sorted(path.stem for path in directory.glob("v*.json"))


def load_snapshot(ref: str) -> dict[str, Any]:
    corpus, version = parse_snapshot_ref(ref)
    path = snapshot_path(corpus, version)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot does not exist: {ref}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_snapshot_ref(ref: str) -> tuple[str, str]:
    if ":" not in ref:
        raise ValueError("Snapshot reference must be in corpus:version form")
    corpus, version = ref.split(":", 1)
    return corpus, version


def snapshot_path(corpus_name: str, version: str) -> Path:
    return SNAPSHOT_DIR / corpus_name / f"{version}.json"


def compute_corpus_hash(documents: list[DocumentRecord]) -> str:
    payload = "\n".join(f"{doc.path}:{doc.sha256}" for doc in sorted(documents, key=lambda item: item.path))
    return sha256_text(payload)
