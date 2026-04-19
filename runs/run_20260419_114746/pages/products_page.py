"""Products Page Object Model."""
from pages.base_page import BasePage
from playwright.sync_api import Page


class ProductsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, 'object_repo/products_page.json')
