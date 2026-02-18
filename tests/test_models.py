"""Unit tests for data models.

Tests validation for valid inputs, rejection of invalid inputs
(negative values, out-of-range percentages), and LSL < USL validation.

Requirements: REQ-19
"""

import pytest
from pydantic import ValidationError

from sample_size_estimator.models import (
    AttributeInput,
    ReliabilityInput,
    VariablesInput,
)


class TestAttributeInput:
    """Test AttributeInput model validation."""

    def test_valid_inputs(self):
        """Test that valid inputs are accepted."""
        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=0
        )
        
        assert input_data.confidence == 95.0
        assert input_data.reliability == 90.0
        assert input_data.allowable_failures == 0

    def test_valid_inputs_without_failures(self):
        """Test that allowable_failures can be None."""
        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0
        )
        
        assert input_data.allowable_failures is None

    def test_confidence_zero_rejected(self):
        """Test that confidence of 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=0.0,
                reliability=90.0
            )
        
        assert "Value must be between 0 and 100 (exclusive)" in str(exc_info.value)

    def test_confidence_hundred_rejected(self):
        """Test that confidence of 100 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=100.0,
                reliability=90.0
            )
        
        assert "Value must be between 0 and 100 (exclusive)" in str(exc_info.value)

    def test_confidence_negative_rejected(self):
        """Test that negative confidence is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=-5.0,
                reliability=90.0
            )
        
        assert "greater than or equal to 0" in str(exc_info.value).lower()

    def test_confidence_over_hundred_rejected(self):
        """Test that confidence over 100 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=105.0,
                reliability=90.0
            )
        
        assert "less than or equal to 100" in str(exc_info.value).lower()

    def test_reliability_zero_rejected(self):
        """Test that reliability of 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=95.0,
                reliability=0.0
            )
        
        assert "Value must be between 0 and 100 (exclusive)" in str(exc_info.value)

    def test_reliability_hundred_rejected(self):
        """Test that reliability of 100 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=95.0,
                reliability=100.0
            )
        
        assert "Value must be between 0 and 100 (exclusive)" in str(exc_info.value)

    def test_negative_failures_rejected(self):
        """Test that negative allowable_failures is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AttributeInput(
                confidence=95.0,
                reliability=90.0,
                allowable_failures=-1
            )
        
        assert "greater than or equal to 0" in str(exc_info.value).lower()

    def test_edge_case_very_low_confidence(self):
        """Test edge case with very low but valid confidence."""
        input_data = AttributeInput(
            confidence=0.01,
            reliability=90.0
        )
        
        assert input_data.confidence == 0.01

    def test_edge_case_very_high_confidence(self):
        """Test edge case with very high but valid confidence."""
        input_data = AttributeInput(
            confidence=99.99,
            reliability=90.0
        )
        
        assert input_data.confidence == 99.99


class TestVariablesInput:
    """Test VariablesInput model validation."""

    def test_valid_inputs_two_sided(self):
        """Test that valid two-sided inputs are accepted."""
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=2.0,
            lsl=5.0,
            usl=15.0,
            sided="two"
        )
        
        assert input_data.confidence == 95.0
        assert input_data.sample_size == 30
        assert input_data.sample_std == 2.0
        assert input_data.lsl == 5.0
        assert input_data.usl == 15.0

    def test_valid_inputs_one_sided(self):
        """Test that valid one-sided inputs are accepted."""
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=2.0,
            sided="one"
        )
        
        assert input_data.sided == "one"
        assert input_data.lsl is None
        assert input_data.usl is None

    def test_confidence_zero_rejected(self):
        """Test that confidence of 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=0.0,
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=2.0,
                sided="two"
            )
        
        assert "Value must be between 0 and 100 (exclusive)" in str(exc_info.value)

    def test_sample_size_one_rejected(self):
        """Test that sample size of 1 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=1,
                sample_mean=10.0,
                sample_std=2.0,
                sided="two"
            )
        
        assert "greater than 1" in str(exc_info.value).lower()

    def test_sample_size_zero_rejected(self):
        """Test that sample size of 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=0,
                sample_mean=10.0,
                sample_std=2.0,
                sided="two"
            )
        
        assert "greater than 1" in str(exc_info.value).lower()

    def test_negative_sample_size_rejected(self):
        """Test that negative sample size is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=-5,
                sample_mean=10.0,
                sample_std=2.0,
                sided="two"
            )
        
        assert "greater than 1" in str(exc_info.value).lower()

    def test_zero_std_rejected(self):
        """Test that standard deviation of 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=0.0,
                sided="two"
            )
        
        # Pydantic's gt constraint triggers before custom validator
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_std_rejected(self):
        """Test that negative standard deviation is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=-1.0,
                sided="two"
            )
        
        assert "greater than 0" in str(exc_info.value).lower()

    def test_lsl_equal_usl_rejected(self):
        """Test that LSL equal to USL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=2.0,
                lsl=10.0,
                usl=10.0,
                sided="two"
            )
        
        assert "Lower specification limit (LSL) must be less than" in str(exc_info.value)

    def test_lsl_greater_than_usl_rejected(self):
        """Test that LSL > USL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VariablesInput(
                confidence=95.0,
                reliability=90.0,
                sample_size=30,
                sample_mean=10.0,
                sample_std=2.0,
                lsl=15.0,
                usl=5.0,
                sided="two"
            )
        
        assert "Lower specification limit (LSL) must be less than" in str(exc_info.value)

    def test_only_lsl_provided(self):
        """Test that only LSL can be provided without USL."""
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=2.0,
            lsl=5.0,
            sided="two"
        )
        
        assert input_data.lsl == 5.0
        assert input_data.usl is None

    def test_only_usl_provided(self):
        """Test that only USL can be provided without LSL."""
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=10.0,
            sample_std=2.0,
            usl=15.0,
            sided="two"
        )
        
        assert input_data.lsl is None
        assert input_data.usl == 15.0

    def test_negative_spec_limits_allowed(self):
        """Test that negative specification limits are allowed if LSL < USL."""
        input_data = VariablesInput(
            confidence=95.0,
            reliability=90.0,
            sample_size=30,
            sample_mean=0.0,
            sample_std=2.0,
            lsl=-10.0,
            usl=-5.0,
            sided="two"
        )
        
        assert input_data.lsl == -10.0
        assert input_data.usl == -5.0


class TestReliabilityInput:
    """Test ReliabilityInput model validation."""

    def test_valid_inputs_without_acceleration(self):
        """Test that valid inputs without acceleration factor are accepted."""
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0
        )
        
        assert input_data.confidence == 95.0
        assert input_data.reliability == 90.0
        assert input_data.failures == 0
        assert input_data.activation_energy is None
        assert input_data.use_temperature is None
        assert input_data.test_temperature is None

    def test_valid_inputs_with_acceleration(self):
        """Test that valid inputs with acceleration factor are accepted."""
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0,
            activation_energy=0.7,
            use_temperature=298.15,
            test_temperature=358.15
        )
        
        assert input_data.activation_energy == 0.7
        assert input_data.use_temperature == 298.15
        assert input_data.test_temperature == 358.15

    def test_confidence_zero_rejected(self):
        """Test that confidence of 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=0.0,
                reliability=90.0,
                failures=0
            )
        
        assert "Value must be between 0 and 100 (exclusive)" in str(exc_info.value)

    def test_negative_failures_rejected(self):
        """Test that negative failures is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=-1
            )
        
        assert "greater than or equal to 0" in str(exc_info.value).lower()

    def test_zero_activation_energy_rejected(self):
        """Test that zero activation energy is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=0,
                activation_energy=0.0,
                use_temperature=298.15,
                test_temperature=358.15
            )
        
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_activation_energy_rejected(self):
        """Test that negative activation energy is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=0,
                activation_energy=-0.5,
                use_temperature=298.15,
                test_temperature=358.15
            )
        
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_use_temperature_rejected(self):
        """Test that zero use temperature is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=0,
                activation_energy=0.7,
                use_temperature=0.0,
                test_temperature=358.15
            )
        
        assert "greater than 0" in str(exc_info.value).lower()

    def test_test_temp_equal_use_temp_rejected(self):
        """Test that test temperature equal to use temperature is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=0,
                activation_energy=0.7,
                use_temperature=298.15,
                test_temperature=298.15
            )
        
        assert "Test temperature must be greater than use temperature" in str(exc_info.value)

    def test_test_temp_less_than_use_temp_rejected(self):
        """Test that test temperature less than use temperature is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReliabilityInput(
                confidence=95.0,
                reliability=90.0,
                failures=0,
                activation_energy=0.7,
                use_temperature=358.15,
                test_temperature=298.15
            )
        
        assert "Test temperature must be greater than use temperature" in str(exc_info.value)

    def test_partial_acceleration_params_allowed(self):
        """Test that partial acceleration parameters are allowed (validation happens at calculation level)."""
        # Only activation energy provided
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=0,
            activation_energy=0.7
        )
        
        assert input_data.activation_energy == 0.7
        assert input_data.use_temperature is None
        assert input_data.test_temperature is None

    def test_positive_failures_allowed(self):
        """Test that positive number of failures is allowed."""
        input_data = ReliabilityInput(
            confidence=95.0,
            reliability=90.0,
            failures=3
        )
        
        assert input_data.failures == 3
