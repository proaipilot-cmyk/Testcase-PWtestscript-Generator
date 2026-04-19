#!/usr/bin/env python
"""Quick validation that resolve_locator_sync works"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from locator import resolve_locator_sync
    print("✅ resolve_locator_sync imported")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

# Test step imports
try:
    from steps.steps import fill_credentials, click_login_button
    print("✅ Step functions imported")
except Exception as e:
    print(f"❌ Failed to import steps: {e}")
    sys.exit(1)

# Check source code has the right function
with open('steps/steps.py') as f:
    content = f.read()
    if 'resolve_locator_sync' in content:
        count = content.count('resolve_locator_sync')
        print(f"✅ steps.py uses resolve_locator_sync ({count} calls)")
    else:
        print("❌ steps.py doesn't use resolve_locator_sync")
        sys.exit(1)
    
    if 'from locator import resolve_locator_sync' in content:
        print("✅ steps.py imports resolve_locator_sync")
    else:
        print("❌ steps.py doesn't import resolve_locator_sync")
        sys.exit(1)

print("\n✨ All validations passed - fix is in place!")
