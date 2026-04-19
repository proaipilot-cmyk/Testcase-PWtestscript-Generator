# Module Reference Card

## 📊 Parser Module

**File**: `parser/parser.py`  
**Purpose**: Convert CSV test cases to normalized JSON format

### Usage
```python
from parser.parser import TestCaseParser

parser = TestCaseParser("data/testcases.csv")
test_cases = parser.parse()
errors = parser.get_errors()

for case in test_cases:
    print(case['id'], case['title'])
```

### CLI
```bash
python parser/demo.py
```

### Input CSV Headers (Flexible)
| Standard | Accepted Variations |
|----------|-------------------|
| `id` | test_case_id, testcase_id, tc_id, id |
| `title` | test_scenario_description, description, title |
| `precondition` | pre-condition, precondition, pre_condition |
| `steps` | test_steps, test_steps, steps, actions |
| `test_data` | test_data, testdata, data |
| `expected_result` | expected_result (er), expected_result, er |

### Output Format
```json
[
  {
    "id": "TC001",
    "title": "User Login",
    "precondition": "User on login page",
    "steps": ["Step 1: Navigate...", "Step 2: Enter..."],
    "test_data": {"username": "admin", "password": "pass123"},
    "expected_result": "Dashboard displayed"
  }
]
```

### Key Methods
- `parse()` - Parse CSV/JSON file
- `get_errors()` - Get parsing errors
- `_normalize_headers()` - Map custom headers to standard format
- `_parse_csv()` - Parse CSV format
- `_parse_json()` - Parse JSON format

---

## 📋 Planner Module

**File**: `planner/planner.py`  
**Purpose**: Convert parsed test cases to canonical action schema

### Usage
```python
from planner.planner import Planner

planner = Planner()
planned_cases = planner.plan_cases(test_cases)

for case in planned_cases:
    for action in case['actions']:
        print(f"Type: {action['type']}, Data: {action}")
```

### CLI
```bash
python planner/demo.py
```

### Pattern Matching
The planner recognizes keywords:
- `launch`, `open`, `navigate to` → `goto` action
- `enter` + `username` → `fill_username`
- `enter` + `password` → `fill_password`
- `click` + `login` → `click_login`
- `add to cart`, `remove` → `click_generic`
- `verify`, `check`, `assert` → `assert`
- `error message` → `assert_error`
- `redirected`, `displayed` → `assert_text`
- `scroll` → `scroll`

### Output Format
```json
[
  {
    "id": "TC001",
    "title": "User Login",
    "actions": [
      {"type": "goto", "url": "https://saucedemo.com"},
      {"type": "fill", "field": "username", "value": "admin"},
      {"type": "fill", "field": "password", "value": "secret_sauce"},
      {"type": "click", "target": "login_button"},
      {"type": "assert_text", "text": "Products"}
    ]
  }
]
```

### Canonical Action Types
- `goto` - Navigate to URL
- `fill` - Enter text in field
- `fill_username` - Enter username
- `fill_password` - Enter password
- `click` - Click button/link
- `click_login` - Click login button
- `click_generic` - Generic click
- `select` - Choose dropdown
- `assert` - Verify state
- `assert_text` - Check text presence
- `assert_error` - Check error display
- `scroll` - Scroll page
- `note` - Unrecognized step

### Key Methods
- `plan_cases(test_cases)` - Plan multiple test cases
- `plan_case(test_case)` - Plan single test case
- `_make_action()` - Create action object
- `_infer_field()` - Extract field name from step

---

## 🏗️ Generator Module

**File**: `generator/generator.py`  
**Purpose**: Convert canonical actions to complete Playwright POM framework

### Usage
```python
from generator.generator import Generator

generator = Generator()
result = generator.generate(planned_cases)

print(result['summary'])  # See what was generated
```

### CLI
```bash
python generator/demo.py
```

### Output Files Generated

1. **Object Repository** (`object_repo/*.json`)
```json
{
  "page_name": "login_page",
  "url_pattern": "saucedemo.com",
  "elements": {
    "username": {
      "selector": "input[data-test='username']",
      "type": "input",
      "desc": "Username field"
    }
  }
}
```

2. **Page Objects** (`pages/*.py`)
```python
class LoginPage(BasePage):
    async def login(self, username: str, password: str):
        await self.fill('username', username)
        await self.fill('password', password)
        await self.click('login_button')
```

3. **Step Functions** (`steps/steps.py`)
```python
async def user_navigates_to_login(page):
    await page.goto("https://saucedemo.com")

async def user_enters_credentials(page, username: str, password: str):
    await page.fill("input[data-test='username']", username)
    await page.fill("input[data-test='password']", password)
```

4. **Test Files** (`tests/test_*.py`)
```python
@pytest.mark.asyncio
async def test_user_login(page):
    login_page = LoginPage(page)
    await login_page.login('standard_user', 'secret_sauce')
    assert await page.title() == "Products"
```

5. **Conftest** (`conftest.py`)
```python
@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        yield await p.chromium.launch()
```

