"""Snapshot Strategy - Discover locators using page.accessibility.snapshot()."""
from typing import Dict, Any, List, Tuple, Optional
from playwright.async_api import Page, Locator
import json


class SnapshotStrategy:
    """
    Strategy 2: Resolve locators using accessibility snapshots.
    Dynamic discovery when repo is incomplete.
    """
    
    async def resolve(self, page: Page, target: str) -> Locator:
        """
        Resolve locator by scanning accessibility snapshot.
        
        Args:
            page: Playwright Page
            target: Element name or pattern (e.g., "login_button")
        
        Returns:
            Playwright Locator
        
        Raises:
            Exception if no matching element found
        """
        snapshot = page.accessibility.snapshot()
        
        # Flatten snapshot and find candidates
        candidates = []
        self._flatten_snapshot(snapshot, target, candidates)
        
        if not candidates:
            raise ValueError(f"No candidates in snapshot for target: {target}")
        
        # Use first candidate (best match)
        return self._build_from_snapshot_node(page, candidates[0])
    
    def _flatten_snapshot(self, node: Dict[str, Any], target: str, candidates: List[Tuple[int, Dict]], depth: int = 0):
        """
        Recursively walk snapshot tree, collecting nodes matching target.
        Stores (depth, node) tuples for priority sorting.
        """
        if not node or not isinstance(node, dict):
            return
        
        name = node.get('name', '').lower()
        role = node.get('role', '')
        
        # Match by exact name or substring
        target_lower = target.lower()
        if target_lower == name or target_lower in name:
            candidates.append((depth, node))
        
        # Recurse into children
        for child in node.get('children', []) or []:
            self._flatten_snapshot(child, target, candidates, depth + 1)
        
        # Sort by depth (shallower = higher priority)
        candidates.sort(key=lambda x: x[0])
    
    def _build_from_snapshot_node(self, page: Page, candidate: Tuple[int, Dict]) -> Locator:
        """Build Playwright locator from snapshot node."""
        depth, node = candidate
        
        role = node.get('role')
        name = node.get('name')
        
        # Prefer ARIA role + accessible name
        if role and name:
            return page.get_by_role(role, name=name)
        
        # Fallback to text
        if name:
            return page.get_by_text(name, exact=False)
        
        raise ValueError(f"Cannot build locator from snapshot node: {node}")
