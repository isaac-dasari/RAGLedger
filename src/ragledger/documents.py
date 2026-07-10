"""Document inspection and metadata extraction."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ragledger.chunking import chunk_text
from ragledger.hashing import sha256_file
from ragledger.models import DocumentRecord

SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".yml", ".yaml"}


def iter_document_paths(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def inspect_document(root: Path, path: Path) -> DocumentRecord:
    relative_path = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8")
    metadata, body = extract_front_matter(text)
    stat = path.stat()
    title = detect_title(body, path)

    return DocumentRecord(
        path=relative_path,
        sha256=sha256_file(path),
        bytes=stat.st_size,
        modified_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        title=title,
        metadata=metadata,
        chunks=chunk_text(relative_path, body),
    )


def extract_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text
    return dict(metadata), parts[2]


def detect_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
        if stripped:
            return stripped[:80]
    return path.stem.replace("_", " ").replace("-", " ").title()
