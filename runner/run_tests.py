"""Entry point for the root Playwright suite and custom report pipeline.

Each run creates a timestamped folder under runs/ with a full copy of the
project source (tests, steps, pages, object_repo, locator).  Pytest executes
inside that isolated folder so artefacts, reports, and __pycache__ never
collide between runs.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories that form the execution-ready project
SOURCE_DIRS = ["tests", "steps", "pages", "object_repo", "locator", "reporting"]


def _copy_source(src_dir: Path, dst_dir: Path) -> None:
    """Copy *src_dir* into *dst_dir*, skipping __pycache__ and .pyc files."""
    for item in src_dir.rglob("*"):
        if "__pycache__" in item.parts or item.suffix == ".pyc":
            continue
        rel = item.relative_to(src_dir)
        target = dst_dir / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def create_run_folder() -> Path:
    """Create a unique timestamped run folder and populate it."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / "runs" / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    for name in SOURCE_DIRS:
        src = ROOT / name
        if src.exists():
            dst = run_dir / name
            dst.mkdir(parents=True, exist_ok=True)
            _copy_source(src, dst)

    return run_dir


def main() -> int:
    print("[runner] Triggering automation generation pipeline...")
    for script in ["parser/demo.py", "planner/demo.py", "generator/demo.py", "validator/demo.py"]:
        print(f"[runner] Running {script}...")
        res = subprocess.run([sys.executable, script], cwd=ROOT)
        if res.returncode != 0:
            print(f"[runner] ERROR: {script} failed with exit code {res.returncode}. Aborting.")
            return res.returncode
            
    run_dir = create_run_folder()
    print(f"[runner] Isolated run folder: {run_dir}")

    # Inject a minimal conftest.py to bridge pytest hooks with our RunCollector
    conftest_path = run_dir / "conftest.py"
    conftest_code = """
import pytest
from reporting.collector import RunCollector

def pytest_addoption(parser):
    parser.addoption("--report-results-root", default="test-results")
    parser.addoption("--report-video", default="on-failure")
    parser.addoption("--report-screenshot", default="on-failure")
    parser.addoption("--report-trace", default="on-failure")

def pytest_configure(config):
    config.pluginmanager.register(RunCollector(config), "run_collector_plugin")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    collector = item.config.pluginmanager.get_plugin("run_collector_plugin")
    if collector:
        collector.record_phase(item, report, call)

def pytest_sessionfinish(session, exitstatus):
    collector = session.config.pluginmanager.get_plugin("run_collector_plugin")
    if collector:
        collector.finalize_session(exitstatus)
"""
    conftest_path.write_text(conftest_code, encoding="utf-8")

    # Only run tests if the tests dir actually exists so pytest doesn't crash on Boot
    tests_target = run_dir / "tests"
    if not tests_target.exists():
        tests_target.mkdir(parents=True, exist_ok=True)
        # Create a tiny dummy test just so the run completes and generates a report
        (tests_target / "test_dummy.py").write_text("def test_placeholder(): pass", encoding="utf-8")

    command = [sys.executable, "-m", "pytest", "tests", "-v"]
    completed = subprocess.run(command, cwd=run_dir, check=False)

    report = run_dir / "test-results" / "playwright_report.html"
    print(f"[runner] Results in: {run_dir}")
    if report.exists():
        print(f"[runner] HTML report: {report}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
