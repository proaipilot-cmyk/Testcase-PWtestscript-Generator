import pytest
from .pages.app_pages import AppPage


def test_tc_login(browser_context):
    """Test Login. Expected: Success"""
    page = browser_context.new_page()
    app = AppPage(page)
    try:
        app.goto('https://www.saucedemo.com')
        # Enter username
        app.fill_field('username', 'standard_user')
        # Enter password
        app.fill_field('password', 'secret_sauce')
        # Click login
        app.click_element('login-button')
        # Assert: Success
        app.assert_text_visible('Success')
    finally:
        page.close()
