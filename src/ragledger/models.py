"""Shared data models for RAGLedger."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CorpusRecord:
    name: str
    path: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    document_path: str
    chunk_hash: str
    char_count: int
    text_preview: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DocumentRecord:
    path: str
    sha256: str
    bytes: int
    modified_time: str
    title: str
    metadata: dict[str, Any]
    chunks: list[ChunkRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["chunks"] = [chunk.to_dict() for chunk in self.chunks]
        return payload


@dataclass(frozen=True)
class Snapshot:
    corpus: str
    version: str
    created_at: str
    corpus_hash: str
    document_count: int
    chunk_count: int
    documents: list[DocumentRecord]

    def to_dict(self) -> dict[str, Any]:
        return {
            "corpus": self.corpus,
            "version": self.version,
            "created_at": self.created_at,
            "corpus_hash": self.corpus_hash,
            "document_count": self.document_count,
            "chunk_count": self.chunk_count,
            "documents": [document.to_dict() for document in self.documents],
        }
