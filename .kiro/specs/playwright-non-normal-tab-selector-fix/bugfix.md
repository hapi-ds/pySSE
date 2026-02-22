# Bugfix Requirements Document

## Introduction

The Playwright tests in `tests/test_ui_playwright_non_normal.py` are failing because they cannot locate the "Non-Normal Distribution" tab button. The tests use a selector that searches for exact text "Non-Normal Distribution", but the actual tab button in the Streamlit app includes an emoji prefix: "📊 Non-Normal Distribution". This mismatch causes all 5 tests in the file to fail as they cannot navigate to the required tab.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the test attempts to click the Non-Normal Distribution tab using `page.locator("button:has-text('Non-Normal Distribution')").first.click()` THEN the selector fails to find the element because it doesn't match the emoji prefix

1.2 WHEN all 5 tests in `tests/test_ui_playwright_non_normal.py` run THEN they all fail because they cannot navigate to the Non-Normal Distribution tab

### Expected Behavior (Correct)

2.1 WHEN the test attempts to click the Non-Normal Distribution tab THEN the selector SHALL successfully locate the button with text "📊 Non-Normal Distribution"

2.2 WHEN all 5 tests in `tests/test_ui_playwright_non_normal.py` run THEN they SHALL successfully navigate to the Non-Normal Distribution tab and execute their test assertions

### Unchanged Behavior (Regression Prevention)

3.1 WHEN tests for other tabs (Normal Distribution, Property-Based Testing) use their respective selectors THEN they SHALL CONTINUE TO work correctly

3.2 WHEN the test suite runs THEN all other passing tests SHALL CONTINUE TO pass without regression

3.3 WHEN the Streamlit app displays the tab button THEN it SHALL CONTINUE TO show "📊 Non-Normal Distribution" with the emoji prefix
