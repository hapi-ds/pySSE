"""Unit tests for validation UI components.

Tests the ValidationUI class methods for rendering validation status,
buttons, metrics, progress, and warnings in Streamlit.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.sample_size_estimator.validation.models import ValidationStatus
from src.sample_size_estimator.validation.ui import ValidationUI


@pytest.fixture
def validation_ui() -> ValidationUI:
    """Create ValidationUI instance for testing."""
    return ValidationUI()


@pytest.fixture
def validated_status() -> ValidationStatus:
    """Create a validated status for testing."""
    return ValidationStatus(
        is_validated=True,
        validation_date=datetime.now() - timedelta(days=10),
        days_until_expiry=355,
        hash_match=True,
        environment_match=True,
        tests_passed=True,
        failure_reasons=[]
    )


@pytest.fixture
def not_validated_status() -> ValidationStatus:
    """Create a non-validated status for testing."""
    return ValidationStatus(
        is_validated=False,
        validation_date=None,
        days_until_expiry=None,
        hash_match=False,
        environment_match=False,
        tests_passed=False,
        failure_reasons=["Hash mismatch", "Environment changed"]
    )


@pytest.fixture
def expiring_soon_status() -> ValidationStatus:
    """Create a status that expires soon for testing."""
    return ValidationStatus(
        is_validated=True,
        validation_date=datetime.now() - timedelta(days=340),
        days_until_expiry=25,
        hash_match=True,
        environment_match=True,
        tests_passed=True,
        failure_reasons=[]
    )


@pytest.fixture
def expired_status() -> ValidationStatus:
    """Create an expired status for testing."""
    return ValidationStatus(
        is_validated=False,
        validation_date=datetime.now() - timedelta(days=400),
        days_until_expiry=-35,
        hash_match=True,
        environment_match=True,
        tests_passed=True,
        failure_reasons=["Validation expired"]
    )


class TestValidationButton:
    """Tests for validation button rendering."""

    @patch('streamlit.button')
    def test_render_button_validated_state(
        self,
        mock_button: MagicMock,
        validation_ui: ValidationUI,
        validated_status: ValidationStatus
    ) -> None:
        """Test button rendering when system is validated."""
        mock_button.return_value = False

        validation_ui.render_validation_button(validated_status)

        # Button should be called with "Re-validate" text and primary type
        mock_button.assert_called_once()
        call_args = mock_button.call_args
        assert call_args[0][0] == "Re-validate"
        assert call_args[1]["type"] == "primary"

    @patch('streamlit.button')
    def test_render_button_not_validated_state(
        self,
        mock_button: MagicMock,
        validation_ui: ValidationUI,
        not_validated_status: ValidationStatus
    ) -> None:
        """Test button rendering when system is not validated."""
        mock_button.return_value = False

        validation_ui.render_validation_button(not_validated_status)

        # Button should be called with "Run Validation" text and secondary type
        mock_button.assert_called_once()
        call_args = mock_button.call_args
        assert call_args[0][0] == "Run Validation"
        assert call_args[1]["type"] == "secondary"

    @patch('streamlit.button')
    def test_button_click_callback(
        self,
        mock_button: MagicMock,
        validation_ui: ValidationUI,
        validated_status: ValidationStatus
    ) -> None:
        """Test button click triggers callback."""
        mock_button.return_value = True
        callback = MagicMock()

        result = validation_ui.render_validation_button(validated_status, on_click=callback)

        assert result is True
        callback.assert_called_once()

    @patch('streamlit.button')
    def test_button_no_click_no_callback(
        self,
        mock_button: MagicMock,
        validation_ui: ValidationUI,
        validated_status: ValidationStatus
    ) -> None:
        """Test button not clicked does not trigger callback."""
        mock_button.return_value = False
        callback = MagicMock()

        result = validation_ui.render_validation_button(validated_status, on_click=callback)

        assert result is False
        callback.assert_not_called()


class TestValidationMetricsDashboard:
    """Tests for validation metrics dashboard rendering."""

    @patch('streamlit.columns')
    @patch('streamlit.metric')
    def test_render_metrics_validated(
        self,
        mock_metric: MagicMock,
        mock_columns: MagicMock,
        validation_ui: ValidationUI,
        validated_status: ValidationStatus
    ) -> None:
        """Test metrics dashboard rendering for validated state."""
        # Mock columns to return mock column objects
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        validation_ui.render_validation_metrics_dashboard(validated_status)

        # Verify columns were created
        mock_columns.assert_called_once_with(3)

        # Verify metric was called 3 times (once per column)
        assert mock_metric.call_count == 3

    @patch('streamlit.columns')
    @patch('streamlit.metric')
    def test_render_metrics_not_validated(
        self,
        mock_metric: MagicMock,
        mock_columns: MagicMock,
        validation_ui: ValidationUI,
        not_validated_status: ValidationStatus
    ) -> None:
        """Test metrics dashboard rendering for non-validated state."""
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        validation_ui.render_validation_metrics_dashboard(not_validated_status)

        # Verify columns were created
        mock_columns.assert_called_once_with(3)

        # Verify metric was called 3 times
        assert mock_metric.call_count == 3


class TestValidationProgress:
    """Tests for validation progress indicator rendering."""

    @patch('streamlit.empty')
    def test_placeholder_creation_on_first_call(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that placeholders are created on first call.
        
        Task 4.1: Verify placeholders are None before first call
        and are created after first call.
        Requirements: 1.1, 1.3
        """
        # Verify placeholders are None before first call
        assert validation_ui._progress_text_placeholder is None
        assert validation_ui._progress_bar_placeholder is None
        
        # Mock st.empty() to return mock placeholder objects
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call render_validation_progress
        validation_ui.render_validation_progress("IQ", 0.5)
        
        # Verify placeholders are created after first call
        assert validation_ui._progress_text_placeholder is not None
        assert validation_ui._progress_bar_placeholder is not None
        assert validation_ui._progress_text_placeholder == mock_text_placeholder
        assert validation_ui._progress_bar_placeholder == mock_progress_placeholder
        
        # Verify st.empty() was called twice (once for text, once for progress)
        assert mock_empty.call_count == 2

    @patch('streamlit.empty')
    def test_placeholder_reuse_across_multiple_calls(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that placeholders are reused across multiple calls.
        
        Task 4.2: Call render_validation_progress multiple times
        and verify placeholder references remain the same.
        Requirements: 1.2, 1.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # First call - placeholders should be created
        validation_ui.render_validation_progress("IQ", 0.25)
        
        # Store references to placeholders after first call
        first_text_placeholder = validation_ui._progress_text_placeholder
        first_progress_placeholder = validation_ui._progress_bar_placeholder
        
        # Verify placeholders were created
        assert first_text_placeholder is not None
        assert first_progress_placeholder is not None
        assert mock_empty.call_count == 2
        
        # Second call - placeholders should be reused (st.empty not called again)
        validation_ui.render_validation_progress("IQ", 0.50)
        
        # Verify same placeholder references are used
        assert validation_ui._progress_text_placeholder is first_text_placeholder
        assert validation_ui._progress_bar_placeholder is first_progress_placeholder
        
        # Verify st.empty() was NOT called again (still 2 calls total)
        assert mock_empty.call_count == 2
        
        # Third call with different phase - placeholders should still be reused
        validation_ui.render_validation_progress("OQ", 0.75)
        
        # Verify same placeholder references are still used
        assert validation_ui._progress_text_placeholder is first_text_placeholder
        assert validation_ui._progress_bar_placeholder is first_progress_placeholder
        
        # Verify st.empty() was still NOT called again (still 2 calls total)
        assert mock_empty.call_count == 2
        
        # Verify the placeholders were updated with new content
        # Text placeholder should have been called 3 times (once per render call)
        assert mock_text_placeholder.text.call_count == 3
        # Progress placeholder should have been called 3 times (once per render call)
        assert mock_progress_placeholder.progress.call_count == 3

    @patch('streamlit.empty')
    def test_render_progress_iq_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test progress rendering for IQ phase."""
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        validation_ui.render_validation_progress("IQ", 0.33)

        mock_text_placeholder.text.assert_called_once_with("Running IQ tests...")
        mock_progress_placeholder.progress.assert_called_once_with(0.33)

    @patch('streamlit.empty')
    def test_render_progress_oq_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test progress rendering for OQ phase."""
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        validation_ui.render_validation_progress("OQ", 0.66)

        mock_text_placeholder.text.assert_called_once_with("Running OQ tests...")
        mock_progress_placeholder.progress.assert_called_once_with(0.66)

    @patch('streamlit.empty')
    def test_render_progress_pq_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test progress rendering for PQ phase."""
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        validation_ui.render_validation_progress("PQ", 1.0)

        mock_text_placeholder.text.assert_called_once_with("Running PQ tests...")
        mock_progress_placeholder.progress.assert_called_once_with(1.0)

    def test_phase_label_formatting_iq(
        self,
        validation_ui: ValidationUI
    ) -> None:
        """Test phase label formatting for IQ phase.
        
        Task 4.3: Test "IQ" → "Running IQ tests..."
        Requirements: 2.1, 7.3
        """
        result = validation_ui._format_phase_label("IQ")
        assert result == "Running IQ tests..."

    def test_phase_label_formatting_oq(
        self,
        validation_ui: ValidationUI
    ) -> None:
        """Test phase label formatting for OQ phase.
        
        Task 4.3: Test "OQ" → "Running OQ tests..."
        Requirements: 2.1, 7.3
        """
        result = validation_ui._format_phase_label("OQ")
        assert result == "Running OQ tests..."

    def test_phase_label_formatting_pq(
        self,
        validation_ui: ValidationUI
    ) -> None:
        """Test phase label formatting for PQ phase.
        
        Task 4.3: Test "PQ" → "Running PQ tests..."
        Requirements: 2.1, 7.3
        """
        result = validation_ui._format_phase_label("PQ")
        assert result == "Running PQ tests..."

    def test_phase_label_formatting_complete(
        self,
        validation_ui: ValidationUI
    ) -> None:
        """Test phase label formatting for Complete phase.
        
        Task 4.3: Test "Complete" → "Validation complete!"
        Requirements: 2.1, 7.3
        """
        result = validation_ui._format_phase_label("Complete")
        assert result == "Validation complete!"

    def test_phase_label_formatting_unknown_phase(
        self,
        validation_ui: ValidationUI
    ) -> None:
        """Test phase label formatting for unknown phase.
        
        Task 4.3: Test unknown phase → "Running {phase}..."
        Requirements: 2.1, 7.3
        """
        result = validation_ui._format_phase_label("CustomPhase")
        assert result == "Running CustomPhase..."

    @patch('streamlit.empty')
    def test_phase_transition_detection(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test phase transition detection updates _current_phase.

        Task 4.4: Call with phase "IQ", verify _current_phase is "IQ"
        Call with phase "OQ", verify _current_phase is "OQ"
        Requirements: 2.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]

        # Verify _current_phase is None initially
        assert validation_ui._current_phase is None

        # Call with phase "IQ"
        validation_ui.render_validation_progress("IQ", 0.5)

        # Verify _current_phase is "IQ"
        assert validation_ui._current_phase == "IQ"

        # Call with phase "OQ"
        validation_ui.render_validation_progress("OQ", 0.3)

        # Verify _current_phase is "OQ"
        assert validation_ui._current_phase == "OQ"

    @patch('streamlit.empty')
    def test_clear_validation_progress(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test clear_validation_progress method clears all placeholders.
        
        Task 4.5: Create placeholders by calling render_validation_progress,
        call clear_validation_progress, and verify all instance variables are None.
        Requirements: 1.4, 6.4
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Create placeholders by calling render_validation_progress
        validation_ui.render_validation_progress("IQ", 0.5)
        
        # Verify placeholders were created
        assert validation_ui._progress_text_placeholder is not None
        assert validation_ui._progress_bar_placeholder is not None
        assert validation_ui._current_phase == "IQ"
        
        # Call clear_validation_progress
        validation_ui.clear_validation_progress()
        
        # Verify all instance variables are None
        assert validation_ui._progress_text_placeholder is None
        assert validation_ui._progress_bar_placeholder is None
        assert validation_ui._current_phase is None
        
        # Verify .empty() was called on both placeholders
        mock_text_placeholder.empty.assert_called_once()
        mock_progress_placeholder.empty.assert_called_once()

    @patch('streamlit.empty')
    def test_error_handling_percentage_below_zero(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that percentage < 0.0 is clamped to 0.0.
        
        Task 4.6: Test percentage < 0.0 is clamped to 0.0
        Requirements: 3.2
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with negative percentage
        validation_ui.render_validation_progress("IQ", -0.5)
        
        # Verify progress bar was called with clamped value (0.0)
        mock_progress_placeholder.progress.assert_called_once_with(0.0)

    @patch('streamlit.empty')
    def test_error_handling_percentage_above_one(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that percentage > 1.0 is clamped to 1.0.
        
        Task 4.6: Test percentage > 1.0 is clamped to 1.0
        Requirements: 3.2
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with percentage greater than 1.0
        validation_ui.render_validation_progress("OQ", 1.5)
        
        # Verify progress bar was called with clamped value (1.0)
        mock_progress_placeholder.progress.assert_called_once_with(1.0)

    @patch('streamlit.empty')
    def test_error_handling_percentage_extreme_negative(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that extreme negative percentage is clamped to 0.0.
        
        Task 4.6: Test percentage < 0.0 is clamped to 0.0 (edge case)
        Requirements: 3.2
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with extreme negative percentage
        validation_ui.render_validation_progress("PQ", -100.0)
        
        # Verify progress bar was called with clamped value (0.0)
        mock_progress_placeholder.progress.assert_called_once_with(0.0)

    @patch('streamlit.empty')
    def test_error_handling_percentage_extreme_positive(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that extreme positive percentage is clamped to 1.0.
        
        Task 4.6: Test percentage > 1.0 is clamped to 1.0 (edge case)
        Requirements: 3.2
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with extreme positive percentage
        validation_ui.render_validation_progress("Complete", 500.0)
        
        # Verify progress bar was called with clamped value (1.0)
        mock_progress_placeholder.progress.assert_called_once_with(1.0)

    @patch('streamlit.empty')
    def test_error_handling_none_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that None phase is handled gracefully.
        
        Task 4.7: Test None phase is handled gracefully
        Requirements: 7.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with None phase - should not raise exception
        validation_ui.render_validation_progress(None, 0.5)
        
        # Verify phase was converted to "Unknown" and formatted
        mock_text_placeholder.text.assert_called_once_with("Running Unknown...")
        
        # Verify progress bar was still updated
        mock_progress_placeholder.progress.assert_called_once_with(0.5)

    @patch('streamlit.empty')
    def test_error_handling_empty_string_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that empty string phase is handled gracefully.
        
        Task 4.7: Test empty string phase is handled gracefully
        Requirements: 7.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with empty string phase - should not raise exception
        validation_ui.render_validation_progress("", 0.75)
        
        # Verify phase was converted to "Unknown" and formatted
        mock_text_placeholder.text.assert_called_once_with("Running Unknown...")
        
        # Verify progress bar was still updated
        mock_progress_placeholder.progress.assert_called_once_with(0.75)

    @patch('streamlit.empty')
    def test_error_handling_whitespace_only_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that whitespace-only phase is handled gracefully.
        
        Task 4.7: Test empty/whitespace phase is handled gracefully (edge case)
        Requirements: 7.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]
        
        # Call with whitespace-only phase - should not raise exception
        validation_ui.render_validation_progress("   ", 0.25)
        
        # Verify phase was converted to "Unknown" and formatted
        # Note: "   " is truthy in Python, so it won't be converted to "Unknown"
        # It will be formatted as "Running    ..."
        mock_text_placeholder.text.assert_called_once_with("Running    ...")
        
        # Verify progress bar was still updated
        mock_progress_placeholder.progress.assert_called_once_with(0.25)
    @patch('streamlit.empty')
    def test_error_handling_none_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that None phase is handled gracefully.

        Task 4.7: Test None phase is handled gracefully
        Requirements: 7.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]

        # Call with None phase - should not raise exception
        validation_ui.render_validation_progress(None, 0.5)

        # Verify phase was converted to "Unknown" and formatted
        mock_text_placeholder.text.assert_called_once_with("Running Unknown...")

        # Verify progress bar was still updated
        mock_progress_placeholder.progress.assert_called_once_with(0.5)

    @patch('streamlit.empty')
    def test_error_handling_empty_string_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that empty string phase is handled gracefully.

        Task 4.7: Test empty string phase is handled gracefully
        Requirements: 7.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]

        # Call with empty string phase - should not raise exception
        validation_ui.render_validation_progress("", 0.75)

        # Verify phase was converted to "Unknown" and formatted
        mock_text_placeholder.text.assert_called_once_with("Running Unknown...")

        # Verify progress bar was still updated
        mock_progress_placeholder.progress.assert_called_once_with(0.75)

    @patch('streamlit.empty')
    def test_error_handling_whitespace_only_phase(
        self,
        mock_empty: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test that whitespace-only phase is handled gracefully.

        Task 4.7: Test empty/whitespace phase is handled gracefully (edge case)
        Requirements: 7.3
        """
        # Mock placeholders
        mock_text_placeholder = MagicMock()
        mock_progress_placeholder = MagicMock()
        mock_empty.side_effect = [mock_text_placeholder, mock_progress_placeholder]

        # Call with whitespace-only phase - should not raise exception
        validation_ui.render_validation_progress("   ", 0.25)

        # Verify phase was converted to "Unknown" and formatted
        # Note: "   " is truthy in Python, so it won't be converted to "Unknown"
        # It will be formatted as "Running    ..."
        mock_text_placeholder.text.assert_called_once_with("Running    ...")

        # Verify progress bar was still updated
        mock_progress_placeholder.progress.assert_called_once_with(0.25)



class TestValidationResult:
    """Tests for validation result rendering."""

    @patch('streamlit.success')
    def test_render_success_result(
        self,
        mock_success: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering success result."""
        validation_ui.render_validation_result(True, "Validation completed successfully!")

        mock_success.assert_called_once_with("Validation completed successfully!")

    @patch('streamlit.error')
    def test_render_failure_result(
        self,
        mock_error: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering failure result."""
        validation_ui.render_validation_result(False, "Validation failed!")

        mock_error.assert_called_once_with("Validation failed!")


class TestValidationFailureDetails:
    """Tests for validation failure details rendering."""

    @patch('streamlit.error')
    @patch('streamlit.markdown')
    def test_render_failure_details_with_reasons(
        self,
        mock_markdown: MagicMock,
        mock_error: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering failure details with multiple reasons."""
        failure_reasons = ["Hash mismatch", "Environment changed", "Tests failed"]

        validation_ui.render_validation_failure_details(failure_reasons)

        mock_error.assert_called_once_with("Validation Failed")
        # Should call markdown for header + 3 reasons
        assert mock_markdown.call_count == 4

    @patch('streamlit.error')
    @patch('streamlit.markdown')
    def test_render_failure_details_empty_list(
        self,
        mock_markdown: MagicMock,
        mock_error: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering failure details with empty list does nothing."""
        validation_ui.render_validation_failure_details([])

        mock_error.assert_not_called()
        mock_markdown.assert_not_called()


class TestExpiryWarning:
    """Tests for expiry warning rendering."""

    @patch('streamlit.warning')
    def test_render_warning_30_day_threshold(
        self,
        mock_warning: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test warning rendering for 30-day threshold."""
        validation_ui.render_expiry_warning(25, 30)

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "25 days" in call_args

    @patch('streamlit.warning')
    def test_render_warning_7_day_threshold(
        self,
        mock_warning: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test warning rendering for 7-day threshold."""
        validation_ui.render_expiry_warning(5, 7)

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "5 days" in call_args

    @patch('streamlit.error')
    def test_render_error_expired(
        self,
        mock_error: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test error rendering for expired validation."""
        validation_ui.render_expiry_warning(-10, 30)

        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        assert "expired" in call_args.lower()

    @patch('streamlit.warning')
    @patch('streamlit.error')
    def test_no_warning_above_threshold(
        self,
        mock_error: MagicMock,
        mock_warning: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test no warning when days until expiry is above threshold."""
        validation_ui.render_expiry_warning(100, 30)

        mock_warning.assert_not_called()
        mock_error.assert_not_called()


class TestNonValidatedBanner:
    """Tests for non-validated banner rendering."""

    @patch('streamlit.warning')
    def test_render_non_validated_banner(
        self,
        mock_warning: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering non-validated banner."""
        validation_ui.render_non_validated_banner()

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Not Validated" in call_args
        assert "run validation" in call_args.lower()


class TestCertificateAccess:
    """Tests for certificate access rendering."""

    @patch('streamlit.info')
    def test_render_no_certificate(
        self,
        mock_info: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering when no certificate exists."""
        validation_ui.render_certificate_access(None, None)

        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        assert "No validation certificate" in call_args

    @patch('streamlit.download_button')
    @patch('streamlit.text')
    @patch('streamlit.markdown')
    @patch('builtins.open', create=True)
    def test_render_with_certificate(
        self,
        mock_open: MagicMock,
        mock_markdown: MagicMock,
        mock_text: MagicMock,
        mock_download: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering with valid certificate."""
        cert_date = datetime(2024, 1, 15, 10, 30, 0)
        mock_file = MagicMock()
        mock_file.read.return_value = b"PDF content"
        mock_open.return_value.__enter__.return_value = mock_file

        validation_ui.render_certificate_access("reports/cert.pdf", cert_date)

        mock_markdown.assert_called_once()
        mock_text.assert_called_once()
        mock_download.assert_called_once()

    @patch('streamlit.error')
    @patch('streamlit.markdown')
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_render_certificate_not_found(
        self,
        mock_open: MagicMock,
        mock_markdown: MagicMock,
        mock_error: MagicMock,
        validation_ui: ValidationUI
    ) -> None:
        """Test rendering when certificate file is not found."""
        cert_date = datetime(2024, 1, 15, 10, 30, 0)

        validation_ui.render_certificate_access("reports/missing.pdf", cert_date)

        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        assert "not found" in call_args.lower()
