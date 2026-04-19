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
    'resolve_locator_sync',
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


def resolve_locator_sync(page, target: str, context_data: Dict[str, Any] = None):
    """Synchronous locator resolution with repository fallback.

    The original implementation only used heuristic selectors, which meant
    elements defined in ``object_repo/*.json`` (e.g., the error message) were
    never found, causing empty ``error_text`` values.  This updated version
    first attempts to locate the element using the repository definition –
    mirroring the async ``resolve_locator`` strategy – and falls back to the
    original heuristics if the repo lookup fails.
    """
    from pathlib import Path
    import json

    # ---------------------------------------------------------------------
    # Repo strategy (sync version of async engine's _repo_strategy)
    # ---------------------------------------------------------------------
    try:
        current_url = getattr(page, "url", "")
        repo_dir = Path.cwd() / "object_repo"
        if repo_dir.exists():
            for json_file in repo_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    url_pattern = data.get("url_pattern", "")
                    if url_pattern and url_pattern in current_url:
                        elements = data.get("elements", {})
                        if target in elements:
                            selector = elements[target].get("selector")
                            if selector:
                                return page.locator(selector)
                except Exception:
                    continue
    except Exception:
        # If any part of the repo lookup fails we silently continue to heuristics
        pass

    # ---------------------------------------------------------------------
    # Heuristic strategies (original logic, unchanged but kept after repo)
    # ---------------------------------------------------------------------
    # Strategy 1: Try ID
    try:
        locator = page.locator(f'#{target}')
        if locator.count() == 1:
            return locator
    except Exception:
        pass

    # Strategy 2: Try data-test-id
    try:
        locator = page.locator(f'[data-test-id="{target}"]')
        count = locator.count()
        if count == 1:
            return locator
        if count > 1:
            return locator.first
    except Exception:
        pass

    # Strategy 3: Try data-test
    try:
        locator = page.locator(f'[data-test="{target}"]')
        count = locator.count()
        if count == 1:
            return locator
        if count > 1:
            return locator.first
    except Exception:
        pass

    # Strategy 4: Try by placeholder
    try:
        locator = page.get_by_placeholder(target)
        count = locator.count()
        if count == 1:
            return locator
        if count > 1:
            return locator.first
    except Exception:
        pass

    # Strategy 5: Try by label
    try:
        locator = page.get_by_label(target)
        count = locator.count()
        if count == 1:
            return locator
        if count > 1:
            return locator.first
    except Exception:
        pass

    # Strategy 6: Try by text
    try:
        locator = page.get_by_text(target)
        count = locator.count()
        if count == 1:
            return locator
        if count > 1:
            return locator.first
    except Exception:
        pass

    # Fallback: Generic selector with healing (return first if multiple)
    locator = page.locator('button[type="button"], input, a, [role="button"]')
    return locator.first if locator.count() > 1 else locator
