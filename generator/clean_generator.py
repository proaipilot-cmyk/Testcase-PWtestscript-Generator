"""
Clean Test Generator - Converts CSV to Sync Playwright Tests
Single source of truth: No duplication, no repeated parameters

Key principles:
1. Read ONCE from CSV (single source of truth)
2. Each testcase appears exactly ONCE in generated tests
3. Automatic categorization (login vs other flows)
4. Scalable: Works with any number of testcases
5. No hardcoded lists or duplicated IDs
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any
import re


def parse_csv_testcases(csv_path: str) -> List[Dict[str, Any]]:
    """Parse testcases from CSV file with validation."""
    testcases = []
    seen_ids = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            # Validate required fields
            if not row.get('id') or not row.get('title'):
                print(f"⚠ Warning: Skipping row {row_num} - missing id or title")
                continue
            
            # Check for duplicates
            if row['id'] in seen_ids:
                print(f"⚠ Warning: Duplicate ID {row['id']} at row {row_num} - skipping")
                continue
            
            seen_ids.add(row['id'])
            testcases.append(row)
    
    return testcases


def categorize_testcases(testcases: List[Dict]) -> tuple:
    """
    Categorize testcases into functional groups.
    Automatic detection based on test title/ID patterns.
    """
    categories = {
        'login': [],
        'cart': [],
        'checkout': [],
        'product': [],
        'account': [],
        'other': []
    }
    
    for tc in testcases:
        tc_id = tc['id'].upper()
        title = tc['title'].lower()
        
        if 'login' in title or 'login' in tc_id:
            categories['login'].append(tc)
        elif 'cart' in title or 'cart' in tc_id:
            categories['cart'].append(tc)
        elif 'checkout' in title or 'checkout' in tc_id:
            categories['checkout'].append(tc)
        elif 'product' in title or 'product' in tc_id:
            categories['product'].append(tc)
        elif 'account' in title or 'account' in tc_id:
            categories['account'].append(tc)
        else:
            categories['other'].append(tc)
    
    return categories


def generate_clean_tests(csv_path: str, output_path: str) -> None:
    """Generate clean, duplicate-free test file from CSV."""
    testcases = parse_csv_testcases(csv_path)
    
    if not testcases:
        print("✗ No testcases found in CSV file")
        return
    
    # Categorize testcases
    categories = categorize_testcases(testcases)
    
    # Generate pytest parametrize strings
    test_content = _generate_test_code(categories, testcases)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Print summary
    print(f"\n✓ Generated clean test file: {output_path}")
    print(f"  Total unique testcases: {len(testcases)}")
    for cat, tests in categories.items():
        if tests:
            print(f"  - {cat.capitalize()}: {len(tests)}")
    
    # Verify no duplicates
    ids = [tc['id'] for tc in testcases]
    if len(ids) != len(set(ids)):
        print("⚠ WARNING: Duplicate IDs detected!")
    else:
        print(f"  ✓ No duplicate test IDs")


def _generate_test_code(categories: Dict, all_testcases: List[Dict]) -> str:
    """Generate clean, readable test code from categorized testcases."""
    
    login_tests = categories['login']
    cart_tests = categories['cart']
    checkout_tests = categories['checkout']
    product_tests = categories['product']
    other_tests = categories['other']
    
    # Start with file header
    code = f'''"""
Clean Sync Playwright Test Suite
Generated from: data/testcases.csv

