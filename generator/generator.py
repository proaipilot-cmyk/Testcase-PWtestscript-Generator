"""
Generator Module - Converts canonical action schema to Playwright POM framework
Produces: object_repo/*.json, pages/*.py, steps/*.py, tests/*.py, conftest.py

NEW APPROACH: Reusable step functions + data-driven parameterized tests
(No duplicate code, domain-agnostic, minimal tokens)
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime


class ObjectRepositoryGenerator:
    """Generate per-page object repository JSON files with locators."""
    
    DEFAULT_LOCATORS = {
        'login_page': {
            'page_name': 'login_page',
            'url_pattern': 'saucedemo.com',
            'elements': {
                'username': {'selector': 'input[data-test="username"]', 'type': 'input', 'desc': 'Username input'},
                'password': {'selector': 'input[data-test="password"]', 'type': 'input', 'desc': 'Password input'},
                'login_button': {'selector': 'input[data-test="login-button"]', 'type': 'button', 'desc': 'Login submit'},
                'error_message': {'selector': 'h3[data-test="error"]', 'type': 'text', 'desc': 'Error display'},
            }
        },
        'products_page': {
            'page_name': 'products_page',
            'url_pattern': 'saucedemo.com/inventory',
            'elements': {
                'inventory_list': {'selector': '.inventory_list', 'type': 'div', 'desc': 'Products list'},
                'add_to_cart': {'selector': 'button[data-test*="add-to-cart"]', 'type': 'button', 'desc': 'Add to cart'},
                'cart_link': {'selector': 'a.shopping_cart_link', 'type': 'link', 'desc': 'Cart link'},
                'title': {'selector': 'h3.title', 'type': 'text', 'desc': 'Page title'},
            }
        }
    }
    
    def __init__(self, output_dir: str = 'object_repo'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self) -> Dict[str, str]:
        generated_files = {}
        for page_name, repo_data in self.DEFAULT_LOCATORS.items():
            file_path = self.output_dir / f"{page_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(repo_data, f, indent=2, ensure_ascii=False)
            generated_files[page_name] = str(file_path)
        return generated_files


class PageObjectGenerator:
    """Generate Page Object Model Python classes."""
    
    BASE_PAGE_TEMPLATE = '''"""Base Page Object Model class."""
from playwright.sync_api import Page
import json


class BasePage:
    """Base class for all page objects. Loads locators from JSON."""
    
    def __init__(self, page: Page, repo_file: str):
        self.page = page
        self.locators = self._load_locators(repo_file)
    
    def _load_locators(self, repo_file: str) -> dict:
        with open(repo_file, 'r', encoding='utf-8') as f:
            repo = json.load(f)
        return repo.get('elements', {})
    
    def get_selector(self, element_name: str) -> str:
        if element_name not in self.locators:
            raise KeyError(f"Locator '{element_name}' not found")
        return self.locators[element_name]['selector']
    
    def fill(self, element_name: str, value: str) -> None:
        selector = self.get_selector(element_name)
        self.page.fill(selector, value)
    
    def click(self, element_name: str) -> None:
        selector = self.get_selector(element_name)
        self.page.click(selector)
    
    def get_text(self, element_name: str) -> str:
        selector = self.get_selector(element_name)
        return self.page.text_content(selector) or ""
    
    def goto(self, url: str) -> None:
        self.page.goto(url)
'''
    
    LOGIN_PAGE_TEMPLATE = '''"""Login Page Object Model."""
from pages.base_page import BasePage
from playwright.sync_api import Page


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, 'object_repo/login_page.json')
    
    def navigate(self, url: str = 'https://www.saucedemo.com') -> None:
        self.goto(url)
'''
    
    PRODUCTS_PAGE_TEMPLATE = '''"""Products Page Object Model."""
from pages.base_page import BasePage
from playwright.sync_api import Page


class ProductsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, 'object_repo/products_page.json')
'''
    
    def __init__(self, output_dir: str = 'pages'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self) -> Dict[str, str]:
        generated_files = {}
        
        base_page_file = self.output_dir / 'base_page.py'
        with open(base_page_file, 'w', encoding='utf-8') as f:
            f.write(self.BASE_PAGE_TEMPLATE)
        generated_files['base_page'] = str(base_page_file)
        
        login_page_file = self.output_dir / 'login_page.py'
        with open(login_page_file, 'w', encoding='utf-8') as f:
            f.write(self.LOGIN_PAGE_TEMPLATE)
        generated_files['login_page'] = str(login_page_file)
        
        products_page_file = self.output_dir / 'products_page.py'
        with open(products_page_file, 'w', encoding='utf-8') as f:
            f.write(self.PRODUCTS_PAGE_TEMPLATE)
        generated_files['products_page'] = str(products_page_file)
        
        return generated_files


class StepLibraryGenerator:
    """Generate reusable step functions (domain-agnostic)."""
    
    STEPS_TEMPLATE = '''"""
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
    
    assert expected_error.lower() in (error_text or '').lower(), \\
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
'''
    
    def __init__(self, output_dir: str = 'steps'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self) -> Dict[str, str]:
        steps_file = self.output_dir / 'steps.py'
        with open(steps_file, 'w', encoding='utf-8') as f:
            f.write(self.STEPS_TEMPLATE)
        return {'steps': str(steps_file)}


class TestGeneratorV2:
    """
    NEW: Data-driven test generator using reusable steps.
    
    Strategy:
    1. Cluster test cases by scenario type (login_success, login_errors, product_actions)
    2. Group similar cases under ONE parameterized test
    3. Call reusable step functions (no duplication)
    4. Extract TC IDs, credentials, expected results from planned cases
    """
    
    CONFTEST_TEMPLATE = '''"""Pytest configuration and fixtures."""
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def browser_context(browser):
    context = browser.new_context()
    yield context
    context.close()
