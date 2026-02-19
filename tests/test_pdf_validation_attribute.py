"""PDF validation tests for Attribute module.

This module validates that PDF reports generated for attribute analysis
contain the same calculation results as the actual calculations.

**Validates: Requirements 29.1, 29.2, 29.3, 29.4, 29.5**
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.sample_size_estimator.calculations.attribute_calcs import (
    calculate_sample_size_with_failures,
    calculate_sample_size_zero_failures,
)
from src.sample_size_estimator.models import CalculationReport
from src.sample_size_estimator.reports import generate_calculation_report
from tests.utils.pdf_validator import extract_pdf_text, parse_attribute_results


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_attribute_pdf_zero_failure_matches_calculation():
    """Test that PDF report shows correct zero-failure calculation results.
    
    Validates that the PDF report for a zero-failure attribute calculation
    contains the same sample size and parameters as the actual calculation.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Perform calculation
    confidence = 95.0
    reliability = 90.0
    
    sample_size = calculate_sample_size_zero_failures(
        confidence=confidence,
        reliability=reliability
    )
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="attribute",
        inputs={
            "Confidence Level (%)": confidence,
            "Reliability (%)": reliability,
            "Allowable Failures (c)": 0
        },
        results={
            "Required Sample Size": sample_size,
            "Method": "Success Run",
            "Allowable Failures": 0
        },
        engine_hash="test_hash_" + "a" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "attribute_zero_failure.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_attribute_results(pdf_text)
        
        # Verify sample size matches
        assert "sample_size" in pdf_results, "Sample size not found in PDF"
        assert pdf_results["sample_size"] == sample_size, (
            f"PDF sample size {pdf_results['sample_size']} does not match "
            f"calculated value {sample_size}"
        )
        
        # Verify confidence level matches
        assert "confidence" in pdf_results, "Confidence level not found in PDF"
        assert abs(pdf_results["confidence"] - confidence) < 0.1, (
            f"PDF confidence {pdf_results['confidence']} does not match "
            f"input value {confidence}"
        )
        
        # Verify reliability level matches
        assert "reliability" in pdf_results, "Reliability level not found in PDF"
        assert abs(pdf_results["reliability"] - reliability) < 0.1, (
            f"PDF reliability {pdf_results['reliability']} does not match "
            f"input value {reliability}"
        )
        
        # Verify method is Success Run
        assert "method" in pdf_results, "Method not found in PDF"
        assert pdf_results["method"] == "Success Run", (
            f"PDF method {pdf_results['method']} should be 'Success Run'"
        )


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_attribute_pdf_with_failures_matches_calculation():
    """Test that PDF report shows correct binomial calculation results.
    
    Validates that the PDF report for attribute calculation with allowable
    failures contains the same sample size and parameters as the calculation.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Perform calculation
    confidence = 95.0
    reliability = 90.0
    failures = 2
    
    sample_size = calculate_sample_size_with_failures(
        confidence=confidence,
        reliability=reliability,
        allowable_failures=failures
    )
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="attribute",
        inputs={
            "Confidence Level (%)": confidence,
            "Reliability (%)": reliability,
            "Allowable Failures (c)": failures
        },
        results={
            "Required Sample Size": sample_size,
            "Method": "Binomial",
            "Allowable Failures": failures
        },
        engine_hash="test_hash_" + "b" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "attribute_with_failures.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_attribute_results(pdf_text)
        
        # Verify sample size matches
        assert "sample_size" in pdf_results, "Sample size not found in PDF"
        assert pdf_results["sample_size"] == sample_size, (
            f"PDF sample size {pdf_results['sample_size']} does not match "
            f"calculated value {sample_size}"
        )
        
        # Verify allowable failures matches
        assert "failures" in pdf_results, "Allowable failures not found in PDF"
        assert pdf_results["failures"] == failures, (
            f"PDF failures {pdf_results['failures']} does not match "
            f"input value {failures}"
        )
        
        # Verify method is Binomial
        assert "method" in pdf_results, "Method not found in PDF"
        assert pdf_results["method"] == "Binomial", (
            f"PDF method {pdf_results['method']} should be 'Binomial'"
        )


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_attribute_pdf_sensitivity_analysis_matches_calculation():
    """Test that PDF report shows correct sensitivity analysis results.
    
    Validates that the PDF report for sensitivity analysis contains all
    calculated sample sizes for different failure scenarios.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4, 29.5**
    """
    # Perform calculations for sensitivity analysis
    confidence = 95.0
    reliability = 90.0
    
    sensitivity_results = []
    for c in range(4):  # c = 0, 1, 2, 3
        if c == 0:
            sample_size = calculate_sample_size_zero_failures(
                confidence=confidence,
                reliability=reliability
            )
            method = "Success Run"
        else:
            sample_size = calculate_sample_size_with_failures(
                confidence=confidence,
                reliability=reliability,
                allowable_failures=c
            )
            method = "Binomial"
        
        sensitivity_results.append({
            "allowable_failures": c,
            "sample_size": sample_size,
            "method": method
        })
    
    # Generate PDF report with sensitivity analysis
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="attribute",
        inputs={
            "Confidence Level (%)": confidence,
            "Reliability (%)": reliability,
            "Sensitivity Analysis": "Yes"
        },
        results={
            "sensitivity_analysis": sensitivity_results
        },
        engine_hash="test_hash_" + "c" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "attribute_sensitivity.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Verify sensitivity analysis table is present
        assert "Sensitivity Analysis" in pdf_text, (
            "Sensitivity analysis section not found in PDF"
        )
        
        # Verify all sample sizes are present in the PDF
        for result in sensitivity_results:
            sample_size_str = str(result["sample_size"])
            assert sample_size_str in pdf_text, (
                f"Sample size {sample_size_str} for c={result['allowable_failures']} "
                f"not found in PDF"
            )
