"""Snapshot diffing."""

from __future__ import annotations

from typing import Any

from ragledger.snapshots import load_snapshot


def diff_snapshots(left_ref: str, right_ref: str) -> dict[str, Any]:
    left = load_snapshot(left_ref)
    right = load_snapshot(right_ref)

    left_docs = {document["path"]: document for document in left.get("documents", [])}
    right_docs = {document["path"]: document for document in right.get("documents", [])}

    added_docs = sorted(set(right_docs) - set(left_docs))
    removed_docs = sorted(set(left_docs) - set(right_docs))
    changed_docs = sorted(
        path for path in set(left_docs) & set(right_docs) if left_docs[path]["sha256"] != right_docs[path]["sha256"]
    )

    left_chunks = _chunks_by_id(left)
    right_chunks = _chunks_by_id(right)
    added_chunks = sorted(set(right_chunks) - set(left_chunks))
    removed_chunks = sorted(set(left_chunks) - set(right_chunks))
    changed_chunks = sorted(
        chunk_id
        for chunk_id in set(left_chunks) & set(right_chunks)
        if left_chunks[chunk_id]["chunk_hash"] != right_chunks[chunk_id]["chunk_hash"]
    )

    return {
        "left": left_ref,
        "right": right_ref,
        "added_documents": added_docs,
        "removed_documents": removed_docs,
        "changed_documents": changed_docs,
        "added_chunks": added_chunks,
        "removed_chunks": removed_chunks,
        "changed_chunks": changed_chunks,
        "summary": {
            "added_document_count": len(added_docs),
            "removed_document_count": len(removed_docs),
            "changed_document_count": len(changed_docs),
            "added_chunk_count": len(added_chunks),
            "removed_chunk_count": len(removed_chunks),
            "changed_chunk_count": len(changed_chunks),
            "retrieval_impact": _impact(len(added_chunks) + len(removed_chunks) + len(changed_chunks)),
        },
    }


def _chunks_by_id(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    chunks = {}
    for document in snapshot.get("documents", []):
        for chunk in document.get("chunks", []):
            chunks[chunk["chunk_id"]] = chunk
    return chunks


def _impact(changed_chunk_count: int) -> str:
    if changed_chunk_count == 0:
        return "none"
    if changed_chunk_count < 5:
        return "low"
    if changed_chunk_count < 20:
        return "medium"
    return "high"
