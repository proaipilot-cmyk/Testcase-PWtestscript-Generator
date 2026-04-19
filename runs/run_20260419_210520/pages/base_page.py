"""Base Page Object Model class."""
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
