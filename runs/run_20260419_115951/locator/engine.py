"""Locator Resolution Engine - Implements late binding strategy pattern."""
from playwright.async_api import Page, Locator, BrowserContext
from typing import Dict, Any, Optional, List, Callable
import json
from pathlib import Path
import asyncio


class LocatorResolutionError(Exception):
    """Raised when a locator cannot be resolved by any strategy."""
    pass


class LocatorEngine:
    """
    Main locator resolution engine.
    Implements strategy pattern: Repo → Snapshot → Fallback.
    
    Contract:
    - Takes planner output: {"action": "click", "target": "login_button"}
    - Returns: playwright Locator object
    
    Late binding: Resolution happens at test execution time, not generation time.
    """
    
    def __init__(self, base_dir: Path = None):
        """Initialize engine with optional base directory for repo loading."""
        self.base_dir = base_dir or Path.cwd()
        self._repo_cache = {}  # Cache loaded repos
        self._learned_locators = {}  # Optional: cache successful snapshots
    
    async def resolve(self, page: Page, target: str, context_data: Dict[str, Any] = None) -> Locator:
        """
        Resolve a locator for the given target element name.
        
        Args:
            page: Playwright Page object
            target: Element name (e.g., "login_button")
            context_data: Optional context for disambiguation
        
        Returns:
            Playwright Locator object
        
        Raises:
            LocatorResolutionError: If no strategy can resolve the target
        """
        context_data = context_data or {}
        
        # Strategy 1: Repository (primary source of truth)
        try:
            locator = await self._repo_strategy(page, target)
            return locator
        except Exception as e:
            pass
        
        # Strategy 2: Snapshot (dynamic discovery)
        try:
            locator = await self._snapshot_strategy(page, target)
            # Optional learning: save successful snapshot to repo
            if context_data.get('learn', False):
                await self._learn_locator(target, locator)
            return locator
        except Exception as e:
            pass
        
        # Strategy 3: Fallback (last resort)
        try:
            locator = await self._fallback_strategy(page, target)
            return locator
        except Exception as e:
            pass
        
        raise LocatorResolutionError(
            f"Could not resolve locator for target '{target}' using any strategy"
        )
    
    async def _repo_strategy(self, page: Page, target: str) -> Locator:
        """
        Strategy 1: Load locator from object_repo/*.json
        Primary source of truth.
        """
        # Determine page name from current URL or context
        current_url = page.url
        repo_file = await self._find_repo_file(current_url)
        
        if not repo_file:
            raise LocatorResolutionError(f"No repo file found for URL: {current_url}")
        
        # Load repo
        with open(repo_file, 'r', encoding='utf-8') as f:
            repo_data = json.load(f)
        
        elements = repo_data.get('elements', {})
        if target not in elements:
            raise LocatorResolutionError(f"Target '{target}' not found in {repo_file.name}")
        
        element_def = elements[target]
        return self._build_locator(page, element_def)
    
    async def _snapshot_strategy(self, page: Page, target: str) -> Locator:
        """
        Strategy 2: Use accessibility snapshot for dynamic discovery.
        Fallback when repo is incomplete.
        """
        snapshot = page.accessibility.snapshot()
        
        # Flatten snapshot tree and find matching nodes
        candidates = []
        self._flatten_snapshot(snapshot, target, candidates)
        
        if not candidates:
            raise LocatorResolutionError(
                f"No candidates found in snapshot for target '{target}'"
            )
        
        # Use first candidate (highest fidelity)
        best_match = candidates[0]
        return self._build_from_snapshot_node(page, best_match)
    
    async def _fallback_strategy(self, page: Page, target: str) -> Locator:
        """
        Strategy 3: Generic fallback patterns.
        Try common attribute patterns.
        """
        patterns = [
            lambda: page.get_by_test_id(target),  # data-test-id=target
            lambda: page.get_by_label(target),     # label text
            lambda: page.get_by_placeholder(target),  # placeholder text
            lambda: page.get_by_text(target),      # visible text
            lambda: page.locator(f"[data-test='{target}']"),  # data-test attribute
            lambda: page.locator(f"#{target}"),    # id attribute
        ]
        
        for pattern in patterns:
            try:
                locator = pattern()
                # Verify locator exists
                count = await locator.count()
                if count > 0:
                    return locator
            except Exception:
                continue
        
        raise LocatorResolutionError(f"All fallback patterns failed for '{target}'")
    
    async def _find_repo_file(self, url: str) -> Optional[Path]:
        """Find repo file matching the current URL pattern."""
        repo_dir = self.base_dir / 'object_repo'
        if not repo_dir.exists():
            return None
        
        for json_file in repo_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    url_pattern = data.get('url_pattern', '')
                    if url_pattern and url_pattern in url:
                        return json_file
                except Exception:
                    continue
        
        return None
    
    def _flatten_snapshot(self, node: Dict[str, Any], target: str, candidates: List[Dict], depth: int = 0):
        """Recursively flatten snapshot tree, collecting matching nodes."""
        if not node or not isinstance(node, dict):
            return
        
        name = node.get('name', '').lower()
        role = node.get('role', '')
        
        # Match by name or role+name combination
        if target.lower() in name or target.lower() == name:
            candidates.append((depth, node))  # Store with depth for priority
        
        for child in node.get('children', []) or []:
            self._flatten_snapshot(child, target, candidates, depth + 1)
        
        # Sort by depth (shallowest first = higher priority)
        candidates.sort(key=lambda x: x[0])
    
    def _build_from_snapshot_node(self, page: Page, snapshot_tuple) -> Locator:
        """Build a Playwright locator from a snapshot node tuple."""
        depth, node = snapshot_tuple
        
        role = node.get('role')
        name = node.get('name')
        
        # Prefer ARIA role + name
        if role and name:
            return page.get_by_role(role, name=name)
        
        if name:
            return page.get_by_text(name)
        
        raise LocatorResolutionError(f"Cannot build locator from snapshot node: {node}")
    
    def _build_locator(self, page: Page, element_def: Dict[str, Any]) -> Locator:
        """
        Build locator from element definition dict.
        Supports: aria_role, label, placeholder, text, selector.
        """
        
        # 1. ARIA Role & Name
        if "aria_role" in element_def:
            role = element_def["aria_role"]
            name = element_def.get("aria_name")
            return page.get_by_role(role, name=name, exact=element_def.get("exact", False))
        
        # 2. Label
        if "label" in element_def:
            return page.get_by_label(element_def["label"], exact=element_def.get("exact", False))
        
        # 3. Placeholder
        if "placeholder" in element_def:
            return page.get_by_placeholder(element_def["placeholder"], exact=element_def.get("exact", False))
        
        # 4. Text
        if "text" in element_def:
            return page.get_by_text(element_def["text"], exact=element_def.get("exact", False))
        
        # 5. Selector (fallback to CSS/XPath)
        if "selector" in element_def:
            return page.locator(element_def["selector"])
        
        raise ValueError(f"Cannot build locator from definition: {element_def}")
    
    async def _learn_locator(self, target: str, locator: Locator):
        """Optional: Cache successful snapshot-based locators for future use."""
        # This could save back to repo or a learning file
        self._learned_locators[target] = locator
        pass
