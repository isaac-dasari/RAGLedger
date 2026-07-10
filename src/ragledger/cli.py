"""RAGLedger command-line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ragledger.diffing import diff_snapshots
from ragledger.manifest import build_manifest, write_manifest
from ragledger.paths import DEFAULT_REPORT_PATH, MANIFEST_DIR
from ragledger.policy import validate_snapshot
from ragledger.registry import init_project, load_registry, register_corpus
from ragledger.reporting import build_report_payload, write_html_report
from ragledger.snapshots import create_snapshot, list_snapshots

app = typer.Typer(help="RAGLedger: RAG corpus versioning and eval data provenance")
console = Console()


@app.command()
def init() -> None:
    """Initialize local RAGLedger metadata."""

    init_project()
    console.print("[green]Initialized RAGLedger in .ragledger/[/green]")


@app.command()
def register(
    path: Path,
    name: Annotated[str, typer.Option("--name", "-n")],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
) -> None:
    """Register a local document corpus."""

    record = register_corpus(path=path, name=name, description=description)
    console.print(f"[green]Registered corpus {record.name}: {record.path}[/green]")


@app.command("list-corpora")
def list_corpora() -> None:
    """List registered corpora."""

    table = Table(title="RAGLedger Corpora")
    table.add_column("Name")
    table.add_column("Path")
    table.add_column("Description")
    for record in load_registry().values():
        table.add_row(record.name, record.path, record.description)
    console.print(table)


@app.command()
def snapshot(corpus: str) -> None:
    """Create a new corpus snapshot."""

    result = create_snapshot(corpus)
    console.print(f"[green]Snapshot created: {result.corpus}:{result.version}[/green]")
    console.print(f"Documents: {result.document_count}")
    console.print(f"Chunks: {result.chunk_count}")
    console.print(f"Corpus hash: {result.corpus_hash[:12]}")


@app.command("list-snapshots")
def list_corpus_snapshots(corpus: str) -> None:
    """List snapshots for one corpus."""

    table = Table(title=f"Snapshots: {corpus}")
    table.add_column("Version")
    for version in list_snapshots(corpus):
        table.add_row(version)
    console.print(table)


@app.command("diff")
def diff_command(left: str, right: str) -> None:
    """Diff two snapshots in corpus:version form."""

    result = diff_snapshots(left, right)
    console.print_json(json.dumps(result))


@app.command()
def validate(
    corpus: Annotated[str, typer.Option("--corpus", "-c")],
    policy: Annotated[Path, typer.Option("--policy", "-p")],
    fail_on_error: Annotated[bool, typer.Option("--fail-on-error")] = False,
) -> None:
    """Validate a snapshot against a RAG data policy."""

    result = validate_snapshot(corpus, policy)
    console.print_json(json.dumps(result))
    if fail_on_error and not result["passed"]:
        raise typer.Exit(code=1)


@app.command()
def manifest(
    corpus: Annotated[str, typer.Option("--corpus", "-c")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    eval_set: Annotated[str, typer.Option("--eval-set")] = "",
    prompt_version: Annotated[str, typer.Option("--prompt-version")] = "",
    top_k: Annotated[int, typer.Option("--top-k")] = 5,
) -> None:
    """Create a reproducibility manifest for a snapshot."""

    result = build_manifest(corpus, eval_set=eval_set, prompt_version=prompt_version, retriever_top_k=top_k)
    output_path = output or (MANIFEST_DIR / f"{corpus.replace(':', '_')}.yml")
    write_manifest(result, output_path)
    console.print(f"[green]Manifest written to {output_path}[/green]")


@app.command()
def report(
    html: Annotated[bool, typer.Option("--html")] = False,
    output: Annotated[Path, typer.Option("--output", "-o")] = DEFAULT_REPORT_PATH,
) -> None:
    """Show or render the RAGLedger project report."""

    payload = build_report_payload()
    table = Table(title="RAGLedger Report")
    table.add_column("Corpus")
    table.add_column("Snapshots")
    table.add_column("Latest")
    table.add_column("Documents")
    table.add_column("Chunks")
    for item in payload.get("corpora", []):
        latest = item.get("latest_snapshot") or {}
        table.add_row(
            str(item.get("name", "")),
            str(item.get("snapshot_count", 0)),
            str(latest.get("version", "-")),
            str(latest.get("document_count", 0)),
            str(latest.get("chunk_count", 0)),
        )
    console.print(table)

    if html:
        write_html_report(payload, output)
        console.print(f"[green]HTML report written to {output}[/green]")
