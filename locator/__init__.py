"""Locator package - Dynamic locator resolution for Playwright tests."""
from pathlib import Path
from playwright.async_api import Page, Locator
from typing import Dict, Any, Optional

# Import engine
from locator.engine import LocatorEngine, LocatorResolutionError
from locator.strategies.repo import RepoStrategy
from locator.strategies.snapshot import SnapshotStrategy
from locator.strategies.fallback import FallbackStrategy

__all__ = [
    'LocatorEngine',
    'LocatorResolutionError',
    'RepoStrategy',
    'SnapshotStrategy',
    'FallbackStrategy',
    'resolve_locator',
    'create_engine',
]


# Global engine instance
_engine: Optional[LocatorEngine] = None


def create_engine(base_dir: Path = None) -> LocatorEngine:
    """
    Create and return a locator engine instance.

    Args:
        base_dir: Base directory for loading object_repo files.
                  Defaults to cwd so it resolves correctly inside
                  timestamped run folders.

    Returns:
        LocatorEngine instance
    """
    global _engine
    if _engine is None:
        _engine = LocatorEngine(base_dir or Path.cwd())
    return _engine


async def resolve_locator(page: Page, target: str, context_data: Dict[str, Any] = None) -> Locator:
    """
    Resolve a locator for the given target.
    
    This is the main entry point for test code and generators.
    
    Contract:
    - Takes planner output: {"action": "click", "target": "login_button"}
    - Returns: Playwright Locator object ready for interaction
    
    Strategy order (MANDATORY):
    1. Repo (primary - from object_repo/*.json)
    2. Snapshot (fallback - from page.accessibility.snapshot())
    3. Fallback (last resort - generic patterns)
    
    Args:
        page: Playwright Page object
        target: Element identifier (e.g., "login_button")
        context_data: Optional context {"learn": True} to cache successful discoveries
    
    Returns:
        Playwright Locator object
    
    Raises:
        LocatorResolutionError: If all strategies fail
    
    Example:
        >>> locator = await resolve_locator(page, "login_button")
        >>> await locator.click()
    """
    engine = create_engine()
    return await engine.resolve(page, target, context_data)
