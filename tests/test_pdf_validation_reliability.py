"""PDF validation tests for Reliability module.

This module validates that PDF reports generated for reliability analysis
contain the same calculation results as the actual calculations.

**Validates: Requirements 29.1, 29.2, 29.3, 29.4, 29.5**
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.sample_size_estimator.calculations.reliability_calcs import (
    calculate_zero_failure_duration,
    calculate_acceleration_factor,
)
from src.sample_size_estimator.models import CalculationReport
from src.sample_size_estimator.reports import generate_calculation_report
from tests.utils.pdf_validator import extract_pdf_text, parse_reliability_results


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_reliability_pdf_test_duration_matches_calculation():
    """Test that PDF report shows correct test duration calculation results.
    
    Validates that the PDF report for reliability analysis contains the same
    test duration and acceleration factor as the actual calculation.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Perform calculation
    confidence = 95.0
    failures = 0
    activation_energy = 0.7
    use_temp = 298.15  # 25°C in Kelvin
    test_temp = 358.15  # 85°C in Kelvin
    
    # Calculate acceleration factor
    acceleration_factor = calculate_acceleration_factor(
        activation_energy=activation_energy,
        use_temperature=use_temp,
        test_temperature=test_temp
    )
    
    # Calculate test duration
    test_duration = calculate_zero_failure_duration(
        confidence=confidence,
        failures=failures
    )
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="reliability",
        inputs={
            "Confidence Level (%)": confidence,
            "Number of Failures": failures,
            "Activation Energy (eV)": activation_energy,
            "Use Temperature (K)": use_temp,
            "Test Temperature (K)": test_temp
        },
        results={
            "Test Duration": round(test_duration, 4),
            "Acceleration Factor": round(acceleration_factor, 4),
            "Confidence Level (%)": confidence,
            "Number of Failures": failures
        },
        engine_hash="test_hash_" + "i" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "reliability_test_duration.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_reliability_results(pdf_text)
        
        # Verify test duration matches (within tolerance)
        assert "test_duration" in pdf_results, "Test duration not found in PDF"
        assert abs(pdf_results["test_duration"] - test_duration) < 0.01, (
            f"PDF test duration {pdf_results['test_duration']} does not match "
            f"calculated value {test_duration}"
        )
        
        # Verify acceleration factor matches
        assert "acceleration_factor" in pdf_results, (
            "Acceleration factor not found in PDF"
        )
        assert abs(pdf_results["acceleration_factor"] - acceleration_factor) < 0.01, (
            f"PDF acceleration factor {pdf_results['acceleration_factor']} "
            f"does not match calculated value {acceleration_factor}"
        )
        
        # Verify confidence level matches
        assert "confidence" in pdf_results, "Confidence level not found in PDF"
        assert abs(pdf_results["confidence"] - confidence) < 0.1, (
            f"PDF confidence {pdf_results['confidence']} does not match "
            f"input value {confidence}"
        )
        
        # Verify number of failures matches
        assert "failures" in pdf_results, "Number of failures not found in PDF"
        assert pdf_results["failures"] == failures, (
            f"PDF failures {pdf_results['failures']} does not match "
            f"input value {failures}"
        )


@pytest.mark.pq
@pytest.mark.urs("URS-REP-01")
@pytest.mark.urs("REQ-29")
def test_reliability_pdf_acceleration_factor_matches_calculation():
    """Test that PDF report shows correct acceleration factor.
    
    Validates that the PDF report for reliability analysis with different
    temperatures contains the correct acceleration factor.
    
    **Validates: Requirements 29.1, 29.2, 29.3, 29.4**
    """
    # Perform calculation with different parameters
    confidence = 90.0
    failures = 0
    activation_energy = 0.5
    use_temp = 298.15
    test_temp = 398.15  # Higher test temperature
    
    # Calculate acceleration factor
    acceleration_factor = calculate_acceleration_factor(
        activation_energy=activation_energy,
        use_temperature=use_temp,
        test_temperature=test_temp
    )
    
    # Calculate test duration
    test_duration = calculate_zero_failure_duration(
        confidence=confidence,
        failures=failures
    )
    
    # Generate PDF report
    report_data = CalculationReport(
        timestamp=datetime.now(),
        module="reliability",
        inputs={
            "Confidence Level (%)": confidence,
            "Number of Failures": failures,
            "Activation Energy (eV)": activation_energy,
            "Use Temperature (K)": use_temp,
            "Test Temperature (K)": test_temp
        },
        results={
            "Test Duration": round(test_duration, 4),
            "Acceleration Factor": round(acceleration_factor, 4)
        },
        engine_hash="test_hash_" + "j" * 54,
        validated_state=True,
        app_version="1.0.0"
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "reliability_acceleration.pdf"
        generate_calculation_report(report_data, str(pdf_path))
        
        # Extract PDF content
        pdf_text = extract_pdf_text(pdf_path)
        
        # Parse results from PDF
        pdf_results = parse_reliability_results(pdf_text)
        
        # Verify acceleration factor matches (within tolerance)
        assert "acceleration_factor" in pdf_results, (
            "Acceleration factor not found in PDF"
        )
        assert abs(pdf_results["acceleration_factor"] - acceleration_factor) < 0.1, (
            f"PDF acceleration factor {pdf_results['acceleration_factor']} "
            f"does not match calculated value {acceleration_factor}"
        )
        
        # Verify test duration is present and reasonable
        assert "test_duration" in pdf_results, "Test duration not found in PDF"
        assert pdf_results["test_duration"] > 0, (
            f"PDF test duration {pdf_results['test_duration']} should be positive"
        )
