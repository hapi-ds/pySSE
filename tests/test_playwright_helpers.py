"""Unit tests for Playwright UI interaction helper functions.

This module tests the helper functions defined in conftest.py that provide
reusable UI interaction patterns for Streamlit elements.

Requirements tested:
- 3.1: Click tab element to navigate
- 3.2: Input numeric value into confidence field
- 3.3: Input numeric value into reliability field
- 3.4: Click calculate button to trigger calculation
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.conftest import (
    click_tab,
    fill_number_input,
    click_button,
    get_text_content,
    wait_for_element,
)


# ============================================================================
# Tests for click_tab()
# ============================================================================

@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_click_tab_success():
    """Test click_tab successfully clicks a tab element.
    
    Validates: Requirements 3.1, 4.1, 5.1, 6.1
    """
    # Arrange
    page = Mock()
    tab_element = Mock()
    page.get_by_role.return_value = tab_element
    
    # Act
    click_tab(page, "Attribute (Binomial)")
    
    # Assert
    page.get_by_role.assert_called_once_with("tab", name="Attribute (Binomial)")
    tab_element.click.assert_called_once()


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_click_tab_element_not_found():
    """Test click_tab raises error when tab element is not found.
    
    Validates: Requirements 3.1 - Error handling
    """
    # Arrange
    page = Mock()
    page.get_by_role.side_effect = PlaywrightTimeoutError("Element not found")
    
    # Act & Assert
    with pytest.raises(PlaywrightTimeoutError, match="Element not found"):
        click_tab(page, "Nonexistent Tab")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_click_tab_with_different_tab_names():
    """Test click_tab works with various tab names.
    
    Validates: Requirements 3.1, 4.1, 5.1, 6.1
    """
    # Arrange
    page = Mock()
    tab_element = Mock()
    page.get_by_role.return_value = tab_element
    
    tab_names = [
        "Attribute (Binomial)",
        "Variables (Normal)",
        "Non-Normal Distribution",
        "Reliability",
    ]
    
    # Act & Assert
    for tab_name in tab_names:
        click_tab(page, tab_name)
        page.get_by_role.assert_called_with("tab", name=tab_name)
    
    assert tab_element.click.call_count == len(tab_names)


# ============================================================================
# Tests for fill_number_input()
# ============================================================================

@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_fill_number_input_success():
    """Test fill_number_input successfully fills a number input.
    
    Validates: Requirements 3.2, 3.3, 4.2, 4.3, 6.2, 6.3
    """
    # Arrange
    page = Mock()
    input_element = Mock()
    page.get_by_label.return_value = input_element
    
    # Act
    fill_number_input(page, "Confidence Level (%)", 95.0)
    
    # Assert
    page.get_by_label.assert_called_once_with("Confidence Level (%)")
    input_element.clear.assert_called_once()
    input_element.fill.assert_called_once_with("95.0")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_fill_number_input_clears_before_filling():
    """Test fill_number_input clears existing value before filling.
    
    Validates: Requirements 3.2, 3.3 - Input field interaction
    """
    # Arrange
    page = Mock()
    input_element = Mock()
    page.get_by_label.return_value = input_element
    
    # Act
    fill_number_input(page, "Reliability (%)", 90.0)
    
    # Assert - verify clear is called before fill
    expected_calls = [call.clear(), call.fill("90.0")]
    assert input_element.method_calls == expected_calls


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_fill_number_input_converts_value_to_string():
    """Test fill_number_input converts numeric values to strings.
    
    Validates: Requirements 3.2, 3.3 - Numeric input handling
    """
    # Arrange
    page = Mock()
    input_element = Mock()
    page.get_by_label.return_value = input_element
    
    # Act - test with integer
    fill_number_input(page, "Sample Size", 30)
    
    # Assert
    input_element.fill.assert_called_with("30")
    
    # Act - test with float
    fill_number_input(page, "Mean", 10.5)
    
    # Assert
    input_element.fill.assert_called_with("10.5")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_fill_number_input_element_not_found():
    """Test fill_number_input raises error when input element is not found.
    
    Validates: Requirements 3.2, 3.3 - Error handling
    """
    # Arrange
    page = Mock()
    page.get_by_label.side_effect = PlaywrightTimeoutError("Element not found")
    
    # Act & Assert
    with pytest.raises(PlaywrightTimeoutError, match="Element not found"):
        fill_number_input(page, "Nonexistent Input", 100.0)


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_fill_number_input_with_various_labels():
    """Test fill_number_input works with different input labels.
    
    Validates: Requirements 3.2, 3.3, 4.2, 4.3, 6.2, 6.3
    """
    # Arrange
    page = Mock()
    input_element = Mock()
    page.get_by_label.return_value = input_element
    
    test_cases = [
        ("Confidence Level (%)", 95.0),
        ("Reliability (%)", 90.0),
        ("Sample Size", 30),
        ("Mean", 10.0),
        ("Standard Deviation", 1.5),
        ("LSL", 7.0),
        ("USL", 13.0),
        ("Activation Energy (eV)", 0.7),
    ]
    
    # Act & Assert
    for label, value in test_cases:
        fill_number_input(page, label, value)
        page.get_by_label.assert_called_with(label)
        input_element.fill.assert_called_with(str(value))


# ============================================================================
# Tests for click_button()
# ============================================================================

@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_click_button_success():
    """Test click_button successfully clicks a button element.
    
    Validates: Requirements 3.4, 4.4, 6.4
    """
    # Arrange
    page = Mock()
    button_element = Mock()
    page.get_by_role.return_value = button_element
    
    # Act
    click_button(page, "Calculate Sample Size")
    
    # Assert
    page.get_by_role.assert_called_once_with("button", name="Calculate Sample Size")
    button_element.click.assert_called_once()


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_click_button_element_not_found():
    """Test click_button raises error when button element is not found.
    
    Validates: Requirements 3.4 - Error handling
    """
    # Arrange
    page = Mock()
    page.get_by_role.side_effect = PlaywrightTimeoutError("Element not found")
    
    # Act & Assert
    with pytest.raises(PlaywrightTimeoutError, match="Element not found"):
        click_button(page, "Nonexistent Button")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_click_button_with_various_button_texts():
    """Test click_button works with different button texts.
    
    Validates: Requirements 3.4, 4.4, 5.3, 5.5, 5.9, 6.4
    """
    # Arrange
    page = Mock()
    button_element = Mock()
    page.get_by_role.return_value = button_element
    
    button_texts = [
        "Calculate Sample Size",
        "Calculate Tolerance Limits",
        "Detect Outliers",
        "Test Normality",
        "Apply Transformation",
        "Calculate Test Duration",
    ]
    
    # Act & Assert
    for button_text in button_texts:
        click_button(page, button_text)
        page.get_by_role.assert_called_with("button", name=button_text)
    
    assert button_element.click.call_count == len(button_texts)


# ============================================================================
# Tests for get_text_content()
# ============================================================================

@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_get_text_content_success():
    """Test get_text_content successfully retrieves text from element.
    
    Validates: Requirements 3.5, 3.6, 4.5, 4.6, 4.7, 4.8
    """
    # Arrange
    page = Mock()
    element = Mock()
    element.text_content.return_value = "Sample Size: 29"
    page.locator.return_value = element
    
    # Act
    result = get_text_content(page, "text=Sample Size")
    
    # Assert
    page.locator.assert_called_once_with("text=Sample Size")
    element.wait_for.assert_called_once_with(state="visible")
    assert result == "Sample Size: 29"


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_get_text_content_waits_for_visibility():
    """Test get_text_content waits for element to be visible.
    
    Validates: Requirements 3.5 - Element visibility verification
    """
    # Arrange
    page = Mock()
    element = Mock()
    element.text_content.return_value = "Result"
    page.locator.return_value = element
    
    # Act
    get_text_content(page, "[data-testid='result']")
    
    # Assert - verify wait_for is called with visible state
    element.wait_for.assert_called_once_with(state="visible")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_get_text_content_element_not_found():
    """Test get_text_content raises error when element is not found.
    
    Validates: Requirements 3.5 - Error handling
    """
    # Arrange
    page = Mock()
    element = Mock()
    element.wait_for.side_effect = PlaywrightTimeoutError("Element not found")
    page.locator.return_value = element
    
    # Act & Assert
    with pytest.raises(PlaywrightTimeoutError, match="Element not found"):
        get_text_content(page, "text=Nonexistent")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_get_text_content_timeout():
    """Test get_text_content handles timeout when element doesn't appear.
    
    Validates: Requirements 3.5 - Timeout behavior
    """
    # Arrange
    page = Mock()
    element = Mock()
    element.wait_for.side_effect = PlaywrightTimeoutError("Timeout waiting for element")
    page.locator.return_value = element
    
    # Act & Assert
    with pytest.raises(PlaywrightTimeoutError, match="Timeout"):
        get_text_content(page, "text=Loading...")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_get_text_content_with_various_selectors():
    """Test get_text_content works with different selector types.
    
    Validates: Requirements 3.5, 3.6, 4.5, 4.6, 4.7, 4.8
    """
    # Arrange
    page = Mock()
    element = Mock()
    element.text_content.return_value = "Content"
    page.locator.return_value = element
    
    selectors = [
        "text=Sample Size",
        "[data-testid='result']",
        ".result-value",
        "#tolerance-factor",
        "text=PASS",
    ]
    
    # Act & Assert
    for selector in selectors:
        result = get_text_content(page, selector)
        page.locator.assert_called_with(selector)
        assert result == "Content"


# ============================================================================
# Tests for wait_for_element()
# ============================================================================

@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_wait_for_element_success():
    """Test wait_for_element successfully waits for element visibility.
    
    Validates: Requirements 3.5, 4.5, 5.4, 5.6, 6.5
    """
    # Arrange
    page = Mock()
    element = Mock()
    page.locator.return_value = element
    
    # Act
    wait_for_element(page, "text=Results")
    
    # Assert
    page.locator.assert_called_once_with("text=Results")
    element.wait_for.assert_called_once_with(state="visible", timeout=30000)


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_wait_for_element_with_custom_timeout():
    """Test wait_for_element respects custom timeout parameter.
    
    Validates: Requirements 3.5 - Timeout configuration
    """
    # Arrange
    page = Mock()
    element = Mock()
    page.locator.return_value = element
    
    # Act
    wait_for_element(page, "text=Results", timeout=5000)
    
    # Assert
    element.wait_for.assert_called_once_with(state="visible", timeout=5000)


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_wait_for_element_timeout():
    """Test wait_for_element raises error when element doesn't appear.
    
    Validates: Requirements 3.5 - Timeout behavior
    """
    # Arrange
    page = Mock()
    element = Mock()
    element.wait_for.side_effect = PlaywrightTimeoutError("Timeout exceeded")
    page.locator.return_value = element
    
    # Act & Assert
    with pytest.raises(PlaywrightTimeoutError, match="Timeout exceeded"):
        wait_for_element(page, "text=Never Appears")


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_wait_for_element_default_timeout():
    """Test wait_for_element uses default timeout of 30 seconds.
    
    Validates: Requirements 2.5 - Default timeout configuration
    """
    # Arrange
    page = Mock()
    element = Mock()
    page.locator.return_value = element
    
    # Act - call without timeout parameter
    wait_for_element(page, "text=Results")
    
    # Assert - verify default timeout is used
    element.wait_for.assert_called_once_with(state="visible", timeout=30000)


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_wait_for_element_with_various_selectors():
    """Test wait_for_element works with different selector types.
    
    Validates: Requirements 3.5, 4.5, 5.4, 5.6, 6.5
    """
    # Arrange
    page = Mock()
    element = Mock()
    page.locator.return_value = element
    
    selectors = [
        "text=Results Table",
        "[data-testid='tolerance-factor']",
        ".outlier-count",
        "#shapiro-wilk-pvalue",
        "text=Test Duration",
    ]
    
    # Act & Assert
    for selector in selectors:
        wait_for_element(page, selector)
        page.locator.assert_called_with(selector)
    
    assert element.wait_for.call_count == len(selectors)


# ============================================================================
# Integration Tests - Helper Function Combinations
# ============================================================================

@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_helper_functions_workflow():
    """Test typical workflow using multiple helper functions together.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
    """
    # Arrange
    page = Mock()
    
    # Mock tab element
    tab_element = Mock()
    
    # Mock input elements
    confidence_input = Mock()
    reliability_input = Mock()
    
    # Mock button element
    button_element = Mock()
    
    # Mock result element
    result_element = Mock()
    result_element.text_content.return_value = "Sample Size: 29"
    
    # Configure page mock to return appropriate elements
    def get_by_role_side_effect(role, name=None):
        if role == "tab":
            return tab_element
        elif role == "button":
            return button_element
        return Mock()
    
    def get_by_label_side_effect(label):
        if "Confidence" in label:
            return confidence_input
        elif "Reliability" in label:
            return reliability_input
        return Mock()
    
    page.get_by_role.side_effect = get_by_role_side_effect
    page.get_by_label.side_effect = get_by_label_side_effect
    page.locator.return_value = result_element
    
    # Act - simulate typical test workflow
    click_tab(page, "Attribute (Binomial)")
    fill_number_input(page, "Confidence Level (%)", 95.0)
    fill_number_input(page, "Reliability (%)", 90.0)
    click_button(page, "Calculate Sample Size")
    result = get_text_content(page, "text=Sample Size")
    
    # Assert - verify all interactions occurred
    tab_element.click.assert_called_once()
    confidence_input.clear.assert_called_once()
    confidence_input.fill.assert_called_once_with("95.0")
    reliability_input.clear.assert_called_once()
    reliability_input.fill.assert_called_once_with("90.0")
    button_element.click.assert_called_once()
    result_element.wait_for.assert_called_once_with(state="visible")
    assert result == "Sample Size: 29"


@pytest.mark.urs("REQ-25")
@pytest.mark.playwright
def test_helper_functions_error_propagation():
    """Test that errors from Playwright API propagate correctly through helpers.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.4 - Error handling
    """
    # Arrange
    page = Mock()
    
    # Test click_tab error propagation
    page.get_by_role.side_effect = PlaywrightTimeoutError("Tab not found")
    with pytest.raises(PlaywrightTimeoutError):
        click_tab(page, "Invalid Tab")
    
    # Test fill_number_input error propagation
    page.get_by_label.side_effect = PlaywrightTimeoutError("Input not found")
    with pytest.raises(PlaywrightTimeoutError):
        fill_number_input(page, "Invalid Input", 100.0)
    
    # Test click_button error propagation
    page.get_by_role.side_effect = PlaywrightTimeoutError("Button not found")
    with pytest.raises(PlaywrightTimeoutError):
        click_button(page, "Invalid Button")
    
    # Test get_text_content error propagation
    element = Mock()
    element.wait_for.side_effect = PlaywrightTimeoutError("Element not visible")
    page.locator.return_value = element
    with pytest.raises(PlaywrightTimeoutError):
        get_text_content(page, "text=Invalid")
    
    # Test wait_for_element error propagation
    element.wait_for.side_effect = PlaywrightTimeoutError("Timeout")
    with pytest.raises(PlaywrightTimeoutError):
        wait_for_element(page, "text=Invalid")
