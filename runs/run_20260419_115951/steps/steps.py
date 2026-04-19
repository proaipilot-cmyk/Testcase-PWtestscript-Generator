"""
Reusable step functions for test automation.
Each step is written ONCE and used across multiple test cases.

Late Binding: Uses dynamic locator resolution via resolve_locator()
- No hardcoded selectors
- Locators resolved at runtime from object_repo or snapshots
"""
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from locator import resolve_locator


# ============================================================================
# LOGIN STEPS
# ============================================================================

def navigate_to_login(page):
    """Navigate to login page using dynamic locator resolution."""
    login_page = LoginPage(page)
    login_page.navigate()
    return login_page


def fill_credentials(login_page, username: str, password: str) -> None:
    """
    Enter username and password (REUSABLE).
    Uses dynamic locator resolution for username and password fields.
    """
    page = login_page.page
    
    # Resolve locators dynamically (Repo → Snapshot → Fallback)
    username_locator = resolve_locator(page, 'username')
    password_locator = resolve_locator(page, 'password')
    
    # Fill fields
    username_locator.fill(username)
    password_locator.fill(password)


def click_login_button(login_page) -> None:
    """
    Click login button (REUSABLE).
    Uses dynamic locator resolution for button identification.
    """
    page = login_page.page
    
    # Resolve locator dynamically
    button_locator = resolve_locator(page, 'login_button')
    button_locator.click()


# ============================================================================
# ASSERTION STEPS
# ============================================================================

def assert_page_contains_text(page, expected_text: str, timeout: int = 5000) -> None:
    """Assert page contains expected text (domain-agnostic)."""
    try:
        page.wait_for_function(
            f"document.body.innerText.includes('{expected_text}')",
            timeout=timeout
        )
    except:
        body_text = page.content()
        raise AssertionError(f"Expected text '{expected_text}' not found on page")


def assert_error_message(login_page, expected_error: str) -> None:
    """
    Assert error message is displayed (REUSABLE).
    Uses dynamic locator resolution for error element.
    """
    page = login_page.page
    
    # Resolve error message locator dynamically
    error_locator = resolve_locator(page, 'error_message')
    error_text = error_locator.text_content()
    
    assert expected_error.lower() in (error_text or '').lower(), \
        f"Expected error '{expected_error}', got '{error_text}'"


# ============================================================================
# PRODUCT PAGE STEPS
# ============================================================================

def verify_products_page(page) -> ProductsPage:
    """
    Navigate to and verify products page.
    Uses dynamic locator resolution for inventory list.
    """
    products_page = ProductsPage(page)
    
    # Resolve inventory list locator dynamically
    inventory_locator = resolve_locator(page, 'inventory_list')
    inventory_locator.wait_for()
    
    return products_page
