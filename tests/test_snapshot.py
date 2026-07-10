from pathlib import Path

from ragledger.registry import register_corpus
from ragledger.snapshots import create_snapshot, list_snapshots, load_snapshot


def test_snapshot_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus_dir = tmp_path / "kb"
    corpus_dir.mkdir()
    (corpus_dir / "policy.md").write_text(
        "---\nowner: team\nsource: handbook\nretention_class: standard\n---\n# Policy\n\nBody text.",
        encoding="utf-8",
    )

    register_corpus(corpus_dir, "kb")
    snapshot = create_snapshot("kb")

    assert snapshot.version == "v1"
    assert snapshot.document_count == 1
    assert snapshot.chunk_count >= 1
    assert list_snapshots("kb") == ["v1"]
    assert load_snapshot("kb:v1")["corpus"] == "kb"
