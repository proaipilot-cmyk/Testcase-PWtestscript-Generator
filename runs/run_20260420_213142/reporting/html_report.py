"""Static HTML report builder for archived Playwright pytest runs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_TEMPLATE_PATH = Path(__file__).parent / "report_template.html"


def build_html_report(output_path: Path, manifest: dict[str, Any], history_index: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    current_run_id = manifest["run"]["run_id"]

    report_tests: list[dict[str, Any]] = []
    history_tests = history_index.get("tests", {})
    for test in manifest["tests"]:
        history_runs = history_tests.get(test["stable_id"], {}).get("runs", [])
        report_tests.append(
            {
                **test,
                "history": [_with_asset_prefix(run, current_run_id=None) for run in history_runs],
                "current": _with_asset_prefix(test, current_run_id=current_run_id),
            }
        )

    payload = {
        "generated_at": manifest["run"]["finished_at"],
        "run": manifest["run"],
        "tests": report_tests,
        "runs": history_index.get("runs", []),
    }

    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.replace("__REPORT_DATA__", json.dumps(payload))
    output_path.write_text(html, encoding="utf-8")


def _with_asset_prefix(entry: dict[str, Any], current_run_id: str | None) -> dict[str, Any]:
    run_id = current_run_id or entry["run_id"]
    artifacts = entry.get("artifacts", {})
    prefix = f"../history/{run_id}/"
    return {
        **entry,
        "artifacts": {
            "screenshot": _prefixed_path(prefix, artifacts.get("screenshot")),
            "trace": _prefixed_path(prefix, artifacts.get("trace")),
            "video": [_prefixed_path(prefix, p) for p in artifacts.get("video", []) if p],
        },
    }


def _prefixed_path(prefix: str, path: str | None) -> str | None:
    if not path:
        return None
    return prefix + path
