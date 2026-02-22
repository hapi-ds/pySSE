# Playwright Non-Normal Tab Selector Fix - Bugfix Design

## Overview

The Playwright tests in `tests/test_ui_playwright_non_normal.py` fail because the tab selector searches for exact text "Non-Normal Distribution" but the actual Streamlit tab button displays "📊 Non-Normal Distribution" with an emoji prefix. This is a simple selector mismatch issue. The fix involves updating the selector to match the actual button text, either by including the emoji or using a partial text match. This is a low-risk fix that only affects test code, not application code.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when tests attempt to locate the Non-Normal Distribution tab using a selector that doesn't match the emoji prefix
- **Property (P)**: The desired behavior when tests run - the selector should successfully locate and click the tab button with text "📊 Non-Normal Distribution"
- **Preservation**: Existing test behavior for other tabs and all other passing tests that must remain unchanged by the fix
- **page.locator()**: Playwright method that creates a selector to find elements in the DOM
- **:has-text()**: Playwright pseudo-selector that matches elements containing specific text (exact match by default)
- **Tab Navigation**: The process of clicking a tab button to switch between different sections of the Streamlit app

## Bug Details

### Fault Condition

The bug manifests when any test in `tests/test_ui_playwright_non_normal.py` attempts to click the Non-Normal Distribution tab. The selector `page.locator("button:has-text('Non-Normal Distribution')").first.click()` fails to find the element because it searches for exact text "Non-Normal Distribution" but the actual button text is "📊 Non-Normal Distribution" with an emoji prefix.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type PlaywrightTestExecution
  OUTPUT: boolean
  
  RETURN input.testFile == "tests/test_ui_playwright_non_normal.py"
         AND input.selectorText == "Non-Normal Distribution"
         AND input.actualButtonText == "📊 Non-Normal Distribution"
         AND NOT input.selectorMatchesButton
END FUNCTION
```

### Examples

- **Test: test_non_normal_tab_renders** - Attempts to click tab with selector `button:has-text('Non-Normal Distribution')` but button text is "📊 Non-Normal Distribution", causing selector to fail and test to fail
- **Test: test_non_normal_outlier_detection** - Same selector mismatch prevents navigation to tab, test fails before reaching outlier detection logic
- **Test: test_non_normal_normality_tests** - Same selector mismatch prevents navigation to tab, test fails before reaching normality test logic
- **Test: test_non_normal_transformation** - Same selector mismatch prevents navigation to tab, test fails before reaching transformation logic
- **Property tests** - Both property-based tests (test_property_data_input_interaction, test_property_dropdown_selection) fail due to same selector mismatch

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Tests for other tabs (Normal Distribution, Property-Based Testing, etc.) must continue to work with their existing selectors
- All other passing tests in the test suite must continue to pass without regression
- The Streamlit app tab button must continue to display "📊 Non-Normal Distribution" with the emoji prefix

**Scope:**
All test selectors that do NOT target the Non-Normal Distribution tab should be completely unaffected by this fix. This includes:
- Selectors for other tab buttons
- Selectors for UI elements within tabs (buttons, inputs, headings, etc.)
- All other test files and their selectors

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear:

1. **Selector Text Mismatch**: The test selector uses exact text "Non-Normal Distribution" but the actual button text includes an emoji prefix "📊 Non-Normal Distribution"
   - Playwright's `:has-text()` pseudo-selector performs exact text matching by default
   - The emoji character is part of the button's text content in the DOM
   - The selector fails to match because "Non-Normal Distribution" ≠ "📊 Non-Normal Distribution"

2. **Inconsistent Tab Naming**: Other tabs in the app also use emoji prefixes (🔢, 📏, ⏱️) but this is the first test file targeting a tab with an emoji, exposing the pattern

## Correctness Properties

Property 1: Fault Condition - Tab Selector Matches Button Text

_For any_ test execution in `tests/test_ui_playwright_non_normal.py` that attempts to navigate to the Non-Normal Distribution tab, the selector SHALL successfully locate the button with text "📊 Non-Normal Distribution" and click it, allowing the test to proceed with its assertions.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Other Tab Selectors Unchanged

_For any_ test execution that targets tabs other than the Non-Normal Distribution tab (Normal Distribution, Property-Based Testing, etc.), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing tab navigation functionality.

**Validates: Requirements 3.1, 3.2, 3.3**

## Fix Implementation

### Changes Required

The root cause is confirmed - this is a simple selector text mismatch.

**File**: `tests/test_ui_playwright_non_normal.py`

**Function**: All test functions that navigate to the Non-Normal Distribution tab

**Specific Changes**:
1. **Update Tab Selector**: Change all occurrences of `page.locator("button:has-text('Non-Normal Distribution')").first.click()` to include the emoji prefix
   - Option A: Use exact text with emoji: `page.locator("button:has-text('📊 Non-Normal Distribution')").first.click()`
   - Option B: Use partial text match: `page.get_by_role("button", name="Non-Normal Distribution").click()` (Playwright's `get_by_role` with `name` parameter does substring matching)
   - Recommended: Option A for consistency with other selectors in the file

2. **Affected Test Functions**: Update the selector in these 7 test functions:
   - `test_non_normal_tab_renders`
   - `test_non_normal_outlier_detection`
   - `test_non_normal_normality_tests`
   - `test_non_normal_transformation`
   - `test_property_data_input_interaction`
   - `test_property_dropdown_selection`

3. **No Application Code Changes**: The Streamlit app code in `src/sample_size_estimator/app.py` should NOT be changed - the tab button correctly displays "📊 Non-Normal Distribution"

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, confirm the bug exists by running tests on unfixed code and observing the selector failure, then verify the fix works correctly and preserves existing behavior for other tests.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm the root cause analysis that the selector text mismatch is the issue.

**Test Plan**: Run the existing tests in `tests/test_ui_playwright_non_normal.py` on the UNFIXED code to observe failures. Inspect the Playwright error messages to confirm the selector cannot find the button element.

**Test Cases**:
1. **Run test_non_normal_tab_renders**: Observe that selector `button:has-text('Non-Normal Distribution')` fails to find element (will fail on unfixed code)
2. **Inspect DOM**: Use Playwright inspector or browser DevTools to confirm button text is "📊 Non-Normal Distribution" (will confirm root cause)
3. **Run all 7 tests**: Observe that all tests fail at the tab navigation step with same selector error (will fail on unfixed code)
4. **Check other tab tests**: Run tests for other tabs to confirm they work correctly (should pass, confirming issue is specific to this selector)

**Expected Counterexamples**:
- Playwright error: "Timeout 30000ms exceeded" or "Element not found" for selector `button:has-text('Non-Normal Distribution')`
- Root cause confirmed: Button text includes emoji prefix "📊" that selector doesn't match

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds (tests navigating to Non-Normal Distribution tab), the fixed selector successfully locates and clicks the button.

**Pseudocode:**
```
FOR ALL test IN tests_targeting_non_normal_tab DO
  result := test.run_with_fixed_selector()
  ASSERT result.tab_navigation_successful
  ASSERT result.test_proceeds_to_assertions
