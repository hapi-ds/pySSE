"""
Unit tests for report generation module.

Tests PDF creation for calculation reports and validation certificates.
"""

import tempfile
from pathlib import Path
from datetime import datetime
import pytest

from src.sample_size_estimator.reports import (
    generate_calculation_report,
    generate_validation_certificate
)
from src.sample_size_estimator.models import CalculationReport


def test_generate_calculation_report_basic() -> None:
    """Test basic calculation report generation."""
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="attribute",
        inputs={
            "confidence": 95.0,
            "reliability": 90.0,
            "allowable_failures": 0
        },
        results={
            "sample_size": 29,
            "method": "success_run"
        },
        engine_hash="abc123" * 10 + "abcd",
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "test_report.pdf"
        
        result_path = generate_calculation_report(report_data, str(output_path))
        
        # Verify file was created
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0


def test_generate_calculation_report_with_validation_state() -> None:
    """Test report generation with different validation states."""
    # Test with validated state = True
    report_data_validated = CalculationReport(
        timestamp=datetime.now(),
        module="variables",
        inputs={"sample_size": 30, "confidence": 95.0},
        results={"tolerance_factor": 2.14},
        engine_hash="def456" * 10 + "defg",
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "validated_report.pdf"
        result_path = generate_calculation_report(
            report_data_validated,
            str(output_path)
        )
        assert Path(result_path).exists()
    
    # Test with validated state = False
    report_data_unvalidated = CalculationReport(
        timestamp=datetime.now(),
        module="reliability",
        inputs={"confidence": 90.0, "failures": 0},
        results={"test_duration": 4.605},
        engine_hash="ghi789" * 10 + "ghij",
        validated_state=False,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "unvalidated_report.pdf"
        result_path = generate_calculation_report(
            report_data_unvalidated,
            str(output_path)
        )
        assert Path(result_path).exists()


def test_generate_calculation_report_creates_directory() -> None:
    """Test that report generation creates output directory if needed."""
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="attribute",
        inputs={"confidence": 95.0},
        results={"sample_size": 29},
        engine_hash="abc" * 21 + "a",
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create path with non-existent subdirectory
        output_path = Path(tmp_dir) / "reports" / "subdir" / "test.pdf"
        
        result_path = generate_calculation_report(report_data, str(output_path))
        
        # Verify directory was created
        assert Path(result_path).parent.exists()
        assert Path(result_path).exists()


def test_generate_validation_certificate_basic() -> None:
    """Test basic validation certificate generation."""
    test_results = {
        "test_date": datetime.now(),
        "tester": "Test System",
        "system_info": {
            "os": "Windows 10",
            "python_version": "3.13.5",
            "dependencies": {"scipy": "1.14.0", "numpy": "2.0.0"}
        },
        "urs_results": [
            {
                "urs_id": "URS-FUNC_A-01",
                "test_name": "test_attribute_validation",
                "status": "PASS"
            },
            {
                "urs_id": "URS-FUNC_A-02",
                "test_name": "test_success_run_theorem",
                "status": "PASS"
            }
        ],
        "validated_hash": "abc123" * 10 + "abcd",
        "all_passed": True
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "validation_cert.pdf"
        
        result_path = generate_validation_certificate(test_results, str(output_path))
        
        # Verify file was created
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0


def test_generate_validation_certificate_with_failures() -> None:
    """Test validation certificate with failed tests."""
    test_results = {
        "test_date": datetime.now(),
        "tester": "Test System",
        "system_info": {
            "os": "Linux",
            "python_version": "3.13.5",
            "dependencies": {}
        },
        "urs_results": [
            {
                "urs_id": "URS-FUNC_A-01",
                "test_name": "test_attribute_validation",
                "status": "PASS"
            },
            {
                "urs_id": "URS-FUNC_A-02",
                "test_name": "test_success_run_theorem",
                "status": "FAIL"
            },
            {
                "urs_id": "URS-FUNC_A-03",
                "test_name": "test_binomial_calculation",
                "status": "PASS"
            }
        ],
        "validated_hash": "def456" * 10 + "defg",
        "all_passed": False
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "failed_cert.pdf"
        
        result_path = generate_validation_certificate(test_results, str(output_path))
        
        # Verify file was created even with failures
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0


def test_generate_validation_certificate_creates_directory() -> None:
    """Test that certificate generation creates output directory if needed."""
    test_results = {
        "test_date": datetime.now(),
        "tester": "Test System",
        "system_info": {
            "os": "macOS",
            "python_version": "3.13.5",
            "dependencies": {}
        },
        "urs_results": [
            {
                "urs_id": "URS-FUNC_A-01",
                "test_name": "test_example",
                "status": "PASS"
            }
        ],
        "validated_hash": "ghi789" * 10 + "ghij",
        "all_passed": True
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create path with non-existent subdirectory
        output_path = Path(tmp_dir) / "certs" / "validation" / "cert.pdf"
        
        result_path = generate_validation_certificate(test_results, str(output_path))
        
        # Verify directory was created
        assert Path(result_path).parent.exists()
        assert Path(result_path).exists()


def test_generate_validation_certificate_empty_results() -> None:
    """Test validation certificate with no test results."""
    test_results = {
        "test_date": datetime.now(),
        "tester": "Test System",
        "system_info": {
            "os": "Windows",
            "python_version": "3.13.5",
            "dependencies": {}
        },
        "urs_results": [],  # Empty results
        "validated_hash": "abc" * 21 + "a",
        "all_passed": True
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "empty_cert.pdf"
        
        result_path = generate_validation_certificate(test_results, str(output_path))
        
        # Should still create a valid PDF
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0
