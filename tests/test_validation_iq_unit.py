"""Unit tests for IQ test execution and result handling.

These tests verify the IQ result aggregation, failure handling, and
edge cases in the IQ testing framework.
"""

from datetime import datetime

import pytest

from src.sample_size_estimator.validation.models import IQCheck, IQResult


def test_iq_result_all_checks_pass() -> None:
    """Test IQ result when all checks pass.
    
    Validates: Requirement 7.6
    """
    checks = [
        IQCheck(
            name="Check 1",
            description="First check",
            passed=True,
            expected_value="expected",
            actual_value="expected"
        ),
        IQCheck(
            name="Check 2",
            description="Second check",
            passed=True,
            expected_value="expected",
            actual_value="expected"
        ),
    ]
    
    result = IQResult(
        passed=True,
        checks=checks,
        timestamp=datetime.now()
    )
    
    assert result.passed
    summary = result.get_summary()
    assert summary["total"] == 2
    assert summary["passed"] == 2
    assert summary["failed"] == 0


def test_iq_result_some_checks_fail() -> None:
    """Test IQ result when some checks fail.
    
    Validates: Requirement 7.6, 7.7
    """
    checks = [
        IQCheck(
            name="Passing Check",
            description="This check passes",
            passed=True,
            expected_value="expected",
            actual_value="expected"
        ),
        IQCheck(
            name="Failing Check",
            description="This check fails",
            passed=False,
            expected_value="expected",
            actual_value="actual",
            failure_reason="Value mismatch"
        ),
    ]
    
    result = IQResult(
        passed=False,
        checks=checks,
        timestamp=datetime.now()
    )
    
    assert not result.passed
    summary = result.get_summary()
    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1


def test_iq_result_all_checks_fail() -> None:
    """Test IQ result when all checks fail.
    
    Validates: Requirement 7.6, 7.7
    """
    checks = [
        IQCheck(
            name="Check 1",
            description="First check",
            passed=False,
            expected_value="expected1",
            actual_value="actual1",
            failure_reason="Mismatch 1"
        ),
        IQCheck(
            name="Check 2",
            description="Second check",
            passed=False,
            expected_value="expected2",
            actual_value="actual2",
            failure_reason="Mismatch 2"
        ),
    ]
    
    result = IQResult(
        passed=False,
        checks=checks,
        timestamp=datetime.now()
    )
    
    assert not result.passed
    summary = result.get_summary()
    assert summary["total"] == 2
    assert summary["passed"] == 0
    assert summary["failed"] == 2


def test_iq_result_empty_checks() -> None:
    """Test IQ result with no checks.
    
    Validates: Requirement 7.6
    """
    result = IQResult(
        passed=True,
        checks=[],
        timestamp=datetime.now()
    )
    
    summary = result.get_summary()
    assert summary["total"] == 0
    assert summary["passed"] == 0
    assert summary["failed"] == 0


def test_iq_check_failure_details() -> None:
    """Test that IQ check captures detailed failure information.
    
    Validates: Requirement 7.7
    """
    check = IQCheck(
        name="Package Version Check",
        description="Verify package version meets requirements",
        passed=False,
        expected_value=">=2.0.0",
        actual_value="1.5.0",
        failure_reason="Installed version 1.5.0 does not meet requirement >=2.0.0"
    )
    
    assert not check.passed
    assert check.expected_value == ">=2.0.0"
    assert check.actual_value == "1.5.0"
    assert check.failure_reason is not None
    assert "1.5.0" in check.failure_reason
    assert "2.0.0" in check.failure_reason


def test_iq_check_success_no_failure_reason() -> None:
    """Test that successful IQ checks have no failure reason.
    
    Validates: Requirement 7.6
    """
    check = IQCheck(
        name="Successful Check",
        description="This check passes",
        passed=True,
        expected_value="expected",
        actual_value="expected"
    )
    
    assert check.passed
    assert check.failure_reason is None


def test_iq_check_optional_values() -> None:
    """Test IQ check with optional expected/actual values.
    
    Validates: Requirement 7.6
    """
    check = IQCheck(
        name="File Exists Check",
        description="Verify file exists",
        passed=True
    )
    
    assert check.passed
    assert check.expected_value is None
    assert check.actual_value is None
    assert check.failure_reason is None


def test_iq_result_timestamp_recorded() -> None:
    """Test that IQ result records timestamp.
    
    Validates: Requirement 7.6
    """
    before = datetime.now()
    
    result = IQResult(
        passed=True,
        checks=[],
        timestamp=datetime.now()
    )
    
    after = datetime.now()
    
    assert before <= result.timestamp <= after


def test_iq_check_with_multiline_failure_reason() -> None:
    """Test IQ check with detailed multiline failure reason.
    
    Validates: Requirement 7.7
    """
    failure_details = """Package version check failed:
    Expected: >=3.0.0
    Actual: 2.5.0
    Please upgrade the package to meet requirements."""
    
    check = IQCheck(
        name="Complex Check",
        description="Check with detailed failure",
        passed=False,
        expected_value=">=3.0.0",
        actual_value="2.5.0",
        failure_reason=failure_details
    )
    
    assert not check.passed
    assert "Expected: >=3.0.0" in check.failure_reason
    assert "Actual: 2.5.0" in check.failure_reason
    assert "upgrade" in check.failure_reason


def test_iq_result_summary_consistency() -> None:
    """Test that IQ result summary is consistent with check list.
    
    Validates: Requirement 7.6
    """
    checks = [
        IQCheck(name=f"Check {i}", description=f"Check {i}", passed=(i % 2 == 0))
        for i in range(10)
    ]
    
    result = IQResult(
        passed=False,  # At least one check failed
        checks=checks,
        timestamp=datetime.now()
    )
    
    summary = result.get_summary()
    assert summary["total"] == 10
    assert summary["passed"] == 5  # Even indices: 0, 2, 4, 6, 8
    assert summary["failed"] == 5  # Odd indices: 1, 3, 5, 7, 9
    assert summary["total"] == summary["passed"] + summary["failed"]


def test_iq_check_name_and_description() -> None:
    """Test that IQ check stores name and description correctly.
    
    Validates: Requirement 7.6
    """
    check = IQCheck(
        name="Python Version Check",
        description="Verify Python version meets minimum requirements (>=3.11)",
        passed=True,
        expected_value=">=3.11",
        actual_value="3.13.5"
    )
    
    assert check.name == "Python Version Check"
    assert "minimum requirements" in check.description
    assert ">=3.11" in check.description
