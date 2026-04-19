"""Locator strategies package."""
from locator.strategies.repo import RepoStrategy
from locator.strategies.snapshot import SnapshotStrategy
from locator.strategies.fallback import FallbackStrategy

__all__ = [
    'RepoStrategy',
    'SnapshotStrategy',
    'FallbackStrategy',
]
