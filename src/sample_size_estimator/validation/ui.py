"""UI components for validation system display in Streamlit.

This module provides Streamlit UI components for displaying validation status,
running validation workflows, and showing validation results.
"""

from datetime import datetime
from typing import Callable

import streamlit as st

from .models import ValidationStatus


class ValidationUI:
    """UI components for validation system display."""

    def __init__(self):
        """Initialize ValidationUI with placeholder references.
        
        Instance variables:
            _progress_text_placeholder: Streamlit placeholder for phase text
            _progress_bar_placeholder: Streamlit placeholder for progress bar
            _current_phase: Current validation phase name
        """
        self._progress_text_placeholder = None
        self._progress_bar_placeholder = None
        self._current_phase = None

    def render_validation_button(
        self,
        status: ValidationStatus,
        on_click: Callable[[], None] | None = None
    ) -> bool:
        """Render validation button with color based on validation state.

        Args:
            status: Current validation status.
            on_click: Optional callback function to execute when button is clicked.

        Returns:
            True if button was clicked, False otherwise.
        """
        button_color = status.get_button_color()
        button_text = "Run Validation" if not status.is_validated else "Re-validate"

        # Use Streamlit's button with custom styling
        button_clicked = st.button(
            button_text,
            type="primary" if button_color == "green" else "secondary",
            use_container_width=True
        )

        if button_clicked and on_click:
            on_click()

        return button_clicked

    def render_validation_metrics_dashboard(
        self,
        status: ValidationStatus
    ) -> None:
        """Render validation metrics dashboard showing status, expiry, and test counts.

        Args:
            status: Current validation status.
        """
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Validation Status",
                value=status.get_status_text(),
                delta="Valid" if status.is_validated else "Invalid",
                delta_color="normal" if status.is_validated else "inverse"
            )

        with col2:
            if status.validation_date:
                st.metric(
                    label="Last Validated",
                    value=status.validation_date.strftime("%Y-%m-%d")
                )
            else:
                st.metric(
                    label="Last Validated",
                    value="Never"
                )

        with col3:
            if status.days_until_expiry is not None:
                st.metric(
                    label="Days Until Expiry",
                    value=status.days_until_expiry,
                    delta="Expired" if status.days_until_expiry < 0 else None,
                    delta_color="inverse" if status.days_until_expiry < 0 else "normal"
                )
            else:
                st.metric(
                    label="Days Until Expiry",
                    value="N/A"
                )

    def render_validation_progress(
        self,
        phase: str,
        percentage: float
    ) -> None:
        """Render validation progress indicator with phase and percentage.

        This method creates placeholders on first call and reuses them
        for subsequent updates, ensuring a single progress bar that
        updates in place.

        Args:
            phase: Current validation phase (e.g., "IQ", "OQ", "PQ").
            percentage: Progress percentage (0.0 to 1.0).

        Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.3, 3.1, 3.2, 4.2
        """
        try:
            # Clamp percentage to valid range
            percentage = max(0.0, min(1.0, percentage))

            # Handle None or empty phase
            if not phase:
                phase = "Unknown"

            # Create placeholders on first call
            if self._progress_text_placeholder is None:
                self._progress_text_placeholder = st.empty()
            if self._progress_bar_placeholder is None:
                self._progress_bar_placeholder = st.empty()

            # Detect phase transitions
            if self._current_phase != phase:
                self._current_phase = phase

            # Update text placeholder with formatted phase label
            phase_label = self._format_phase_label(phase)
            self._progress_text_placeholder.text(phase_label)

            # Update progress bar placeholder with percentage
            self._progress_bar_placeholder.progress(percentage)

        except Exception as e:
            # Log error but don't crash the validation workflow
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating progress bar: {e}")

    def _format_phase_label(self, phase: str) -> str:
        """Format phase name into user-friendly label.

        Args:
            phase: Phase name from orchestrator.

        Returns:
            Formatted label string.

        Validates: Requirements 2.1, 2.4
        """
        phase_labels = {
            "Starting validation": "Starting validation...",
            "IQ": "Running IQ tests...",
            "OQ": "Running OQ tests...",
            "PQ": "Running PQ tests...",
            "Generating certificate": "Generating certificate...",
            "Complete": "Validation complete!"
        }
        return phase_labels.get(phase, f"Running {phase}...")

    def clear_validation_progress(self) -> None:
        """Clear progress bar and text after validation completes or fails.

        Validates: Requirements 1.4, 6.2, 6.4
        """
        if self._progress_text_placeholder is not None:
            self._progress_text_placeholder.empty()
            self._progress_text_placeholder = None

        if self._progress_bar_placeholder is not None:
            self._progress_bar_placeholder.empty()
            self._progress_bar_placeholder = None

        self._current_phase = None

    def render_validation_result(
        self,
        success: bool,
        message: str
    ) -> None:
        """Render validation result with success/failure message.

        Args:
            success: Whether validation succeeded.
            message: Result message to display.
        """
        if success:
            st.success(message)
        else:
            st.error(message)

    def render_validation_failure_details(
        self,
        failure_reasons: list[str]
    ) -> None:
        """Render validation failure details with specific failure reasons.

        Args:
            failure_reasons: List of failure reason strings.
        """
        if not failure_reasons:
            return

        st.error("Validation Failed")
        st.markdown("**Failure Reasons:**")
        for reason in failure_reasons:
            st.markdown(f"- {reason}")

    def render_expiry_warning(
        self,
        days_until_expiry: int,
        threshold: int
    ) -> None:
        """Render expiry warning for 30-day and 7-day thresholds.

        Args:
            days_until_expiry: Number of days until validation expires.
            threshold: Warning threshold in days (e.g., 30 or 7).
        """
        if days_until_expiry <= 0:
            st.error(
                f"⚠️ Validation has expired! Please re-validate immediately."
            )
        elif days_until_expiry <= threshold:
            st.warning(
                f"⚠️ Validation expires in {days_until_expiry} days. "
                f"Please plan to re-validate soon."
            )

    def render_non_validated_banner(self) -> None:
        """Render persistent warning banner for non-validated state."""
        st.warning(
            "⚠️ **System Not Validated** - This application has not been validated. "
            "Calculations may not be reliable. Please run validation before using "
            "for regulatory submissions."
        )

    def render_certificate_access(
        self,
        certificate_path: str | None,
        certificate_date: datetime | None
    ) -> None:
        """Render certificate access button and information.

        Args:
            certificate_path: Path to the validation certificate PDF.
            certificate_date: Date when certificate was generated.
        """
        if certificate_path is None:
            st.info("No validation certificate available. Run validation to generate one.")
            return

        st.markdown("### Validation Certificate")

        if certificate_date:
            st.text(f"Generated: {certificate_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Provide download button for certificate
        try:
            with open(certificate_path, "rb") as f:
                certificate_data = f.read()

            st.download_button(
                label="📄 Download Validation Certificate",
                data=certificate_data,
                file_name="validation_certificate.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except FileNotFoundError:
            st.error(f"Certificate file not found: {certificate_path}")
        except Exception as e:
            st.error(f"Error loading certificate: {e}")

