import asyncio
import json
from playwright.async_api import async_playwright

async def debug_accessibility(url):
    """
    Captures the accessibility snapshot and prints elements that can be used for locators.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        
        # Wait for some time to ensure page is loaded
        await page.wait_for_timeout(2000)
        
        snapshot = await page.accessibility.snapshot()
        print(f"--- Accessibility Snapshot for {url} ---")
        
        def print_node(node, indent=0):
            role = node.get("role")
            name = node.get("name")
            if role and name:
                print(f"{'  ' * indent}[{role}] \"{name}\"")
                # Suggest locator
                if role in ["button", "link", "checkbox", "menuitem"]:
                    print(f"{'  ' * (indent+1)}Suggested: {{\"aria_role\": \"{role}\", \"aria_name\": \"{name}\"}}")
            
            for child in node.get("children", []):
                print_node(child, indent + 1)

        print_node(snapshot)
        await browser.close()

if __name__ == "__main__":
    # Example usage: Replace with your target URL
    target_url = "https://www.saucedemo.com/"
    asyncio.run(debug_accessibility(target_url))
