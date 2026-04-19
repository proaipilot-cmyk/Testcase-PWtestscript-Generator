# Testcase-Agnostic Framework Design

## Key Principle

The framework makes NO assumptions about specific test case contents. Instead, it:

1. **Extracts actual data** from test cases (field names, values, expected results)
2. **Classifies dynamically** based on what fields are present
3. **Generates appropriately** based on classification

## How It's Testcase-Agnostic

### 1. Field-Based Classification (NOT Hardcoded)

```python
# INSTEAD OF: "Is this a login test?" (hardcoded list of keywords)
# WE USE: "What fields are used in this test?"

fields_used = set()
for action in actions:
    if action.get('type') == 'fill':
        field = action.get('field', '').lower()
        fields_used.add(field)

is_login_context = 'username' in fields_used or 'login' in title
```

**Why this works for ANY test case**:
- If test case uses username/password fields → must be login scenario
- If test case uses email/card_number fields → not a login scenario
- No assumptions about what scenarios exist

### 2. Dynamic Test Data Extraction

```python
def _extract_test_data(self, planned_case: Dict[str, Any]) -> Dict[str, Any]:
    """Extract credentials and assertions from planned case."""
    expected = planned_case.get('expected_result', '')
    
    # Extract from actions - whatever fields are present
    actions = planned_case.get('actions', [])
    username = ''
    password = ''
    for action in actions:
        if action.get('type') == 'fill':
            field = action.get('field', '').lower()
            value = action.get('value', '')
            if field == 'username':
                username = value
            elif field == 'password':
                password = value
    
    # Fallback to test_data if present (supports multiple CSV formats)
    test_data = planned_case.get('test_data', {})
    if not username and 'username' in test_data:
        username = test_data['username']
    if not password and 'password' in test_data:
        password = test_data['password']
    
    return {
        'tc_id': planned_case.get('id', 'UNKNOWN'),
        'username': username,
        'password': password,
        'expected_result': expected,
    }
```

**Why this works for ANY test case format**:
- Looks in `actions` (structured format from planner)
- Falls back to `test_data` (flexible CSV format)
- Returns consistent dict regardless of source format

### 3. CSV Format Independence

The framework supports MULTIPLE CSV formats:

#### Format A: Structured Test Data Column
```csv
id, title, steps, test_data
TC_001, Login test, "1. Enter username 2. Enter password", "username: standard_user, password: secret_sauce"
```

#### Format B: Inline Steps with Data
```csv
id, title, steps
TC_001, Login test, "1. Enter Username: standard_user 2. Enter Password: secret_sauce"
```

Both work because:
1. **Parser** normalizes headers flexibly
2. **Planner** extracts fields from steps (inline: "Username: value") OR from test_data column
3. **Generator** accepts fields from either source

### 4. Scenario-Independent Clustering

```python
# CLASSIFIER: Doesn't assume what scenarios exist
clusters = {}
for case in planned_cases:
    # Determine scenario based on ACTUAL CONTENT
    is_login_context = 'username' in fields_used or 'login' in title
    
    if is_login_context:
        if is_success:
            scenario = 'login_success'
        elif is_error:
            scenario = 'login_errors'
        else:
            scenario = 'other'
    else:
        scenario = 'other'
```

**Why this is testcase-agnostic**:
- Doesn't have a list of expected scenarios
- Dynamically determines based on test case properties
- Handles unexpected scenarios gracefully (→ 'other')

## Comparison: Hardcoded vs. Testcase-Agnostic

### ❌ Hardcoded Approach (OLD)
```python
SCENARIO_KEYWORDS = {
    'login_success': ['products', 'inventory', 'logged in'],
    'login_errors': ['error', 'locked', 'do not match'],
    'cart': ['cart', 'add to cart'],
}

# Problem: Any new scenario not in the list fails
# Problem: Misclassification based on keywords alone
# Problem: Can't handle multi-word scenarios
```

### ✅ Testcase-Agnostic Approach (NEW)
```python
# No predefined list!
# Classification logic:
1. Extract WHAT data is used (fields)
2. Determine CONTEXT (login vs. other)
3. Classify based on CONTEXT + EXPECTED RESULT
4. Handle unknowns gracefully

# Benefit: Works with ANY test case
# Benefit: No misclassification due to keywords
# Benefit: Extensible without changes
```

## Real-World Example

### Test Case 1: Login Error (Works ✓)
```json
{
  "id": "TC_002",
  "title": "Login with invalid username",
  "actions": [
    {"type": "fill", "field": "username", "value": "invalid"},
    {"type": "fill", "field": "password", "value": "secret"}
  ],
  "expected_result": "Error message displayed"
}
```
- **Fields extracted**: {username, password}
- **Context**: `'username' in fields` → is_login_context = true
- **Classification**: 'login_errors'
- **Test generated**: Runs on login page ✓

### Test Case 2: Account Change (Works ✓)
```json
{
  "id": "ACCOUNT_TC_009",
  "title": "Change email requires current password",
  "actions": [
    {"type": "fill", "field": "email", "value": ""},
    {"type": "fill", "field": "password", "value": ""}
  ],
  "expected_result": "Error: Current password is incorrect"
}
```
- **Fields extracted**: {email, password}
- **Context**: `'username' not in fields` → is_login_context = false
- **Classification**: 'other'
- **Test generated**: Skipped with comment ✓

### Test Case 3: Payment Processing (Works ✓)
```json
{
  "id": "PAYMENT_TC_001",
  "title": "Process payment with valid card",
  "actions": [
    {"type": "fill", "field": "card_number", "value": "4242424242424242"},
    {"type": "fill", "field": "cvv", "value": "123"}
  ],
  "expected_result": "Payment authorized"
}
```
- **Fields extracted**: {card_number, cvv}
- **Context**: `'username' not in fields` → is_login_context = false
- **Classification**: 'other'
- **Test generated**: Skipped with comment ✓

## Extensibility

To add support for new scenarios:

### Step 1: Identify a new scenario
```json
{"id": "SEARCH_TC_001", "actions": [{"field": "search_query"}]}
```

### Step 2: NO CHANGES NEEDED ✓
The classifier will:
1. Detect `'username' not in fields` → not login
2. Classify as 'other'
3. Handle gracefully

### Step 3: When ready to implement
1. Create SearchPage generator
2. Add new scenario handler in `_generate_parameterized_test`
3. Add conditional check: `if 'search_query' in fields_used`
4. Route to new handler

No changes to core logic needed!

## Summary

The framework is testcase-agnostic because:

✓ It extracts data dynamically from test cases
✓ It classifies based on actual fields present, not assumptions
✓ It supports multiple CSV formats
✓ It handles unknown scenarios gracefully
✓ It's extensible without breaking existing code

Any new test case format or scenario will be:
- Correctly parsed (flexible header parsing)
- Correctly planned (field extraction from steps)
- Correctly classified (based on fields present)
- Gracefully handled (unknown scenarios → 'other')
