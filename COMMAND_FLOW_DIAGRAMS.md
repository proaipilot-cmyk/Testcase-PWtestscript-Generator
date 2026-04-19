# Visual Command Flow & Decision Tree

## 📊 Complete Pipeline Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                  TEST CASE TO AUTOMATION COMMAND FLOW                      │
└────────────────────────────────────────────────────────────────────────────┘

START HERE ↓

Option 1: AUTO-GENERATE from CSV (Fastest)
══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Prepare CSV File                                                    │
│ ────────────────────────────────────────────────────────────────────────────│
│ File: data/testcases.csv                                                    │
│                                                                              │
│ Test Case ID | Test Scenario | Steps | Test Data | Expected Result         │
│ ────────────┼────────────────┼───────┼───────────┼────────────────         │
│ TC001        | Login Test     | ...   | ...       | ...                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 1: PARSE                                                            │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ python parser/demo.py                                                     │
│                                                                              │
│ Input:  data/testcases.csv                                                  │
│ Output: data/parsed_testcases.json                                          │
│                                                                              │
│ ✓ Normalizes CSV headers                                                    │
│ ✓ Validates test case structure                                            │
│ ✓ Extracts id, title, steps, test_data, expected_result                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 2: PLAN                                                             │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ python planner/demo.py                                                    │
│                                                                              │
│ Input:  data/parsed_testcases.json                                          │
│ Output: data/planned_testcases.json                                         │
│                                                                              │
│ ✓ Recognizes patterns (navigate, fill, click, assert)                      │
│ ✓ Converts to canonical actions                                            │
│ ✓ Extracts URLs, field names, button labels                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    ⚠️  REVIEW POINT (Optional)
                    cat data/planned_testcases.json
                    Check actions are correct
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 3: GENERATE                                                         │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ python generator/demo.py                                                  │
│                                                                              │
│ Input:  data/planned_testcases.json                                         │
│ Output: ├─ object_repo/*.json (locator repositories)                       │
│         ├─ pages/*.py (Page Object Model classes)                          │
│         ├─ steps/steps.py (reusable functions)                             │
│         ├─ tests/test_*.py (test files)                                    │
│         └─ conftest.py (pytest fixtures)                                   │
│                                                                              │
│ ✓ Creates complete POM framework                                           │
│ ✓ Generates parameterized tests                                            │
│ ✓ Includes fixtures and utilities                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 4: VALIDATE                                                         │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ python validator/demo.py                                                  │
│                                                                              │
│ Input:  Generated framework files                                           │
│ Output: validation_report.json                                              │
│                                                                              │
│ ✓ Syntax validation (AST parsing)                                           │
│ ✓ Import validation                                                         │
│ ✓ JSON structure validation                                                 │
│ ✓ Code quality checks                                                       │
│ ✓ Selector best practices                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    ✅ VALIDATION PASSED?
                    ├─ YES → Continue to Step 5
                    └─ NO → Review errors and fix manually
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 5: RUN TESTS                                                        │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ pytest tests/ -v                                                          │
│ $ pytest tests/ -v --html=report.html                                       │
│                                                                              │
│ Output: Test results + HTML report                                          │
│                                                                              │
│ ✓ All tests pass                                                            │
│ ✓ HTML report generated                                                     │
│ ✓ Logs available in stdout                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                            ✅ SUCCESS!


Option 2: MANUAL WORKFLOW (Flexible)
══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Create Workflow JSON                                                │
│ ────────────────────────────────────────────────────────────────────────────│
│ File: workflows/your_test.json                                              │
│                                                                              │
│ {                                                                            │
│   "workflow": "registration_flow",                                          │
│   "steps": [                                                                │
│     {"navigate": "https://example.com/register"},                          │
│     {"fill": {"field_label": "Email", "value": "user@email.com"}},        │
│     {"click": {"button_text": "Register", "find_by": "button_text"}},     │
│     {"capture_locators": {"checkpoint_name": "after_register"}}            │
│   ]                                                                         │
│ }                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 1: EXTRACT LOCATORS                                                 │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ python tools/intelligent_locator_extractor.py workflows/your_test.json   │
│                                                                              │
│ Input:  workflows/your_test.json                                            │
│ Output: data/snapshots/YYYYMMDD_HHMMSS_locators.json                       │
│                                                                              │
│ ✓ Executes workflow on live page                                            │
│ ✓ Discovers locators at each step                                           │
│ ✓ Captures multiple strategies per element                                  │
│ ✓ Groups by element type                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: Create Test Script                                                  │
│ ────────────────────────────────────────────────────────────────────────────│
│ File: tests/test_your_name.py                                               │
│                                                                              │
│ import pytest                                                               │
│ from playwright.sync_api import sync_playwright                            │
│                                                                              │
│ def test_registration():                                                    │
│     with sync_playwright() as p:                                            │
│         page = p.chromium.launch().new_context().new_page()               │
│         page.goto("https://example.com/register")                          │
│         page.fill("#email", "user@email.com")  # from extracted locators  │
│         page.click("button:text('Register')")                              │
│         assert page.title() == "Success"                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command 2: RUN TEST                                                         │
│ ────────────────────────────────────────────────────────────────────────────│
│ $ pytest tests/test_your_name.py -v                                         │
│                                                                              │
│ Output: Test results                                                        │
│                                                                              │
│ ✓ Test passes                                                               │
│ ✓ All assertions successful                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                            ✅ SUCCESS!


Option 3: HYBRID (Recommended)
══════════════════════════════════════════════════════════════════════════════

┌────────────────────────────────────────────────────────────────────────────┐
│ Combine benefits of Option 1 + Option 2                                    │
├────────────────────────────────────────────────────────────────────────────┤
│ 1. Auto-generate from CSV (Parser + Planner)                               │
│ 2. Manual review of planned actions                                        │
│ 3. Auto-generate framework (Generator)                                     │
│ 4. Validate quality (Validator)                                            │
│ 5. Fine-tune if needed (manual edits)                                      │
│ 6. Run tests (Pytest)                                                      │
│                                                                             │
│ ✓ Best of both worlds                                                      │
│ ✓ Automation saves time                                                    │
│ ✓ Manual review catches issues                                             │
│ ✓ Quality assurance built in                                               │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Decision Tree

```
START: You have test cases to automate

    Are they in a spreadsheet/CSV?
    ├─ YES ──→ Use Option 1: CSV → Auto-Generate
    │          (Commands: parser → planner → generator → validator → pytest)
    │          Time: 15 min for 10 tests
    │
    └─ NO  ──→ Do you have detailed step descriptions?
               ├─ YES ──→ Create Workflow JSON → Option 2
               │          (Commands: create JSON → locator extractor → write test → pytest)
               │          Time: 10 min per workflow
               │
               └─ NO  ──→ Just exploring page?
                          Use Snapshot Enricher
                          (Command: python tools/enrich_snapshot_with_locators.py)
                          Time: 2 min

    Want to review before generating?
    ├─ YES ──→ Use Option 3: Hybrid
    │          (Run parser + planner, review, then generate)
    │
    └─ NO  ──→ Use Option 1: Full Auto
               (All steps automated)

    Need to customize framework?
    ├─ YES ──→ Generate → Validate → Manual Edit
    │
    └─ NO  ──→ Use as-is after generation
```

---

## 📋 Command Reference Matrix

| Goal | Command | Input | Output |
|------|---------|-------|--------|
| **Parse CSV** | `python parser/demo.py` | testcases.csv | parsed_testcases.json |
| **Plan Actions** | `python planner/demo.py` | parsed_testcases.json | planned_testcases.json |
| **Generate Framework** | `python generator/demo.py` | planned_testcases.json | object_repo/, pages/, steps/, tests/, conftest.py |
| **Validate Quality** | `python validator/demo.py` | Framework files | validation_report.json |
| **Extract Locators** | `python tools/intelligent_locator_extractor.py workflows/test.json` | workflow.json | snapshots/locators.json |
| **Enrich Snapshot** | `python tools/enrich_snapshot_with_locators.py URL` | URL | enriched_snapshot.json |
| **Run Tests** | `pytest tests/ -v` | Test files | Test results |
| **Run with Report** | `pytest tests/ -v --html=report.html` | Test files | Test results + HTML report |

---

## ⏱️ Time Estimates

| Scenario | Time | Steps |
|----------|------|-------|
| **Auto-Generate 1 test** | 2 min | CSV → Parse → Plan → Generate → Validate |
| **Auto-Generate 10 tests** | 15 min | CSV → Parse → Plan → Generate → Validate |
| **Auto-Generate 100 tests** | 45 min | CSV → Parse → Plan → Generate → Validate |
| **Extract 1 workflow** | 5 min | Workflow JSON → Extract → Review |
| **Customize framework** | 30 min | Generate → Edit → Validate |
| **Debug & fix test** | 10 min | Run → Fix → Run |

---

## 🚀 Fastest Path

```
FASTEST AUTOMATION IN 3 COMMANDS:

1. Create data/testcases.csv with tests

2. Run pipeline (combine all):
   python parser/demo.py && \
   python planner/demo.py && \
   python generator/demo.py && \
   python validator/demo.py

3. Execute tests:
   pytest tests/ -v

Total Time: 5 minutes for complete framework + tests
```

---

## 🔄 Most Flexible Path

```
MOST FLEXIBLE IN 4 STEPS:

1. Create workflows/my_test.json
   (Define exactly what you want to test)

2. Run extractor:
   python tools/intelligent_locator_extractor.py workflows/my_test.json

3. Write test script (manual):
   tests/test_my_test.py
   (Use extracted locators)

4. Run:
   pytest tests/test_my_test.py -v

Total Time: 10 minutes, full control
```

---

## 📊 File Dependencies

```
testcases.csv
    │
    ├─→ parser/demo.py
    │       │
    │       ├─→ parsed_testcases.json
    │               │
    │               └─→ planner/demo.py
    │                       │
    │                       ├─→ planned_testcases.json
    │                       │
    │                       ├─→ generator/demo.py
    │                       │   │
    │                       │   ├─→ object_repo/*.json
    │                       │   ├─→ pages/*.py
    │                       │   ├─→ steps/steps.py
    │                       │   ├─→ tests/test_*.py
    │                       │   └─→ conftest.py
    │                       │       │
    │                       │       └─→ validator/demo.py
    │                       │           │
    │                       │           └─→ validation_report.json
    │                       │
    │                       └─→ Tests Ready
    │                           │
    │                           └─→ pytest
    │                               │
    │                               └─→ Results ✅
    │
    └─→ (Alternative Path) workflows/test.json
            │
            └─→ intelligent_locator_extractor.py
                    │
                    ├─→ snapshots/locators.json
                    │
                    └─→ Manual test/results ✅
```

---

## 💾 Generated File Structure

```
Project0/
│
├── Input Files
│   ├── data/testcases.csv ────────────────────── Your test cases
│   └── workflows/test.json ───────────────────── Your workflow (alternative)
│
├── Intermediate Files (can delete after framework generated)
│   ├── data/parsed_testcases.json ────────────── Parser output
│   └── data/planned_testcases.json ──────────── Planner output
│
├── Generated Framework (KEEP - used by tests)
│   ├── object_repo/
│   │   ├── login_page.json
│   │   ├── products_page.json
│   │   └── checkout_page.json
│   │
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   ├── products_page.py
│   │   └── checkout_page.py
│   │
│   ├── steps/
│   │   └── steps.py
│   │
│   ├── tests/
│   │   ├── test_login.py
│   │   ├── test_products.py
│   │   └── test_checkout.py
│   │
│   └── conftest.py
│
├── Output Files
│   ├── validation_report.json ─────────────────── Quality report
│   ├── data/snapshots/locators.json ──────────── Extracted locators
│   └── pytest results ────────────────────────── Test execution results
│
└── Documentation
    ├── LOCATOR_AUTOMATION_GUIDE.md ────────── Complete guide
    ├── QUICK_START.md ────────────────────── Quick reference
    ├── MODULE_REFERENCE.md ──────────────── Module details
    └── This file ──────────────────────────── Flow diagrams
```

---

**Created**: April 12, 2026  
**Status**: Ready to use ✅
