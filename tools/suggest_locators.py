"""Suggest Playwright locators from an accessibility snapshot JSON.

Usage:
    python tools/suggest_locators.py <snapshot.json> [out.json]

The script walks the accessibility snapshot and emits a JSON array
of suggested locator entries.
"""
import json
import sys
from pathlib import Path


def walk(node, out):
    if not node or not isinstance(node, dict):
        return

    role = node.get('role')
    name = node.get('name')
    attributes = node.get('attributes') or {}

    # Prefer data-test / data-testid attributes
    data_test = None
    for key in ('data-test', 'data-test-id', 'data-testid', 'data_test'):
        if attributes and key in attributes:
            data_test = attributes[key]
            break

    # Build selector candidates
    candidates = []
    if role and name:
        sel = f'role={role}[name="{name}"]'
        candidates.append((sel, 1, 'ARIA role+name preferred'))

    if data_test:
        sel = f'css=[data-test="{data_test}"]'
        candidates.append((sel, 1, 'data-test attribute preferred'))
    elif attributes and 'id' in attributes:
        ident = attributes['id']
        # crude check for stable id (not purely numeric or long auto-generated)
        if not ident.isdigit() and len(ident) < 80:
            sel = f'css=#{ident}'
            candidates.append((sel, 2, 'id attribute - verify stability'))

    # Text fallback if nothing else
    if not candidates and name:
        sel = f'text="{name}"'
        candidates.append((sel, 3, 'text fallback (may be localized)'))

    if candidates:
        # Short key name: normalize role+name or id
        key = None
        if name:
            key = name.lower().strip().replace(' ', '_')[:50]
        elif attributes and 'id' in attributes:
            key = attributes['id'][:50]
        else:
            key = f"elem_{len(out)+1}"

        entry = {
            'name': key,
            'role': role,
            'accessible_name': name,
            'candidates': [],
        }

        seen = set()
        for sel, prio, note in candidates:
            if sel in seen:
                continue
            seen.add(sel)
            entry['candidates'].append({
                'selector': sel,
                'priority': prio,
                'notes': note
            })

        out.append(entry)

    for child in node.get('children', []) or []:
        walk(child, out)


def main():
    if len(sys.argv) < 2:
        print('Usage: python tools/suggest_locators.py <snapshot.json> [out.json]')
        sys.exit(2)

    path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not path.exists():
        print('Snapshot file not found:', path)
        sys.exit(2)

    data = json.load(open(path, 'r', encoding='utf-8'))
    suggestions = []
    walk(data, suggestions)

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)
        print('Wrote suggestions to', out_path)
    else:
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
