"""Unit tests for PQ (Performance Qualification) test execution.

This module tests PQ result aggregation, failure handling, and workflow
description extraction.

**Validates: Requirements 9.6, 9.7**
"""

import pytest

from src.sample_size_estimator.validation.models import PQTest, PQResult


def test_pq_result_aggregation_all_pass():
    """Test PQ result aggregation when all tests pass.
    
    **Validates: Requirement 9.6**
    """
    # Create PQ test results with all passing
    tests = [
        PQTest(
            test_name="test_attribute_tab_renders",
            urs_id="URS-VAL-03",
            urs_requirement="UI shall display attribute analysis tab",
            module="Attribute",
            workflow_description="Navigate to attribute tab and verify rendering",
            passed=True,
            failure_reason=None
        ),
        PQTest(
            test_name="test_variables_calculation",
            urs_id="URS-VAL-04",
            urs_requirement="UI shall calculate variables tolerance limits",
            module="Variables",
            workflow_description="Enter parameters and calculate tolerance limits",
            passed=True,
            failure_reason=None
        ),
        PQTest(
            test_name="test_reliability_workflow",
            urs_id="URS-VAL-05",
            urs_requirement="UI shall calculate reliability test duration",
            module="Reliability",
            workflow_description="Enter Arrhenius parameters and calculate duration",
            passed=True,
            failure_reason=None
        )
    ]
    
    # Create PQ result
    from datetime import datetime
    pq_result = PQResult(
        passed=True,
        tests=tests,
        timestamp=datetime.now()
    )
    
    # Verify aggregation
    summary = pq_result.get_summary()
    assert summary["total"] == 3
    assert summary["passed"] == 3
    assert summary["failed"] == 0
    assert pq_result.passed is True


def test_pq_result_aggregation_with_failures():
    """Test PQ result aggregation when some tests fail.
    
    **Validates: Requirement 9.7**
    """
    # Create PQ test results with some failures
    tests = [
        PQTest(
            test_name="test_attribute_tab_renders",
            urs_id="URS-VAL-03",
            urs_requirement="UI shall display attribute analysis tab",
            module="Attribute",
            workflow_description="Navigate to attribute tab and verify rendering",
            passed=True,
            failure_reason=None
        ),
        PQTest(
            test_name="test_variables_calculation",
            urs_id="URS-VAL-04",
            urs_requirement="UI shall calculate variables tolerance limits",
            module="Variables",
            workflow_description="Enter parameters and calculate tolerance limits",
            passed=False,
            failure_reason="Calculation button not found"
        ),
        PQTest(
            test_name="test_reliability_workflow",
            urs_id="URS-VAL-05",
            urs_requirement="UI shall calculate reliability test duration",
            module="Reliability",
            workflow_description="Enter Arrhenius parameters and calculate duration",
            passed=False,
            failure_reason="Results section did not appear"
        )
    ]
    
    # Create PQ result
    from datetime import datetime
    pq_result = PQResult(
        passed=False,
        tests=tests,
        timestamp=datetime.now()
    )
    
    # Verify aggregation
    summary = pq_result.get_summary()
    assert summary["total"] == 3
    assert summary["passed"] == 1
    assert summary["failed"] == 2
    assert pq_result.passed is False


def test_pq_result_group_by_module():
    """Test grouping PQ tests by analysis module.
    
    **Validates: Requirement 9.2**
    """
    # Create PQ test results for different modules
    tests = [
        PQTest(
            test_name="test_attribute_zero_failure",
            urs_id="URS-VAL-03",
            urs_requirement="UI shall calculate attribute sample size",
            module="Attribute",
            workflow_description="Calculate zero-failure sample size",
            passed=True,
            failure_reason=None
        ),
        PQTest(
            test_name="test_attribute_sensitivity",
            urs_id="URS-VAL-03",
            urs_requirement="UI shall display sensitivity analysis",
            module="Attribute",
            workflow_description="Display sensitivity analysis results",
            passed=True,
            failure_reason=None
        ),
        PQTest(
            test_name="test_variables_tolerance",
            urs_id="URS-VAL-04",
            urs_requirement="UI shall calculate tolerance limits",
            module="Variables",
            workflow_description="Calculate tolerance limits from sample data",
            passed=True,
            failure_reason=None
        ),
        PQTest(
            test_name="test_non_normal_transformation",
            urs_id="URS-VAL-06",
            urs_requirement="UI shall apply data transformations",
            module="Non-Normal",
            workflow_description="Apply log transformation to data",
            passed=True,
            failure_reason=None
        )
    ]
    
    # Create PQ result
    from datetime import datetime
    pq_result = PQResult(
        passed=True,
        tests=tests,
        timestamp=datetime.now()
    )
    
    # Group by module
    grouped = pq_result.group_by_module()
    
    # Verify grouping
    assert "Attribute" in grouped
    assert len(grouped["Attribute"]) == 2
    assert "Variables" in grouped
    assert len(grouped["Variables"]) == 1
    assert "Non-Normal" in grouped
    assert len(grouped["Non-Normal"]) == 1


