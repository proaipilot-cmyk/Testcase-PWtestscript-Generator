# Project0 - Clean Sync Playwright Test Framework

## Overview

This is a clean, production-ready Playwright test framework using sync APIs. The project is designed with a **single source of truth** - testcases are defined once in CSV and no duplication occurs anywhere in the codebase.

## Key Features

✓ **Single Source of Truth**: All testcases defined in `data/testcases.csv` - each appears exactly ONCE  
✓ **Sync Playwright**: Using synchronous Playwright API (not async)  
✓ **Reusable Steps**: Step functions written once, used across multiple tests  
✓ **Auto-categorization**: Tests automatically organized by type (login, cart, checkout, etc.)  
✓ **Scalable**: Works with any number of testcases  
✓ **Clean Code**: No duplication, no hardcoded test data  

## Project Structure

```
Project0/
├── data/
│   ├── testcases.csv          # Single source of truth (all testcases)
│   └── [other test data]
├── generator/
│   ├── clean_generator.py     # Converts CSV → pytest test file
│   ├── generator.py           # Additional generation utilities
│   └── __init__.py
├── locator/
│   ├── engine.py              # Locator resolution (late binding)
│   ├── __init__.py
│   └── strategies/            # Resolution strategies
├── pages/
│   ├── base_page.py           # Page Object Model base
│   ├── login_page.py          # Login page object
│   ├── products_page.py       # Products page object
│   └── __init__.py
├── steps/
│   ├── steps.py               # Reusable step functions
│   └── __init__.py
├── tests/
│   ├── conftest.py            # Pytest configuration & fixtures
│   ├── test_automation.py     # Generated from testcases.csv
│   └── [other test files]
├── object_repo/
│   ├── login_page.json        # Locators for login page
│   └── products_page.json     # Locators for products page
├── pytest.ini                 # Pytest configuration
└── README.md                  # This file
```

## Getting Started

### Setup

1. **Install dependencies**:
   ```bash
   pip install playwright pytest
   playwright install chromium
   ```

2. **Activate virtual environment** (if using one):
   ```bash
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

### Adding/Modifying Tests

1. **Edit testcases**:
   - All testcases are in `data/testcases.csv`
   - Add new rows with: `id, title, precondition, steps, test_data, expected_result`
   - Example:
     ```csv
     TC_007,New login test,User on login page,"1. Enter user
     2. Enter pass
     3. Click","user: test, pass: 123","Success message"
     ```

2. **Generate tests**:
   ```bash
   python generator/clean_generator.py
   ```
   This creates `tests/test_automation.py` with NO duplication.

3. **Run tests**:
   ```bash
   pytest tests/test_automation.py -v
   ```

### Running Tests

```bash
# Run all tests
pytest tests/test_automation.py -v

# Run specific test
pytest tests/test_automation.py::test_login_scenarios[TC_001] -v

# Run with headful browser (see UI)
# (Edit conftest.py and set headless=False)

# View test collection only
pytest tests/test_automation.py --collect-only
```

## Architecture

### CSV → Test Flow

```
data/testcases.csv
    ↓
    ├─→ Parsed by clean_generator.py
    ├─→ Categorized (login, cart, checkout, etc.)
    ├─→ Each test written ONCE with parametrize
    ↓
tests/test_automation.py (GENERATED)
    ↓
    ├─→ pytest collects tests (NO duplicates)
    ├─→ Executes with Playwright sync API
    ├─→ Uses reusable step functions
    ↓
RESULTS
```

### Testcase Categories

Tests are automatically categorized by type:

| Category | Test IDs | Function |
|----------|----------|----------|
| Login | TC_001-TC_004 | `test_login_scenarios()` |
| Cart | TC_005-TC_006 | `test_cart_scenarios()` |
| Checkout | (if any) | `test_checkout_scenarios()` |
| Product | (if any) | `test_product_scenarios()` |
| Other | (if any) | `test_generic_scenarios()` |

### Step Functions

Steps are defined once in `steps/steps.py` and reused across tests:

- `navigate_to_login(page)` - Go to login page
- `fill_credentials(login_page, user, pwd)` - Enter credentials
- `click_login_button(login_page)` - Click login
- `assert_page_contains_text(page, text)` - Verify text on page
- `assert_error_message(login_page, error)` - Verify error message
- `verify_products_page(page)` - Verify products page loaded

### Locators

Locators are managed in `object_repo/` as JSON files:

- `login_page.json` - Login page selectors
- `products_page.json` - Products page selectors

Late binding strategy: Locators resolved at runtime using `resolve_locator_sync()`.

## Test Counts

Current test count: **6 unique tests**
- Login tests: 4
- Cart tests: 2

To verify:
```bash
pytest tests/test_automation.py --collect-only
```

## No Duplication Guarantee

This framework enforces a single source of truth:

✓ **Testcases**: Defined once in CSV  
✓ **Test code**: Generated once from CSV (no manual duplicates)  
✓ **Locators**: Defined once in JSON per page  
✓ **Steps**: Written once, used multiple times via parametrize  

If you see duplicate testcase IDs, the generator will report it:
```
⚠ WARNING: Duplicate IDs detected!
```

## Contributing

1. **Add new testcase**: Edit `data/testcases.csv`
2. **Generate tests**: Run `python generator/clean_generator.py`
3. **Verify**: `pytest tests/test_automation.py --collect-only`
4. **Run**: `pytest tests/test_automation.py -v`

## Troubleshooting

### Tests not found
```bash
pytest tests/test_automation.py --collect-only
```
If no tests show, regenerate:
```bash
python generator/clean_generator.py
```

### Import errors
Ensure you're in the project root:
```bash
cd c:\myprojects\Project0
python generator/clean_generator.py
```

### Browser issues
Ensure Chromium is installed:
```bash
playwright install chromium
```

## License

See LICENSE file.
