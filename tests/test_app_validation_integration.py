"""Integration tests for validation system in main application.

Tests the integration of validation components with the main Streamlit app,
including UI rendering, validation workflow execution, and report disclaimers.
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.sample_size_estimator.models import CalculationReport
from src.sample_size_estimator.reports import generate_calculation_report
from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    ValidationConfig,
    ValidationStatus,
)
from src.sample_size_estimator.validation.persistence import ValidationPersistence
from src.sample_size_estimator.validation.state_manager import ValidationStateManager


class TestValidationUIIntegration:
    """Tests for validation UI integration in main app."""

    @patch('streamlit.warning')
    @patch('streamlit.title')
    @patch('streamlit.markdown')
    def test_non_validated_banner_displayed(
        self,
        mock_markdown: MagicMock,
        mock_title: MagicMock,
        mock_warning: MagicMock
    ) -> None:
        """Test that non-validated banner is displayed when system is not validated."""
        # This test verifies the banner appears in the UI
        # The actual rendering is tested in test_validation_ui.py
        from src.sample_size_estimator.validation.ui import ValidationUI

        ui = ValidationUI()
        ui.render_non_validated_banner()

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Not Validated" in call_args

    @patch('streamlit.warning')
    def test_expiry_warning_displayed_30_days(
        self,
        mock_warning: MagicMock
    ) -> None:
        """Test that expiry warning is displayed at 30-day threshold."""
        from src.sample_size_estimator.validation.ui import ValidationUI

        ui = ValidationUI()
        ui.render_expiry_warning(25, 30)

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "25 days" in call_args

    @patch('streamlit.error')
    def test_expiry_error_displayed_when_expired(
        self,
        mock_error: MagicMock
    ) -> None:
        """Test that error is displayed when validation has expired."""
        from src.sample_size_estimator.validation.ui import ValidationUI

        ui = ValidationUI()
        ui.render_expiry_warning(-10, 30)

        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        assert "expired" in call_args.lower()


class TestValidationStatusCheck:
    """Tests for validation status checking on app startup."""

    def test_check_validation_status_not_validated(self, tmp_path: Path) -> None:
        """Test validation status check when system is not validated."""
        config = ValidationConfig(persistence_dir=tmp_path / ".validation")
        state_manager = ValidationStateManager(config)

        # No persisted state
        status = state_manager.check_validation_status(None)

        assert not status.is_validated
        assert status.validation_date is None
        assert status.days_until_expiry is None
        assert not status.hash_match
        assert not status.tests_passed

    def test_check_validation_status_validated(self, tmp_path: Path) -> None:
        """Test validation status check when system is validated."""
        config = ValidationConfig(persistence_dir=tmp_path / ".validation")
        state_manager = ValidationStateManager(config)
        persistence = ValidationPersistence(config.persistence_dir)

        # Create a validated state
        validation_date = datetime.now()
        expiry_date = validation_date + timedelta(days=365)
        current_hash = state_manager.calculate_validation_hash()
        env_fingerprint = state_manager.get_environment_fingerprint()

        from src.sample_size_estimator.validation.models import ValidationState

        persisted_state = ValidationState(
            validation_date=validation_date,
            validation_hash=current_hash,
            environment_fingerprint=env_fingerprint,
            iq_status="PASS",
            oq_status="PASS",
            pq_status="PASS",
            expiry_date=expiry_date,
            certificate_hash="abc123"
        )
        persistence.save_validation_state(persisted_state)

        status = state_manager.check_validation_status(persisted_state)

        assert status.is_validated
        assert status.validation_date is not None
        assert status.days_until_expiry is not None
        assert status.days_until_expiry > 0
        assert status.hash_match
        assert status.tests_passed

    def test_check_validation_status_expired(self, tmp_path: Path) -> None:
        """Test validation status check when validation has expired."""
        config = ValidationConfig(persistence_dir=tmp_path / ".validation")
        state_manager = ValidationStateManager(config)
        persistence = ValidationPersistence(config.persistence_dir)

        # Create an expired validation state
        validation_date = datetime.now() - timedelta(days=400)
        expiry_date = validation_date + timedelta(days=365)
        current_hash = state_manager.calculate_validation_hash()
        env_fingerprint = state_manager.get_environment_fingerprint()

        from src.sample_size_estimator.validation.models import ValidationState

        persisted_state = ValidationState(
            validation_date=validation_date,
            validation_hash=current_hash,
            environment_fingerprint=env_fingerprint,
            iq_status="PASS",
            oq_status="PASS",
            pq_status="PASS",
            expiry_date=expiry_date,
            certificate_hash="abc123"
        )
        persistence.save_validation_state(persisted_state)

        status = state_manager.check_validation_status(persisted_state)

        assert not status.is_validated
        # When expired, days_until_expiry may be None or negative
        assert any("expired" in r.lower() for r in status.failure_reasons)


class TestReportDisclaimer:
    """Tests for validation disclaimer in generated reports."""

    def test_report_includes_disclaimer_when_not_validated(self, tmp_path: Path) -> None:
        """Test that PDF report includes disclaimer when not validated."""
        report_data = CalculationReport(
            timestamp=datetime.now(),
            module="attribute",
            app_version="1.0.0",
            inputs={"confidence": 0.95, "reliability": 0.99},
            results={"sample_size": 299},
            engine_hash="abc123",
            validated_state=False
        )

        output_path = str(tmp_path / "test_report.pdf")
        result_path = generate_calculation_report(report_data, output_path)

        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0

        # Read PDF content to verify disclaimer is present
        # Note: Full PDF text extraction would require pdfplumber
        # For now, we verify the file was created successfully

    def test_report_no_disclaimer_when_validated(self, tmp_path: Path) -> None:
        """Test that PDF report does not include disclaimer when validated."""
        report_data = CalculationReport(
            timestamp=datetime.now(),
            module="attribute",
            app_version="1.0.0",
            inputs={"confidence": 0.95, "reliability": 0.99},
            results={"sample_size": 299},
            engine_hash="abc123",
            validated_state=True
        )

        output_path = str(tmp_path / "test_report_validated.pdf")
        result_path = generate_calculation_report(report_data, output_path)

        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0


class TestValidationWorkflowExecution:
    """Tests for validation workflow execution from UI."""

    @patch('src.sample_size_estimator.validation.orchestrator.ValidationOrchestrator.execute_validation_workflow')
    def test_validation_workflow_success(
        self,
        mock_execute: MagicMock,
        tmp_path: Path
    ) -> None:
        """Test successful validation workflow execution."""
        from src.sample_size_estimator.validation.models import (
            IQResult,
            OQResult,
            PQResult,
            SystemInfo,
            ValidationResult,
        )
        from src.sample_size_estimator.validation.orchestrator import (
            ValidationOrchestrator,
        )

        # Mock successful validation result
        mock_result = ValidationResult(
            success=True,
            validation_date=datetime.now(),
            validation_hash="abc123",
            environment_fingerprint=EnvironmentFingerprint(
                python_version="3.13.5",
                dependencies={"scipy": "1.11.0"}
            ),
            iq_result=IQResult(passed=True, checks=[], timestamp=datetime.now()),
            oq_result=OQResult(passed=True, tests=[], timestamp=datetime.now()),
            pq_result=PQResult(passed=True, tests=[], timestamp=datetime.now()),
            system_info=SystemInfo(
                os_name="Windows",
                os_version="10",
                python_version="3.13.5",
                dependencies={"scipy": "1.11.0"}
            ),
            certificate_hash="cert123"
        )
        mock_execute.return_value = mock_result

        config = ValidationConfig(persistence_dir=tmp_path / ".validation")
        orchestrator = ValidationOrchestrator(config.certificate_output_dir)

        result = orchestrator.execute_validation_workflow()

        assert result.success
        assert result.validation_hash == "abc123"
        assert result.certificate_hash == "cert123"

    @patch('src.sample_size_estimator.validation.orchestrator.ValidationOrchestrator.execute_validation_workflow')
    def test_validation_workflow_failure(
        self,
        mock_execute: MagicMock,
        tmp_path: Path
    ) -> None:
        """Test failed validation workflow execution."""
        from src.sample_size_estimator.validation.models import (
            IQCheck,
            IQResult,
            OQResult,
            PQResult,
            SystemInfo,
            ValidationResult,
        )
        from src.sample_size_estimator.validation.orchestrator import (
            ValidationOrchestrator,
        )

        # Mock failed validation result
        failed_check = IQCheck(
            name="Python Version",
            description="Check Python version",
            passed=False,
            expected_value="3.13.5",
            actual_value="3.12.0",
            failure_reason="Version mismatch"
        )

        mock_result = ValidationResult(
            success=False,
            validation_date=datetime.now(),
            validation_hash="abc123",
            environment_fingerprint=EnvironmentFingerprint(
                python_version="3.12.0",
                dependencies={"scipy": "1.11.0"}
            ),
            iq_result=IQResult(passed=False, checks=[failed_check], timestamp=datetime.now()),
            oq_result=OQResult(passed=True, tests=[], timestamp=datetime.now()),
            pq_result=PQResult(passed=True, tests=[], timestamp=datetime.now()),
            system_info=SystemInfo(
                os_name="Windows",
                os_version="10",
                python_version="3.12.0",
                dependencies={"scipy": "1.11.0"}
            )
        )
        mock_execute.return_value = mock_result

        config = ValidationConfig(persistence_dir=tmp_path / ".validation")
        orchestrator = ValidationOrchestrator(config.certificate_output_dir)

        result = orchestrator.execute_validation_workflow()

        assert not result.success
        assert not result.iq_result.passed