def test_pq_failure_handling():
    """Test that PQ failures are properly captured with details.
    
    **Validates: Requirement 9.7**
    """
    # Create a failed PQ test
    failed_test = PQTest(
        test_name="test_attribute_invalid_input",
        urs_id="URS-VAL-07",
        urs_requirement="UI shall display error for invalid inputs",
        module="Attribute",
        workflow_description="Enter invalid confidence level and verify error",
        passed=False,
        failure_reason="Error message did not appear within timeout"
    )
    
    # Verify failure details are captured
    assert failed_test.passed is False
    assert failed_test.failure_reason is not None
    assert "timeout" in failed_test.failure_reason.lower()
    assert failed_test.test_name == "test_attribute_invalid_input"
    assert failed_test.urs_id == "URS-VAL-07"


def test_pq_workflow_description_extraction():
    """Test that workflow descriptions are properly extracted and stored.
    
    **Validates: Requirement 13.4**
    """
    # Create PQ tests with workflow descriptions
    test_with_workflow = PQTest(
        test_name="test_complete_attribute_workflow",
        urs_id="URS-VAL-03",
        urs_requirement="UI shall support complete attribute analysis workflow",
        module="Attribute",
        workflow_description=(
            "1. Navigate to Attribute tab\n"
            "2. Enter confidence level (95%)\n"
            "3. Enter reliability level (90%)\n"
            "4. Click calculate button\n"
            "5. Verify results display"
        ),
        passed=True,
        failure_reason=None
    )
    
    # Verify workflow description is captured
    assert test_with_workflow.workflow_description is not None
    assert "Navigate to Attribute tab" in test_with_workflow.workflow_description
    assert "Click calculate button" in test_with_workflow.workflow_description
    assert "Verify results display" in test_with_workflow.workflow_description


def test_pq_result_empty_tests():
    """Test PQ result with no tests.
    
    **Validates: Requirement 9.6**
    """
    # Create PQ result with empty test list
    from datetime import datetime
    pq_result = PQResult(
        passed=True,
        tests=[],
        timestamp=datetime.now()
    )
    
    # Verify summary handles empty list
    summary = pq_result.get_summary()
    assert summary["total"] == 0
    assert summary["passed"] == 0
    assert summary["failed"] == 0


def test_pq_result_timestamp():
    """Test that PQ result includes execution timestamp.
    
    **Validates: Requirement 13.6**
    """
    # Create PQ result
    from datetime import datetime
    test_time = datetime.now()
    
    pq_result = PQResult(
        passed=True,
        tests=[],
        timestamp=test_time
    )
    
    # Verify timestamp is captured
    assert pq_result.timestamp == test_time
    assert isinstance(pq_result.timestamp, datetime)


def test_pq_test_urs_traceability():
    """Test that PQ tests maintain URS traceability.
    
    **Validates: Requirements 14.1, 14.2, 14.3**
    """
    # Create PQ test with URS information
    pq_test = PQTest(
        test_name="test_variables_ppk_calculation",
        urs_id="URS-FUNC_B-05",
        urs_requirement="System shall calculate Ppk from sample data and spec limits",
        module="Variables",
        workflow_description="Enter sample data and spec limits, verify Ppk calculation",
        passed=True,
        failure_reason=None
    )
    
    # Verify URS traceability
    assert pq_test.urs_id == "URS-FUNC_B-05"
    assert pq_test.urs_requirement is not None
    assert "Ppk" in pq_test.urs_requirement
    assert pq_test.test_name == "test_variables_ppk_calculation"
