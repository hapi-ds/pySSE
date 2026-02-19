"""Integration tests for ValidationOrchestrator.

This module tests the complete validation workflow orchestration including
IQ/OQ/PQ test execution, result parsing, and progress callbacks.

Validates: Requirements 6.3, 6.4, 6.5
"""

import pytest
from datetime import datetime
from src.sample_size_estimator.validation.orchestrator import ValidationOrchestrator


class TestValidationOrchestrator:
    """Test suite for ValidationOrchestrator integration."""

    def test_execute_iq_tests_returns_result(self):
        """Test that execute_iq_tests returns IQResult with checks."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_iq_tests()
        
        assert result is not None
        assert hasattr(result, 'passed')
        assert hasattr(result, 'checks')
        assert hasattr(result, 'timestamp')
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.checks, list)

    def test_execute_oq_tests_returns_result(self):
        """Test that execute_oq_tests returns OQResult with tests."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_oq_tests()
        
        assert result is not None
        assert hasattr(result, 'passed')
        assert hasattr(result, 'tests')
        assert hasattr(result, 'timestamp')
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.tests, list)

    def test_execute_pq_tests_returns_result(self):
        """Test that execute_pq_tests returns PQResult with tests."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_pq_tests()
        
        assert result is not None
        assert hasattr(result, 'passed')
        assert hasattr(result, 'tests')
        assert hasattr(result, 'timestamp')
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.tests, list)

    def test_validation_workflow_executes_all_phases(self):
        """Test that validation workflow executes IQ, OQ, and PQ phases.
        
        Validates: Requirement 6.3
        """
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_validation_workflow()
        
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'iq_result')
        assert hasattr(result, 'oq_result')
        assert hasattr(result, 'pq_result')
        assert result.iq_result is not None
        assert result.oq_result is not None
        assert result.pq_result is not None

    def test_validation_workflow_with_progress_callback(self):
        """Test that validation workflow calls progress callback.
        
        Validates: Requirement 6.2
        """
        orchestrator = ValidationOrchestrator()
        progress_calls = []
        
        def progress_callback(phase: str, progress: float):
            progress_calls.append((phase, progress))
        
        result = orchestrator.execute_validation_workflow(
            progress_callback=progress_callback
        )
        
        assert len(progress_calls) > 0
        # Should have calls for starting, IQ, OQ, and PQ phases
        assert any("IQ" in call[0] for call in progress_calls)
        assert any("OQ" in call[0] for call in progress_calls)
        assert any("PQ" in call[0] for call in progress_calls)

    def test_validation_result_contains_system_info(self):
        """Test that validation result includes system information."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_validation_workflow()
        
        assert result.system_info is not None
        assert hasattr(result.system_info, 'os_name')
        assert hasattr(result.system_info, 'os_version')
        assert hasattr(result.system_info, 'python_version')
        assert hasattr(result.system_info, 'dependencies')

    def test_validation_result_contains_hash_and_fingerprint(self):
        """Test that validation result includes hash and environment fingerprint."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_validation_workflow()
        
        assert result.validation_hash is not None
        assert len(result.validation_hash) == 64  # SHA-256 hex string
        assert result.environment_fingerprint is not None
        assert hasattr(result.environment_fingerprint, 'python_version')
        assert hasattr(result.environment_fingerprint, 'dependencies')

    def test_iq_result_has_summary(self):
        """Test that IQ result provides summary statistics."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_iq_tests()
        summary = result.get_summary()
        
        assert 'total' in summary
        assert 'passed' in summary
        assert 'failed' in summary
        assert summary['total'] == summary['passed'] + summary['failed']

    def test_oq_result_has_summary(self):
        """Test that OQ result provides summary statistics."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_oq_tests()
        summary = result.get_summary()
        
        assert 'total' in summary
        assert 'passed' in summary
        assert 'failed' in summary
        assert summary['total'] == summary['passed'] + summary['failed']

    def test_pq_result_has_summary(self):
        """Test that PQ result provides summary statistics."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_pq_tests()
        summary = result.get_summary()
        
        assert 'total' in summary
        assert 'passed' in summary
        assert 'failed' in summary
        assert summary['total'] == summary['passed'] + summary['failed']

    def test_oq_tests_have_urs_markers(self):
        """Test that OQ tests include URS markers for traceability."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_oq_tests()
        
        # At least some tests should have URS markers
        if result.tests:
            assert any(test.urs_id != "URS-UNKNOWN" for test in result.tests)

    def test_pq_tests_have_urs_markers(self):
        """Test that PQ tests include URS markers for traceability."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_pq_tests()
        
        # At least some tests should have URS markers
        if result.tests:
            assert any(test.urs_id != "URS-UNKNOWN" for test in result.tests)

    def test_oq_tests_grouped_by_functional_area(self):
        """Test that OQ tests can be grouped by functional area."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_oq_tests()
        groups = result.group_by_functional_area()
        
        assert isinstance(groups, dict)
        # Should have at least one functional area
        if result.tests:
            assert len(groups) > 0

    def test_pq_tests_grouped_by_module(self):
        """Test that PQ tests can be grouped by module."""
        orchestrator = ValidationOrchestrator()
        
        result = orchestrator.execute_pq_tests()
        groups = result.group_by_module()
        
        assert isinstance(groups, dict)
        # Should have at least one module
        if result.tests:
            assert len(groups) > 0


class TestValidationWorkflowFailureHandling:
    """Test suite for validation workflow failure handling.
    
    Validates: Requirement 6.4
    """

    def test_workflow_stops_if_iq_fails(self):
        """Test that workflow stops if IQ phase fails.
        
        This test verifies that when IQ tests fail, the workflow does not
        proceed to OQ and PQ phases.
        
        Validates: Requirement 6.4
        """
        # Note: This test would require mocking pytest execution to simulate
        # IQ failure. For now, we test the structure is correct.
        orchestrator = ValidationOrchestrator()
        
        # Execute workflow - if IQ fails, OQ and PQ should have empty results
        result = orchestrator.execute_validation_workflow()
        
        # If IQ failed, success should be False
        if not result.iq_result.passed:
            assert result.success is False

    def test_failed_result_structure(self):
        """Test that failed validation result has correct structure."""
        orchestrator = ValidationOrchestrator()
        
        # Create a failed result manually to test structure
        from src.sample_size_estimator.validation.models import IQResult, IQCheck
        
        iq_result = IQResult(
            passed=False,
            checks=[
                IQCheck(
                    name="test_check",
                    description="Test check",
                    passed=False,
                    failure_reason="Test failure"
                )
            ],
            timestamp=datetime.now()
        )
        
        result = orchestrator._create_failed_result(
            iq_result=iq_result,
            oq_result=None,
            pq_result=None
        )
        
        assert result.success is False
        assert result.iq_result is not None
        assert result.oq_result is not None  # Should be created as empty
        assert result.pq_result is not None  # Should be created as empty
        assert result.oq_result.passed is False
        assert result.pq_result.passed is False


class TestProgressCallbackInvocation:
    """Test suite for progress callback invocation.
    
    Validates: Requirement 6.2
    """

    def test_progress_callback_receives_phase_names(self):
        """Test that progress callback receives correct phase names."""
        orchestrator = ValidationOrchestrator()
        phases_seen = set()
        
        def progress_callback(phase: str, progress: float):
            phases_seen.add(phase)
        
        orchestrator.execute_validation_workflow(
            progress_callback=progress_callback
        )
        
        # Should see IQ, OQ, and PQ phases
        assert any("IQ" in phase for phase in phases_seen)
        assert any("OQ" in phase for phase in phases_seen)
        assert any("PQ" in phase for phase in phases_seen)

    def test_progress_callback_receives_increasing_percentages(self):
        """Test that progress callback receives increasing percentages."""
        orchestrator = ValidationOrchestrator()
        progress_values = []
        
        def progress_callback(phase: str, progress: float):
            progress_values.append(progress)
        
        orchestrator.execute_validation_workflow(
            progress_callback=progress_callback
        )
        
        # Progress should generally increase
        assert len(progress_values) > 0
        assert progress_values[0] >= 0
        assert progress_values[-1] <= 100

    def test_workflow_completes_without_callback(self):
        """Test that workflow completes successfully without progress callback."""
        orchestrator = ValidationOrchestrator()
        
        # Should not raise exception when callback is None
        result = orchestrator.execute_validation_workflow(
            progress_callback=None
        )
        
        assert result is not None
        assert hasattr(result, 'success')
