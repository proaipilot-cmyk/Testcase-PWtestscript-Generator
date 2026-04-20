
from playwright.sync_api import sync_playwright
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(r'c:\myprojects\Project0')))

from locator import resolve_locator_sync

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.saucedemo.com')
        
        print(f"URL: {page.url}")
        
        # Try to resolve username
        loc = resolve_locator_sync(page, 'username')
        print(f"Locator for username: {loc}")
        if loc:
            print(f"Count: {loc.count()}")
            
        browser.close()

if __name__ == "__main__":
    test()
