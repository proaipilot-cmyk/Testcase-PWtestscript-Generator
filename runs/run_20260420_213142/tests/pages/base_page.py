from locator import resolve_locator_sync

class BasePage:
    def __init__(self, page):
        self.page = page

    def goto(self, url):
        self.page.goto(url)

    def wait_for_load(self):
        self.page.wait_for_load_state('load')

    def fill_field(self, field_name, value):
        loc = resolve_locator_sync(self.page, field_name)
        if loc: loc.fill(value)

    def click_element(self, element_name):
        loc = resolve_locator_sync(self.page, element_name)
        if loc: loc.click()

    def assert_text_visible(self, text):
        _v = text.lower()
        try:
            self.page.wait_for_function(f"document.body.innerText.toLowerCase().includes({{_v!r}})", timeout=5000)
        except:
            # Restricted validation scope: check inner_text of body
            body_text = self.page.inner_text("body").lower()
            if _v not in body_text:
                raise AssertionError(f"Text '{{text}}' not found in body. (Checked visible text only)")
