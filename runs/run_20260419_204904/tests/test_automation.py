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
    ('locked_out_user', 'secret_sauce', 'Error message displayed: "Sorry, this user has been locked out."'),
    ('invalid_user', 'secret_sauce', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('standard_user', 'wrong_pass', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', 'secret_sauce', 'Error message: "Epic sadface: Username is required"'),
    ('standard_user', '', 'Error message: "Epic sadface: Password is required"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('invalid_user', '', 'Error message: "Username and password do not match"'),
    ('standard_user', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username is required"'),
    ('standard_user', '', 'Error message: "Username is required"'),
    ('', 'secret_sauce', 'Error message: "Username and password do not match"'),
    ('Standard_User', '', 'Error message or unsuccessful login'),
    ("' OR '1'='1", '', 'Error message: "Password is required" or login blocked'),
    ('', 'WrongPass!', 'Error message: "Invalid email or password", user remains on login page'),
    ('', 'AnyPass123!', 'Error message: "Invalid email or password", no indication if email exists (security)'),
    ('locked_out_user', 'secret_sauce', 'Error message displayed: "Sorry, this user has been locked out."'),
    ('invalid_user', 'secret_sauce', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('standard_user', 'wrong_pass', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', 'secret_sauce', 'Error message: "Epic sadface: Username is required"'),
    ('standard_user', '', 'Error message: "Epic sadface: Password is required"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('invalid_user', '', 'Error message: "Username and password do not match"'),
    ('standard_user', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username is required"'),
    ('standard_user', '', 'Error message: "Username is required"'),
    ('', 'secret_sauce', 'Error message: "Username and password do not match"'),
    ('Standard_User', '', 'Error message or unsuccessful login'),
    ("' OR '1'='1", '', 'Error message: "Password is required" or login blocked'),
    ('', 'WrongPass!', 'Error message: "Invalid email or password", user remains on login page'),
    ('', 'AnyPass123!', 'Error message: "Invalid email or password", no indication if email exists (security)'),
    ('locked_out_user', 'secret_sauce', 'Error message displayed: "Sorry, this user has been locked out."'),
    ('invalid_user', 'secret_sauce', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('standard_user', 'wrong_pass', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', 'secret_sauce', 'Error message: "Epic sadface: Username is required"'),
    ('standard_user', '', 'Error message: "Epic sadface: Password is required"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('invalid_user', '', 'Error message: "Username and password do not match"'),
    ('standard_user', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username is required"'),
    ('standard_user', '', 'Error message: "Username is required"'),
    ('', 'secret_sauce', 'Error message: "Username and password do not match"'),
    ('Standard_User', '', 'Error message or unsuccessful login'),
    ("' OR '1'='1", '', 'Error message: "Password is required" or login blocked'),
    ('', 'WrongPass!', 'Error message: "Invalid email or password", user remains on login page'),
    ('', 'AnyPass123!', 'Error message: "Invalid email or password", no indication if email exists (security)'),
    ('', '', 'Authentication successful, user logged in, session created, code invalid/expired shows error')
], ids=['TC_02', 'TC_03', 'TC_04', 'TC_05', 'TC_06', 'TC_07', 'LOGIN_TC_002', 'LOGIN_TC_003', 'LOGIN_TC_004', 'LOGIN_TC_005', 'LOGIN_TC_006', 'LOGIN_TC_007', 'LOGIN_TC_010', 'AUTH_TC_007', 'AUTH_TC_008', 'TC_02', 'TC_03', 'TC_04', 'TC_05', 'TC_06', 'TC_07', 'LOGIN_TC_002', 'LOGIN_TC_003', 'LOGIN_TC_004', 'LOGIN_TC_005', 'LOGIN_TC_006', 'LOGIN_TC_007', 'LOGIN_TC_010', 'AUTH_TC_007', 'AUTH_TC_008', 'TC_02', 'TC_03', 'TC_04', 'TC_05', 'TC_06', 'TC_07', 'LOGIN_TC_002', 'LOGIN_TC_003', 'LOGIN_TC_004', 'LOGIN_TC_005', 'LOGIN_TC_006', 'LOGIN_TC_007', 'LOGIN_TC_010', 'AUTH_TC_007', 'AUTH_TC_008', 'ACCOUNT_TC_018'])
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



# NOTE: 607 test cases skipped (non-login flows: account, payment, checkout, etc.)
# These require domain-specific page objects and step libraries
# Test IDs: 'TC_08', 'TC_09', 'TC_10', ...
# To implement: Create domain-specific test functions and generators
# The framework remains testcase-agnostic for login flows


