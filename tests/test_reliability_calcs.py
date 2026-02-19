"""Tests for reliability calculations module.

Tests cover:
- Zero-failure duration calculation
- Arrhenius acceleration factor
- Temperature conversion
- Main entry point calculate_reliability()

Requirements: REQ-15, REQ-16
"""

import pytest
from hypothesis import given, strategies as st
import numpy as np
from scipy import stats

from src.sample_size_estimator.calculations.reliability_calcs import (
    calculate_zero_failure_duration,
    BOLTZMANN_CONSTANT,
)
from src.sample_size_estimator.models import ReliabilityInput, ReliabilityResult


@pytest.mark.oq
@pytest.mark.urs("URS-REL-01")
class TestZeroFailureDuration:
    """Tests for zero-failure duration calculation."""

    def test_zero_failure_duration_basic(self):
        """Test zero-failure duration with typical values."""
        # REQ-15.1, REQ-15.2
        confidence = 95.0
        failures = 0
        
        result = calculate_zero_failure_duration(confidence, failures)
        
        # Verify it's a positive value
        assert result > 0
        
        # Verify it matches chi-squared calculation
        c_decimal = confidence / 100.0
        df = 2 * (failures + 1)
        expected = stats.chi2.ppf(c_decimal, df)
        
        assert abs(result - expected) < 1e-10

    def test_zero_failure_duration_different_confidence_levels(self):
        """Test that higher confidence requires longer duration."""
        # REQ-15.1
        failures = 0
        
        duration_90 = calculate_zero_failure_duration(90.0, failures)
        duration_95 = calculate_zero_failure_duration(95.0, failures)
        duration_99 = calculate_zero_failure_duration(99.0, failures)
        
        # Higher confidence should require longer test duration
        assert duration_90 < duration_95 < duration_99

    def test_zero_failure_duration_with_failures(self):
        """Test duration calculation with non-zero failures."""
        # REQ-15.2
        confidence = 95.0
        
        duration_0 = calculate_zero_failure_duration(confidence, 0)
        duration_1 = calculate_zero_failure_duration(confidence, 1)
        duration_2 = calculate_zero_failure_duration(confidence, 2)
        
        # More allowed failures should require longer test duration
        assert duration_0 < duration_1 < duration_2

    @given(
        confidence=st.floats(min_value=50.0, max_value=99.9),
        failures=st.integers(min_value=0, max_value=10)
    )
    def test_property_zero_failure_duration_correctness(self, confidence, failures):
        """Property 23: Zero-Failure Duration Correctness.
        
        For any confidence level C and failures r, the calculated test duration
        should equal chi^2_{1-C/100, 2(r+1)}
        
        Validates: Requirements 15.1, 15.2
        """
        result = calculate_zero_failure_duration(confidence, failures)
        
        # Calculate expected value using chi-squared distribution
        c_decimal = confidence / 100.0
        df = 2 * (failures + 1)
        expected = stats.chi2.ppf(c_decimal, df)
        
        # Verify the result matches the formula
        assert abs(result - expected) < 1e-10
        
        # Verify result is positive
        assert result > 0

    def test_zero_failure_duration_edge_cases(self):
        """Test edge cases for zero-failure duration."""
        # Very low confidence
        result_low = calculate_zero_failure_duration(1.0, 0)
        assert result_low > 0
        
        # Very high confidence
        result_high = calculate_zero_failure_duration(99.9, 0)
        assert result_high > 0
        assert result_high > result_low



@pytest.mark.oq
@pytest.mark.urs("URS-REL-02")
class TestTemperatureConversion:
    """Tests for temperature conversion helper."""

    def test_celsius_to_kelvin_basic(self):
        """Test basic Celsius to Kelvin conversion."""
        # REQ-16.3
        from src.sample_size_estimator.calculations.reliability_calcs import celsius_to_kelvin
        
        # Test common values
        assert celsius_to_kelvin(0.0) == 273.15
        assert celsius_to_kelvin(100.0) == 373.15
        assert celsius_to_kelvin(25.0) == 298.15
        assert celsius_to_kelvin(-273.15) == 0.0  # Absolute zero

    def test_celsius_to_kelvin_negative(self):
        """Test conversion with negative Celsius values."""
        from src.sample_size_estimator.calculations.reliability_calcs import celsius_to_kelvin
        
        assert abs(celsius_to_kelvin(-40.0) - 233.15) < 1e-10
        assert abs(celsius_to_kelvin(-100.0) - 173.15) < 1e-10

    @given(celsius=st.floats(min_value=-273.15, max_value=1000.0))
    def test_property_celsius_to_kelvin_formula(self, celsius):
        """Property test: Celsius to Kelvin conversion follows K = C + 273.15.
        
        Validates: Requirements 16.3
        """
        from src.sample_size_estimator.calculations.reliability_calcs import celsius_to_kelvin
        
        result = celsius_to_kelvin(celsius)
        expected = celsius + 273.15
        
        assert abs(result - expected) < 1e-10



