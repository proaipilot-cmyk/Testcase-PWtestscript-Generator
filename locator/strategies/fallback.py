"""Fallback Strategy - Generic patterns for locator discovery."""
from typing import Optional
from playwright.async_api import Page, Locator


class FallbackStrategy:
    """
    Strategy 3: Generic fallback locator patterns.
    Last resort when repo and snapshot strategies fail.
    """
    
    async def resolve(self, page: Page, target: str) -> Locator:
        """
        Try common attribute and selector patterns.
        
        Args:
            page: Playwright Page
            target: Element name or identifier
        
        Returns:
            Playwright Locator
        
        Raises:
            Exception if all patterns fail
        """
        patterns = [
            # Pattern 1: data-test-id attribute
            lambda: page.get_by_test_id(target),
            # Pattern 2: Label text
            lambda: page.get_by_label(target, exact=False),
            # Pattern 3: Placeholder text
            lambda: page.get_by_placeholder(target, exact=False),
            # Pattern 4: Visible text content
            lambda: page.get_by_text(target, exact=False),
            # Pattern 5: data-test attribute (CSS selector)
            lambda: page.locator(f"[data-test='{target}']"),
            # Pattern 6: HTML id attribute
            lambda: page.locator(f"#{target}"),
            # Pattern 7: data-testid attribute (CSS selector)
            lambda: page.locator(f"[data-testid='{target}']"),
            # Pattern 8: name attribute (for forms)
            lambda: page.locator(f"[name='{target}']"),
        ]
        
        for i, pattern in enumerate(patterns):
            try:
                locator = pattern()
                # Verify locator is visible/exists on page
                count = await locator.count()
                if count > 0:
                    return locator
            except Exception:
                continue
        
        raise ValueError(f"All fallback patterns failed for target: {target}")
