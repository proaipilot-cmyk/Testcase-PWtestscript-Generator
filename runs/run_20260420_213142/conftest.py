
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
