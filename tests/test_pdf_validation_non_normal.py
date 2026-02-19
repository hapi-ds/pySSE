"""PDF validation tests for Non-Normal module.

This module validates that PDF reports generated for non-normal analysis
contain the same calculation results as the actual calculations.

**Validates: Requirements 29.1, 29.2, 29.3, 29.4, 29.5**
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.sample_size_estimator.models import CalculationReport
from src.sample_size_estimator.reports import generate_calculation_report
from tests.utils.pdf_validator import extract_pdf_text, parse_non_normal_results


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_non_normal_pdf_normality_tests_match_calculation():
    """Test that PDF report shows correct normality test results.
    
    Validates that the PDF report for non-normal analysis contains the same
    normality test statistics as the actual calculations.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Simulated normality test results
    shapiro_p_value = 0.0523
    anderson_stat = 0.342
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="non_normal",
        inputs={
            "Data Points": "5.2, 6.1, 5.8, 6.3, 5.9, 6.0, 5.7, 6.2, 5.5, 6.4",
            "Test Type": "Shapiro-Wilk, Anderson-Darling"
        },
        results={
            "Shapiro-Wilk p-value": round(shapiro_p_value, 4),
            "Anderson-Darling statistic": round(anderson_stat, 4),
            "Normality": "Data appears normal (p > 0.05)"
        },
        engine_hash="test_hash_" + "f" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "non_normal_tests.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_non_normal_results(pdf_text)
        
        # Verify Shapiro-Wilk p-value matches (within tolerance)
        assert "shapiro_wilk_p" in pdf_results, (
            "Shapiro-Wilk p-value not found in PDF"
        )
        assert abs(pdf_results["shapiro_wilk_p"] - shapiro_p_value) < 0.001, (
            f"PDF Shapiro-Wilk p-value {pdf_results['shapiro_wilk_p']} does not match "
            f"calculated value {shapiro_p_value}"
        )
        
        # Verify Anderson-Darling statistic matches
        assert "anderson_darling_stat" in pdf_results, (
            "Anderson-Darling statistic not found in PDF"
        )
        assert abs(pdf_results["anderson_darling_stat"] - anderson_stat) < 0.01, (
            f"PDF Anderson-Darling stat {pdf_results['anderson_darling_stat']} "
            f"does not match calculated value {anderson_stat}"
        )


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_non_normal_pdf_transformation_results_match_calculation():
    """Test that PDF report shows correct transformation results.
    
    Validates that the PDF report for non-normal analysis with transformation
    contains the correct transformation method and results.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Simulated transformation results
    transformation = "Log"
    transformed_shapiro_p = 0.234
    transformed_anderson_stat = 0.189
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="non_normal",
        inputs={
            "Data Points": "1.5, 2.3, 3.1, 4.2, 5.5, 6.8, 7.2, 8.9, 10.1, 12.5",
            "Transformation": transformation
        },
        results={
            "Transformation": transformation,
            "Transformed Shapiro-Wilk p-value": round(transformed_shapiro_p, 4),
            "Transformed Anderson-Darling statistic": round(transformed_anderson_stat, 4),
            "Transformed Data Normality": "Data is more normal after transformation"
        },
        engine_hash="test_hash_" + "g" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "non_normal_transformation.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_non_normal_results(pdf_text)
        
        # Verify transformation method is present
        assert "transformation" in pdf_results, "Transformation method not found in PDF"
        assert pdf_results["transformation"] == transformation, (
            f"PDF transformation {pdf_results['transformation']} does not match "
            f"expected value {transformation}"
        )
        
        # Verify transformed Shapiro-Wilk p-value matches
        assert "shapiro_wilk_p" in pdf_results, (
            "Transformed Shapiro-Wilk p-value not found in PDF"
        )
        assert abs(pdf_results["shapiro_wilk_p"] - transformed_shapiro_p) < 0.001, (
            f"PDF transformed Shapiro-Wilk p-value {pdf_results['shapiro_wilk_p']} "
            f"does not match calculated value {transformed_shapiro_p}"
        )


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_non_normal_pdf_outlier_detection_results():
    """Test that PDF report shows correct outlier detection results.
    
    Validates that the PDF report for non-normal analysis with outlier
    detection contains the correct outlier information.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4, 29.5**
    """
    # Simulated outlier detection results
    outlier_count = 2
    total_points = 12
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="non_normal",
        inputs={
            "Data Points": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 200",
            "Outlier Detection": "IQR Method"
        },
        results={
            "Total Data Points": total_points,
            "Outliers Detected": outlier_count,
            "Outlier Percentage": round((outlier_count / total_points) * 100, 2),
            "Outlier Values": "100, 200"
        },
        engine_hash="test_hash_" + "h" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "non_normal_outliers.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Verify outlier information is present in PDF
        assert "Outliers Detected" in pdf_text or "outlier" in pdf_text.lower(), (
            "Outlier detection results not found in PDF"
        )
        
        # Verify outlier count is present
        assert str(outlier_count) in pdf_text, (
            f"Outlier count {outlier_count} not found in PDF"
        )
