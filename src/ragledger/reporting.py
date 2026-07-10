"""Report rendering for RAGLedger."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from ragledger.paths import DEFAULT_REPORT_PATH
from ragledger.registry import load_registry
from ragledger.snapshots import list_snapshots, load_snapshot


def build_report_payload() -> dict[str, Any]:
    corpora = load_registry()
    payload = {"corpora": []}
    for name, record in sorted(corpora.items()):
        snapshots = list_snapshots(name)
        latest = load_snapshot(f"{name}:{snapshots[-1]}") if snapshots else None
        payload["corpora"].append(
            {
                "name": name,
                "path": record.path,
                "description": record.description,
                "snapshot_count": len(snapshots),
                "latest_snapshot": latest,
            }
        )
    return payload


def write_html_report(payload: dict[str, Any], output: Path = DEFAULT_REPORT_PATH) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(_corpus_row(item) for item in payload.get("corpora", [])) or (
        '<tr><td colspan="6">No corpora registered.</td></tr>'
    )
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAGLedger Report</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f172a; color: #e2e8f0; }}
    header {{ padding: 32px; background: linear-gradient(135deg, #111827, #1e293b); border-bottom: 1px solid #334155; }}
    h1 {{ margin: 0 0 8px 0; font-size: 32px; }}
    p {{ color: #94a3b8; }}
    main {{ padding: 32px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #334155; border-radius: 14px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #1f2937; text-align: left; vertical-align: top; font-size: 14px; }}
    th {{ background: #1e293b; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
  </style>
</head>
<body>
  <header>
    <h1>RAGLedger Report</h1>
    <p>Corpus versioning, provenance, and reproducibility summary.</p>
  </header>
  <main>
    <table>
      <thead><tr><th>Corpus</th><th>Path</th><th>Snapshots</th><th>Latest</th><th>Documents</th><th>Chunks</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output.write_text(page, encoding="utf-8")
    return output


def _corpus_row(item: dict[str, Any]) -> str:
    latest = item.get("latest_snapshot") or {}
    return (
        "<tr>"
        f"<td>{escape(str(item.get('name', '')))}</td>"
        f"<td>{escape(str(item.get('path', '')))}</td>"
        f"<td>{item.get('snapshot_count', 0)}</td>"
        f"<td>{escape(str(latest.get('version', '-')))}</td>"
        f"<td>{latest.get('document_count', 0)}</td>"
        f"<td>{latest.get('chunk_count', 0)}</td>"
        "</tr>"
    )
