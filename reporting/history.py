"""Helpers for archived run manifests and history indexes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_history_index(history_root: Path) -> dict[str, Any]:
    manifests = sorted(history_root.glob("*/run_manifest.json"))
    runs: list[dict[str, Any]] = []
    tests: dict[str, dict[str, Any]] = {}

    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        run = manifest["run"]
        runs.append(
            {
                "run_id": run["run_id"],
                "started_at": run["started_at"],
                "duration_ms": run["duration_ms"],
                "summary": run["summary"],
                "manifest_path": manifest_path.relative_to(history_root).as_posix(),
            }
        )

        for test in manifest["tests"]:
            stable_id = test["stable_id"]
            entry = tests.setdefault(
                stable_id,
                {
                    "stable_id": stable_id,
                    "display_name": test["display_name"],
                    "nodeid": test["nodeid"],
                    "module": test["module"],
                    "class_name": test["class_name"],
                    "param_id": test["param_id"],
                    "runs": [],
                },
            )
            entry["runs"].append(
                {
                    "run_id": run["run_id"],
                    "started_at": run["started_at"],
                    "status": test["status"],
                    "duration_ms": test["duration_ms"],
                    "failure_message": test["failure"]["message"],
                    "artifacts": test["artifacts"],
                    "page": test["page"],
                }
            )

    runs.sort(key=lambda run: run["started_at"], reverse=True)
    for entry in tests.values():
        entry["runs"].sort(key=lambda run: run["started_at"], reverse=True)

    return {
        "schema_version": 1,
        "generated_at": runs[0]["started_at"] if runs else None,
        "runs": runs,
        "tests": tests,
    }
