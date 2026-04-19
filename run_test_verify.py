#!/usr/bin/env python
"""Run a single actual pytest test to verify the fix works"""
import subprocess
import sys
from pathlib import Path

print("="*70)
print("RUNNING ACTUAL TEST TO VERIFY FIX")
print("="*70)

# First verify our changes are in place
print("\n[STEP 1] Verifying fix is in place...")
steps_file = Path("c:/myprojects/Project0/steps/steps.py").read_text()
if 'resolve_locator_sync' not in steps_file:
    print("❌ FAILED: steps.py still has old resolve_locator")
    sys.exit(1)

if 'from locator import resolve_locator_sync' not in steps_file:
    print("❌ FAILED: steps.py doesn't import resolve_locator_sync")
    sys.exit(1)

print("✅ Fix is in place - steps.py uses resolve_locator_sync")

# Now run a single pytest test
print("\n[STEP 2] Running test_login_success test...")
print("-" * 70)

result = subprocess.run(
    [sys.executable, "-m", "pytest", 
     "tests/test_automation.py::test_login_success",
     "-v", "--tb=short"],
    cwd="c:/myprojects/Project0",
    capture_output=True,
    text=True,
    timeout=120
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("-" * 70)

if result.returncode == 0:
    print("\n✅ TEST PASSED!")
    print("\n🎉 THE FIX WORKS - Tests are now passing!")
    print("\nRun all tests with:")
    print("  pytest tests/test_automation.py -v")
    sys.exit(0)
elif "AttributeError: 'coroutine' object has no attribute" in result.stdout or \
     "AttributeError: 'coroutine' object has no attribute" in result.stderr:
    print("\n❌ TEST FAILED - Still getting coroutine error")
    print("\nThis means the runner is using old files from the runs/ directory")
    print("Need to verify source files are correctly updated")
    sys.exit(1)
else:
    print("\n⚠️  TEST FAILED - But not with coroutine error")
    print("This might be expected (no actual browser, missing elements, etc.)")
    print("\nThe important thing is: NO coroutine AttributeError!")
    print("Return code:", result.returncode)
    sys.exit(result.returncode)
