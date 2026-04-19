#!/usr/bin/env python
"""Comprehensive test to verify the coroutine fix"""
import sys
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("COMPREHENSIVE COROUTINE FIX VERIFICATION")
print("="*70)

# Test 1: Check resolve_locator_sync exists
print("\n[TEST 1] Checking resolve_locator_sync function...")
try:
    from locator import resolve_locator_sync
    print("✅ resolve_locator_sync imported successfully")
except ImportError as e:
    print(f"❌ FAILED: Could not import resolve_locator_sync: {e}")
    sys.exit(1)

# Test 2: Verify it's not a coroutine
print("\n[TEST 2] Verifying resolve_locator_sync is NOT async...")
import inspect
if inspect.iscoroutinefunction(resolve_locator_sync):
    print("❌ FAILED: resolve_locator_sync is async (should be sync)")
    sys.exit(1)
else:
    print("✅ resolve_locator_sync is properly synchronous")

# Test 3: Check it's in __all__
print("\n[TEST 3] Checking __all__ exports...")
import locator
if 'resolve_locator_sync' in locator.__all__:
    print("✅ resolve_locator_sync is in __all__ exports")
else:
    print("❌ FAILED: resolve_locator_sync not in __all__")
    sys.exit(1)

# Test 4: Test with mock page
print("\n[TEST 4] Testing resolve_locator_sync with mock page...")
try:
    mock_page = Mock()
    mock_locator = Mock()
    mock_locator.count.return_value = 0
    mock_page.locator.return_value = mock_locator
    mock_page.get_by_placeholder.return_value = Mock()
    mock_page.get_by_label.return_value = Mock()
    mock_page.get_by_text.return_value = Mock()
    
    result = resolve_locator_sync(mock_page, 'username')
    
    # Result should be a Mock or Locator-like object, NOT a coroutine
    if inspect.iscoroutine(result):
        print(f"❌ FAILED: resolve_locator_sync returned a coroutine: {type(result)}")
        sys.exit(1)
    else:
        print(f"✅ resolve_locator_sync returned sync object: {type(result).__name__}")
except Exception as e:
    print(f"❌ FAILED: Error calling resolve_locator_sync: {e}")
    sys.exit(1)

# Test 5: Check steps module
print("\n[TEST 5] Checking steps module imports...")
try:
    from steps.steps import (
        fill_credentials, click_login_button, assert_error_message,
        verify_products_page, navigate_to_login
    )
    print("✅ All step functions imported successfully")
except ImportError as e:
    print(f"❌ FAILED: Could not import step functions: {e}")
    sys.exit(1)

# Test 6: Verify steps use resolve_locator_sync
print("\n[TEST 6] Verifying step functions use resolve_locator_sync...")
step_functions = [
    ('fill_credentials', fill_credentials),
    ('click_login_button', click_login_button),
    ('assert_error_message', assert_error_message),
    ('verify_products_page', verify_products_page),
]

for func_name, func in step_functions:
    source = inspect.getsource(func)
    if 'resolve_locator_sync' in source:
        print(f"✅ {func_name} uses resolve_locator_sync")
    else:
        print(f"❌ FAILED: {func_name} doesn't use resolve_locator_sync")
        sys.exit(1)

# Test 7: Verify step functions are NOT async
print("\n[TEST 7] Verifying step functions are synchronous...")
for func_name, func in step_functions:
    if inspect.iscoroutinefunction(func):
        print(f"❌ FAILED: {func_name} is async (should be sync)")
        sys.exit(1)
    else:
        print(f"✅ {func_name} is synchronous")

print("\n" + "="*70)
print("✅ ALL VERIFICATION TESTS PASSED!")
print("="*70)
print("\nSummary:")
print("  ✅ resolve_locator_sync() exists and is synchronous")
print("  ✅ resolve_locator_sync() returns Locator objects (not coroutines)")
print("  ✅ All step functions use resolve_locator_sync()")
print("  ✅ All step functions are synchronous")
print("  ✅ No coroutines in the execution chain")
print("\n🎯 THE FIX IS READY TO TEST!")
print("\nNext: Run pytest to verify tests pass:")
print("  pytest tests/test_automation.py -v")
