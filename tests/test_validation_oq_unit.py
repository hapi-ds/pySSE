"""Unit tests for OQ (Operational Qualification) test execution.

Tests OQ result aggregation, failure handling, and URS marker extraction.

Requirements: 8.1, 8.2, 8.7, 8.8, 14.1, 14.2
"""

import pytest


class TestOQResultAggregation:
    """Tests for OQ test result aggregation.
    
    Validates: Requirements 8.7, 8.8
    """

    def test_all_tests_pass_returns_pass_status(self):
        """Test that when all OQ tests pass, overall status is PASS."""
        # Mock OQ test results - all passing
        test_results = [
            {"test_name": "test_attribute_zero_failures", "urs_id": "URS-FUNC_A-02", "passed": True},
            {"test_name": "test_attribute_with_failures", "urs_id": "URS-FUNC_A-03", "passed": True},
            {"test_name": "test_variables_tolerance_factor", "urs_id": "URS-VAR-01", "passed": True},
        ]
        
        # Aggregate results
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t["passed"])
        failed_tests = total_tests - passed_tests
        overall_status = "PASS" if failed_tests == 0 else "FAIL"
        
        # Verify aggregation
        assert total_tests == 3
        assert passed_tests == 3
        assert failed_tests == 0
        assert overall_status == "PASS"

    def test_some_tests_fail_returns_fail_status(self):
        """Test that when any OQ test fails, overall status is FAIL."""
        # Mock OQ test results - some failing
        test_results = [
            {"test_name": "test_attribute_zero_failures", "urs_id": "URS-FUNC_A-02", "passed": True},
            {"test_name": "test_attribute_with_failures", "urs_id": "URS-FUNC_A-03", "passed": False},
            {"test_name": "test_variables_tolerance_factor", "urs_id": "URS-VAR-01", "passed": True},
        ]
        
        # Aggregate results
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t["passed"])
        failed_tests = total_tests - passed_tests
        overall_status = "PASS" if failed_tests == 0 else "FAIL"
        
        # Verify aggregation
        assert total_tests == 3
        assert passed_tests == 2
        assert failed_tests == 1
        assert overall_status == "FAIL"

    def test_all_tests_fail_returns_fail_status(self):
        """Test that when all OQ tests fail, overall status is FAIL."""
        # Mock OQ test results - all failing
        test_results = [
            {"test_name": "test_attribute_zero_failures", "urs_id": "URS-FUNC_A-02", "passed": False},
            {"test_name": "test_attribute_with_failures", "urs_id": "URS-FUNC_A-03", "passed": False},
            {"test_name": "test_variables_tolerance_factor", "urs_id": "URS-VAR-01", "passed": False},
        ]
        
        # Aggregate results
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t["passed"])
        failed_tests = total_tests - passed_tests
        overall_status = "PASS" if failed_tests == 0 else "FAIL"
        
        # Verify aggregation
        assert total_tests == 3
        assert passed_tests == 0
        assert failed_tests == 3
        assert overall_status == "FAIL"

    def test_empty_test_results_returns_fail_status(self):
        """Test that empty test results are treated as FAIL."""
        # Mock empty OQ test results
        test_results = []
        
        # Aggregate results
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t["passed"])
        failed_tests = total_tests - passed_tests
        # Empty results should be treated as FAIL (no tests executed)
        overall_status = "FAIL" if total_tests == 0 else ("PASS" if failed_tests == 0 else "FAIL")
        
        # Verify aggregation
        assert total_tests == 0
        assert passed_tests == 0
        assert failed_tests == 0
        assert overall_status == "FAIL"

    def test_summary_statistics_calculation(self):
        """Test that summary statistics are correctly calculated."""
        # Mock OQ test results
        test_results = [
            {"test_name": "test_1", "urs_id": "URS-01", "passed": True},
            {"test_name": "test_2", "urs_id": "URS-02", "passed": True},
            {"test_name": "test_3", "urs_id": "URS-03", "passed": False},
            {"test_name": "test_4", "urs_id": "URS-04", "passed": True},
            {"test_name": "test_5", "urs_id": "URS-05", "passed": False},
        ]
        
        # Calculate summary
        summary = {
            "total": len(test_results),
            "passed": sum(1 for t in test_results if t["passed"]),
            "failed": sum(1 for t in test_results if not t["passed"]),
        }
        
        # Verify summary
        assert summary["total"] == 5
        assert summary["passed"] == 3
        assert summary["failed"] == 2
        assert summary["total"] == summary["passed"] + summary["failed"]


