"""Login Page Object Model."""
from pages.base_page import BasePage
from playwright.sync_api import Page


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, 'object_repo/login_page.json')
    
    def navigate(self, url: str = 'https://www.saucedemo.com') -> None:
        self.goto(url)
