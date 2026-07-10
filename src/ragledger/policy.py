"""Policy validation for RAG corpora."""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ragledger.snapshots import load_snapshot

DEFAULT_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}


def validate_snapshot(corpus_ref: str, policy_path: Path) -> dict[str, Any]:
    snapshot = load_snapshot(corpus_ref)
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    violations: list[dict[str, Any]] = []

    violations.extend(_required_metadata(snapshot, policy.get("required_metadata", [])))
    violations.extend(_duplicate_titles(snapshot, bool(policy.get("allow_duplicate_titles", True))))
    violations.extend(_stale_documents(snapshot, policy.get("max_document_age_days")))
    violations.extend(_blocked_patterns(snapshot, policy.get("blocked_patterns", [])))

    return {
        "corpus": corpus_ref,
        "policy": str(policy_path),
        "passed": not violations,
        "violation_count": len(violations),
        "violations": violations,
    }


def _required_metadata(snapshot: dict[str, Any], required: list[str]) -> list[dict[str, Any]]:
    violations = []
    for document in snapshot.get("documents", []):
        metadata = document.get("metadata", {})
        for key in required:
            if key not in metadata or metadata[key] in {None, ""}:
                violations.append(
                    {
                        "code": "MISSING_METADATA",
                        "severity": "error",
                        "path": document["path"],
                        "message": f"Missing required metadata: {key}",
                    }
                )
    return violations


def _duplicate_titles(snapshot: dict[str, Any], allow_duplicate_titles: bool) -> list[dict[str, Any]]:
    if allow_duplicate_titles:
        return []
    titles = Counter(document.get("title", "") for document in snapshot.get("documents", []))
    duplicates = {title for title, count in titles.items() if title and count > 1}
    return [
        {
            "code": "DUPLICATE_TITLE",
            "severity": "warn",
            "path": document["path"],
            "message": f"Duplicate title detected: {document.get('title', '')}",
        }
        for document in snapshot.get("documents", [])
        if document.get("title", "") in duplicates
    ]


def _stale_documents(snapshot: dict[str, Any], max_age_days: int | None) -> list[dict[str, Any]]:
    if max_age_days is None:
        return []
    now = datetime.now(timezone.utc)
    violations = []
    for document in snapshot.get("documents", []):
        modified = datetime.fromisoformat(document["modified_time"])
        age_days = (now - modified).days
        if age_days > int(max_age_days):
            violations.append(
                {
                    "code": "STALE_DOCUMENT",
                    "severity": "warn",
                    "path": document["path"],
                    "message": f"Document is {age_days} days old",
                }
            )
    return violations


def _blocked_patterns(snapshot: dict[str, Any], pattern_names: list[str]) -> list[dict[str, Any]]:
    compiled = {name: re.compile(DEFAULT_PATTERNS[name]) for name in pattern_names if name in DEFAULT_PATTERNS}
    violations = []
    for document in snapshot.get("documents", []):
        text = "\n".join(chunk.get("text_preview", "") for chunk in document.get("chunks", []))
        for name, pattern in compiled.items():
            if pattern.search(text):
                violations.append(
                    {
                        "code": "BLOCKED_PATTERN",
                        "severity": "error",
                        "path": document["path"],
                        "message": f"Blocked pattern detected: {name}",
                    }
                )
    return violations
