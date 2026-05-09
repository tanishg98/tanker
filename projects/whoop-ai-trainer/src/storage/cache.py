"""Simple JSON-based report cache for saving and loading daily briefs."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

REPORTS_DIR = Path.home() / ".cache" / "whoop_ai_trainer" / "reports"


def save_report(report: str, specialist_reports: dict[str, str]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    path = REPORTS_DIR / f"{today}.json"
    payload = {"date": today, "master": report, "specialists": specialist_reports}
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_latest_report() -> dict | None:
    if not REPORTS_DIR.exists():
        return None
    reports = sorted(REPORTS_DIR.glob("*.json"), reverse=True)
    if not reports:
        return None
    return json.loads(reports[0].read_text())


def load_report_for_date(target_date: date) -> dict | None:
    path = REPORTS_DIR / f"{target_date.isoformat()}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None