END FOR
```

**Test Plan**: After updating the selector to include the emoji, run all 7 tests in `tests/test_ui_playwright_non_normal.py` and verify they successfully navigate to the tab and execute their test logic.

**Test Cases**:
1. **test_non_normal_tab_renders**: Verify tab navigation succeeds and heading is visible
2. **test_non_normal_outlier_detection**: Verify tab navigation succeeds and outlier detection works
3. **test_non_normal_normality_tests**: Verify tab navigation succeeds and normality tests work
4. **test_non_normal_transformation**: Verify tab navigation succeeds and transformation works
5. **test_property_data_input_interaction**: Verify tab navigation succeeds and data input property holds
6. **test_property_dropdown_selection**: Verify tab navigation succeeds and dropdown selection property holds

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold (tests for other tabs, other test files), the fixed code produces the same result as the original code.

**Pseudocode:**
```
FOR ALL test WHERE NOT test.targets_non_normal_tab DO
  ASSERT test.run_with_fix() = test.run_without_fix()
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Run the full test suite (excluding the 7 Non-Normal tab tests) on both unfixed and fixed code to verify identical behavior. Focus on tests that use similar tab navigation patterns.

**Test Cases**:
1. **Other Tab Navigation Tests**: Verify tests for Normal Distribution, Property-Based Testing, and other tabs continue to work correctly
2. **Other Playwright Tests**: Verify all other Playwright tests in the test suite continue to pass
3. **Non-Playwright Tests**: Verify unit tests, integration tests, and other test types are unaffected
4. **Tab Button Display**: Verify the Streamlit app still displays "📊 Non-Normal Distribution" with emoji

### Unit Tests

- Run all 7 tests in `tests/test_ui_playwright_non_normal.py` individually to verify each passes
- Verify tab navigation succeeds in each test (no selector timeout errors)
- Verify each test's specific assertions execute correctly (outlier detection, normality tests, transformations, etc.)

### Property-Based Tests

- The file already contains 2 property-based tests (test_property_data_input_interaction, test_property_dropdown_selection)
- Verify these property tests pass after the fix
- Consider adding a property test that verifies tab navigation works for all tabs with emoji prefixes

### Integration Tests

- Run the full Playwright test suite to verify no regressions
- Test the complete user flow: launch app → navigate to Non-Normal tab → perform analysis
- Verify the fix works in different browser contexts (Chromium, Firefox, WebKit if configured)
