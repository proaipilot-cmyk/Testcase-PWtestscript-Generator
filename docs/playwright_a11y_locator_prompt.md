# Playwright Accessibility Snapshot → Locator Update Prompt

This document describes the workflow and provides a ready-to-use LLM prompt to convert Playwright accessibility snapshots into suggested stable locators for the project's `object_repo/*.json`.

Steps
1. Capture an accessibility snapshot using Playwright (see `tools/capture_a11y_snapshot.py`).
2. Run the suggestion tool to extract candidate locators: `python tools/suggest_locators.py <snapshot.json> > suggestions.json`.
3. Review `suggestions.json` and merge approved locators into the appropriate file under `object_repo/`.
4. Run `python validator/demo.py` and a short smoke test to confirm changes.

LLM Prompt (use this with your favorite LLM to refine selectors)
---
You will be given a JSON-formatted Playwright accessibility snapshot representing one page state. Your goal: produce a list of stable, prioritized locator suggestions suitable for Playwright tests. For each candidate element output these fields: `name` (short key), `role` (ARIA role if any), `accessible_name` (the node.name), `selector` (Playwright-friendly selector string), `priority` (1-high,2-medium,3-low), and `notes` (why chosen and any caveats).

Rules:
- Prefer `role`+`name` ARIA selectors: `role=<role>[name="<accessible_name>"]`.
- If node has `attributes` including `data-test` or `data-testid`, prefer `css=[data-test="..."]` or `css=[data-testid="..."]`.
- Use `id` only if it appears stable (not auto-generated numeric suffixes); prefer `#id` where safe.
- For input fields consider `get_by_label()` when a label exists.
- Avoid selectors that match visible text fragments which may be localized unless no alternative exists.
- If multiple nodes match the same suggestion, add a `fallback_selectors` array with alternates.

Output format (JSON array):
[
  {
    "name": "login_button",
    "role": "button",
    "accessible_name": "Log in",
    "selector": "role=button[name=\"Log in\"]",
    "priority": 1,
    "notes": "ARIA role+name is stable"
  },
  ...
]

Example usage
```
python tools/suggest_locators.py data/snapshots/my_snapshot.json > data/snapshots/my_snapshot_suggestions.json
```

Notes
- Capture multiple snapshots for different states (logged-in, checkout, error state) and run suggestions per snapshot.
- Keep backups of `object_repo/*.json` before applying bulk changes.
