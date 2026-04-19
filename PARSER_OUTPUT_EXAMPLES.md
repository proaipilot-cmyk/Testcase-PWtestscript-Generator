# Parser Output Examples

## Overview
The parser module (`parser/parser.py`) converts raw CSV test cases into structured, machine-readable JSON format ready for downstream processing by the planner module.

---

## Input Format (Raw CSV)

```csv
id,title,precondition,steps,test_data,expected_result
TC_001,Verify successful login with valid credentials,User is on the login page,"1. Enter username
2. Enter password
3. Click Login button","username: standard_user, password: secret_sauce","User is redirected to Products page, inventory items are displayed"
```

---

## Output Format (Structured JSON)

### Example 1: Login Test Case
```json
{
  "id": "TC_001",
  "title": "Verify successful login with valid credentials",
  "precondition": "User is on the login page",
  "steps": [
    "Enter username",
    "Enter password",
    "Click Login button"
  ],
  "test_data": {
    "username": "standard_user",
    "password": "secret_sauce"
  },
  "expected_result": "User is redirected to Products page, inventory items are displayed",
  "row_number": 2
}
```

### Example 2: Locked User Test Case
```json
{
  "id": "TC_002",
  "title": "Verify login denied for locked out user",
  "precondition": "User is on the login page",
  "steps": [
    "Enter username for locked out user",
    "Enter password",
    "Click Login button"
  ],
  "test_data": {
    "username": "locked_out_user",
    "password": "secret_sauce"
  },
  "expected_result": "Error message displayed: Sorry, this user has been locked out.",
  "row_number": 3
}
```

### Example 3: Add to Cart Test Case
```json
{
  "id": "TC_005",
  "title": "Verify user can add item to cart",
  "precondition": "User is logged in and on Products page",
  "steps": [
    "Click on Add to Cart button for Backpack",
    "Verify item is added"
  ],
  "test_data": {
    "item": "Backpack",
    "quantity": "1"
  },
  "expected_result": "Item is added to cart, cart count increments to 1",
  "row_number": 6
}
```

---

## Key Features of Parser

✅ **Input Flexibility**
- Handles CSV format (easily extensible to JSON)
- Supports multi-line steps
- Parses key:value test data

✅ **Data Normalization**
- Removes numbering from steps (1., 2., etc.)
- Strips whitespace
- Converts comma/newline-separated data

✅ **Error Handling**
- Validates required fields (id, title, steps)
- Tracks parsing errors per row
- Reports missing columns

✅ **Output Structure**
- Clean, predictable JSON format
- Includes row number for tracing
- Ready for planner module consumption

---

## Parser Usage

### Basic Usage
```python
from parser.parser import TestCaseParser

# Initialize parser
parser = TestCaseParser('data/testcases.csv')

# Parse all test cases
test_cases = parser.parse()

# Get errors (if any)
errors = parser.get_errors()

# Output as JSON
parser.to_json('data/parsed_testcases.json')
```

### Convenience Function
```python
from parser.parser import parse_test_cases

cases, errors = parse_test_cases('data/testcases.csv')
```

---

## Sample Data Summary

Currently 6 test cases in `data/testcases.csv`:

| ID | Title | Steps | Status |
|-----|-------|-------|--------|
| TC_001 | Verify successful login | 3 | ✅ Parsed |
| TC_002 | Verify login denied (locked) | 3 | ✅ Parsed |
| TC_003 | Verify login fails (invalid username) | 3 | ✅ Parsed |
| TC_004 | Verify login fails (invalid password) | 3 | ✅ Parsed |
| TC_005 | Verify add item to cart | 2 | ✅ Parsed |
| TC_006 | Verify remove item from cart | 2 | ✅ Parsed |

---

## Integration with Pipeline

The parser output is designed to feed into the **planner** module:

```
Parser Output (JSON)
        ↓
Planner (Converts steps to actions)
        ↓
Locator Engine (Maps to UI elements)
        ↓
Generator (Creates Playwright code)
```

---

## Parser Implementation Details

### File: `parser/parser.py`

**Main Class: `TestCaseParser`**
- `__init__(file_path)` - Initialize with file path
- `parse()` - Main parsing method
- `_parse_csv()` - CSV-specific parsing
- `_parse_json()` - JSON-specific parsing
- `_normalize_test_case()` - Standardize test case structure
- `_parse_steps()` - Extract and clean steps
- `_parse_test_data()` - Parse key:value data
- `to_json()` - Export to JSON format

**Error Handling:**
- FileNotFoundError if file doesn't exist
- ValueError for missing required columns or empty fields
- Tracks row-level errors without stopping parsing

---

## Next Steps

After parser approval, the next modules to develop:

1. **Planner** - Convert parsed steps into actionable commands
2. **Locator Engine** - Map UI elements to selectors
3. **Generator** - Create Playwright Python scripts
