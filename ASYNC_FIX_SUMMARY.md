# Fix: Coroutine AttributeError - Async/Await Transition

## Problem
Test failure: `AttributeError: 'coroutine' object has no attribute 'fill'`

The error occurred because:
1. `resolve_locator()` in `locator/__init__.py` is an async function (line 45)
2. `LocatorEngine.resolve()` in `locator/engine.py` is async (line 32)
3. Step functions in `steps/steps.py` were calling these async functions WITHOUT `await`
4. Test functions were calling step functions WITHOUT handling async/await

## Root Cause
When an async function is called without `await`, it returns a coroutine object instead of the actual result. The test code tried to call `.fill()` on a coroutine, causing the error.

## Solution Implemented

### 1. Updated `steps/steps.py`
Made all step functions async and added `await` for async calls:
- `navigate_to_login()` → `async def navigate_to_login()`
- `fill_credentials()` → `async def fill_credentials()` with `await resolve_locator()` and `await .fill()`
- `click_login_button()` → `async def click_login_button()` with `await resolve_locator()` and `await .click()`
- `assert_page_contains_text()` → `async def` with `await page.wait_for_function()`
- `assert_error_message()` → `async def` with `await resolve_locator()` and `await .text_content()`
- `verify_products_page()` → `async def` with `await resolve_locator()` and `await .wait_for()`

### 2. Updated `tests/test_automation.py`
Wrapped test bodies in async functions and used `asyncio.run()`:
- `test_login_success()` - wrapped body in `async def _test()` and called `asyncio.run(_test())`
- `test_login_error_scenarios()` - same pattern
- `test_cart_operations()` - same pattern

This approach:
- Keeps test functions synchronous (pytest requires this)
- Properly handles async step functions
- Maintains compatibility with pytest fixtures

## Files Changed
1. `steps/steps.py` - Made all step functions async
2. `tests/test_automation.py` - Added async wrapper pattern to test functions

## Verification
The fix ensures:
- ✅ `resolve_locator()` is properly awaited
- ✅ Locator methods (`.fill()`, `.click()`, etc.) are properly awaited
- ✅ Page methods (`.wait_for_function()`, `.content()`) are properly awaited
- ✅ Tests remain synchronous (pytest compatible)
- ✅ Async execution is properly handled via `asyncio.run()`

## Test Result
Tests should now execute without "AttributeError: 'coroutine' object has no attribute 'fill'" errors.
