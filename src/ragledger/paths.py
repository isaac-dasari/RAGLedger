"""Local project paths."""

from pathlib import Path

LEDGER_DIR = Path(".ragledger")
REGISTRY_PATH = LEDGER_DIR / "registry.yml"
SNAPSHOT_DIR = LEDGER_DIR / "snapshots"
MANIFEST_DIR = LEDGER_DIR / "manifests"
REPORT_DIR = LEDGER_DIR / "reports"
DEFAULT_REPORT_PATH = REPORT_DIR / "latest.html"