### Key Classes
- `ObjectRepositoryGenerator` - Create object_repo/*.json
- `PageObjectGenerator` - Create pages/*.py
- `StepFunctionGenerator` - Create steps/steps.py
- `TestGenerator` - Create tests/*.py
- `ConfTestGenerator` - Create conftest.py

---

## 📍 Locator Engine Module

**File**: `locator/engine.py`  
**Purpose**: Resolve locators at runtime using multiple strategies

### Usage
```python
from locator.engine import LocatorEngine
from playwright.sync_api import sync_playwright

engine = LocatorEngine()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Resolve locator by name
    locator = engine.resolve(page, "login_button")
    locator.click()
```

### Resolution Strategies (Priority)

1. **Repo Strategy** - Load from `object_repo/*.json`
   ```json
   {"login_button": {"selector": "button#login"}}
   ```

2. **Snapshot Strategy** - Dynamic discovery using accessibility snapshot
   - Queries page accessibility tree
   - Matches by role, label, text

3. **Fallback Strategy** - Last resort patterns
   - CSS selectors
   - XPath patterns
   - Text matching

### Key Methods
- `resolve(page, target, context_data)` - Main resolution method
- `_repo_strategy()` - Load from repository
- `_snapshot_strategy()` - Discover dynamically
- `_fallback_strategy()` - Use fallback patterns
- `_find_repo_file()` - Locate correct repo JSON

---

## ✅ Validator Module

**File**: `validator/validator.py`  
**Purpose**: Quality validation of generated framework

### Usage
```python
from validator.validator import Validator

validator = Validator(base_dir=".")
report = validator.validate_generated_framework()

print(f"Passed: {report['passed']}")
print(f"Failed: {report['failed']}")
```

### CLI
```bash
python validator/demo.py
```

### Validation Checks

| Check | Purpose |
|-------|---------|
| **Syntax** | Valid Python syntax (AST parsing) |
| **Imports** | All imports resolvable |
| **JSON** | Valid JSON structure |
| **Locators** | Selector best practices |
| **Code Quality** | Style, naming, documentation |

### Output Report
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

### Key Classes
- `ValidationResult` - Container for check results
- `SyntaxValidator` - Python syntax validation
- `ImportValidator` - Import resolution checking
- `JSONValidator` - JSON structure validation
- `LocatorValidator` - CSS selector validation
- `CodeQualityValidator` - Style/naming checks

---

## 🎯 Intelligent Locator Extractor

**File**: `tools/intelligent_locator_extractor.py`  
**Purpose**: Extract locators from live page using workflow

### Usage
```bash
python tools/intelligent_locator_extractor.py workflows/registration.json
```

### Input (Workflow JSON)
```json
{
  "workflow": "registration",
  "steps": [
    {"navigate": "https://example.com/register"},
    {"fill": {"field_label": "Email", "value": "user@example.com", "find_by": "label"}},
    {"click": {"button_text": "Register", "find_by": "button_text"}},
    {"capture_locators": {"checkpoint_name": "after_register"}}
  ]
}
```

### Output
```json
{
  "metadata": {"extracted_at": "2026-04-12...", "total_elements": 42},
  "workflow_checkpoints": [...],
  "locators_by_type": {
    "form_field": [
      {
        "label": "Email",
        "best_locator": "locator(\"#email\")",
        "locators": ["#email", "[name='email']", ...]
      }
    ]
  }
}
```

### Locator Discovery Strategies (Priority)
1. `data-testid` attributes
2. `id` attributes
3. `aria-label` attributes
4. Role + text (semantic)
5. `name` attributes
6. Placeholder text
7. CSS selectors
8. Text content matching

### Key Methods
- `execute_workflow(workflow_file)` - Execute workflow
- `_find_locator_by_intent()` - Intelligent locator discovery
- `extract_locators()` - Analyze page elements
- `save_locators()` - Export JSON results

---

## Data Flow Diagram

```
CSV File
   ↓
┌─────────────┐
│ PARSER      │ → parsed_testcases.json
└─────────────┘
   ↓
┌─────────────┐
│ PLANNER     │ → planned_testcases.json
└─────────────┘
   ↓
┌─────────────────────────┬──────────────────────────┐
│ GENERATOR               │ LOCATOR EXTRACTOR        │
│ (Auto generate all)     │ (Extract from live page) │
└──────────┬──────────────┴────────┬─────────────────┘
           │                       │
    ┌──────▼──────┐       ┌────────▼────────┐
    │ POM         │       │ Locators JSON   │
    │ Framework   │       │ (Manual write   │
    │             │       │  test)          │
    └──────┬──────┘       │                 │
           │              └────────┬────────┘
           │                       │
    ┌──────▼──────┐        ┌──────▼─────┐
    │ VALIDATOR   │        │ Test File  │
    └──────┬──────┘        └──────┬─────┘
           │                       │
           └───────────┬───────────┘
                       ↓
            ┌──────────────────┐
            │ PYTEST EXECUTION │
            │ pytest tests/ -v │
            └──────────────────┘
```

---

## Environment Setup

### Install Dependencies
```bash
pip install -r requirements.txt
# Contains: playwright, pytest, pytest-asyncio, pytest-html
```

### Virtual Environment
```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate
```

### Install Playwright Browsers
```bash
playwright install chromium
```

---

## Common Commands Cheat Sheet

```bash
# Parse test cases
python parser/demo.py

# Plan actions
python planner/demo.py

# Generate framework
python generator/demo.py

# Validate framework
python validator/demo.py

# Extract locators (manual workflow)
python tools/intelligent_locator_extractor.py workflows/test.json

# Run tests
pytest tests/ -v
pytest tests/test_login.py -v
pytest tests/ -v --html=report.html

# Run specific test
pytest tests/test_login.py::test_user_login -v

# Run with markers
pytest tests/ -v -m "regression"
pytest tests/ -v -m "not slow"
```

---

Updated April 2026
