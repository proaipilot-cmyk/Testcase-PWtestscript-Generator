import pytest
from .pages.app_pages import AppPage


def test_tc_01(browser_context):
    """Verify that the user is able to login successfully with valid credentials. Expected: Success"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter valid username
        app.fill_field('username', 'standard_user')
        # Enter valid password
        app.fill_field('password', 'secret_sauce')
        # Click on Login button
        app.click_element('login-button')
        # Assert: Success
        page.wait_for_timeout(10000)
        app.assert_text_visible('Products')
    finally:
        page.close()

def test_tc_02(browser_context):
    """Verify that login is denied for locked out user. Expected: error message displayed: 'sorry, this user has been locked out.'"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter Username: locked_out_user
        app.fill_field('username', 'locked_out_user')
        # Enter Password: secret_sauce
        app.fill_field('password', 'secret_sauce')
        # Click Login button
        app.click_element('login-button')
        # Assert: error message displayed: 'sorry, this user has been locked out.'
        page.wait_for_timeout(10000)
        app.assert_text_visible("error message displayed: 'sorry, this user has been locked out.'")
    finally:
        page.close()

def test_tc_03(browser_context):
    """Verify that login fails with invalid username. Expected: error message: 'epic sadface: username and password do not match any user in this service'"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter invalid username
        app.fill_field('username', 'invalid_user')
        # Enter valid password
        app.fill_field('password', 'secret_sauce')
        # Click Login
        app.click_element('login-button')
        
        # Assert: error message: 'epic sadface: username and password do not match any user in this service'
        app.assert_text_visible("error message: 'epic sadface: username and password do not match any user in this service'")
    finally:
        page.close()

def test_tc_04(browser_context):
    """Verify that login fails with invalid password. Expected: error message: 'epic sadface: username and password do not match any user in this service'"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter valid username
        app.fill_field('username', 'standard_user')
        # Enter invalid password
        app.fill_field('password', 'wrong_pass')
        # Click Login
        app.click_element('login-button')
        # Assert: error message: 'epic sadface: username and password do not match any user in this service'
        
        app.assert_text_visible("error message: 'epic sadface: username and password do not match any user in this service'")
    finally:
        page.close()

def test_tc_05(browser_context):
    """Verify that login fails when username is empty. Expected: error message: 'epic sadface: username is required'"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter any password
        app.fill_field('password', 'secret_sauce')
        # Click Login
        app.click_element('login-button')
        # Assert: error message: 'epic sadface: username is required'
        
        app.assert_text_visible("error message: 'Epic sadface: Username is required'")
    finally:
        page.close()

def test_tc_06(browser_context):
    """Verify that login fails when password is empty. Expected: error message: 'epic sadface: password is required'"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter valid username
        app.fill_field('username', 'standard_user')
        # Click Login
        app.click_element('login-button')
        # Assert: error message: 'epic sadface: password is required'
        
        app.assert_text_visible('Epic sadface: Password is required')
    finally:
        page.close()

def test_tc_07(browser_context):
    """Verify that login fails when both fields are empty. Expected: error message: 'epic sadface: username is required'"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Click Login
        app.click_element('login-button')
        # Assert: error message: 'epic sadface: username is required'
        page.wait_for_timeout(10000)
        app.assert_text_visible("Epic sadface: Username is required")
    finally:
        page.close()

def test_tc_08(browser_context):
    """Verify error message is displayed for performance glitch user. Expected: login succeeds but page may load slowly or show glitch behavior"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter Username: performance_glitch_user
        app.fill_field('username', 'performance_glitch_user')
        # Enter Password: secret_sauce
        app.fill_field('password', 'secret_sauce')
        # Click Login
        app.click_element('login-button')
        # Assert: login succeeds but page may load slowly or show glitch behavior
        page.wait_for_timeout(10000)
        app.assert_text_visible('login succeeds but page may load slowly or show glitch behavior')
    finally:
        page.close()
