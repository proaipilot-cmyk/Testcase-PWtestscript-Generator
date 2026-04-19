"""Capture Playwright accessibility snapshot and save to JSON.

Usage:
    python tools/capture_a11y_snapshot.py <url> [out.json]

If `out.json` is not provided the file will be saved to `data/snapshots/<timestamp>_snapshot.json`.
"""
from playwright.sync_api import sync_playwright
import json
import sys
from datetime import datetime
from pathlib import Path


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.example.com'
    out = sys.argv[2] if len(sys.argv) > 2 else None

    out_dir = Path('data/snapshots')
    out_dir.mkdir(parents=True, exist_ok=True)

    if not out:
        out = out_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_snapshot.json"
    else:
        out = Path(out)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            # Navigate and wait for network idle so dynamic UI stabilizes
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(800)

            snap = None

            # Preferred API: page.accessibility.snapshot() (most Playwright versions)
            try:
                if hasattr(page, 'accessibility') and getattr(page, 'accessibility') is not None:
                    snap = page.accessibility.snapshot()
            except Exception:
                snap = None

            # Alternative API: some bindings expose a direct function
            if snap is None:
                try:
                    # older/newer variations
                    snap = page.accessibility_snapshot()  # type: ignore
                except Exception:
                    snap = None

            # Last-resort fallback: extract basic ARIA-like info from DOM
            if snap is None:
                snap = page.evaluate("""() => {
                    const out = { name: document.title || '', role: 'document', children: [] };
                    function nodeInfo(el) {
                        return {
                            role: el.getAttribute && el.getAttribute('role') || null,
                            name: el.getAttribute && (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) || (el.innerText || '').trim().slice(0,200),
                            id: el.id || null,
                            class: el.className || null,
                        };
                    }
                    function walk(src, dst) {
                        for (const child of src.children || []) {
                            const info = nodeInfo(child);
                            const node = { ...info, children: [] };
                            dst.children.push(node);
                            walk(child, node);
                        }
                    }
                    walk(document.body, out);
                    return out;
                }""")

        finally:
            browser.close()

    with open(out, 'w', encoding='utf-8') as f:
        json.dump(snap, f, indent=2, ensure_ascii=False)

    print(f"Saved snapshot to: {out}")


if __name__ == '__main__':
    main()
