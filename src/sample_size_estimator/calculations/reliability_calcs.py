"""Reliability life testing calculations module.

This module implements reliability calculations including:
- Zero-failure demonstration test duration
- Arrhenius acceleration factors
- Temperature conversions

Requirements: REQ-15, REQ-16
"""

import numpy as np
from scipy import stats

from ..models import ReliabilityInput, ReliabilityResult

# Boltzmann constant in eV/K
BOLTZMANN_CONSTANT = 8.617333262e-5


def calculate_zero_failure_duration(
    confidence: float,
    failures: int = 0
) -> float:
    """Calculate required test duration for zero-failure demonstration.

    Uses the chi-squared distribution to determine the required test duration
    or number of test units for reliability demonstration with a specified
    number of failures.

    Args:
        confidence: Confidence level as percentage (0-100)
        failures: Number of failures (typically 0)

    Returns:
        Test duration (proportional to chi-squared value)

    Formula: Duration ∝ chi^2_{1-C, 2(r+1)}

    Requirements: REQ-15.1, REQ-15.2
    """
    c_decimal = confidence / 100.0
    df = 2 * (failures + 1)

    chi2_value = stats.chi2.ppf(c_decimal, df)

    return float(chi2_value)



def celsius_to_kelvin(celsius: float) -> float:
    """Convert temperature from Celsius to Kelvin.

    Args:
        celsius: Temperature in Celsius

    Returns:
        Temperature in Kelvin

    Formula: K = C + 273.15

    Requirements: REQ-16.3
    """
    return celsius + 273.15



def calculate_acceleration_factor(
    activation_energy: float,
    use_temperature: float,
    test_temperature: float
) -> float:
    """Calculate acceleration factor using Arrhenius equation.

    The Arrhenius equation models the temperature dependence of reaction rates
    and is used in accelerated life testing to relate test conditions to
    use conditions.

    Args:
        activation_energy: Activation energy in eV
        use_temperature: Use temperature in Kelvin
        test_temperature: Test temperature in Kelvin

    Returns:
        Acceleration factor (AF)

    Formula: AF = exp[(Ea/k) * (1/T_use - 1/T_test)]
    where k is Boltzmann's constant (8.617333262e-5 eV/K)

    Raises:
        ValueError: If test temperature <= use temperature

    Requirements: REQ-16.1, REQ-16.2, REQ-16.4
    """
    if test_temperature <= use_temperature:
        raise ValueError("Test temperature must be greater than use temperature")

    exponent = (activation_energy / BOLTZMANN_CONSTANT) * (
        1 / use_temperature - 1 / test_temperature
    )

    af = np.exp(exponent)

    return float(af)



def calculate_reliability(input_data: ReliabilityInput) -> ReliabilityResult:
    """Main entry point for reliability calculations.

    Integrates zero-failure duration calculation with optional acceleration
    factor calculation for accelerated life testing scenarios.

    Args:
        input_data: Validated input parameters

    Returns:
        Complete reliability analysis results including test duration and
        optional acceleration factor

    Requirements: REQ-15, REQ-16
    """
    # Calculate test duration
    duration = calculate_zero_failure_duration(
        input_data.confidence,
        input_data.failures
    )

    # Calculate acceleration factor if parameters provided
    af = None
    if all([
        input_data.activation_energy is not None,
        input_data.use_temperature is not None,
        input_data.test_temperature is not None
    ]):
        # Type narrowing: we've checked all are not None
        assert input_data.activation_energy is not None
        assert input_data.use_temperature is not None
        assert input_data.test_temperature is not None
        af = calculate_acceleration_factor(
            input_data.activation_energy,
            input_data.use_temperature,
            input_data.test_temperature
        )

    # Determine method description
    method = "Chi-squared zero-failure demonstration"
    if af is not None:
        method += " with Arrhenius acceleration"

    return ReliabilityResult(
        test_duration=duration,
        acceleration_factor=af,
        method=method
    )
