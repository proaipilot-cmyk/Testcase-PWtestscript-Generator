"""
Generator Module - High Reliability Code Generator
"""

import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class GenericTestGenerator:
    """
    Sanitized, data-driven test generator with robust file handling and POM support.
    """
    
    CONFTEST_TEMPLATE = '''import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture
def browser_context(browser):
    context = browser.new_context()
    yield context
    context.close()
'''

    BASE_PAGE_TEMPLATE = '''from locator import resolve_locator_sync

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
'''

    def __init__(self, output_dir: str = 'tests'):
        self.output_dir = Path(output_dir)
        self.locators_dir = self.output_dir / 'locators'
        self.pages_dir = self.output_dir / 'pages'
        
        for d in [self.output_dir, self.locators_dir, self.pages_dir]:
            d.mkdir(parents=True, exist_ok=True)
            (d / '__init__.py').touch()
    
    def _sanitize(self, val: Any) -> str:
        if val is None: return ""
        s = str(val).replace('\r', '').replace('\n', ' ').replace('"', "'")
        return re.sub(r'[^\x20-\x7E]', '', s).strip()

    def _normalize_er(self, msg: str) -> str:
        if not msg: return "Success"
        msg = self._sanitize(msg).lower()
        if any(w in msg for w in ['success', 'dashboard', 'products', 'welcome', 'inventory']):
            return "Success"
        return msg[:100]

    def _generate_page_class(self, cases: List[Dict[str, Any]]) -> str:
        lines = ["from .base_page import BasePage", "", "class AppPage(BasePage):", "    def __init__(self, page):", "        super().__init__(page)", ""]
        # Basic generic actions can be added here if needed, 
        # but for now we'll rely on base_page methods.
        return "\n".join(lines)

    def _generate_test_body(self, case: Dict[str, Any]) -> str:
        tid = re.sub(r'[^a-z0-9_]', '_', self._sanitize(case.get('id', '')).lower())
        if not tid: tid = f"tc_{uuid.uuid4().hex[:8]}"
        
        expected = self._normalize_er(case.get('expected_result', ''))
        precon = self._sanitize(case.get('precondition', '')).lower()
        title = self._sanitize(case.get('title', 'Testcase'))
        
        lines = []
        lines.append(f"def test_{tid}(browser_context):")
        lines.append(f"    \"\"\"{title}. Expected: {expected}\"\"\"")
        lines.append(f"    page = browser_context.new_page()")
        lines.append(f"    app = AppPage(page)")
        lines.append(f"    try:")
        
        actions = case.get('actions', [])
        has_goto = any(a.get('type') == 'goto' for a in actions)
        
        if not has_goto:
            url_match = re.search(r'(https?://\S+)', precon)
            url = url_match.group(1) if url_match else "https://www.saucedemo.com"
            lines.append(f"        app.goto({repr(url)})")
            
        if 'logged' in precon or 'items' in precon:
            lines.append(f"        # Generic setup")
            lines.append(f"        for f, v in [('username', 'standard_user'), ('password', 'secret_sauce')]:")
            lines.append(f"            app.fill_field(f, v)")
            lines.append(f"        app.click_element('login-button')")
            lines.append(f"        app.wait_for_load()")

        for act in actions:
            atype = act.get('type')
            raw = self._sanitize(act.get('raw', ''))
            if atype == 'fill':
                lines.append(f"        # {raw}")
                lines.append(f"        app.fill_field({repr(act.get('field', ''))}, {repr(act.get('value', ''))})")
            elif atype == 'click':
                lines.append(f"        # {raw}")
                lines.append(f"        app.click_element({repr(act.get('target', ''))})")
            elif atype in ['assert', 'assert_text', 'assert_error']:
                t_val = self._normalize_er(act.get('text', '') or act.get('value', ''))
                if t_val:
                    lines.append(f"        # Assert: {t_val}")
                    lines.append(f"        app.assert_text_visible({repr(t_val)})")
            elif atype == 'goto':
                lines.append(f"        app.goto({repr(act.get('url', ''))})")
        
        lines.append(f"    finally:")
        lines.append(f"        page.close()")
        return "\n".join(lines)

    def generate(self, cases: List[Dict[str, Any]]) -> Dict[str, str]:
        # Generate base infrastructure
        (self.output_dir / 'conftest.py').write_text(self.CONFTEST_TEMPLATE, encoding='utf-8')
        (self.pages_dir / 'base_page.py').write_text(self.BASE_PAGE_TEMPLATE, encoding='utf-8')
        (self.pages_dir / 'app_pages.py').write_text(self._generate_page_class(cases), encoding='utf-8')
        
        # Generate locators (stub for now, as they are resolved dynamically)
        (self.locators_dir / 'common_locators.py').write_text("# Elements are resolved dynamically using locator engine\nLOCATORS = {}\n", encoding='utf-8')
        
        test_file = self.output_dir / 'test_automation.py'
        content = [
            "import pytest",
            "from .pages.app_pages import AppPage",
            "",
            ""
        ]
        
        seen_ids = set()
        for case in cases:
            base_id = re.sub(r'[^a-z0-9_]', '_', str(case.get('id', '')).lower())
            final_id = base_id
            i = 1
            while not final_id or final_id in seen_ids:
                final_id = f"{base_id}_{i}"
                i += 1
            seen_ids.add(final_id)
            case['id'] = final_id
            content.append(self._generate_test_body(case))
            content.append("")
        
        test_file.write_text("\n".join(content), encoding='utf-8')
        return {'test_automation': str(test_file)}


class Generator:
    def __init__(self, base: str = '.'):
        self.g = GenericTestGenerator(str(Path(base) / 'tests'))
    def generate(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {'timestamp': datetime.now().isoformat(), 'tests': self.g.generate(cases), 'summary': {'test_cases': len(cases)}}
