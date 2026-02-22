# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - Tab Selector Fails to Match Button Text with Emoji
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the selector mismatch bug exists
  - **Scoped PBT Approach**: Scope the property to the concrete failing case - selector text "Non-Normal Distribution" vs actual button text "📊 Non-Normal Distribution"
  - Test that for any test execution in `tests/test_ui_playwright_non_normal.py`, the selector `button:has-text('Non-Normal Distribution')` fails to locate the button with text "📊 Non-Normal Distribution"
  - The test assertions should verify that the selector times out or fails to find the element
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found: specific Playwright error messages showing selector timeout or element not found
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Other Tab Selectors Continue to Work
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (tests targeting other tabs like Normal Distribution, Property-Based Testing)
  - Write property-based tests capturing observed behavior patterns: tab navigation succeeds for all tabs that don't have the selector mismatch
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Fix tab selector mismatch in Non-Normal Distribution tests

  - [x] 3.1 Update tab selector to include emoji prefix
    - Update all occurrences of `page.locator("button:has-text('Non-Normal Distribution')").first.click()` to `page.locator("button:has-text('📊 Non-Normal Distribution')").first.click()`
    - Affected test functions in `tests/test_ui_playwright_non_normal.py`:
      - `test_non_normal_tab_renders`
      - `test_non_normal_outlier_detection`
      - `test_non_normal_normality_tests`
      - `test_non_normal_transformation`
      - `test_property_data_input_interaction`
      - `test_property_dropdown_selection`
    - Do NOT change the Streamlit app code - the button correctly displays "📊 Non-Normal Distribution"
    - _Bug_Condition: isBugCondition(input) where input.selectorText == "Non-Normal Distribution" AND input.actualButtonText == "📊 Non-Normal Distribution" AND NOT input.selectorMatchesButton_
    - _Expected_Behavior: Selector successfully locates button with text "📊 Non-Normal Distribution" and clicks it_
    - _Preservation: Tests for other tabs (Normal Distribution, Property-Based Testing, etc.) continue to work with their existing selectors; all other passing tests continue to pass_
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Tab Selector Successfully Matches Button Text
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Other Tab Selectors Remain Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Checkpoint - Ensure all tests pass
  - Run all 7 tests in `tests/test_ui_playwright_non_normal.py` to verify they pass
  - Run full Playwright test suite to verify no regressions in other test files
  - Verify tab navigation succeeds for all tests (no selector timeout errors)
  - Ask the user if questions arise