'''
    
    def __init__(self, output_dir: str = 'tests'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _cluster_test_cases(self, planned_cases: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Cluster test cases by scenario type.
        Returns dict: scenario_type -> [test_cases]
        """
        clusters = {}
        
        for case in planned_cases:
            expected = (case.get('expected_result') or '').lower()
            title = (case.get('title') or '').lower()
            
            # Classify by expected result keywords
            if 'error' in expected or 'locked' in expected or 'do not match' in expected:
                scenario = 'login_errors'
            elif 'products' in expected or 'inventory' in expected:
                scenario = 'login_success'
            elif 'cart' in expected or 'add' in expected:
                scenario = 'cart_operations'
            else:
                scenario = 'other'
            
            if scenario not in clusters:
                clusters[scenario] = []
            clusters[scenario].append(case)
        
        return clusters
    
    def _extract_test_data(self, planned_case: Dict[str, Any]) -> Dict[str, Any]:
        """Extract credentials and assertions from planned case."""
        test_data = planned_case.get('test_data', {})
        expected = planned_case.get('expected_result', '')
        
        # Normalize test_data keys (case-insensitive)
        normalized_td = {}
        for k, v in test_data.items():
            normalized_td[k.lower()] = v
        
        return {
            'tc_id': planned_case.get('id', 'UNKNOWN'),
            'username': normalized_td.get('username', ''),
            'password': normalized_td.get('password', ''),
            'expected_result': expected,
        }
    
    def _generate_parameterized_test(self, scenario: str, cases: List[Dict[str, Any]]) -> str:
        """Generate ONE parameterized test for a cluster of cases."""
        
        if scenario == 'login_success':
            # Single success case
            case = cases[0]
            data = self._extract_test_data(case)
            
            return f'''
def test_login_success(browser_context):
    """
    {case.get('title')}
    
    TC ID: {data['tc_id']}
    Precondition: {case.get('precondition', 'N/A')}
    Expected: {data['expected_result']}
    """
    page = browser_context.new_page()
    try:
        login_page = navigate_to_login(page)
        fill_credentials(login_page, '{data['username']}', '{data['password']}')
        click_login_button(login_page)
        assert_page_contains_text(page, 'Products')
    finally:
        page.close()
'''
        
        elif scenario == 'login_errors':
            # Build parameter list SAFELY using repr() to escape quotes
            param_tuples = []
            tc_ids = []
            
            for case in cases:
                data = self._extract_test_data(case)
                # repr() automatically escapes quotes properly
                username_repr = repr(data['username'])
                password_repr = repr(data['password'])
                error_repr = repr(data['expected_result'])
                
                param_tuples.append(f"({username_repr}, {password_repr}, {error_repr})")
                tc_ids.append(repr(data['tc_id']))
            
            params_str = ',\n    '.join(param_tuples)
            tc_ids_str = ', '.join(tc_ids)
            
            return f'''
@pytest.mark.parametrize("username,password,expected_error", [
    {params_str}
], ids=[{tc_ids_str}])
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
'''
        
        elif scenario == 'cart_operations':
            # Placeholder for cart tests
            case = cases[0]
            return f'''
def test_cart_operations(browser_context):
    """
    {case.get('title')}
    
    TC ID: {case.get('id', 'UNKNOWN')}
    Expected: {case.get('expected_result', 'N/A')}
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
'''
        
        else:
            return "# Unclassified test scenario"
    
    def generate(self, planned_cases: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate consolidated, data-driven test file."""
        
        # Cluster cases
        clusters = self._cluster_test_cases(planned_cases)
        
        # Build test file
        test_code = '''"""
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


'''
        
        # Generate tests for each cluster
        for scenario, cases in clusters.items():
            test_code += self._generate_parameterized_test(scenario, cases)
            test_code += '\n\n'
        
        # Write conftest.py
        conftest_file = self.output_dir / 'conftest.py'
        with open(conftest_file, 'w', encoding='utf-8') as f:
            f.write(self.CONFTEST_TEMPLATE)
        
        # Write consolidated test file
        test_file = self.output_dir / 'test_automation.py'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        return {'test_automation': str(test_file), 'conftest': str(conftest_file)}


class Generator:
    """Main generator orchestrator."""
    
    def __init__(self, output_base: str = '.'):
        self.output_base = Path(output_base)
        self.object_repo_gen = ObjectRepositoryGenerator(str(self.output_base / 'object_repo'))
        self.page_gen = PageObjectGenerator(str(self.output_base / 'pages'))
        self.steps_gen = StepLibraryGenerator(str(self.output_base / 'steps'))
        self.test_gen = TestGeneratorV2(str(self.output_base / 'tests'))
    
    def generate(self, planned_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate complete POM framework (NEW: data-driven, minimal duplication)."""
        result = {
            'timestamp': datetime.now().isoformat(),
            'object_repo': self.object_repo_gen.generate(),
            'pages': self.page_gen.generate(),
            'steps': self.steps_gen.generate(),
            'tests': self.test_gen.generate(planned_cases),
            'summary': {
                'test_cases': len(planned_cases),
                'pages_generated': 3,
                'step_functions': 7,
                'consolidated_test_file': 'test_automation.py (no duplication)'
            }
        }
        return result