@pytest.mark.oq
@pytest.mark.urs("URS-REL-02")
class TestAccelerationFactor:
    """Tests for Arrhenius acceleration factor calculation."""

    def test_acceleration_factor_basic(self):
        """Test acceleration factor with typical values."""
        # REQ-16.1, REQ-16.2
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        # Typical values for semiconductor devices
        activation_energy = 0.7  # eV
        use_temperature = 298.15  # 25°C in Kelvin
        test_temperature = 398.15  # 125°C in Kelvin
        
        result = calculate_acceleration_factor(
            activation_energy, use_temperature, test_temperature
        )
        
        # Verify it's greater than 1 (acceleration)
        assert result > 1
        
        # Verify it's a reasonable value (typically 10-1000 for these conditions)
        assert 10 < result < 1000

    def test_acceleration_factor_higher_test_temp_increases_af(self):
        """Test that higher test temperature increases acceleration factor."""
        # REQ-16.1
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        activation_energy = 0.7
        use_temperature = 298.15
        
        af_100 = calculate_acceleration_factor(activation_energy, use_temperature, 373.15)
        af_125 = calculate_acceleration_factor(activation_energy, use_temperature, 398.15)
        af_150 = calculate_acceleration_factor(activation_energy, use_temperature, 423.15)
        
        # Higher test temperature should give higher acceleration
        assert af_100 < af_125 < af_150

    def test_acceleration_factor_temperature_validation(self):
        """Test that test temperature must be greater than use temperature."""
        # REQ-16.4
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        activation_energy = 0.7
        use_temperature = 398.15
        test_temperature = 298.15  # Lower than use temperature
        
        with pytest.raises(ValueError, match="Test temperature must be greater than use temperature"):
            calculate_acceleration_factor(activation_energy, use_temperature, test_temperature)

    def test_acceleration_factor_equal_temperatures(self):
        """Test that equal temperatures are rejected."""
        # REQ-16.4
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        activation_energy = 0.7
        temperature = 298.15
        
        with pytest.raises(ValueError, match="Test temperature must be greater than use temperature"):
            calculate_acceleration_factor(activation_energy, temperature, temperature)

    @given(
        activation_energy=st.floats(min_value=0.1, max_value=2.0),
        use_temperature=st.floats(min_value=250.0, max_value=350.0),
        temp_diff=st.floats(min_value=10.0, max_value=200.0)
    )
    def test_property_arrhenius_formula_correctness(
        self, activation_energy, use_temperature, temp_diff
    ):
        """Property 24: Arrhenius Acceleration Factor Correctness.
        
        For any activation energy Ea, use temperature T_use, and test temperature
        T_test (where T_test > T_use), the acceleration factor should equal
        exp[(Ea/k_B) * (1/T_use - 1/T_test)] where k_B is Boltzmann's constant.
        
        Validates: Requirements 16.1, 16.2
        """
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        test_temperature = use_temperature + temp_diff
        
        result = calculate_acceleration_factor(
            activation_energy, use_temperature, test_temperature
        )
        
        # Calculate expected value using Arrhenius equation
        exponent = (activation_energy / BOLTZMANN_CONSTANT) * (
            1 / use_temperature - 1 / test_temperature
        )
        expected = np.exp(exponent)
        
        # Verify the result matches the formula
        assert abs(result - expected) < 1e-10
        
        # Verify result is greater than 1 (acceleration)
        assert result > 1

    @given(
        activation_energy=st.floats(min_value=0.1, max_value=2.0),
        use_temperature=st.floats(min_value=250.0, max_value=400.0),
        test_temperature=st.floats(min_value=250.0, max_value=400.0)
    )
    def test_property_temperature_validation(
        self, activation_energy, use_temperature, test_temperature
    ):
        """Property 25: Temperature Validation.
        
        For any acceleration factor calculation, the system should accept
        temperatures if and only if T_test > T_use and both are positive (in Kelvin).
        
        Validates: Requirements 16.3, 16.4
        """
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        if test_temperature > use_temperature:
            # Should succeed
            result = calculate_acceleration_factor(
                activation_energy, use_temperature, test_temperature
            )
            assert result > 0
        else:
            # Should raise ValueError
            with pytest.raises(ValueError):
                calculate_acceleration_factor(
                    activation_energy, use_temperature, test_temperature
                )

    def test_acceleration_factor_known_values(self):
        """Test acceleration factor with known reference values."""
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_acceleration_factor,
        )
        
        # Example from reliability engineering literature
        # Ea = 0.7 eV, T_use = 25°C (298.15K), T_test = 125°C (398.15K)
        activation_energy = 0.7
        use_temperature = 298.15
        test_temperature = 398.15
        
        result = calculate_acceleration_factor(
            activation_energy, use_temperature, test_temperature
        )
        
        # Calculate expected value manually
        exponent = (0.7 / BOLTZMANN_CONSTANT) * (1/298.15 - 1/398.15)
        expected = np.exp(exponent)
        
        assert abs(result - expected) < 1e-10



