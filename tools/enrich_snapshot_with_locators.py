"""Enrich accessibility snapshots with Playwright locator information.

Usage:
    python tools/enrich_snapshot_with_locators.py <url> [out.json]
    python tools/enrich_snapshot_with_locators.py --snapshot <snapshot.json> [out.json]

If output is not provided, saves to `data/snapshots/<timestamp>_enriched_snapshot.json`.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


def extract_locator_data(page):
    """Extract locator information from all elements on the page.
    
    Returns a dict mapping element IDs to their locator data.
    """
    locators = page.evaluate("""() => {
        const locatorMap = {};
        let elementId = 0;
        
        function walk(el, depth = 0) {
            if (depth > 20) return;  // Limit depth
            
            const id = 'elem_' + elementId++;
            
            // Extract locator data
            const testId = el.getAttribute?.('data-testid');
            const role = el.getAttribute?.('role') || el.tagName?.toLowerCase();
            const ariaLabel = el.getAttribute?.('aria-label');
            const ariaLabelledBy = el.getAttribute?.('aria-labelledby');
            const placeholder = el.getAttribute?.('placeholder');
            const title = el.getAttribute?.('title');
            const name = el.textContent?.trim().slice(0, 100);
            const className = el.className || '';
            const id_attr = el.id;
            
            // Build selector candidates
            const selectors = [];
            if (testId) selectors.push(`[data-testid="${testId}"]`);
            if (id_attr) selectors.push(`#${id_attr}`);
            if (role && role !== 'script' && role !== 'style') {
                selectors.push(el.tagName.toLowerCase());
            }
            
            const locator = {
                element_id: id,
                tag_name: el.tagName?.toLowerCase(),
                role: role !== el.tagName?.toLowerCase() ? role : null,
                aria_label: ariaLabel,
                aria_labelledby: ariaLabelledBy,
                data_testid: testId,
                placeholder: placeholder,
                title: title,
                text_content: name,
                class_name: className,
                id: id_attr,
                selectors: selectors,
                locator_string: testId 
                    ? `getByTestId("${testId}")`
                    : ariaLabel
                    ? `getByRole("${role}", { name: "${ariaLabel}" })`
                    : null
            };
            
            locatorMap[id] = locator;
            
            // Recurse to children
            for (const child of el.children || []) {
                walk(child, depth + 1);
            }
        }
        
        walk(document.documentElement);
        return locatorMap;
    }""")
    
    return locators


def capture_snapshot_with_locators(url, output_path=None):
    """Navigate to URL, capture accessibility snapshot, and enrich with locators."""
    
    out_dir = Path('data/snapshots')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not output_path:
        output_path = out_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_enriched_snapshot.json"
    else:
        output_path = Path(output_path)
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            # Navigate and wait for page to stabilize
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(800)
            
            # Capture accessibility snapshot
            snap = None
            try:
                if hasattr(page, 'accessibility') and getattr(page, 'accessibility') is not None:
                    snap = page.accessibility.snapshot()
            except Exception:
                snap = None
            
            if snap is None:
                try:
                    snap = page.accessibility_snapshot()  # type: ignore
                except Exception:
                    snap = None
            
            if snap is None:
                snap = {"name": page.title(), "role": "document", "children": []}
            
            # Extract locator data
            locators = extract_locator_data(page)
            
            # Enrich snapshot structure with locator references
            enriched = {
                "url": url,
                "title": page.title(),
                "timestamp": datetime.now().isoformat(),
                "accessibility_snapshot": snap,
                "locators": locators,
                "locator_summary": {
                    "total_elements": len(locators),
                    "elements_with_testid": len([l for l in locators.values() if l.get('data_testid')]),
                    "elements_with_arialabel": len([l for l in locators.values() if l.get('aria_label')]),
                    "elements_with_id": len([l for l in locators.values() if l.get('id')])
                }
            }
            
        finally:
            browser.close()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f"Saved enriched snapshot to: {output_path}")
    return str(output_path)


def enrich_existing_snapshot(snapshot_path, output_path=None):
    """Load an existing accessibility snapshot and add locator suggestions."""
    
    snapshot_path = Path(snapshot_path)
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {snapshot_path}")
    
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    
    out_dir = Path('data/snapshots')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not output_path:
        output_path = out_dir / f"{snapshot_path.stem}_with_locators.json"
    else:
        output_path = Path(output_path)
    
    # Add locator context
    enriched = {
        "source_snapshot": snapshot_path.name,
        "enriched_at": datetime.now().isoformat(),
        "accessibility_snapshot": snap,
        "locators": {},
        "note": "Locators were not extracted (snapshot was pre-generated). Re-run with a live URL to populate locators."
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f"Saved enriched snapshot to: {output_path}")
    return str(output_path)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if sys.argv[1] == '--snapshot':
        # Enrich an existing snapshot file
        if len(sys.argv) < 3:
            print("Usage: python enrich_snapshot_with_locators.py --snapshot <snapshot.json> [out.json]")
            sys.exit(1)
        snapshot_file = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None
        enrich_existing_snapshot(snapshot_file, output)
    else:
        # Navigate to URL and capture with locators
        url = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        capture_snapshot_with_locators(url, output)


if __name__ == '__main__':
    main()
