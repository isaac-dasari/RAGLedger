"""Simple deterministic document chunking."""

from __future__ import annotations

from ragledger.hashing import sha256_text
from ragledger.models import ChunkRecord


def chunk_text(document_path: str, text: str, max_chars: int = 900) -> list[ChunkRecord]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []

    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue
        for start in range(0, len(paragraph), max_chars):
            chunk = paragraph[start : start + max_chars].strip()
            if chunk:
                chunks.append(chunk)

    records = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_hash = sha256_text(chunk)
        records.append(
            ChunkRecord(
                chunk_id=f"{document_path}#chunk_{index:04d}",
                document_path=document_path,
                chunk_hash=chunk_hash,
                char_count=len(chunk),
                text_preview=chunk[:160],
            )
        )
    return records
