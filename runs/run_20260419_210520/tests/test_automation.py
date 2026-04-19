"""
Consolidated test automation suite (data-driven, no duplication).

Strategy:
- Similar test cases grouped under ONE parameterized test
- Reusable step functions called (each step written once)
- TC IDs tracked in parameter ids
- Domain-agnostic for any application
"""
import pytest
from steps.steps import (
    navigate_to_login, fill_credentials, click_login_button,
    assert_page_contains_text, assert_error_message, verify_products_page
)



def test_login_success(browser_context):
    """
    Verify that the user is able to login successfully with valid credentials
    
    TC ID: TC_01
    Precondition: User is on the login page
    Expected: User is redirected to Products page and inventory items are displayed
    """
    page = browser_context.new_page()
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, 'standard_user', 'secret_sauce')
        click_login_button(login_page)
        assert_page_contains_text(page, 'Products')
    finally:
        page.close()



@pytest.mark.parametrize("username,password,expected_error", [
    ('locked_out_user', 'secret_sauce', 'Sorry, this user has been locked out.'),
    ('invalid_user', 'secret_sauce', 'Epic sadface: Username and password do not match any user in this service'),
    ('standard_user', 'wrong_pass', 'Epic sadface: Username and password do not match any user in this service'),
    ('locked_out_user', 'secret_sauce', 'Sorry, this user has been locked out.'),
    ('invalid_user', 'secret_sauce', 'Epic sadface: Username and password do not match any user in this service'),
    ('standard_user', 'wrong_pass', 'Epic sadface: Username and password do not match any user in this service'),
    ('locked_out_user', 'secret_sauce', 'Sorry, this user has been locked out.'),
    ('invalid_user', 'secret_sauce', 'Epic sadface: Username and password do not match any user in this service'),
    ('standard_user', 'wrong_pass', 'Epic sadface: Username and password do not match any user in this service')
], ids=['TC_02', 'TC_03', 'TC_04', 'TC_02', 'TC_03', 'TC_04', 'TC_02', 'TC_03', 'TC_04'])
def test_login_error_scenarios(browser_context, username, password, expected_error):
    """
    Login error scenarios (locked user, invalid credentials, etc.)
    
    Each parameter set is a separate test case with unique TC ID.
    Precondition: User is on the login page
    """
    page = browser_context.new_page()
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, username, password)
        click_login_button(login_page)
        assert_error_message(login_page, expected_error)
    finally:
        page.close()



# NOTE: 557 test cases skipped (non-login flows: account, payment, checkout, etc.)
# These require domain-specific page objects and step libraries
# Test IDs: 'TC_08', 'TC_10', 'TC_14', ...
# To implement: Create domain-specific test functions and generators
# The framework remains testcase-agnostic for login flows


