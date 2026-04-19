"""Repository Strategy - Load locators from object_repo/*.json files."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import Page, Locator


class RepoStrategy:
    """
    Strategy 1: Resolve locators from object_repo JSON files.
    Primary source of truth.
    """
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self._cache = {}
    
    async def resolve(self, page: Page, target: str) -> Locator:
        """
        Resolve locator from repo.
        
        Args:
            page: Playwright Page
            target: Element name (e.g., "login_button")
        
        Returns:
            Playwright Locator
        
        Raises:
            Exception if target not found
        """
        current_url = page.url
        repo_file = await self._find_repo_file(current_url)
        
        if not repo_file:
            raise ValueError(f"No repo file found for URL: {current_url}")
        
        # Load repo from cache or disk
        if repo_file not in self._cache:
            with open(repo_file, 'r', encoding='utf-8') as f:
                self._cache[repo_file] = json.load(f)
        
        repo_data = self._cache[repo_file]
        elements = repo_data.get('elements', {})
        
        if target not in elements:
            raise KeyError(f"Target '{target}' not found in {repo_file.name}")
        
        element_def = elements[target]
        return self._build_locator(page, element_def)
    
    async def _find_repo_file(self, url: str) -> Optional[Path]:
        """Find repo file matching URL pattern."""
        repo_dir = self.base_dir / 'object_repo'
        if not repo_dir.exists():
            return None
        
        for json_file in sorted(repo_dir.glob('*.json')):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    url_pattern = data.get('url_pattern', '')
                    if url_pattern and url_pattern in url:
                        return json_file
            except Exception:
                continue
        
        return None
    
    def _build_locator(self, page: Page, element_def: Dict[str, Any]) -> Locator:
        """Build Playwright locator from element definition."""
        
        # Priority order: ARIA > label > placeholder > text > selector
        if "aria_role" in element_def:
            role = element_def["aria_role"]
            name = element_def.get("aria_name")
            return page.get_by_role(role, name=name, exact=element_def.get("exact", False))
        
        if "label" in element_def:
            return page.get_by_label(element_def["label"], exact=element_def.get("exact", False))
        
        if "placeholder" in element_def:
            return page.get_by_placeholder(element_def["placeholder"], exact=element_def.get("exact", False))
        
        if "text" in element_def:
            return page.get_by_text(element_def["text"], exact=element_def.get("exact", False))
        
        if "selector" in element_def:
            return page.locator(element_def["selector"])
        
        raise ValueError(f"No supported locator field in definition: {element_def}")
