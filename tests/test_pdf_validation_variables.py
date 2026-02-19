"""PDF validation tests for Variables module.

This module validates that PDF reports generated for variables analysis
contain the same calculation results as the actual calculations.

**Validates: Requirements 29.1, 29.2, 29.3, 29.4, 29.5**
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.sample_size_estimator.calculations.variables_calcs import (
    calculate_two_sided_tolerance_factor,
    calculate_tolerance_limits,
    calculate_ppk,
)
from src.sample_size_estimator.models import CalculationReport
from src.sample_size_estimator.reports import generate_calculation_report
from tests.utils.pdf_validator import extract_pdf_text, parse_variables_results


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_variables_pdf_tolerance_limits_match_calculation():
    """Test that PDF report shows correct tolerance limit calculation results.
    
    Validates that the PDF report for variables analysis contains the same
    tolerance factor and limits as the actual calculation.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Perform calculation
    confidence = 95.0
    reliability = 90.0
    n = 30
    mean = 10.0
    std_dev = 1.0
    
    tolerance_factor = calculate_two_sided_tolerance_factor(
        n=n,
        confidence=confidence,
        reliability=reliability
    )
    
    lower_tl, upper_tl = calculate_tolerance_limits(
        mean=mean,
        std=std_dev,
        k=tolerance_factor,
        sided="two"
    )
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="variables",
        inputs={
            "Confidence Level (%)": confidence,
            "Reliability (%)": reliability,
            "Sample Size (n)": n,
            "Sample Mean": mean,
            "Sample Standard Deviation": std_dev
        },
        results={
            "Tolerance Factor (k)": round(tolerance_factor, 4),
            "Lower Tolerance Limit": round(lower_tl, 4),
            "Upper Tolerance Limit": round(upper_tl, 4)
        },
        engine_hash="test_hash_" + "d" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "variables_tolerance.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_variables_results(pdf_text)
        
        # Verify tolerance factor matches (within tolerance)
        assert "tolerance_factor" in pdf_results, "Tolerance factor not found in PDF"
        assert abs(pdf_results["tolerance_factor"] - tolerance_factor) < 0.01, (
            f"PDF tolerance factor {pdf_results['tolerance_factor']} does not match "
            f"calculated value {tolerance_factor}"
        )
        
        # Verify lower tolerance limit matches
        assert "lower_tolerance_limit" in pdf_results, (
            "Lower tolerance limit not found in PDF"
        )
        assert abs(pdf_results["lower_tolerance_limit"] - lower_tl) < 0.01, (
            f"PDF lower TL {pdf_results['lower_tolerance_limit']} does not match "
            f"calculated value {lower_tl}"
        )
        
        # Verify upper tolerance limit matches
        assert "upper_tolerance_limit" in pdf_results, (
            "Upper tolerance limit not found in PDF"
        )
        assert abs(pdf_results["upper_tolerance_limit"] - upper_tl) < 0.01, (
            f"PDF upper TL {pdf_results['upper_tolerance_limit']} does not match "
            f"calculated value {upper_tl}"
        )


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_variables_pdf_with_ppk_matches_calculation():
    """Test that PDF report shows correct Ppk calculation results.
    
    Validates that the PDF report for variables analysis with specification
    limits contains the correct Ppk value.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Perform calculation
    confidence = 95.0
    reliability = 90.0
    n = 30
    mean = 10.0
    std_dev = 1.0
    lsl = 7.0
    usl = 13.0
    
    tolerance_factor = calculate_two_sided_tolerance_factor(
        n=n,
        confidence=confidence,
        reliability=reliability
    )
    
    lower_tl, upper_tl = calculate_tolerance_limits(
        mean=mean,
        std=std_dev,
        k=tolerance_factor,
        sided="two"
    )
    
    ppk = calculate_ppk(
        mean=mean,
        std=std_dev,
        lsl=lsl,
        usl=usl
    )
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="variables",
        inputs={
            "Confidence Level (%)": confidence,
            "Reliability (%)": reliability,
            "Sample Size (n)": n,
            "Sample Mean": mean,
            "Sample Standard Deviation": std_dev,
            "Lower Specification Limit (LSL)": lsl,
            "Upper Specification Limit (USL)": usl
        },
        results={
            "Tolerance Factor (k)": round(tolerance_factor, 4),
            "Lower Tolerance Limit": round(lower_tl, 4),
            "Upper Tolerance Limit": round(upper_tl, 4),
            "Ppk": round(ppk, 4)
        },
        engine_hash="test_hash_" + "e" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "variables_ppk.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_variables_results(pdf_text)
        
        # Verify Ppk matches (within tolerance)
        assert "ppk" in pdf_results, "Ppk not found in PDF"
        assert abs(pdf_results["ppk"] - ppk) < 0.01, (
            f"PDF Ppk {pdf_results['ppk']} does not match "
            f"calculated value {ppk}"
        )
        
        # Verify sample size is present
        assert "sample_size" in pdf_results, "Sample size not found in PDF"
        assert pdf_results["sample_size"] == n, (
            f"PDF sample size {pdf_results['sample_size']} does not match "
            f"input value {n}"
        )
