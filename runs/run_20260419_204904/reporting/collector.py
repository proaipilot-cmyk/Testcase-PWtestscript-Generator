"""Run collector for archived Playwright pytest results."""
from __future__ import annotations

import hashlib
import platform
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from reporting.history import build_history_index, write_json
from reporting.html_report import build_html_report


@dataclass(frozen=True)
class RunPaths:
    results_root: Path
    history_root: Path
    latest_root: Path
    run_dir: Path
    run_manifest: Path
    history_index: Path
    latest_report: Path
    latest_manifest: Path
    latest_index: Path
    screenshots_dir: Path
    traces_dir: Path
    videos_dir: Path


class RunCollector:
    """Collects per-test execution metadata and emits archived reports."""

    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        self.results_root = (Path(str(config.rootpath)) / config.getoption("--report-results-root")).resolve()
        self.history_root = self.results_root / "history"
        self.latest_root = self.results_root / "latest"
        self.run_dir = self.history_root / self.run_id
        self.artifacts_dir = self.run_dir / "artifacts"
        self.screenshots_dir = self.artifacts_dir / "screenshots"
        self.traces_dir = self.artifacts_dir / "traces"
        self.videos_dir = self.artifacts_dir / "videos"
        for path in [
            self.results_root,
            self.history_root,
            self.latest_root,
            self.run_dir,
            self.screenshots_dir,
            self.traces_dir,
            self.videos_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        self.paths = RunPaths(
            results_root=self.results_root,
            history_root=self.history_root,
            latest_root=self.latest_root,
            run_dir=self.run_dir,
            run_manifest=self.run_dir / "run_manifest.json",
            history_index=self.history_root / "index.json",
            latest_report=self.latest_root / "playwright_report.html",
            latest_manifest=self.latest_root / "run_manifest.json",
            latest_index=self.latest_root / "history_index.json",
            screenshots_dir=self.screenshots_dir,
            traces_dir=self.traces_dir,
            videos_dir=self.videos_dir,
        )
        self.started_at = _iso_now()
        self.video_mode = config.getoption("--report-video")
        self.screenshot_mode = config.getoption("--report-screenshot")
        self.trace_mode = config.getoption("--report-trace")
        self.records: dict[str, dict[str, Any]] = {}

    def record_phase(
        self,
        item: pytest.Item,
        report: pytest.TestReport,
        call: pytest.CallInfo[object],
    ) -> None:
        record = self._ensure_record(item)
        phase = report.when
        record["outcome_by_phase"][phase] = report.outcome
        record["duration_ms"] += round(report.duration * 1000)
        record["phases"][phase] = {"outcome": report.outcome, "duration_ms": round(report.duration * 1000)}

        for section_name, content in getattr(report, "sections", []):
            if not content.strip():
                continue
            bucket = self._output_bucket(section_name)
            if not bucket:
                continue
            record["output"].setdefault(phase, []).append(f"[{bucket}] {content.rstrip()}")

        if report.failed:
            record["status"] = self._status_for_failure(phase, call)
            record["failure"] = {
                "phase": phase,
                "message": self._extract_failure_message(report),
                "trace": self._extract_trace(report),
                "exception_type": self._extract_exception_type(call),
            }
        elif report.skipped and record["status"] not in {"failed", "broken"}:
            record["status"] = "skipped"
            record["failure"] = {
                "phase": phase,
                "message": self._extract_failure_message(report),
                "trace": self._extract_trace(report),
                "exception_type": self._extract_exception_type(call),
            }
        elif phase == "call" and report.passed and record["status"] == "pending":
            record["status"] = "passed"

    def record_page_state(self, item: pytest.Item, page: Any) -> None:
        record = self._ensure_record(item)
        if record["page"]["url"] == "-":
            record["page"]["url"] = getattr(page, "url", "-") or "-"

    def record_internal_error(self, item: pytest.Item, area: str, exc: Exception) -> None:
        record = self._ensure_record(item)
        record["internal_errors"].append({"area": area, "message": str(exc)})

    def attach_artifact(self, item: pytest.Item, kind: str, path: Path) -> None:
        record = self._ensure_record(item)
        relative_path = path.relative_to(self.run_dir).as_posix()
        if kind == "video":
            if relative_path not in record["artifacts"]["video"]:
                record["artifacts"]["video"].append(relative_path)
            return
        record["artifacts"][kind] = relative_path

    def screenshot_path_for(self, item: pytest.Item) -> Path:
        return self.screenshots_dir / f"{self._slug_for(item)}.png"

    def trace_path_for(self, item: pytest.Item) -> Path:
        return self.traces_dir / f"{self._slug_for(item)}.zip"

    def item_has_failure(self, item: pytest.Item) -> bool:
        return any(
            getattr(item, attr, None) and getattr(getattr(item, attr), "failed", False)
            for attr in ("rep_setup", "rep_call", "rep_teardown")
        )

    def finalize_session(self, exitstatus: int) -> None:
        finished_at = _iso_now()
        manifest = self._build_manifest(exitstatus, finished_at)
        write_json(self.paths.run_manifest, manifest)
        history_index = build_history_index(self.history_root)
        write_json(self.paths.history_index, history_index)
        build_html_report(self.paths.latest_report, manifest, history_index)
        write_json(self.paths.latest_manifest, manifest)
        write_json(self.paths.latest_index, history_index)

    def _build_manifest(self, exitstatus: int, finished_at: str) -> dict[str, Any]:
        tests = sorted(self.records.values(), key=lambda entry: entry["nodeid"])
        summary = {
            "total": len(tests),
            "passed": sum(1 for test in tests if test["status"] == "passed"),
            "failed": sum(1 for test in tests if test["status"] == "failed"),
            "broken": sum(1 for test in tests if test["status"] == "broken"),
            "skipped": sum(1 for test in tests if test["status"] == "skipped"),
        }
        summary["pass_rate"] = round((summary["passed"] / summary["total"]) * 100, 1) if summary["total"] else 0.0
        duration_ms = sum(test["duration_ms"] for test in tests)
        return {
            "schema_version": 1,
            "run": {
                "run_id": self.run_id,
                "started_at": self.started_at,
                "finished_at": finished_at,
                "duration_ms": duration_ms,
                "exitstatus": exitstatus,
                "results_root": self.results_root.as_posix(),
                "summary": summary,
                "environment": {
                    "python": sys.version.split()[0],
                    "platform": platform.platform(),
                    "pytest": pytest.__version__,
                    "cwd": str(self.config.rootpath),
                    "video_mode": self.video_mode,
                    "screenshot_mode": self.screenshot_mode,
                    "trace_mode": self.trace_mode,
                },
            },
            "tests": tests,
        }

    def _ensure_record(self, item: pytest.Item) -> dict[str, Any]:
        stable_id = item.nodeid
        if stable_id in self.records:
            return self.records[stable_id]

        callspec = getattr(item, "callspec", None)
        param_id = getattr(callspec, "id", None)
        parameters = {}
        if callspec:
            parameters = {name: repr(value) for name, value in callspec.params.items()}

        cls = getattr(item, "cls", None)
        record = {
            "stable_id": stable_id,
            "nodeid": item.nodeid,
            "display_name": item.name,
            "module": getattr(item, "module", None).__name__ if getattr(item, "module", None) else "",
            "class_name": cls.__name__ if cls else "",
            "param_id": param_id,
            "parameters": parameters,
            "status": "pending",
            "duration_ms": 0,
            "outcome_by_phase": {},
            "phases": {},
            "failure": {"phase": None, "message": "", "trace": "", "exception_type": ""},
            "artifacts": {"screenshot": None, "trace": None, "video": []},
            "output": {},
            "page": {"url": "-"},
            "internal_errors": [],
        }
        self.records[stable_id] = record
        return record

    def _slug_for(self, item: pytest.Item) -> str:
        base = re.sub(r"[^A-Za-z0-9._-]+", "-", item.nodeid).strip("-")
        digest = hashlib.sha1(item.nodeid.encode("utf-8")).hexdigest()[:10]
        return f"{base[:90]}-{digest}"

    @staticmethod
    def _output_bucket(section_name: str) -> str | None:
        normalized = section_name.lower()
        if "stdout" in normalized:
            return "stdout"
        if "stderr" in normalized:
            return "stderr"
        if "log" in normalized:
            return "log"
        return None

    @staticmethod
    def _status_for_failure(phase: str, call: pytest.CallInfo[object]) -> str:
        if phase != "call":
            return "broken"
        if call.excinfo and call.excinfo.errisinstance(AssertionError):
            return "failed"
        return "broken"

    @staticmethod
    def _extract_failure_message(report: pytest.TestReport) -> str:
        lines = [line.strip() for line in str(report.longrepr).splitlines() if line.strip()]
        if not lines:
            return report.outcome
        return lines[-1][:400]

    @staticmethod
    def _extract_trace(report: pytest.TestReport) -> str:
        return str(report.longrepr) if report.longrepr else ""

    @staticmethod
    def _extract_exception_type(call: pytest.CallInfo[object]) -> str:
        if not call.excinfo:
            return ""
        return call.excinfo.typename or call.excinfo.type.__name__


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()
