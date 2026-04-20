# Quick Start Guide

## Project0 - Sync Playwright Test Framework

### TL;DR

```bash
# Add testcases to CSV
edit data/testcases.csv

# Generate clean tests (no duplication)
python generator/clean_generator.py

# Verify no duplicates
python verify_no_duplication.py

# Run tests
pytest tests/test_automation.py -v
```

### Key Facts

✓ **6 unique testcases** - each appears exactly ONCE  
✓ **Sync Playwright** - simple synchronous API  
✓ **Single Source of Truth** - `data/testcases.csv` only  
✓ **Auto-categorized** - login, cart, checkout, etc.  
✓ **Production-ready** - no duplication guaranteed  

### File Locations

| File | Purpose |
|------|---------|
| `data/testcases.csv` | All testcases (source of truth) |
| `generator/clean_generator.py` | CSV → pytest converter |
| `tests/test_automation.py` | Generated test file (auto-generated) |
| `tests/conftest.py` | Pytest fixtures |
| `steps/steps.py` | Reusable step functions |
| `pages/` | Page Object Model |
| `object_repo/` | Locator definitions |

### Test Categories

```
4 Login tests      (TC_001-TC_004)  → test_login_scenarios()
2 Cart tests       (TC_005-TC_006)  → test_cart_scenarios()
```

### Never Do This

❌ Manually edit `tests/test_automation.py`  
❌ Add test IDs manually  
❌ Duplicate testcases in CSV  

### Always Do This

✅ Edit `data/testcases.csv` to add/modify tests  
✅ Run `python generator/clean_generator.py`  
✅ Verify with `python verify_no_duplication.py`  
✅ Run tests with `pytest tests/test_automation.py -v`  

### Test Counts

Current: **6 tests** (NO duplicates)

To verify:
```bash
pytest tests/test_automation.py --collect-only
# Output should show exactly 6 tests collected
```

### Adding New Tests

1. Edit `data/testcases.csv` - add new row:
   ```csv
   TC_007,Test name,Precondition,"Steps","Data","Expected"
   ```

2. Generate: `python generator/clean_generator.py`

3. Verify: `python verify_no_duplication.py`

4. Run: `pytest tests/test_automation.py -v`

### Structure

```
Project0/
├── data/testcases.csv           ← EDIT THIS for tests
├── generator/clean_generator.py ← RUN THIS to generate
├── tests/
│   ├── test_automation.py      ← GENERATED (don't edit)
│   └── conftest.py             ← Fixtures
├── steps/steps.py              ← Reusable functions
├── pages/                       ← Page Objects
├── object_repo/                ← Locators
└── README.md                   ← Full documentation
```

### Verification

```bash
# Verify framework integrity
python verify_no_duplication.py

# Expected output:
# ✓ CSV has 6 unique testcases (no duplicates)
# ✓ Test file has 6 unique test IDs (no duplicates)
# ✓ Pytest collected 6 tests
# ✓ ALL VERIFICATIONS PASSED - NO DUPLICATION DETECTED
```

### Troubleshooting

**Tests not found?**
```bash
python generator/clean_generator.py
pytest tests/test_automation.py --collect-only
```

**Import errors?**
```bash
cd c:\myprojects\Project0
pip install playwright pytest
```

**Browser not installed?**
```bash
playwright install chromium
```

### Summary

| Aspect | Status |
|--------|--------|
| Duplication | ✓ ZERO |
| Single Source of Truth | ✓ YES (CSV) |
| Test Organization | ✓ AUTO (categories) |
| Scalability | ✓ UNLIMITED |
| Maintenance | ✓ EASY (CSV only) |
| Framework | ✓ PRODUCTION READY |

---

**Need help?** See `README.md` for detailed documentation.