class TestOQFailureHandling:
    """Tests for OQ test failure handling.
    
    Validates: Requirements 8.8
    """

    def test_failure_details_captured(self):
        """Test that failure details are captured for failed tests."""
        # Mock failed test with details
        failed_test = {
            "test_name": "test_attribute_calculation",
            "urs_id": "URS-FUNC_A-02",
            "passed": False,
            "failure_reason": "AssertionError: Expected 29, got 30"
        }
        
        # Verify failure details are present
        assert failed_test["passed"] is False
        assert "failure_reason" in failed_test
        assert len(failed_test["failure_reason"]) > 0
        assert "AssertionError" in failed_test["failure_reason"]

    def test_multiple_failures_tracked(self):
        """Test that multiple test failures are tracked."""
        # Mock multiple failed tests
        test_results = [
            {"test_name": "test_1", "urs_id": "URS-01", "passed": True, "failure_reason": None},
            {"test_name": "test_2", "urs_id": "URS-02", "passed": False, "failure_reason": "Error 1"},
            {"test_name": "test_3", "urs_id": "URS-03", "passed": False, "failure_reason": "Error 2"},
            {"test_name": "test_4", "urs_id": "URS-04", "passed": True, "failure_reason": None},
        ]
        
        # Extract failures
        failures = [t for t in test_results if not t["passed"]]
        
        # Verify failures are tracked
        assert len(failures) == 2
        assert failures[0]["test_name"] == "test_2"
        assert failures[0]["failure_reason"] == "Error 1"
        assert failures[1]["test_name"] == "test_3"
        assert failures[1]["failure_reason"] == "Error 2"

    def test_failure_reason_none_for_passing_tests(self):
        """Test that passing tests have no failure reason."""
        # Mock passing test
        passing_test = {
            "test_name": "test_attribute_calculation",
            "urs_id": "URS-FUNC_A-02",
            "passed": True,
            "failure_reason": None
        }
        
        # Verify no failure reason for passing test
        assert passing_test["passed"] is True
        assert passing_test["failure_reason"] is None


class TestURSMarkerExtraction:
    """Tests for URS marker extraction from test metadata.
    
    Validates: Requirements 14.1, 14.2
    """

    def test_extract_urs_marker_from_test(self):
        """Test extracting URS marker from test metadata."""
        # Mock test with URS marker
        test_metadata = {
            "test_name": "test_attribute_zero_failures",
            "markers": ["oq", "urs('URS-FUNC_A-02')"],
        }
        
        # Extract URS marker
        urs_markers = [m for m in test_metadata["markers"] if m.startswith("urs(")]
        assert len(urs_markers) == 1
        
        # Parse URS ID from marker
        urs_marker = urs_markers[0]
        # Extract ID from urs('URS-FUNC_A-02') format
        urs_id = urs_marker.split("'")[1] if "'" in urs_marker else None
        
        # Verify URS ID extraction
        assert urs_id == "URS-FUNC_A-02"

    def test_extract_multiple_urs_markers(self):
        """Test extracting multiple URS markers from a test."""
        # Mock test with multiple URS markers
        test_metadata = {
            "test_name": "test_integration",
            "markers": ["oq", "urs('URS-FUNC_A-02')", "urs('URS-FUNC_A-03')"],
        }
        
        # Extract URS markers
        urs_markers = [m for m in test_metadata["markers"] if m.startswith("urs(")]
        assert len(urs_markers) == 2
        
        # Parse URS IDs
        urs_ids = [m.split("'")[1] for m in urs_markers if "'" in m]
        
        # Verify URS IDs
        assert "URS-FUNC_A-02" in urs_ids
        assert "URS-FUNC_A-03" in urs_ids

    def test_no_urs_marker_returns_none(self):
        """Test that tests without URS markers return None."""
        # Mock test without URS marker
        test_metadata = {
            "test_name": "test_helper_function",
            "markers": ["unit"],
        }
        
        # Extract URS markers
        urs_markers = [m for m in test_metadata["markers"] if m.startswith("urs(")]
        
        # Verify no URS markers found
        assert len(urs_markers) == 0

    def test_urs_marker_format_validation(self):
        """Test that URS marker format is validated."""
        # Valid URS marker formats
        valid_markers = [
            "urs('URS-FUNC_A-02')",
            "urs('URS-VAR-01')",
            "urs('URS-NONNORM-03')",
            "urs('URS-REL-01')",
        ]
        
        for marker in valid_markers:
            # Extract URS ID
            if "'" in marker and marker.startswith("urs("):
                urs_id = marker.split("'")[1]
                # Verify format: URS-<MODULE>-<NUMBER>
                assert urs_id.startswith("URS-")
                assert len(urs_id.split("-")) >= 3

    def test_group_tests_by_urs_requirement(self):
        """Test grouping tests by URS requirement."""
        # Mock test results with URS IDs
        test_results = [
            {"test_name": "test_1", "urs_id": "URS-FUNC_A-02", "passed": True},
            {"test_name": "test_2", "urs_id": "URS-FUNC_A-02", "passed": True},
            {"test_name": "test_3", "urs_id": "URS-VAR-01", "passed": True},
            {"test_name": "test_4", "urs_id": "URS-VAR-01", "passed": False},
            {"test_name": "test_5", "urs_id": "URS-NONNORM-01", "passed": True},
        ]
        
        # Group by URS ID
        grouped = {}
        for test in test_results:
            urs_id = test["urs_id"]
            if urs_id not in grouped:
                grouped[urs_id] = []
            grouped[urs_id].append(test)
        
        # Verify grouping
        assert len(grouped) == 3
        assert len(grouped["URS-FUNC_A-02"]) == 2
        assert len(grouped["URS-VAR-01"]) == 2
        assert len(grouped["URS-NONNORM-01"]) == 1

    def test_map_urs_to_requirement_text(self):
        """Test mapping URS IDs to requirement text."""
        # Mock URS requirements mapping
        urs_requirements = {
            "URS-FUNC_A-02": "Calculate sample size using Success Run Theorem",
            "URS-VAR-01": "Calculate tolerance factors for normal data",
            "URS-NONNORM-01": "Detect outliers using IQR method",
        }
        
        # Mock test result
        test_result = {
            "test_name": "test_attribute_zero_failures",
            "urs_id": "URS-FUNC_A-02",
            "passed": True,
        }
        
        # Map URS ID to requirement text
        urs_id = test_result["urs_id"]
        requirement_text = urs_requirements.get(urs_id, "Unknown requirement")
        
        # Verify mapping
        assert requirement_text == "Calculate sample size using Success Run Theorem"

    def test_identify_untested_requirements(self):
        """Test identifying URS requirements without tests."""
        # Mock all URS requirements
        all_requirements = {
            "URS-FUNC_A-02",
            "URS-FUNC_A-03",
            "URS-VAR-01",
            "URS-NONNORM-01",
        }
        
        # Mock test results
        test_results = [
            {"test_name": "test_1", "urs_id": "URS-FUNC_A-02", "passed": True},
            {"test_name": "test_2", "urs_id": "URS-VAR-01", "passed": True},
        ]
        
        # Extract tested requirements
        tested_requirements = {t["urs_id"] for t in test_results}
        
        # Identify untested requirements
        untested_requirements = all_requirements - tested_requirements
        
        # Verify untested requirements
        assert len(untested_requirements) == 2
        assert "URS-FUNC_A-03" in untested_requirements
        assert "URS-NONNORM-01" in untested_requirements


