# Test Case to Automation Script - Complete Guide

## 📋 Complete Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEST CASE TO AUTOMATION PIPELINE                     │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  CSV FILE    │ ← Test cases from spreadsheet
    └──────┬───────┘
           │
           ↓
    ┌─────────────────────┐
    │ 1. PARSER           │ ← Normalize CSV headers, extract fields
    │ (parser/parser.py)  │   Output: parsed_testcases.json
    └──────┬──────────────┘
           │
           ↓
    ┌─────────────────────┐
    │ 2. PLANNER          │ ← Convert to canonical action schema
    │ (planner/planner.py)│   Output: planned_testcases.json
    └──────┬──────────────┘
           │
           ├─────────────────────────────────────────────┐
           │                                             │
           ↓                                             ↓
    ┌──────────────────────┐              ┌─────────────────────────┐
    │ 3A. GENERATOR        │              │ 3B. LOCATOR EXTRACTOR   │
    │ (generator/)         │              │ (intelligent_locator_   │
    │ Creates POM          │              │  extractor.py)          │
    │ Framework            │              │ OR                      │
    │ Output: object_repo/ │              │ Manually create         │
    │         pages/       │              │ workflow.json           │
    │         steps/       │              │                         │
    │         tests/       │              │ Output: locators.json   │
    └──────┬───────────────┘              └──────┬──────────────────┘
           │                                    │
           ├────────────────┬───────────────────┘
           │                │
           ↓                ↓
    ┌──────────────────┐  ┌──────────────────┐
    │ 4. VALIDATOR     │  │ Manual Test File │
    │ (validator/)     │  │ (tests/test_*.py)│
    │ Quality checks   │  └──────────────────┘
    │ Output: report   │
    └──────┬───────────┘
           │
           ↓
    ┌──────────────────┐
    │ 5. RUN TESTS     │
    │ pytest tests/    │
    │ Output: Results  │
    └──────────────────┘
```

---

## 🚀 Quick Start Paths

### Path 1: CSV → Auto-Generate Framework (Fastest)
```
CSV → Parser → Planner → Generator → Validator → Run Tests
Commands:
  python parser/demo.py
  python planner/demo.py
  python generator/demo.py
  python validator/demo.py
  pytest tests/ -v
```

### Path 2: Manual Workflow → Extract Locators (Flexible)
```
Manual Test → Workflow JSON → Intelligent Locator Extractor → Test Script
Commands:
  Create workflows/your_test.json
  python tools/intelligent_locator_extractor.py workflows/your_test.json
  Write tests/test_your_name.py
  pytest tests/test_your_name.py -v
```

### Path 3: Hybrid (Recommended)
```
CSV → Parser → Planner → [Manual Review] → Generator → Validator
```

---

## Step 1: Define Your Test Case

### What You Need
- **Test name**: Descriptive name of what you're testing
- **Test steps**: Manual steps written in plain English
- **Expected data**: Input values, field names, button labels

### Example Test Case
```
Test Name: User Registration Flow
Steps:
1. Navigate to registration page
2. Enter "Agent1" in First Name field
3. Enter "Yser1" in Last Name field
4. Enter "agentuser1@email.com" in Email field
5. Enter "Welcome10" in Password field
6. Click Create button
7. Verify account created message appears
```

### Alternative: Use CSV Format
If you have multiple test cases, add them to [data/testcases.csv](data/testcases.csv):

```csv
Test Case ID,Test Scenario Description,Pre-condition,Test Steps,Test Data,Expected Result (ER)
TC001,User Registration,"User on registration page","1. Enter first name 2. Enter last name 3. Enter email 4. Enter password 5. Click Create","first_name=Agent1,last_name=Yser1,email=agentuser1@email.com,password=Welcome10","Account created successfully"
TC002,User Login,"User registered","1. Enter username 2. Enter password 3. Click Login","username=standard_user,password=secret_sauce","Dashboard displayed"
```

---

## Step 1.5: (Optional) Parse Test Cases with Parser Module

If you have a CSV file with multiple test cases, use the **Parser** module to convert them to structured format.

### Parser Overview
The **Parser** converts CSV test cases to normalized structured data (JSON):
- Flexible column header matching (handles "Test Case ID", "test_case_id", "TC_ID", etc.)
- Extracts: id, title, precondition, steps, test_data, expected_result
- Validates test case structure
- Outputs JSON for next stages

### Run Parser
```bash
python parser/demo.py
```

### Expected Output
```
🚀 PARSER DEMO - Test Case Structure Conversion
================================================================================
✅ Successfully Parsed: 3 test cases

