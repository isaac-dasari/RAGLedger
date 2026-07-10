from pathlib import Path

from ragledger.diffing import diff_snapshots
from ragledger.manifest import build_manifest
from ragledger.policy import validate_snapshot
from ragledger.registry import register_corpus
from ragledger.snapshots import create_snapshot


def _write_doc(path: Path, title: str, body: str, metadata: bool = True) -> None:
    prefix = ""
    if metadata:
        prefix = "---\nowner: team\nsource: handbook\nretention_class: standard\n---\n"
    path.write_text(f"{prefix}# {title}\n\n{body}", encoding="utf-8")


def test_diff_policy_and_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus_dir = tmp_path / "kb"
    corpus_dir.mkdir()
    _write_doc(corpus_dir / "refund.md", "Refund", "Original refund policy.")

    register_corpus(corpus_dir, "kb")
    create_snapshot("kb")
    _write_doc(corpus_dir / "refund.md", "Refund", "Updated refund policy.")
    create_snapshot("kb")

    diff = diff_snapshots("kb:v1", "kb:v2")
    assert diff["summary"]["changed_document_count"] == 1
    assert diff["summary"]["retrieval_impact"] in {"low", "medium", "high"}

    policy = tmp_path / "policy.yml"
    policy.write_text(
        "required_metadata:\n  - owner\n  - source\n  - retention_class\nblocked_patterns:\n  - ssn\nallow_duplicate_titles: false\n",
        encoding="utf-8",
    )
    result = validate_snapshot("kb:v2", policy)
    assert result["passed"]

    manifest = build_manifest("kb:v2", eval_set="support_eval", prompt_version="prompt_v1")
    assert manifest["corpus"] == "kb"
    assert manifest["eval_set"] == "support_eval"
