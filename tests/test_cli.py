from typer.testing import CliRunner

from ragledger.cli import app

runner = CliRunner()


def test_cli_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    corpus = tmp_path / "kb"
    corpus.mkdir()
    (corpus / "refund.md").write_text(
        "---\nowner: team\nsource: handbook\nretention_class: standard\n---\n# Refund\n\nRefund body.",
        encoding="utf-8",
    )
    policy = tmp_path / "policy.yml"
    policy.write_text(
        "required_metadata:\n  - owner\n  - source\n  - retention_class\nblocked_patterns:\n  - ssn\nallow_duplicate_titles: false\n",
        encoding="utf-8",
    )

    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["register", str(corpus), "--name", "kb"]).exit_code == 0
    assert runner.invoke(app, ["snapshot", "kb"]).exit_code == 0
    assert runner.invoke(app, ["list-corpora"]).exit_code == 0
    assert runner.invoke(app, ["list-snapshots", "kb"]).exit_code == 0
    assert runner.invoke(app, ["validate", "--corpus", "kb:v1", "--policy", str(policy)]).exit_code == 0
    assert runner.invoke(app, ["manifest", "--corpus", "kb:v1"]).exit_code == 0
    report = runner.invoke(app, ["report", "--html"])
    assert report.exit_code == 0
    assert (tmp_path / ".ragledger/reports/latest.html").exists()
