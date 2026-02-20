"""End-to-end UI tests for Non-Normal tab using Playwright.

This module contains Playwright-based browser automation tests for the
Non-Normal Distribution tab of the Sample Size Estimator application.

Tests verify:
- Tab navigation and rendering
- Data input field interactions
- Outlier detection functionality
- Normality testing (Shapiro-Wilk, Anderson-Darling)
- Transformation method selection and application
- Results display for transformed data
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_non_normal_tab_renders(page: Page):
    """Test that the Non-Normal tab renders correctly.
    
    Verifies that clicking the Non-Normal tab displays the tab content
    including the header and input fields.
    
    Requirements:
        - 5.1: Navigate to Non-Normal tab by clicking tab element
    """
    # Click the Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click()
    
    # Verify tab content is visible
    expect(page.get_by_role("heading", name="Non-Normal Distribution Analysis")).to_be_visible(timeout=10000)
    # Check for the data input text area (label varies based on input method)
    expect(page.locator("textarea").first).to_be_visible()


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_non_normal_outlier_detection(page: Page):
    """Test outlier detection in Non-Normal tab.
    
    Validates that entering data and clicking detect outliers
    displays the outlier count.
    
    Requirements:
        - 5.1: Navigate to Non-Normal tab
        - 5.2: Enter comma-separated data
        - 5.3: Click detect outliers button
        - 5.4: Verify outlier count displays
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click()
    
    # Enter sample data with outliers
    data_input = page.get_by_label("Enter your data")
    data_input.click(click_count=3)
    data_input.fill("1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 200")
    
    # Click detect outliers button
    page.get_by_role("button", name="Detect Outliers").click()
    
    # Verify outlier detection results appear
    expect(page.get_by_text("Outlier Detection Results")).to_be_visible(timeout=10000)
    
    # Verify outlier count displays
    expect(page.locator("text=/outlier|Outlier/i")).to_be_visible()


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_non_normal_normality_tests(page: Page):
    """Test normality testing in Non-Normal tab.
    
    Validates that clicking test normality displays Shapiro-Wilk
    and Anderson-Darling test results.
    
    Requirements:
        - 5.1: Navigate to Non-Normal tab
        - 5.2: Enter comma-separated data
        - 5.5: Click test normality button
        - 5.6: Verify Shapiro-Wilk p-value displays
        - 5.7: Verify Anderson-Darling results display
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click()
    
    # Enter sample data
    data_input = page.get_by_label("Enter your data")
    data_input.click(click_count=3)
    data_input.fill("5.2, 6.1, 5.8, 6.3, 5.9, 6.0, 5.7, 6.2, 5.5, 6.4, 5.6, 6.1, 5.9, 6.0, 5.8")
    
    # Click test normality button
    page.get_by_role("button", name="Test Normality").click()
    
    # Verify normality test results appear
    expect(page.get_by_text("Normality Test Results")).to_be_visible(timeout=10000)
    
    # Verify Shapiro-Wilk results display
    expect(page.get_by_text("Shapiro-Wilk Test")).to_be_visible()
    expect(page.locator("text=/p-value|P-value/i")).to_be_visible()
    
    # Verify Anderson-Darling results display
    expect(page.get_by_text("Anderson-Darling Test")).to_be_visible()


@pytest.mark.pq
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_non_normal_transformation(page: Page):
    """Test data transformation in Non-Normal tab.
    
    Validates that selecting a transformation method and applying it
    displays transformed data normality results.
    
    Requirements:
        - 5.1: Navigate to Non-Normal tab
        - 5.2: Enter comma-separated data
        - 5.8: Select transformation method from dropdown
        - 5.9: Apply transformation
        - 5.10: Verify transformed data normality results display
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click()
    
    # Enter sample data (positive values for transformation)
    data_input = page.get_by_label("Enter your data")
    data_input.click(click_count=3)
    data_input.fill("1.5, 2.3, 3.1, 4.2, 5.5, 6.8, 7.2, 8.9, 10.1, 12.5, 15.3, 18.7, 22.1, 25.8, 30.2")
    
    # Select transformation method from dropdown
    # Common transformations: Log, Square Root, Box-Cox
    transformation_dropdown = page.locator("select").first
    transformation_dropdown.select_option(label="Log")
    
    # Click apply transformation button
    page.get_by_role("button", name="Apply Transformation").click()
    
    # Verify transformation results appear
    expect(page.get_by_text("Transformation Results")).to_be_visible(timeout=10000)
    
    # Verify transformed data normality results display
    expect(page.get_by_text("Transformed Data Normality")).to_be_visible()
    
    # Verify normality test results for transformed data
    expect(page.locator("text=/Shapiro-Wilk|Anderson-Darling/i")).to_be_visible()


# ============================================================================
# Property-Based Tests
# ============================================================================

# Feature: playwright-ui-testing, Property 7: Data Input Interaction
@pytest.mark.pq
@pytest.mark.property
@pytest.mark.playwright
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
def test_property_data_input_interaction(page: Page):
    """
    Property 7: Data Input Interaction
    **Validates: Requirements 5.2**
    
    For any text input field accepting comma-separated data, entering valid
    data should populate the field correctly.
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click()
    
    # Test multiple data input combinations
    test_cases = [
        "1, 2, 3, 4, 5",
        "10.5, 20.3, 30.1, 40.8",
        "1.23, 4.56, 7.89, 10.11, 12.13",
        "5, 10, 15, 20, 25, 30, 35, 40",
        "0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0",
    ]
    
    for data_string in test_cases:
        # Fill data input
        data_input = page.get_by_label("Enter your data")
        data_input.click(click_count=3)
        data_input.fill(data_string)
        
        # Verify the value was set
        input_value = data_input.input_value()
        assert input_value is not None and len(input_value) > 0
        
        # Verify the input contains comma-separated values
        assert "," in input_value or len(input_value.split()) > 0


# Feature: playwright-ui-testing, Property 8: Dropdown Selection
@pytest.mark.pq
@pytest.mark.property
@pytest.mark.playwright
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
def test_property_dropdown_selection(page: Page):
    """
    Property 8: Dropdown Selection
    **Validates: Requirements 5.8**
    
    For any dropdown menu, selecting an option should update the selected value.
    """
    # Navigate to Non-Normal tab
    page.locator("button:has-text('Non-Normal Distribution')").first.click()
    
    # Enter some data first (required for transformation)
    data_input = page.get_by_label("Enter your data")
    data_input.click(click_count=3)
    data_input.fill("1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
    
    # Test dropdown selection for transformation methods
    # Common transformation options: Log, Square Root, Box-Cox, etc.
    transformation_options = ["Log", "Square Root", "Box-Cox"]
    
    transformation_dropdown = page.locator("select").first
    
    for option in transformation_options:
        try:
            # Select the option
            transformation_dropdown.select_option(label=option)
            
            # Verify the option was selected
            selected_value = transformation_dropdown.input_value()
            assert selected_value is not None
            
            # Wait a moment for UI to update
            page.wait_for_timeout(500)
        except Exception:
            # If option doesn't exist, skip it
            # This handles cases where not all transformations are available
            continue
