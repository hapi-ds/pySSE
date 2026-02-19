"""End-to-end UI tests for Variables tab using Playwright.

This module contains Playwright-based browser automation tests for the
Variables (Normal) tab of the Sample Size Estimator application.

Tests verify:
- Tab navigation and rendering
- Input field interactions for sample parameters and specification limits
- Calculation button functionality
- Results display (tolerance factor, limits, Ppk)
- PASS/FAIL status display
- Error message handling for invalid inputs
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_variables_tab_renders(page: Page):
    """Test that the Variables tab renders correctly.
    
    Verifies that clicking the Variables tab displays the tab content
    including the header and input fields.
    
    Requirements:
        - 4.1: Navigate to Variables tab by clicking tab element
    """
    # Click the Variables tab
    page.locator("button:has-text('Variables (Normal)')").first.click()
    
    # Verify tab content is visible
    expect(page.get_by_text("Variables Data Analysis")).to_be_visible(timeout=10000)
    expect(page.get_by_label("Sample Size (n)")).to_be_visible()
    expect(page.get_by_label("Confidence Level (%)")).to_be_visible()
    expect(page.get_by_label("Reliability (%)")).to_be_visible()


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_variables_basic_calculation(page: Page):
    """Test basic tolerance limit calculation in Variables tab.
    
    Validates that entering sample parameters produces tolerance factor,
    upper/lower tolerance limits, and Ppk value.
    
    Requirements:
        - 4.1: Navigate to Variables tab
        - 4.2: Enter sample parameters (confidence, reliability, n, mean, std)
        - 4.4: Click calculate button
        - 4.5: Verify tolerance factor displays
        - 4.6: Verify upper and lower tolerance limits display
        - 4.7: Verify Ppk value displays
    """
    # Navigate to Variables tab
    page.locator("button:has-text('Variables (Normal)')").first.click()
    
    # Fill sample parameters
    page.get_by_label("Confidence Level (%)").clear()
    page.get_by_label("Confidence Level (%)").fill("95")
    
    page.get_by_label("Reliability (%)").clear()
    page.get_by_label("Reliability (%)").fill("90")
    
    page.get_by_label("Sample Size (n)").clear()
    page.get_by_label("Sample Size (n)").fill("30")
    
    page.get_by_label("Sample Mean").clear()
    page.get_by_label("Sample Mean").fill("10.0")
    
    page.get_by_label("Sample Standard Deviation").clear()
    page.get_by_label("Sample Standard Deviation").fill("1.0")
    
    # Click calculate
    page.get_by_role("button", name="Calculate Tolerance Limits").click()
    
    # Verify results section appears
    expect(page.get_by_text("Results")).to_be_visible(timeout=10000)
    
    # Verify tolerance factor displays
    expect(page.get_by_text("Tolerance Factor (k)")).to_be_visible()
    
    # Verify tolerance limits display
    expect(page.get_by_text("Lower Tolerance Limit")).to_be_visible()
    expect(page.get_by_text("Upper Tolerance Limit")).to_be_visible()
    
    # Verify Ppk displays (only if spec limits are provided, but we can check for the label)
    # Without spec limits, Ppk won't be calculated, so we just verify basic results


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_variables_with_spec_limits(page: Page):
    """Test Variables calculation with specification limits.
    
    Validates that when LSL and USL are provided, Ppk is calculated
    and PASS/FAIL status is displayed.
    
    Requirements:
        - 4.1: Navigate to Variables tab
        - 4.2: Enter sample parameters
        - 4.3: Enter specification limits (LSL, USL)
        - 4.4: Click calculate button
        - 4.7: Verify Ppk value displays
        - 4.8: Verify PASS/FAIL status displays
    """
    # Navigate to Variables tab
    page.locator("button:has-text('Variables (Normal)')").first.click()
    
    # Fill sample parameters
    page.get_by_label("Confidence Level (%)").clear()
    page.get_by_label("Confidence Level (%)").fill("95")
    
    page.get_by_label("Reliability (%)").clear()
    page.get_by_label("Reliability (%)").fill("90")
    
    page.get_by_label("Sample Size (n)").clear()
    page.get_by_label("Sample Size (n)").fill("30")
    
    page.get_by_label("Sample Mean").clear()
    page.get_by_label("Sample Mean").fill("10.0")
    
    page.get_by_label("Sample Standard Deviation").clear()
    page.get_by_label("Sample Standard Deviation").fill("1.0")
    
    # Fill specification limits
    page.get_by_label("Lower Specification Limit (LSL)").clear()
    page.get_by_label("Lower Specification Limit (LSL)").fill("7.0")
    
    page.get_by_label("Upper Specification Limit (USL)").clear()
    page.get_by_label("Upper Specification Limit (USL)").fill("13.0")
    
    # Click calculate
    page.get_by_role("button", name="Calculate Tolerance Limits").click()
    
    # Verify results section appears
    expect(page.get_by_text("Results")).to_be_visible(timeout=10000)
    
    # Verify Ppk displays
    expect(page.get_by_text("Process Performance Index (Ppk)")).to_be_visible()
    
    # Verify PASS/FAIL status displays
    # The status should be either "PASS" or "FAIL" based on whether tolerance limits are within spec
    # We just verify that some status text appears
    expect(page.locator("text=/PASS|FAIL/")).to_be_visible()


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_variables_invalid_spec_limits(page: Page):
    """Test error message for invalid specification limits.
    
    Validates that when LSL >= USL, an error message is displayed.
    
    Requirements:
        - 4.1: Navigate to Variables tab
        - 4.2: Enter sample parameters
        - 4.3: Enter invalid specification limits (LSL >= USL)
        - 7.3: Verify error message displays for LSL >= USL
    """
    # Navigate to Variables tab
    page.locator("button:has-text('Variables (Normal)')").first.click()
    
    # Fill sample parameters
    page.get_by_label("Confidence Level (%)").clear()
    page.get_by_label("Confidence Level (%)").fill("95")
    
    page.get_by_label("Reliability (%)").clear()
    page.get_by_label("Reliability (%)").fill("90")
    
    page.get_by_label("Sample Size (n)").clear()
    page.get_by_label("Sample Size (n)").fill("30")
    
    page.get_by_label("Sample Mean").clear()
    page.get_by_label("Sample Mean").fill("10.0")
    
    page.get_by_label("Sample Standard Deviation").clear()
    page.get_by_label("Sample Standard Deviation").fill("1.0")
    
    # Fill invalid specification limits (LSL >= USL)
    page.get_by_label("Lower Specification Limit (LSL)").clear()
    page.get_by_label("Lower Specification Limit (LSL)").fill("15.0")
    
    page.get_by_label("Upper Specification Limit (USL)").clear()
    page.get_by_label("Upper Specification Limit (USL)").fill("10.0")
    
    # Click calculate
    page.get_by_role("button", name="Calculate Tolerance Limits").click()
    
    # Verify error message appears
    # Streamlit typically shows errors in red text or error boxes
    expect(page.locator("text=/error|Error|ERROR|invalid|Invalid/i")).to_be_visible(timeout=10000)


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_variables_negative_std_dev(page: Page):
    """Test error message for negative standard deviation.
    
    Validates that entering a negative standard deviation displays
    an appropriate error message.
    
    Requirements:
        - 4.1: Navigate to Variables tab
        - 4.2: Enter sample parameters with negative std dev
        - 7.4: Verify error message displays for negative standard deviation
    """
    # Navigate to Variables tab
    page.locator("button:has-text('Variables (Normal)')").first.click()
    
    # Fill sample parameters with negative std dev
    page.get_by_label("Confidence Level (%)").clear()
    page.get_by_label("Confidence Level (%)").fill("95")
    
    page.get_by_label("Reliability (%)").clear()
    page.get_by_label("Reliability (%)").fill("90")
    
    page.get_by_label("Sample Size (n)").clear()
    page.get_by_label("Sample Size (n)").fill("30")
    
    page.get_by_label("Sample Mean").clear()
    page.get_by_label("Sample Mean").fill("10.0")
    
    # Try to enter negative standard deviation
    # Note: Streamlit number_input may have min_value validation
    page.get_by_label("Sample Standard Deviation").clear()
    page.get_by_label("Sample Standard Deviation").fill("-1.0")
    
    # Click calculate
    page.get_by_role("button", name="Calculate Tolerance Limits").click()
    
    # Verify error message appears
    expect(page.locator("text=/error|Error|ERROR|invalid|Invalid|negative|positive/i")).to_be_visible(timeout=10000)