📋 PARSED TEST CASES (Structured Output)
================================================================================

[1] Test Case ID: TC001
   Title: User Registration Flow
   Precondition: User on registration page
   Steps:
      1. Navigate to registration page
      2. Enter first name
      3. Enter last name
      ...
   Test Data:
      first_name: Agent1
      last_name: Yser1
      email: agentuser1@email.com
      password: Welcome10
   Expected Result: Account created successfully
```

### Generated Output File
```
data/parsed_testcases.json  (structured test cases for next stage)
```

---

## Step 2: (Optional) Create Plan from Parsed Cases with Planner Module

The **Planner** converts parsed test cases to **canonical action schema** (framework-agnostic):

### Planner Overview
The **Planner** uses rule-based patterns to convert text steps to structured actions:
- Recognizes keywords: "navigate", "click", "enter", "verify", "assert"
- Extracts URLs, field names, button labels
- Outputs actions like: goto, fill, click, assert
- Serves as intermediate format for generator

### Run Planner
```bash
python planner/demo.py
```

### Expected Output
```
🚀 PLANNER DEMO - Test Case to Canonical Action Schema Conversion
====================================================

[STEP 1] PARSING TEST CASES
✅ Successfully parsed 3 test cases

[STEP 2] PLANNING TEST CASES (Generating Canonical Actions)
✅ Successfully planned 3 test cases

[CASE 1] TC001 - User Registration Flow
================================================
Actions Generated (7):

  Action 1: goto
     url: https://sauce-demo.myshopify.com/account/register

  Action 2: fill
     field: first_name
     value: Agent1

  Action 3: fill
     field: last_name
     value: Yser1

  Action 4: click
     target: create_button
```

### Generated Output File
```
data/planned_testcases.json  (canonical actions for generator)
```

### Canonical Action Schema
```json
{
  "type": "goto",
  "url": "https://..."
}

{
  "type": "fill",
  "field": "username",
  "value": "standard_user"
}

{
  "type": "click",
  "target": "login_button"
}

{
  "type": "assert_text",
  "text": "Products"
}
```

---

## Step 2B: Alternative - Create Workflow JSON File Directly

### File Location
```
workflows/your_workflow_name.json
```

### File Format

For **FORM FILLING** (by label):
```json
{
  "workflow": "your_test_name",
  "steps": [
    {
      "navigate": "https://example.com/page"
    },
    {
      "capture_locators": {
        "checkpoint_name": "page_loaded"
      }
    },
    {
      "fill": {
        "field_label": "Field Display Name",
        "value": "value to enter",
        "find_by": "label"
      }
    },
    {
      "click": {
        "button_text": "Button Text",
        "find_by": "button_text",
        "wait_for_navigation": false
      }
    },
    {
      "capture_locators": {
        "checkpoint_name": "after_action"
      }
    }
  ]
}
```

### Key Concepts

**Actions Available:**
- `navigate` - Go to URL
- `fill` - Enter text in form field
- `click` - Click button or link
- `select` - Choose dropdown option
- `wait` - Wait for element or timeout
- `capture_locators` - Extract locators at this point

**Fill Options:**
- `find_by: "label"` - Find input by associated label text (BEST)
- `find_by: "placeholder"` - Find by placeholder text
- `find_by: "aria_label"` - Find by accessibility label

**Click Options:**
- `find_by: "button_text"` - Find by button/link text (BEST)
- `wait_for_navigation: true` - Wait for page load after click
- `wait_for_navigation: false` - Don't wait (default)

---

## Step 3: Create the Workflow JSON

### Example: Complete Registration Flow
```json
{
  "workflow": "user_registration_flow",
  "steps": [
    {
      "navigate": "https://sauce-demo.myshopify.com/account/register"
    },
    {
      "capture_locators": {
        "checkpoint_name": "registration_page_loaded"
      }
    },
    {
      "fill": {
        "field_label": "First Name",
        "value": "Agent1",
        "find_by": "label"
      }
    },
    {
      "fill": {
        "field_label": "Last Name",
        "value": "Yser1",
        "find_by": "label"
      }
    },
    {
      "fill": {
        "field_label": "Email Address",
        "value": "agentuser1@email.com",
        "find_by": "label"
      }
    },
    {
      "fill": {
        "field_label": "Password",
        "value": "Welcome10",
        "find_by": "label"
      }
    },
    {
      "capture_locators": {
        "checkpoint_name": "form_filled"
      }
    },
    {
      "click": {
        "button_text": "Create",
        "find_by": "button_text",
        "wait_for_navigation": true
      }
    },
    {
      "capture_locators": {
        "checkpoint_name": "after_submission"
      }
    }
  ]
}
```

---

## Step 4: Run the Intelligent Locator Extractor

### Prerequisites
- Python 3.8+
- Playwright installed (already in project)
- Virtual environment activated

### Command
```bash
# Activate virtual environment
source .venv/Scripts/activate  # On Linux/Mac
# OR
.venv\Scripts\Activate.ps1  # On Windows PowerShell