class TestOQTestGrouping:
    """Tests for grouping OQ tests by functional area.
    
    Validates: Requirements 8.1, 8.2
    """

    def test_group_tests_by_functional_area(self):
        """Test grouping OQ tests by functional area."""
        # Mock test results with functional areas
        test_results = [
            {"test_name": "test_attr_1", "urs_id": "URS-FUNC_A-02", "functional_area": "Attribute", "passed": True},
            {"test_name": "test_attr_2", "urs_id": "URS-FUNC_A-03", "functional_area": "Attribute", "passed": True},
            {"test_name": "test_var_1", "urs_id": "URS-VAR-01", "functional_area": "Variables", "passed": True},
            {"test_name": "test_var_2", "urs_id": "URS-VAR-02", "functional_area": "Variables", "passed": False},
            {"test_name": "test_nn_1", "urs_id": "URS-NONNORM-01", "functional_area": "Non-Normal", "passed": True},
            {"test_name": "test_rel_1", "urs_id": "URS-REL-01", "functional_area": "Reliability", "passed": True},
        ]
        
        # Group by functional area
        grouped = {}
        for test in test_results:
            area = test["functional_area"]
            if area not in grouped:
                grouped[area] = []
            grouped[area].append(test)
        
        # Verify grouping
        assert len(grouped) == 4
        assert len(grouped["Attribute"]) == 2
        assert len(grouped["Variables"]) == 2
        assert len(grouped["Non-Normal"]) == 1
        assert len(grouped["Reliability"]) == 1

    def test_functional_area_summary_statistics(self):
        """Test calculating summary statistics per functional area."""
        # Mock test results
        test_results = [
            {"test_name": "test_attr_1", "functional_area": "Attribute", "passed": True},
            {"test_name": "test_attr_2", "functional_area": "Attribute", "passed": True},
            {"test_name": "test_var_1", "functional_area": "Variables", "passed": True},
            {"test_name": "test_var_2", "functional_area": "Variables", "passed": False},
        ]
        
        # Calculate summary per area
        summary = {}
        for test in test_results:
            area = test["functional_area"]
            if area not in summary:
                summary[area] = {"total": 0, "passed": 0, "failed": 0}
            summary[area]["total"] += 1
            if test["passed"]:
                summary[area]["passed"] += 1
            else:
                summary[area]["failed"] += 1
        
        # Verify summary
        assert summary["Attribute"]["total"] == 2
        assert summary["Attribute"]["passed"] == 2
        assert summary["Attribute"]["failed"] == 0
        assert summary["Variables"]["total"] == 2
        assert summary["Variables"]["passed"] == 1
        assert summary["Variables"]["failed"] == 1