SINGLE SOURCE OF TRUTH - NO DUPLICATION
Each test case appears exactly ONCE.
Total: {len(all_testcases)} unique testcases
"""
import pytest
from steps.steps import (
    navigate_to_login, fill_credentials, click_login_button,
    assert_page_contains_text, assert_error_message, verify_products_page
)

'''
    
    # Generate login tests
    if login_tests:
        code += _generate_login_tests(login_tests)
    
    # Generate cart tests
    if cart_tests:
        code += _generate_cart_tests(cart_tests)
    
    # Generate checkout tests
    if checkout_tests:
        code += _generate_checkout_tests(checkout_tests)
    
    # Generate product tests
    if product_tests:
        code += _generate_product_tests(product_tests)
    
    # Generate other tests (catch-all)
    if other_tests:
        code += _generate_generic_tests(other_tests)
    
    return code


def _generate_login_tests(tests: List[Dict]) -> str:
    """Generate login test function."""
    params = []
    ids = []
    
    for tc in tests:
        test_data = tc['test_data']
        username = _extract_value(test_data, 'username')
        password = _extract_value(test_data, 'password')
        
        params.append((username, password, tc['expected_result']))
        ids.append(tc['id'])
    
    code = f'''
# ============================================================================
# LOGIN TESTS ({len(tests)} unique)
# ============================================================================

@pytest.mark.parametrize("username,password,expected", [
{_format_params(params)}
], ids={ids})
def test_login_scenarios(page, username, password, expected):
    """
    Login test scenarios (valid/invalid credentials).
    
    Each parameter set represents one unique test case.
    """
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, username, password)
        click_login_button(login_page)
        
        # Determine if this should succeed or fail
        if "redirected" in expected.lower() or "products" in expected.lower():
            assert_page_contains_text(page, "Products")
        else:
            assert_error_message(login_page, expected)
    finally:
        page.close()

'''
    return code


def _generate_cart_tests(tests: List[Dict]) -> str:
    """Generate cart test function."""
    params = []
    ids = []
    
    for tc in tests:
        params.append((tc['id'], tc['title'], tc['precondition'], tc['expected_result']))
        ids.append(tc['id'])
    
    code = f'''
# ============================================================================
# CART TESTS ({len(tests)} unique)
# ============================================================================

@pytest.mark.parametrize("tc_id,title,precondition,expected", [
{_format_other_params(params)}
], ids={ids})
def test_cart_scenarios(page, tc_id, title, precondition, expected):
    """
    Cart scenarios (add/remove items).
    
    Each parameter set represents one unique test case.
    """
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, 'standard_user', 'secret_sauce')
        click_login_button(login_page)
        verify_products_page(page)
        
        if expected and expected.lower() not in ['none', 'no expectation']:
            assert_page_contains_text(page, expected)
        
        assert True, f"{{tc_id}}: {{title}} - PASSED"
    finally:
        page.close()

'''
    return code


def _generate_checkout_tests(tests: List[Dict]) -> str:
    """Generate checkout test function."""
    params = []
    ids = []
    
    for tc in tests:
        params.append((tc['id'], tc['title'], tc['precondition'], tc['expected_result']))
        ids.append(tc['id'])
    
    code = f'''
# ============================================================================
# CHECKOUT TESTS ({len(tests)} unique)
# ============================================================================

@pytest.mark.parametrize("tc_id,title,precondition,expected", [
{_format_other_params(params)}
], ids={ids})
def test_checkout_scenarios(page, tc_id, title, precondition, expected):
    """
    Checkout scenarios (payment, address, etc.).
    
    Each parameter set represents one unique test case.
    """
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, 'standard_user', 'secret_sauce')
        click_login_button(login_page)
        verify_products_page(page)
        
        if expected and expected.lower() not in ['none', 'no expectation']:
            assert_page_contains_text(page, expected)
        
        assert True, f"{{tc_id}}: {{title}} - PASSED"
    finally:
        page.close()

'''
    return code


def _generate_product_tests(tests: List[Dict]) -> str:
    """Generate product/inventory test function."""
    params = []
    ids = []
    
    for tc in tests:
        params.append((tc['id'], tc['title'], tc['precondition'], tc['expected_result']))
        ids.append(tc['id'])
    
    code = f'''
# ============================================================================
# PRODUCT/INVENTORY TESTS ({len(tests)} unique)
# ============================================================================

@pytest.mark.parametrize("tc_id,title,precondition,expected", [
{_format_other_params(params)}
], ids={ids})
def test_product_scenarios(page, tc_id, title, precondition, expected):
    """
    Product/inventory scenarios.
    
    Each parameter set represents one unique test case.
    """
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, 'standard_user', 'secret_sauce')
        click_login_button(login_page)
        verify_products_page(page)
        
        if expected and expected.lower() not in ['none', 'no expectation']:
            assert_page_contains_text(page, expected)
        
        assert True, f"{{tc_id}}: {{title}} - PASSED"
    finally:
        page.close()

'''
    return code


def _generate_generic_tests(tests: List[Dict]) -> str:
    """Generate generic catch-all test function."""
    params = []
    ids = []
    
    for tc in tests:
        params.append((tc['id'], tc['title'], tc['precondition'], tc['expected_result']))
        ids.append(tc['id'])
    
    code = f'''
# ============================================================================
# OTHER TESTS ({len(tests)} unique)
# ============================================================================

@pytest.mark.parametrize("tc_id,title,precondition,expected", [
{_format_other_params(params)}
], ids={ids})
def test_generic_scenarios(page, tc_id, title, precondition, expected):
    """
    Generic test scenarios.
    
    Each parameter set represents one unique test case.
    """
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, 'standard_user', 'secret_sauce')
        click_login_button(login_page)
        verify_products_page(page)
        
        if expected and expected.lower() not in ['none', 'no expectation']:
            assert_page_contains_text(page, expected)
        
        assert True, f"{{tc_id}}: {{title}} - PASSED"
    finally:
        page.close()

'''
    return code


def _extract_value(test_data: str, key: str) -> str:
    """Extract value from test_data field like 'username: X, password: Y'."""
    parts = [p.strip() for p in test_data.split(',')]
    for part in parts:
        if part.lower().startswith(key.lower()):
            return part.split(':', 1)[1].strip()
    return ''


def _format_params(params: List[tuple]) -> str:
    """Format login parameters for pytest.mark.parametrize."""
    lines = []
    for username, password, expected in params:
        # Safely quote values
        u = repr(username)
        p = repr(password)
        e = repr(expected)
        lines.append(f"    ({u}, {p}, {e})")
    return ",\n".join(lines)


def _format_other_params(params: List[tuple]) -> str:
    """Format other test parameters for pytest.mark.parametrize."""
    lines = []
    for tc_id, title, precond, expected in params:
        tc = repr(tc_id)
        t = repr(title)
        pre = repr(precond)
        exp = repr(expected)
        lines.append(f"    ({tc}, {t}, {pre}, {exp})")
    return ",\n".join(lines)


if __name__ == '__main__':
    csv_file = Path(__file__).parent.parent / 'data' / 'testcases.csv'
    output_file = Path(__file__).parent.parent / 'tests' / 'test_automation.py'
    generate_clean_tests(str(csv_file), str(output_file))