# Run the workflow
python tools/intelligent_locator_extractor.py workflows/your_workflow.json
```

### Expected Output
```
📋 Executing workflow with 9 steps...

--- Step 1 ---
  🔗 Navigating to: https://sauce-demo.myshopify.com/account/register
  ✓ Page loaded: Create Account – Sauce Demo

--- Step 2 ---
  📸 Capturing locators - Checkpoint: 'registration_page_loaded'
  📍 Found 42 interactive elements
  ✓ Captured 42 locators

--- Step 3 ---
  ✏️  Filling 'First Name'
     Found locator: #first_name
  ✓ Filled successfully

... [more steps] ...

✓ Locators saved to: data/snapshots/20260412_120402_locators.json
✓ Total elements analyzed: 87
✓ Grouped by type: ['form_field', 'button', 'link']
✓ Workflow checkpoints: 3
```

---

## Step 3: Run the Intelligent Locator Extractor

### Prerequisites
- Python 3.8+
- Playwright installed (already in project)
- Virtual environment activated

### Command
```bash
# Activate virtual environment
source .venv/Scripts/activate  # On Linux/Mac
# OR
.venv\Scripts\Activate.ps1  # On Windows PowerShell

# Run the workflow
python tools/intelligent_locator_extractor.py workflows/your_workflow.json
```

### Expected Output
```
📋 Executing workflow with 9 steps...

--- Step 1 ---
  🔗 Navigating to: https://sauce-demo.myshopify.com/account/register
  ✓ Page loaded: Create Account – Sauce Demo

--- Step 2 ---
  📸 Capturing locators - Checkpoint: 'registration_page_loaded'
  📍 Found 42 interactive elements
  ✓ Captured 42 locators

--- Step 3 ---
  ✏️  Filling 'First Name'
     Found locator: #first_name
  ✓ Filled successfully

... [more steps] ...