@pytest.mark.oq
@pytest.mark.urs("URS-REL-03")
class TestCalculateReliability:
    """Tests for main entry point calculate_reliability()."""

    def test_calculate_reliability_without_acceleration(self):
        """Test reliability calculation without acceleration factor."""
        # REQ-15
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability,
        )
        
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0
        )
        
        result = calculate_reliability(input_data)
        
        assert result.test_duration > 0
        assert result.acceleration_factor is None
        assert "Chi-squared zero-failure demonstration" in result.method
        assert "Arrhenius" not in result.method

    def test_calculate_reliability_with_acceleration(self):
        """Test reliability calculation with acceleration factor."""
        # REQ-15, REQ-16
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability,
        )
        
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0,
            activation_energy=0.7,
            use_temperature=298.15,
            test_temperature=398.15
        )
        
        result = calculate_reliability(input_data)
        
        assert result.test_duration > 0
        assert result.acceleration_factor is not None
        assert result.acceleration_factor > 1
        assert "Chi-squared zero-failure demonstration" in result.method
        assert "Arrhenius acceleration" in result.method

    def test_calculate_reliability_partial_acceleration_params(self):
        """Test that partial acceleration parameters don't calculate AF."""
        # REQ-16
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability,
        )
        
        # Only activation energy provided
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0,
            activation_energy=0.7
        )
        
        result = calculate_reliability(input_data)
        
        assert result.test_duration > 0
        assert result.acceleration_factor is None

    def test_calculate_reliability_with_failures(self):
        """Test reliability calculation with non-zero failures."""
        # REQ-15
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability,
        )
        
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=2
        )
        
        result = calculate_reliability(input_data)
        
        assert result.test_duration > 0
        assert result.acceleration_factor is None

    def test_calculate_reliability_validates_temperatures(self):
        """Test that temperature validation is enforced."""
        # REQ-16.4
        
        # Test temperature <= use temperature should fail at model validation
        with pytest.raises(ValueError, match="Test temperature must be greater than use temperature"):
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=0,
                activation_energy=0.7,
                use_temperature=398.15,
                test_temperature=298.15
            )

    def test_calculate_reliability_result_structure(self):
        """Test that result has correct structure."""
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability,
        )
        
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0,
            activation_energy=0.7,
            use_temperature=298.15,
            test_temperature=398.15
        )
        
        result = calculate_reliability(input_data)
        
        # Verify result is a ReliabilityResult
        assert isinstance(result, ReliabilityResult)
        assert hasattr(result, 'test_duration')
        assert hasattr(result, 'acceleration_factor')
        assert hasattr(result, 'method')

    @given(
        confidence=st.floats(min_value=50.0, max_value=99.9),
        failures=st.integers(min_value=0, max_value=5)
    )
    def test_property_calculate_reliability_integration(self, confidence, failures):
        """Property test: Integration of duration and acceleration calculations.
        
        Validates: Requirements 15, 16
        """
        from src.sample_size_estimator.calculations.reliability_calcs import (
            calculate_reliability,
        )
        
        # Test without acceleration
        input_data = ReliabilityInput(
            confidence=confidence,
            reliability=90.0,
            failures=failures
        )
        
        result = calculate_reliability(input_data)
        
        assert result.test_duration > 0
        assert result.acceleration_factor is None
        assert isinstance(result.method, str)
        assert len(result.method) > 0
