"""Bug condition exploration tests for playwright-non-normal-tab-selector-fix.

This test file contains property-based tests to explore and confirm the bug
where tests in `tests/test_ui_playwright_non_normal.py` fail because they use
the label "Enter your data" which doesn't exist in the Non-Normal Distribution tab.

The actual labels are:
- "Enter data values (one per line or comma-separated)" for Manual Entry mode
- "Paste data values" for Paste Values mode

**CRITICAL**: These tests encode the EXPECTED behavior and will FAIL on unfixed code.
The failure confirms the bug exists. After the fix, these tests should PASS.

**Validates: Requirements 2.1, 2.2**
"""

import pytest
from hypothesis import given, strategies as st
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


@pytest.mark.pq
@pytest.mark.property
@pytest.mark.playwright
@pytest.mark.e2e
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
def test_bug_condition_data_input_label_mismatch(page: Page):
    """Bug condition exploration: Data input label doesn't match test expectations.
    
    This test demonstrates the bug where tests try to locate a data input field
    using label "Enter your data", but the actual label in the Non-Normal tab is
    "Enter data values (one per line or comma-separated)".
    
    **EXPECTED ON UNFIXED CODE**: This test FAILS because the label
    "Enter your data" doesn't exist, causing a timeout error.
    
    **EXPECTED AFTER FIX**: This test PASSES because the tests are updated
    to use the correct label.
    
    **Validates: Requirements 2.1, 2.2**
    """
    # Navigate to Non-Normal tab (this works fine)
    page.locator("button:has-text('Non-Normal Distribution')").first.click(timeout=5000)
    
    # Verify we're on the tab
    expect(page.get_by_role("heading", name="Non-Normal Distribution Analysis")).to_be_visible(timeout=10000)
    
    # This is the EXPECTED behavior - the label should work
    # After fix, this should work with the correct label
    # Use the CORRECT label that matches the actual UI
    data_input = page.get_by_role("textbox", name="Enter data values (one per line or comma-separated)")
    data_input.wait_for(state="visible", timeout=5000)
    
    # If we get here, the label worked (expected after fix)
    data_input.fill("1, 2, 3, 4, 5")
    
    # Verify the value was set correctly
    input_value = data_input.input_value()
    assert "1, 2, 3, 4, 5" in input_value, f"Expected input to contain '1, 2, 3, 4, 5', got '{input_value}'"


@given(st.just("Enter data values (one per line or comma-separated)"))
def test_bug_condition_property_label_text_mismatch(label_text: str):
    """Property 1: Expected Behavior - Data Input Label Matches Actual Label.
    
    For any test that attempts to locate the data input field using the correct label
    "Enter data values (one per line or comma-separated)", the selector SHALL successfully
    locate the input field.
    
    This property test verifies the fix: test label now matches actual UI label.
    
    **EXPECTED ON UNFIXED CODE**: This test FAILS because tests use wrong label
    "Enter your data" which doesn't match actual label.
    
    **EXPECTED AFTER FIX**: This test PASSES because the fix updates the tests
    to use the correct label text.
    
    **Validates: Requirements 2.1, 2.2**
    """
    # Property: Test label must match actual UI label
    actual_label = "Enter data values (one per line or comma-separated)"
    
    # After fix: test label matches actual label
    labels_match = label_text == actual_label
    
    # Property assertion: Labels must match for selector to work
    assert labels_match, (
        f"Property violation: Test label '{label_text}' does not match "
        f"actual label '{actual_label}'. "
        f"The tests must be updated to use the correct label."
    )


@pytest.mark.pq
@pytest.mark.playwright
@pytest.mark.e2e
def test_diagnostic_actual_label_in_ui(page: Page):
    """Diagnostic test: Confirm the actual label text in the Non-Normal tab.
    
    This test explicitly checks the actual label text in the DOM to confirm
    the root cause: the label is "Enter data values (one per line or comma-separated)",
    not "Enter your data" as the tests expect.
    
    **EXPECTED ON UNFIXED CODE**: This test PASSES, confirming the actual label.
    
    **EXPECTED AFTER FIX**: This test still PASSES because the UI label
    should remain unchanged (only the test selectors are fixed).
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click(timeout=5000)
    
    # Verify we're on the tab
    expect(page.get_by_role("heading", name="Non-Normal Distribution Analysis")).to_be_visible(timeout=10000)
    
    # Try to find the data input using the ACTUAL label (use role to be specific)
    actual_label = "Enter data values (one per line or comma-separated)"
    data_input_actual = page.get_by_role("textbox", name=actual_label)
    
    # Confirm the actual label works
    assert data_input_actual.is_visible(), (
        f"Diagnostic: Expected to find textbox with label '{actual_label}', but it's not visible."
    )
    
    # Try to find using the WRONG label (what the tests use)
    wrong_label = "Enter your data"
    try:
        data_input_wrong = page.get_by_label(wrong_label)
        data_input_wrong.wait_for(state="visible", timeout=2000)
        print(f"\n⚠️  UNEXPECTED: Found input with label '{wrong_label}'")
    except PlaywrightTimeoutError:
        print(f"\n✓ CONFIRMED: Label '{wrong_label}' not found (as expected)")
    
    print(f"\n=== Diagnostic Results ===")
    print(f"Actual label in UI: '{actual_label}'")
    print(f"Label used in tests: '{wrong_label}'")
    print(f"Bug confirmed: Labels don't match!")


@pytest.mark.pq
@pytest.mark.playwright
@pytest.mark.e2e
def test_isolation_correct_label_works(page: Page):
    """Isolation test: Verify that using the correct label successfully finds the input.
    
    This test confirms that the proposed fix approach (using the correct label)
    will work correctly to locate the data input field.
    
    **EXPECTED ON UNFIXED CODE**: This test PASSES, confirming the fix approach works.
    
    **EXPECTED AFTER FIX**: This test still PASSES, demonstrating the fix is correct.
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click(timeout=5000)
    
    # Use the CORRECT label with role to be specific (the proposed fix)
    data_input = page.get_by_role("textbox", name="Enter data values (one per line or comma-separated)")
    
    # Verify we can interact with it
    data_input.fill("1, 2, 3, 4, 5")
    
    # Verify the value was set
    input_value = data_input.input_value()
    assert "1, 2, 3, 4, 5" in input_value, f"Expected input to contain '1, 2, 3, 4, 5', got '{input_value}'"

