"""Quick validation that resolve_locator_sync is properly exported."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Test 1: Import the sync function
try:
    from locator import resolve_locator_sync
    print("✅ resolve_locator_sync imported successfully")
except ImportError as e:
    print(f"❌ Failed to import resolve_locator_sync: {e}")
    sys.exit(1)

# Test 2: Check it's callable
if callable(resolve_locator_sync):
    print("✅ resolve_locator_sync is callable")
else:
    print("❌ resolve_locator_sync is not callable")
    sys.exit(1)

# Test 3: Check steps module imports it
try:
    from steps.steps import fill_credentials, click_login_button, assert_error_message
    print("✅ Step functions imported successfully")
except ImportError as e:
    print(f"❌ Failed to import step functions: {e}")
    sys.exit(1)

# Test 4: Verify step functions don't have async in their signature
import inspect
if not inspect.iscoroutinefunction(fill_credentials):
    print("✅ fill_credentials is synchronous")
else:
    print("❌ fill_credentials is async (should be sync)")
    sys.exit(1)

if not inspect.iscoroutinefunction(click_login_button):
    print("✅ click_login_button is synchronous")
else:
    print("❌ click_login_button is async (should be sync)")
    sys.exit(1)

print("\n✨ All validations passed!")
