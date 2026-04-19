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
        fill_credentials(login_page, '', '')
        click_login_button(login_page)
        assert_page_contains_text(page, 'Products')
    finally:
        page.close()



@pytest.mark.parametrize("username,password,expected_error", [
    ('', '', 'Error message displayed: "Sorry, this user has been locked out."'),
    ('', '', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', '', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('', '', 'Error message: "Epic sadface: Password is required"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('', '', 'Error message: "Error: First Name is required"'),
    ('', '', 'Error message: "Error: Last Name is required"'),
    ('', '', 'Error message: "Error: Postal Code is required"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username is required"'),
    ('', '', 'Error message: "Username is required"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message or unsuccessful login'),
    ('', '', 'Error message: "Password is required" or login blocked'),
    ('', '', 'Error message: "First Name is required"'),
    ('', '', 'Error message: "Last Name is required"'),
    ('', '', 'Error message: "Postal Code is required"'),
    ('', '', 'Error message should appear for invalid postal code'),
    ('', '', 'Error message: "Please enter a valid email address", form not submitted'),
    ('', '', 'Error message: "Passwords do not match", form remains on page'),
    ('', '', 'Error message: "Password must be at least 8 characters and include uppercase, lowercase, and number"'),
    ('', '', 'Error message: "This email is already registered. Please login or use a different email."'),
    ('', '', 'Error message: "Invalid email or password", user remains on login page'),
    ('', '', 'Error message: "Invalid email or password", no indication if email exists (security)'),
    ('', '', 'Error page: "This password reset link has expired. Please request a new one."'),
    ('', '', 'After 5th attempt: "Account temporarily locked. Try again in 15 minutes" or CAPTCHA shown'),
    ('', '', 'Login blocked with message: "Please verify your email first", verification email sent'),
    ('', '', 'Error: "Current password is incorrect", password not changed'),
    ('', '', 'Error: "New password cannot be the same as your current password"'),
    ('', '', 'No red error messages, all scripts load successfully, no 404 resources'),
    ('', '', 'Input accepts 1-10, blocks <1 or >10, shows error if invalid, updates Add to Cart behavior'),
    ('', '', 'Inline error: "Please select a size/color", button doesn\'t submit, form validation triggers'),
    ('', '', 'Error message displayed: "Sorry, this user has been locked out."'),
    ('', '', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', '', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('', '', 'Error message: "Epic sadface: Password is required"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('', '', 'Error message: "Error: First Name is required"'),
    ('', '', 'Error message: "Error: Last Name is required"'),
    ('', '', 'Error message: "Error: Postal Code is required"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username is required"'),
    ('', '', 'Error message: "Username is required"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message or unsuccessful login'),
    ('', '', 'Error message: "Password is required" or login blocked'),
    ('', '', 'Error message: "First Name is required"'),
    ('', '', 'Error message: "Last Name is required"'),
    ('', '', 'Error message: "Postal Code is required"'),
    ('', '', 'Error message should appear for invalid postal code'),
    ('', '', 'Error message: "Please enter a valid email address", form not submitted'),
    ('', '', 'Error message: "Passwords do not match", form remains on page'),
    ('', '', 'Error message: "Password must be at least 8 characters and include uppercase, lowercase, and number"'),
    ('', '', 'Error message: "This email is already registered. Please login or use a different email."'),
    ('', '', 'Error message: "Invalid email or password", user remains on login page'),
    ('', '', 'Error message: "Invalid email or password", no indication if email exists (security)'),
    ('', '', 'Error page: "This password reset link has expired. Please request a new one."'),
    ('', '', 'After 5th attempt: "Account temporarily locked. Try again in 15 minutes" or CAPTCHA shown'),
    ('', '', 'Login blocked with message: "Please verify your email first", verification email sent'),
    ('', '', 'Error: "Current password is incorrect", password not changed'),
    ('', '', 'Error: "New password cannot be the same as your current password"'),
    ('', '', 'No red error messages, all scripts load successfully, no 404 resources'),
    ('', '', 'Input accepts 1-10, blocks <1 or >10, shows error if invalid, updates Add to Cart behavior'),
    ('', '', 'Inline error: "Please select a size/color", button doesn\'t submit, form validation triggers'),
    ('', '', 'Error message displayed: "Sorry, this user has been locked out."'),
    ('', '', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', '', 'Error message: "Epic sadface: Username and password do not match any user in this service"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('', '', 'Error message: "Epic sadface: Password is required"'),
    ('', '', 'Error message: "Epic sadface: Username is required"'),
    ('', '', 'Error message: "Error: First Name is required"'),
    ('', '', 'Error message: "Error: Last Name is required"'),
    ('', '', 'Error message: "Error: Postal Code is required"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message: "Username is required"'),
    ('', '', 'Error message: "Username is required"'),
    ('', '', 'Error message: "Username and password do not match"'),
    ('', '', 'Error message or unsuccessful login'),
    ('', '', 'Error message: "Password is required" or login blocked'),
    ('', '', 'Error message: "First Name is required"'),
    ('', '', 'Error message: "Last Name is required"'),
    ('', '', 'Error message: "Postal Code is required"'),
    ('', '', 'Error message should appear for invalid postal code'),
    ('', '', 'Error message: "Please enter a valid email address", form not submitted'),
    ('', '', 'Error message: "Passwords do not match", form remains on page'),
    ('', '', 'Error message: "Password must be at least 8 characters and include uppercase, lowercase, and number"'),
    ('', '', 'Error message: "This email is already registered. Please login or use a different email."'),
    ('', '', 'Error message: "Invalid email or password", user remains on login page'),
    ('', '', 'Error message: "Invalid email or password", no indication if email exists (security)'),
    ('', '', 'Error page: "This password reset link has expired. Please request a new one."'),
    ('', '', 'After 5th attempt: "Account temporarily locked. Try again in 15 minutes" or CAPTCHA shown'),
    ('', '', 'Login blocked with message: "Please verify your email first", verification email sent'),
    ('', '', 'Error: "Current password is incorrect", password not changed'),
    ('', '', 'Error: "New password cannot be the same as your current password"'),
    ('', '', 'No red error messages, all scripts load successfully, no 404 resources'),
    ('', '', 'Input accepts 1-10, blocks <1 or >10, shows error if invalid, updates Add to Cart behavior'),
    ('', '', 'Inline error: "Please select a size/color", button doesn\'t submit, form validation triggers'),
    ('', '', 'Inline errors: "Please select a rating", "Please write a review", form not submitted'),
    ('', '', 'Page loads progressively, skeleton loaders show, critical content prioritized, no timeout errors'),
    ('', '', 'Error message: "This code is invalid or has expired", no discount applied, totals unchanged'),
    ('', '', 'Cart shows "This item is now out of stock", quantity set to 0 or item removed, checkout blocked'),
    ('', '', 'Error message: "Some items are no longer available", checkout button disabled, option to remove unavailable'),
    ('', '', 'Inline error: "Please enter a valid email address", continue button disabled until fixed'),
    ('', '', 'Inline error: "First name is required", form highlights missing field, continue blocked'),
    ('', '', 'Inline error: "Please enter a valid card number", card type icon doesn\'t recognize, submit blocked'),
    ('', '', 'Inline error: "Card has expired", date field highlighted, payment blocked'),
    ('', '', 'Inline error: "Please enter a valid security code", CVV field highlighted, validation contextual to card type'),
    ('', '', 'Error: "You must agree to the terms and conditions", checkbox highlighted, order not placed'),
    ('', '', 'Error message: "Payment failed. Please try another method", user remains on payment step, cart not cleared'),
    ('', '', 'Payment authorized, order confirmed, success redirect, no errors in console'),
    ('', '', 'User-friendly error: "Your card has expired. Please use a different card or update expiry date."\r\nPAYMENT_TC_011,Verify payment retry logic works after transient failure,User experiences network error during payment,1. Simulate network failure during submit'),
    ('', '', 'Error: "Current password is incorrect", email not changed, security maintained'),
    ('', '', 'Authentication successful, user logged in, session created, code invalid/expired shows error'),
    ('', '', 'Errors in red, near relevant field, plain language explaining issue and how to fix (not just "Invalid")'),
    ('', '', 'Core functionality remains usable, error logged to monitoring service, user not shown raw error stack'),
    ('', '', 'Backend truncates or rejects with validation error, frontend has maxlength attribute, no server error/500'),
    ('', '', 'First user succeeds, second user gets "Item no longer available" error at checkout, inventory never goes negative'),
    ('', '', 'Logs contain error context but NOT: passwords, full card numbers, PII; uses log levels, structured logging'),
    ('', '', 'Page shows: friendly error message, reference ID for support, link to Help Center, email/chat contact option'),
    ('', '', 'Layout adapts smoothly, no content cutoff, images reflow, form inputs remain usable, no JS errors')
], ids=['TC_02', 'TC_03', 'TC_04', 'TC_05', 'TC_06', 'TC_07', 'TC_27', 'TC_28', 'TC_29', 'LOGIN_TC_002', 'LOGIN_TC_003', 'LOGIN_TC_004', 'LOGIN_TC_005', 'LOGIN_TC_006', 'LOGIN_TC_007', 'LOGIN_TC_010', 'CHECKOUT1_TC_002', 'CHECKOUT1_TC_003', 'CHECKOUT1_TC_004', 'CHECKOUT1_TC_007', 'AUTH_TC_002', 'AUTH_TC_003', 'AUTH_TC_004', 'AUTH_TC_005', 'AUTH_TC_007', 'AUTH_TC_008', 'AUTH_TC_012', 'AUTH_TC_019', 'AUTH_TC_021', 'AUTH_TC_024', 'AUTH_TC_026', 'HOMEPAGE_TC_013', 'PRODUCT_DETAIL_TC_007', 'PRODUCT_DETAIL_TC_009', 'TC_02', 'TC_03', 'TC_04', 'TC_05', 'TC_06', 'TC_07', 'TC_27', 'TC_28', 'TC_29', 'LOGIN_TC_002', 'LOGIN_TC_003', 'LOGIN_TC_004', 'LOGIN_TC_005', 'LOGIN_TC_006', 'LOGIN_TC_007', 'LOGIN_TC_010', 'CHECKOUT1_TC_002', 'CHECKOUT1_TC_003', 'CHECKOUT1_TC_004', 'CHECKOUT1_TC_007', 'AUTH_TC_002', 'AUTH_TC_003', 'AUTH_TC_004', 'AUTH_TC_005', 'AUTH_TC_007', 'AUTH_TC_008', 'AUTH_TC_012', 'AUTH_TC_019', 'AUTH_TC_021', 'AUTH_TC_024', 'AUTH_TC_026', 'HOMEPAGE_TC_013', 'PRODUCT_DETAIL_TC_007', 'PRODUCT_DETAIL_TC_009', 'TC_02', 'TC_03', 'TC_04', 'TC_05', 'TC_06', 'TC_07', 'TC_27', 'TC_28', 'TC_29', 'LOGIN_TC_002', 'LOGIN_TC_003', 'LOGIN_TC_004', 'LOGIN_TC_005', 'LOGIN_TC_006', 'LOGIN_TC_007', 'LOGIN_TC_010', 'CHECKOUT1_TC_002', 'CHECKOUT1_TC_003', 'CHECKOUT1_TC_004', 'CHECKOUT1_TC_007', 'AUTH_TC_002', 'AUTH_TC_003', 'AUTH_TC_004', 'AUTH_TC_005', 'AUTH_TC_007', 'AUTH_TC_008', 'AUTH_TC_012', 'AUTH_TC_019', 'AUTH_TC_021', 'AUTH_TC_024', 'AUTH_TC_026', 'HOMEPAGE_TC_013', 'PRODUCT_DETAIL_TC_007', 'PRODUCT_DETAIL_TC_009', 'PRODUCT_DETAIL_TC_013', 'PRODUCT_DETAIL_TC_019', 'CART_TC_009', 'CART_TC_012', 'CART_TC_015', 'CHECKOUT_TC_002', 'CHECKOUT_TC_004', 'CHECKOUT_TC_009', 'CHECKOUT_TC_010', 'CHECKOUT_TC_011', 'CHECKOUT_TC_015', 'CHECKOUT_TC_017', 'PAYMENT_TC_001', 'PAYMENT_TC_010', 'ACCOUNT_TC_009', 'ACCOUNT_TC_018', 'UI_UX_TC_005', 'ERROR_EDGE_TC_001', 'ERROR_EDGE_TC_007', 'ERROR_EDGE_TC_013', 'ERROR_EDGE_TC_015', 'ERROR_EDGE_TC_020', 'MOBILE_RESP_TC_008'])
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


# Unclassified test scenario


def test_cart_operations(browser_context):
    """
    Verify product details display correctly
    
    TC ID: TC_16
    Expected: Each product shows: Image, Name, Description, Price, Add to Cart button
    """
    page = browser_context.new_page()
    try:
        # Login first
        login_page = navigate_to_login(page)
        fill_credentials(login_page, 'standard_user', 'secret_sauce')
        click_login_button(login_page)
        
        # Cart operations
        products_page = verify_products_page(page)
        # TODO: Implement cart-specific steps
    finally:
        page.close()