✓ Locators saved to: data/snapshots/20260412_120402_locators.json
✓ Total elements analyzed: 87
✓ Grouped by type: ['form_field', 'button', 'link']
✓ Workflow checkpoints: 3
```

---

## Step 4: (Optional) Generate POM Framework with Generator Module

The **Generator** converts planned test cases to a complete **Playwright Page Object Model** framework:

### Generator Overview
The **Generator** creates:
- `object_repo/*.json` - Locator repositories per page
- `pages/*.py` - Page Object Model classes
- `steps/*.py` - Reusable step functions
- `tests/*.py` - Data-driven parameterized tests
- `conftest.py` - Pytest fixtures

### Run Generator
```bash
python generator/demo.py
```

### Expected Output
```
🚀 GENERATOR DEMO - Canonical Actions to Playwright POM Framework
====================================================

[STEP 1] PARSING TEST CASES
✅ Parsed 3 test cases

[STEP 2] PLANNING TEST CASES
✅ Planned 3 test cases

[STEP 3] GENERATING POM FRAMEWORK
✅ Generated framework:

{
  "summary": {
    "object_repos": 3,
    "page_objects": 3,
    "step_functions": 7,
    "test_files": 3,
    "conftest": 1
  }
}

📁 Generated Files:
================================================================================
object_repo/
  ✓ login_page.json (6 elements)
  ✓ products_page.json (8 elements)
  ✓ checkout_page.json (12 elements)

pages/
  ✓ base_page.py (BasePage class with locator loading)
  ✓ login_page.py (LoginPage class)
  ✓ products_page.py (ProductsPage class)
  ✓ checkout_page.py (CheckoutPage class)

steps/
  ✓ steps.py (Reusable step functions)

tests/
  ✓ test_registration.py
  ✓ test_login.py
  ✓ test_checkout.py

conftest.py (Pytest fixtures)

```

### Generated Framework Structure
```
object_repo/login_page.json:
{
  "page_name": "login_page",
  "url_pattern": "saucedemo.com",
  "elements": {
    "username": {
      "selector": "input[data-test=\"username\"]",
      "type": "input",
      "desc": "Username input"
    },
    "password": {
      "selector": "input[data-test=\"password\"]",
      "type": "input",
      "desc": "Password input"
    },
    "login_button": {
      "selector": "input[data-test=\"login-button\"]",
      "type": "button",
      "desc": "Login submit"
    }
  }
}

pages/login_page.py:
class LoginPage(BasePage):
    async def login(self, username: str, password: str):
        await self.fill('username', username)
        await self.fill('password', password)
        await self.click('login_button')
        await self.page.wait_for_load_state('networkidle')

tests/test_login.py:
@pytest.mark.asyncio
async def test_login_standard_user(page):
    login_page = LoginPage(page)
    await login_page.login('standard_user', 'secret_sauce')
    # assertions...
```

---

## Step 5: (Optional) Validate Generated Framework with Validator Module

The **Validator** performs comprehensive quality checks on generated POM framework:

### Validator Overview
The **Validator** checks:
- **Syntax Validation**: All Python files have valid syntax (AST parsing)
- **Import Validation**: All imports can be resolved
- **JSON Validation**: All repository files are valid JSON
- **Locator Validation**: Selectors follow best practices
- **Code Quality**: Style, naming conventions, structure

### Run Validator
```bash
python validator/demo.py
```

### Expected Output
```
✅ VALIDATOR - Comprehensive Framework Quality Checks
================================================

📊 VALIDATION REPORT
------------------------
Total Checks: 15
Passed: 14 ✅
Failed: 1 ❌
Errors: 1
Warnings: 2

📋 DETAILED RESULTS
------------------------

[✅ PASS] Syntax: login_page.py
   ✓ Valid Python syntax

[✅ PASS] Imports: login_page.py
   ✓ All imports can be resolved

[✅ PASS] JSON Structure: login_page.json
   ✓ Valid JSON structure

[⚠️  WARN] Code Quality: steps.py
   Warnings (1):
      ⚠️  Missing docstring for function 'fill_field'

[❌ FAIL] Locator Quality: products_page.json
   Errors (1):
      ❌ Selector too generic: .title (consider using data-testid)
   Warnings (1):
      ⚠️  Selector uses class name (may be fragile)

Summary:
✅ Framework is production-ready with minor quality improvements suggested
```

### Validation Report File
```
validation_report.json  (detailed validation results)
```

---

## Step 3B: Review Captured Locators

### Output File Location
```
data/snapshots/YYYYMMDD_HHMMSS_locators.json
```

### File Structure
```json
{
  "metadata": {
    "extracted_at": "2026-04-12T12:04:21",
    "url": "https://...",
    "title": "Page Title",
    "total_elements": 87,
    "workflow_steps": 3
  },
  "workflow_checkpoints": [
    {
      "step": 1,
      "checkpoint": "registration_page_loaded",
      "url": "https://...",
      "locators_count": 42
    }
  ],
  "locators_by_type": {
    "form_field": [
      {
        "element_id": "elem_0",
        "tag_name": "input",
        "label": "First Name",
        "attributes": {
          "id": "first_name",
          "name": "customer[first_name]",
          "type": "text"
        },
        "best_locator": "locator(\"#first_name\")",
        "locators": [
          "locator(\"#first_name\")",
          "getByLabel(\"First Name\")",
          "locator(\"[name=\\\"customer[first_name]\\\"]\")"
        ]
      }
    ],
    "button": [...],
    "link": [...]
  }
}
```

---

## Step 5B: Extract Locators for Test Automation

### For Each Form Field

Look in `locators_by_type -> form_field` and get the `best_locator`:

```python
# Example locators
first_name_locator = "locator(\"#first_name\")"
last_name_locator = "locator(\"#last_name\")"
email_locator = "locator(\"#email\")"
password_locator = "locator(\"#password\")"
```

### For Buttons/Links

Look in `locators_by_type -> button` and `locators_by_type -> link`:

```python
# Example locators
create_button_locator = "locator(\"input[type='submit'][value='Create']\")"
login_link_locator = "locator(\"#customer_login_link\")"
```

---

## Step 6B: Create Pytest Test Script

### File Location
```
tests/test_registration.py
```

### Test Script Template
```python
import pytest
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_user_registration():
    """Test: User Registration Flow"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Step 1: Navigate
            await page.goto("https://sauce-demo.myshopify.com/account/register")
            await page.wait_for_load_state("networkidle")
            
            # Step 2: Fill First Name
            await page.fill("#first_name", "Agent1")
            
            # Step 3: Fill Last Name
            await page.fill("#last_name", "Yser1")
            
            # Step 4: Fill Email
            await page.fill("#email", "agentuser1@email.com")
            
            # Step 5: Fill Password
            await page.fill("#password", "Welcome10")
            
            # Step 6: Click Create
            await page.click("input[type='submit'][value='Create']")
            await page.wait_for_timeout(2000)  # Wait for response
            
            # Step 7: Verify
            title = await page.title()
            assert "Create Account" in title or "Success" in title
            
            print("✓ Registration test passed")
            
        finally:
            await browser.close()


# Run test
# Command: pytest tests/test_registration.py -v
```

---

## Step 7B: Run Your Test

### Command
```bash
# Run single test
pytest tests/test_registration.py -v

# Run with headless browser
pytest tests/test_registration.py -v --headless

# Run with screenshot on failure
pytest tests/test_registration.py -v --screenshot=on_failure
```

### Expected Output
```
tests/test_registration.py::test_user_registration PASSED [100%]

===================== 1 passed in 5.23s ======================
✓ Registration test passed
```

---

## Complete Module Commands Reference

### 🔷 Parser Module
**Purpose**: Convert CSV test cases to structured format

```bash
# Run parser demo
python parser/demo.py

# Run in your code:
from parser.parser import TestCaseParser

parser = TestCaseParser("data/testcases.csv")
test_cases = parser.parse()  # Returns: List[Dict]
errors = parser.get_errors()
```

**Input**: CSV file with flexible headers
```csv
Test Case ID,Test Scenario Description,Pre-condition,Test Steps,Test Data,Expected Result
TC001,Login Test,...,...,...,...
```

**Output**: JSON structured format
```json
[
  {
    "id": "TC001",
    "title": "Login Test",
    "precondition": "...",
    "steps": ["Step 1", "Step 2", ...],
    "test_data": {"username": "...", "password": "..."},
    "expected_result": "..."
  }
]
```

---

### 🔷 Planner Module
**Purpose**: Convert structured test cases to canonical action schema

```bash
# Run planner demo
python planner/demo.py

# Run in your code:
from planner.planner import Planner

planner = Planner()
planned_cases = planner.plan_cases(test_cases)  # Returns: List[Dict]
```

**Input**: Parsed test cases from Parser
```json
{
  "id": "TC001",
  "title": "Login Test",
  "steps": ["Navigate to login page", "Enter username: admin", "Click login button"]
}
```

**Output**: Canonical action schema
```json
{
  "id": "TC001",
  "title": "Login Test",
  "actions": [
    {"type": "goto", "url": "https://..."},
    {"type": "fill", "field": "username", "value": "admin"},
    {"type": "click", "target": "login_button"}
  ]
}
```

---

### 🔷 Locator Module (Engine)
**Purpose**: Resolve locators using late-binding strategy pattern

```bash
# Run locator demo (if available)
python locator/demo.py

# Run in your code:
from locator.engine import LocatorEngine
from playwright.sync_api import sync_playwright

engine = LocatorEngine()
with sync_playwright() as p:
    page = p.chromium.launch().new_context().new_page()
    locator = engine.resolve(page, target="login_button")
    locator.click()
```

**Resolution Strategy (Priority Order)**:
1. **Repo Strategy**: Load from `object_repo/*.json`
2. **Snapshot Strategy**: Dynamic discovery using accessibility snapshot
3. **Fallback Strategy**: Last resort fallback patterns

**Output**: Playwright Locator object

---

### 🔷 Generator Module
**Purpose**: Convert planned actions to complete POM framework

```bash
# Run generator demo
python generator/demo.py

# Run in your code:
from generator.generator import Generator

generator = Generator()
result = generator.generate(planned_cases)
# Generates:
# - object_repo/*.json
# - pages/*.py
# - steps/*.py
# - tests/*.py
# - conftest.py
```

**Input**: Planned test cases with canonical actions

**Output Files**:
- `object_repo/page_name.json` - Locator repositories
- `pages/page_name.py` - Page Object Model classes
- `steps/steps.py` - Reusable step functions
- `tests/test_name.py` - Parameterized test files
- `conftest.py` - Pytest fixtures

**Generated Code Example**:
```python
# pages/login_page.py
class LoginPage(BasePage):
    async def login(self, username: str, password: str):
        await self.fill('username', username)
        await self.fill('password', password)
        await self.click('login_button')

# tests/test_login.py
@pytest.mark.asyncio
async def test_login_standard_user(page):
    login_page = LoginPage(page)
    await login_page.login('standard_user', 'secret_sauce')
    assert await page.title() == "Products"
```

---

### 🔷 Validator Module
**Purpose**: Validate generated framework quality

```bash
# Run validator demo
python validator/demo.py

# Run in your code:
from validator.validator import Validator

validator = Validator(base_dir=".")
report = validator.validate_generated_framework()
```

**Validation Checks**:
- ✅ Syntax validation (AST parsing)
- ✅ Import validation (can imports be resolved?)
- ✅ JSON validation (valid structure?)
- ✅ Locator validation (selectors best practices?)
- ✅ Code quality (style, naming, structure?)

**Output**: JSON validation report
```json
{
  "total_checks": 15,
  "passed": 14,
  "failed": 1,
  "total_errors": 1,
  "total_warnings": 2,
  "results": [
    {
      "name": "Syntax: login_page.py",
      "passed": true,
      "errors": [],
      "warnings": []
    }
  ]
}
```

---

## Complete Workflow Checklist

### Before Running
- [ ] Define test case steps
- [ ] Identify all form fields and buttons
- [ ] Get exact label/button text from UI

### Create Workflow JSON
- [ ] File location: `workflows/your_test.json`
- [ ] All steps have correct action names
- [ ] Field labels match UI exactly
- [ ] Button text matches UI exactly
- [ ] Added `capture_locators` at key checkpoints

### Run Extractor
- [ ] Virtual environment activated
- [ ] Run: `python tools/intelligent_locator_extractor.py workflows/your_test.json`
- [ ] Execution completed without errors
- [ ] Output file created in `data/snapshots/`

### Review & Extract
- [ ] Opened JSON output file
- [ ] Found all form field locators
- [ ] Found all button locators
- [ ] Copied locators to test script

### Create Test Script
- [ ] File location: `tests/test_your_name.py`
- [ ] All locators replaced with correct IDs/selectors
- [ ] All input values match test case
- [ ] Navigation and waits configured
- [ ] Assertions added for verification

### Run Test
- [ ] Virtual environment activated
- [ ] Run: `pytest tests/test_your_name.py -v`
- [ ] Test passes with green checkmark
- [ ] Screenshot/logs captured if needed

---

## Troubleshooting

### Issue: Locator Not Found
**Solution:** Check workflow JSON
- Verify field label matches UI exactly (case-sensitive)
- Check for typos in button text
- Try using developer tools (F12) to verify element attributes

### Issue: Element Not Filling
**Solution:** Inspect element type
- Open DevTools (F12)
- Check if element is `<input>`, `<textarea>`, or `<select>`
- Verify it's not hidden or disabled
- Check for wrapper divs that need CSS selectors

### Issue: Navigation Timeout
**Solution:** Adjust wait strategy
- Some pages have CAPTCHA - use `wait_for_navigation: false`
- Reduce timeout to 5 seconds
- Wait for specific element instead: `await page.wait_for_selector("#success_message")`

### Issue: Test Flakiness
**Solution:** Add explicit waits
```python
# Wait for specific element
await page.wait_for_selector("#expected_element")

# Wait for network idle
await page.wait_for_load_state("networkidle")

# Wait fixed time
await page.wait_for_timeout(1000)

# Wait for element visibility
await page.wait_for_selector("button:text('Submit')", state="visible")
```

---

## Advanced: Multiple Test Cases

### Organize Workflows
```
workflows/
  ├── user_registration.json
  ├── user_login.json
  ├── product_search.json
  └── checkout_flow.json
```

### Run All Workflows
```bash
for file in workflows/*.json; do
    echo "Running $file..."
    python tools/intelligent_locator_extractor.py "$file"
done
```

### Run All Tests
```bash
pytest tests/ -v --html=report.html
```

---

## Summary

**Convert Test → Automation using Complete Pipeline:**

### Option 1: CSV → Auto-Generate (5 Commands)
1. ✅ **Create CSV** with test cases
2. ✅ **Parse**: `python parser/demo.py` → structured format
3. ✅ **Plan**: `python planner/demo.py` → canonical actions
4. ✅ **Generate**: `python generator/demo.py` → POM framework
5. ✅ **Validate**: `python validator/demo.py` → quality check
6. ✅ **Run**: `pytest tests/ -v` → execute tests

### Option 2: Manual Workflow (3 Commands)
1. ✅ **Define**: Manually write workflow.json
2. ✅ **Extract**: `python tools/intelligent_locator_extractor.py workflows/test.json` → locators.json
3. ✅ **Write**: Create test script manually
4. ✅ **Run**: `pytest tests/test_name.py -v` → execute test

### Option 3: Hybrid (Recommended - 7 Commands)
1. ✅ **Create CSV** with all test cases
2. ✅ **Parse**: `python parser/demo.py` 
3. ✅ **Plan**: `python planner/demo.py`
4. ✅ **Review**: Check planned_testcases.json for accuracy
5. ✅ **Generate**: `python generator/demo.py`
6. ✅ **Validate**: `python validator/demo.py`
7. ✅ **Run**: `pytest tests/ -v`

**Key Advantages**:
- 🎯 **No manual locator hunting** - Auto-discovered from UI
- 🔍 **Accessibility-aware** - Uses labels, ARIA attributes
- 📊 **Multiple strategies** - 8 fallback locator methods
- 🚀 **Framework-agnostic** - Works with any website
- 🛡️ **Validated output** - Quality checks prevent errors
- 📝 **Framework-generated** - Complete POM structure
- ✅ **Production-ready** - Immediately usable tests

---

## Module Comparison Table

| Module | Input | Output | Purpose | Command |
|--------|-------|--------|---------|---------|
| **Parser** | CSV | JSON (parsed) | Normalize test case structure | `python parser/demo.py` |
| **Planner** | JSON (parsed) | JSON (actions) | Convert to canonical schema | `python planner/demo.py` |
| **Generator** | JSON (actions) | POM framework | Create complete test framework | `python generator/demo.py` |
| **Locator Engine** | Page object | Playwright Locator | Resolve elements at runtime | (Used by generator) |
| **Validator** | Generated files | Report JSON | Quality checks | `python validator/demo.py` |
| **Intelligent Extractor** | Workflow JSON | Locators JSON | Extract locators from live page | `python tools/intelligent_locator_extractor.py` |

---

## File Structure After Complete Pipeline

```
Project0/
├── data/
│   ├── testcases.csv              ← Your test cases
│   ├── parsed_testcases.json      ← Parser output
│   └── planned_testcases.json     ← Planner output
├── object_repo/                   ← Generator output
│   ├── login_page.json
│   ├── products_page.json
│   └── checkout_page.json
├── pages/                         ← Generator output
│   ├── base_page.py
│   ├── login_page.py
│   ├── products_page.py
│   └── checkout_page.py
├── steps/                         ← Generator output
│   └── steps.py
├── tests/                         ← Generator output
│   ├── test_login.py
│   ├── test_products.py
│   └── test_checkout.py
├── conftest.py                    ← Generator output
├── validation_report.json         ← Validator output
└── tools/
    ├── intelligent_locator_extractor.py  ← For workflow approach
    └── enrich_snapshot_with_locators.py
```

---

## Quick Reference

### Workflow JSON Template
```json
{
  "workflow": "test_name",
  "steps": [
    {"navigate": "URL"},
    {"capture_locators": {"checkpoint_name": "name"}},
    {"fill": {"field_label": "Label", "value": "val", "find_by": "label"}},
    {"click": {"button_text": "Text", "find_by": "button_text", "wait_for_navigation": false}},
    {"capture_locators": {"checkpoint_name": "final"}}
  ]
}
```

### Run Commands
```bash
# Extract locators
python tools/intelligent_locator_extractor.py workflows/test.json

# Run tests
pytest tests/test_name.py -v

# Run all tests with report
pytest tests/ -v --html=report.html --self-contained-html
```

---

**Need help?** See [Architecture Guide](Architecture.md) or run with `-v` flag for verbose output.

---

## All Available Commands

### 📊 Data & Parsing
```bash
# View available test data
cat data/testcases.csv
cat data/Source_TestCase.csv

# Parse test cases from CSV
python parser/demo.py

# Output: data/parsed_testcases.json
```

### 📋 Planning & Action Schema
```bash
# Generate canonical action schema from parsed tests
python planner/demo.py

# Output: data/planned_testcases.json
```

### 🏗️ Framework Generation
```bash
# Generate complete POM framework
python generator/demo.py

# Outputs:
#   - object_repo/*.json
#   - pages/*.py
#   - steps/*.py
#   - tests/*.py
#   - conftest.py
```

### 📍 Locator Extraction (Manual Workflow)
```bash
# Extract locators from live page using workflow JSON
python tools/intelligent_locator_extractor.py workflows/your_workflow.json

# Output: data/snapshots/YYYYMMDD_HHMMSS_locators.json
```

### ✅ Validation
```bash
# Validate generated framework quality
python validator/demo.py

# Output: validation_report.json
```

### 🧪 Test Execution
```bash
# Run single test file
pytest tests/test_login.py -v

# Run all tests with HTML report
pytest tests/ -v --html=report.html --self-contained-html

# Run with specific marker
pytest tests/ -v -m "regression"

# Run with coverage
pytest tests/ -v --cov=pages --cov=steps
```

### 📸 Snapshot Capture
```bash
# Capture accessibility snapshot with locators
python tools/enrich_snapshot_with_locators.py https://example.com/page

# Output: data/snapshots/YYYYMMDD_HHMMSS_enriched_snapshot.json
```

---

## Decision Tree: Which Path to Choose?

```
Do you have test cases in CSV?
├─ YES → Use CSV → Parser → Planner → Generator → Validator
│        (Most automated, best for large test sets)
│
├─ NO: Do you have plain text/manual steps?
│    ├─ YES → Create Workflow JSON → Intelligent Locator Extractor
│    │        (Most flexible, manual control over each step)
│    │
│    └─ NO: Do you just want to snapshot a page?
│         └─ YES → Use Snapshot Enricher
│                  (Quick one-time locator capture)

Want hybrid approach?
├─ Create CSV
├─ Run Parser → Planner
├─ Manually review data/planned_testcases.json
├─ Run Generator → Validator
└─ Tests ready to execute
```
