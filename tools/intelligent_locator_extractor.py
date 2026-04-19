"""
Intelligent Locator Extractor - Analyzes page and extracts smart locators for automation.
Supports multi-step workflows with session persistence and step-by-step locator capture.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


class IntelligentLocatorExtractor:
    def __init__(self, output_dir="data/snapshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.page = None
        self.browser = None
        self.context = None
        self.locators_map = {}
        self.workflow_steps = []
        self.step_counter = 0
        
    def start(self, url):
        """Navigate to URL and prepare for locator extraction"""
        self.browser = sync_playwright().start().chromium.launch()
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(url)
        print(f"✓ Navigated to: {url}")
        return self
    
    def execute_workflow(self, workflow_file):
        """Execute a multi-step workflow from JSON file"""
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        steps = workflow.get("steps", [])
        print(f"\n📋 Executing workflow with {len(steps)} steps...\n")
        
        # Initialize browser before executing steps
        if not self.browser:
            self.browser = sync_playwright().start().chromium.launch()
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print("✓ Browser initialized\n")
        
        for idx, step in enumerate(steps, 1):
            self.step_counter = idx
            print(f"--- Step {idx} ---")
            self._execute_step(step)
            print()
        
        return self
    
    def _execute_step(self, step):
        """Execute a single workflow step"""
        if "navigate" in step:
            self._step_navigate(step["navigate"])
        
        elif "fill" in step:
            self._step_fill(step["fill"])
        
        elif "click" in step:
            self._step_click(step["click"])
        
        elif "select" in step:
            self._step_select(step["select"])
        
        elif "wait" in step:
            self._step_wait(step["wait"])
        
        elif "capture_locators" in step:
            self._step_capture_locators(step["capture_locators"])
        
        elif "extract_from_current_page" in step:
            self._step_extract_current_page(step["extract_from_current_page"])
    
    def _step_navigate(self, url):
        """Navigate to URL"""
        print(f"  🔗 Navigating to: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        print(f"  ✓ Page loaded: {self.page.title()}")
    
    def _step_fill(self, fill_config):
        """Fill form field - intelligently find the locator"""
        find_by = fill_config.get("find_by", "label")
        value = fill_config.get("value")
        field_label = fill_config.get("field_label")
        
        # Find locator intelligently based on accessibility
        locator = self._find_locator_by_intent(find_by, field_label)
        
        if not locator:
            print(f"  ❌ Could not find field: {field_label}")
            return
        
        print(f"  ✏️  Filling '{field_label}'")
        print(f"     Found locator: {locator}")
        self.page.fill(locator, value)
        print(f"  ✓ Filled successfully")
    
    def _step_click(self, click_config):
        """Click element - intelligently find the locator"""
        find_by = click_config.get("find_by", "button_text")
        button_text = click_config.get("button_text")
        
        # Find locator intelligently
        locator = self._find_locator_by_intent(find_by, button_text)
        
        if not locator:
            print(f"  ❌ Could not find button: {button_text}")
            return
        
        print(f"  🖱️  Clicking: {button_text}")
        print(f"     Found locator: {locator}")
        self.page.click(locator)
        
        if click_config.get("wait_for_navigation", False):
            try:
                # Try to wait for navigation with reduced timeout (5 seconds)
                self.page.wait_for_load_state("networkidle", timeout=5000)
                print(f"  ✓ Navigation complete")
            except:
                # If timeout occurs (e.g., due to CAPTCHA), just wait a bit and continue
                print(f"  ⚠️  Navigation wait timed out (possible CAPTCHA or dynamic content)")
                self.page.wait_for_timeout(2000)
                print(f"  ✓ Continued after wait")
        else:
            self.page.wait_for_timeout(500)
            print(f"  ✓ Clicked successfully")
    
    def _step_select(self, select_config):
        """Select dropdown option"""
        locator = select_config.get("locator")
        value = select_config.get("value")
        option_name = select_config.get("option_name", value)
        
        print(f"  📋 Selecting '{option_name}'")
        self.page.select_option(locator, value)
        print(f"  ✓ Selected successfully")
    
    def _step_wait(self, wait_config):
        """Wait for element or timeout"""
        if "locator" in wait_config:
            locator = wait_config["locator"]
            print(f"  ⏳ Waiting for element: {locator}")
            self.page.wait_for_selector(locator, timeout=10000)
            print(f"  ✓ Element found")
        elif "timeout" in wait_config:
            timeout = wait_config["timeout"]
            print(f"  ⏳ Waiting {timeout}ms")
            self.page.wait_for_timeout(timeout)
            print(f"  ✓ Wait complete")
    
    def _step_capture_locators(self, capture_config):
        """Capture locators at current step"""
        checkpoint_name = capture_config.get("checkpoint_name", f"step_{self.step_counter}")
        selector_filter = capture_config.get("selector_filter", None)
        
        print(f"  📸 Capturing locators - Checkpoint: '{checkpoint_name}'")
        self.extract_locators(selector_filter)
        self.workflow_steps.append({
            "step": self.step_counter,
            "checkpoint": checkpoint_name,
            "url": self.page.url,
            "title": self.page.title(),
            "locators_count": len(self.locators_map)
        })
        print(f"  ✓ Captured {len(self.locators_map)} locators")
    
    def _step_extract_current_page(self, config):
        """Extract all locators from current page (alias for capture_locators)"""
        self._step_capture_locators(config)
    
    def extract_locators(self, selector_filter=None):
        """Extract intelligent locators for all interactive elements"""
        
        if selector_filter:
            # Use custom selector filter
            elements = self.page.query_selector_all(selector_filter)
            print(f"  ℹ️  Using custom selector: {selector_filter}")
        else:
            # Default: find all interactive elements
            elements = self.page.query_selector_all(
                "input, button, a, select, textarea, form, [role='button'], [role='link']"
            )
        
        print(f"  📍 Found {len(elements)} interactive elements")
        
        # Clear previous locators for fresh extraction
        self.locators_map = {}
        
        for idx, element in enumerate(elements):
            locator_data = self._analyze_element(element, idx)
            if locator_data:
                self.locators_map[locator_data["element_id"]] = locator_data
        
        return self
    
    def _analyze_element(self, element, idx):
        """Analyze a single element and extract best locators"""
        try:
            tag_name = element.evaluate("el => el.tagName.toLowerCase()")
            element_id = element.evaluate("el => el.id || el.name || ''")
            
            # Skip invisible elements
            visible = element.evaluate("el => el.offsetParent !== null")
            if not visible:
                return None
            
            locator_data = {
                "element_id": f"elem_{idx}",
                "tag_name": tag_name,
                "label": self._get_label(element),
                "text_content": element.evaluate("el => el.textContent.trim()"),
                "attributes": self._extract_attributes(element),
                "locators": self._generate_locators(element, tag_name, element_id),
                "best_locator": None,
                "element_type": self._classify_element(tag_name, element)
            }
            
            # Set best locator (highest priority)
            if locator_data["locators"]:
                locator_data["best_locator"] = locator_data["locators"][0]
            
            return locator_data
        except:
            return None
    
    def _extract_attributes(self, element):
        """Extract useful attributes"""
        return element.evaluate("""el => ({
            id: el.id,
            name: el.name,
            class: el.className,
            type: el.type,
            value: el.value,
            placeholder: el.placeholder,
            'data-testid': el.getAttribute('data-testid'),
            'aria-label': el.getAttribute('aria-label'),
            'aria-labelledby': el.getAttribute('aria-labelledby'),
            role: el.getAttribute('role'),
            title: el.title
        })""")
    
    def _generate_locators(self, element, tag_name, element_id):
        """Generate multiple locator strategies, prioritized"""
        locators = []
        attrs = self._extract_attributes(element)
        text = element.evaluate("el => el.textContent.trim()")
        
        # Priority 1: data-testid (most reliable)
        if attrs.get('data-testid'):
            locators.append(f'getByTestId("{attrs["data-testid"]}")')
        
        # Priority 2: ID (strong)
        if attrs.get('id'):
            locators.append(f'locator("#{attrs["id"]}")')
        
        # Priority 3: aria-label (accessible)
        if attrs.get('aria-label'):
            locators.append(f'getByLabel("{attrs["aria-label"]}")')
        
        # Priority 4: Role + text (semantic, Playwright native)
        role = attrs.get('role') or self._infer_role(tag_name)
        if role and text:
            text_short = text[:50].replace('"', "'")
            locators.append(f'getByRole("{role}", {{ name: "{text_short}" }})')
        
        # Priority 5: Name attribute (for inputs)
        if attrs.get('name'):
            locators.append(f'locator("[name=\\"{attrs["name"]}\\"]")')
        
        # Priority 6: Placeholder (for inputs)
        if attrs.get('placeholder'):
            locators.append(f'locator("[placeholder=\\"{attrs["placeholder"]}\\"]")')
        
        # Priority 7: CSS selector
        css = element.evaluate("el => el.className ? `.${el.className.split(' ').join('.')}` : null")
        if css and css != ".":
            locators.append(f'locator("{css}")')
        
        # Priority 8: XPath-like text matching
        if text and len(text) < 100:
            text_short = text[:50].replace('"', "'")
            locators.append(f'locator("text={text_short}")')
        
        return locators
    
    def _infer_role(self, tag_name):
        """Infer ARIA role from tag name"""
        role_map = {
            "button": "button",
            "a": "link",
            "input": "textbox",
            "select": "combobox",
            "textarea": "textbox",
            "form": "form",
            "h1": "heading",
            "h2": "heading"
        }
        return role_map.get(tag_name, None)
    
    def _get_label(self, element):
        """Find associated label"""
        try:
            element_id = element.evaluate("el => el.id")
            if element_id:
                label = self.page.query_selector(f'label[for="{element_id}"]')
                if label:
                    return label.evaluate("el => el.textContent.trim()")
            return None
        except:
            return None
    
    def _classify_element(self, tag_name, element):
        """Classify element type"""
        classifications = {
            "input": "form_field",
            "button": "button",
            "a": "link",
            "select": "form_field",
            "textarea": "form_field",
            "form": "form"
        }
        return classifications.get(tag_name, "interactive")
    
    def _find_locator_by_intent(self, find_by, search_term):
        """Intelligently find locator using accessibility snapshot"""
        
        if find_by == "label":
            # Find input by associated label text
            try:
                label = self.page.query_selector(f'label:has-text("{search_term}")')
                if label:
                    # Try 1: Get the 'for' attribute and find input with that ID
                    for_id = label.get_attribute("for")
                    if for_id:
                        # First check if the element with that ID is an input
                        elem_by_id = self.page.query_selector(f'#{for_id}')
                        if elem_by_id and elem_by_id.evaluate("el => el.tagName.toLowerCase()") == "input":
                            return f"#{for_id}"
                        # If it's a div wrapper, find the input inside it
                        input_inside = elem_by_id.query_selector("input") if elem_by_id else None
                        if input_inside:
                            return f"#{for_id} input"
                    
                    # Try 2: Find input inside label
                    input_elem = label.query_selector("input")
                    if input_elem:
                        input_id = input_elem.get_attribute("id")
                        if input_id:
                            return f"#{input_id}"
                        return "input"
                    
                    # Try 3: Find input in parent's children
                    parent = label.query_selector("..")
                    if parent:
                        input_elem = parent.query_selector("input")
                        if input_elem:
                            input_id = input_elem.get_attribute("id")
                            if input_id:
                                return f"#{input_id}"
                            input_name = input_elem.get_attribute("name")
                            if input_name:
                                return f'input[name="{input_name}"]'
            except:
                pass
        
        elif find_by == "button_text":
            # Find button by text content
            try:
                button = self.page.query_selector(f'input[type="submit"][value="{search_term}"]')
                if button:
                    button_id = button.get_attribute("id")
                    if button_id:
                        return f"#{button_id}"
                    return f'input[type="submit"][value="{search_term}"]'
            except:
                pass
        
        elif find_by == "aria_label":
            # Find by aria-label attribute
            try:
                elem = self.page.query_selector(f'[aria-label="{search_term}"]')
                if elem:
                    elem_id = elem.get_attribute("id")
                    if elem_id:
                        return f"#{elem_id}"
            except:
                pass
        
        elif find_by == "placeholder":
            # Find input by placeholder text
            try:
                input_elem = self.page.query_selector(f'input[placeholder="{search_term}"]')
                if input_elem:
                    input_id = input_elem.get_attribute("id")
                    if input_id:
                        return f"#{input_id}"
                    return f'input[placeholder="{search_term}"]'
            except:
                pass
        
        return None
    
    def save_locators(self, filename=None):
        """Save extracted locators to JSON"""
        if not filename:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_locators.json"
        
        filepath = self.output_dir / filename
        
        # Group by element type
        grouped = {}
        for elem_id, data in self.locators_map.items():
            elem_type = data["element_type"]
            if elem_type not in grouped:
                grouped[elem_type] = []
            grouped[elem_type].append(data)
        
        output = {
            "metadata": {
                "extracted_at": datetime.now().isoformat(),
                "url": self.page.url,
                "title": self.page.title(),
                "total_elements": len(self.locators_map),
                "workflow_steps": len(self.workflow_steps)
            },
            "workflow_checkpoints": self.workflow_steps,
            "locators_by_type": grouped,
            "all_locators": self.locators_map
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Locators saved to: {filepath}")
        print(f"✓ Total elements analyzed: {len(self.locators_map)}")
        print(f"✓ Grouped by type: {list(grouped.keys())}")
        print(f"✓ Workflow checkpoints: {len(self.workflow_steps)}")
        
        return filepath
    
    def stop(self):
        """Close browser"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()


# Example usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Execute workflow from file
        workflow_file = sys.argv[1]
        extractor = IntelligentLocatorExtractor()
        try:
            (extractor
             .execute_workflow(workflow_file)
             .save_locators())
        finally:
            extractor.stop()
    else:
        # Single page extraction (default)
        extractor = IntelligentLocatorExtractor()
        try:
            (extractor
             .start("https://sauce-demo.myshopify.com/account/register")
             .extract_locators()
             .save_locators())
        finally:
            extractor.stop()