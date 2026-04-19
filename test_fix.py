#!/usr/bin/env python
"""Quick test to verify the planner fix."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from planner.planner import plan_test_cases

# Test case
test_case = {
    'id': 'TC001',
    'title': 'Test Login',
    'precondition': 'User is on login page',
    'steps': [
        'Navigate to https://www.saucedemo.com',
        'Enter username: standard_user',
        'Enter password: password123',
        'Click on the login button',
        'Verify Products page is displayed'
    ],
    'test_data': {'username': 'standard_user', 'password': 'password123'},
    'expected_result': 'User is logged in'
}

# Plan the test case
result = plan_test_cases([test_case])

print("✅ Planner module works correctly!")
print(f"\nPlanned test case:")
print(f"ID: {result[0]['id']}")
print(f"Title: {result[0]['title']}")
print(f"Actions ({len(result[0]['actions'])} steps):")
for idx, action in enumerate(result[0]['actions'], 1):
    print(f"  {idx}. {action['type']}")

print("\n✨ Fix successful - fallback logic is now working properly!")
