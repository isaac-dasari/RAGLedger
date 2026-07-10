"""Corpus registry management."""

from __future__ import annotations

from pathlib import Path

import yaml

from ragledger.models import CorpusRecord
from ragledger.paths import LEDGER_DIR, REGISTRY_PATH


def init_project() -> None:
    LEDGER_DIR.mkdir(exist_ok=True)
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text("corpora: {}\n", encoding="utf-8")


def load_registry() -> dict[str, CorpusRecord]:
    init_project()
    payload = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {"corpora": {}}
    records = {}
    for name, raw in payload.get("corpora", {}).items():
        records[name] = CorpusRecord(
            name=name,
            path=str(raw.get("path", "")),
            description=str(raw.get("description", "")),
        )
    return records


def save_registry(records: dict[str, CorpusRecord]) -> None:
    init_project()
    payload = {"corpora": {name: record.to_dict() for name, record in sorted(records.items())}}
    REGISTRY_PATH.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")


def register_corpus(path: Path, name: str, description: str = "") -> CorpusRecord:
    if not path.exists():
        raise FileNotFoundError(f"Corpus path does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Corpus path is not a directory: {path}")
    records = load_registry()
    record = CorpusRecord(name=name, path=str(path), description=description)
    records[name] = record
    save_registry(records)
    return record


def get_corpus(name: str) -> CorpusRecord:
    records = load_registry()
    if name not in records:
        raise KeyError(f"Corpus is not registered: {name}")
    return records[name]
