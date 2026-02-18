"""
Unit tests for variables calculations module.

Tests tolerance factor calculations for normally distributed data.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy import stats

from sample_size_estimator.calculations.variables_calcs import (
    calculate_one_sided_tolerance_factor,
    calculate_tolerance_limits,
    calculate_two_sided_tolerance_factor,
)


class TestOneSidedToleranceFactor:
    """Tests for one-sided tolerance factor calculation."""

    def test_basic_calculation(self):
        """Test one-sided tolerance factor with standard inputs."""
        # Standard case: n=30, C=95%, R=95%
        k1 = calculate_one_sided_tolerance_factor(n=30, confidence=95.0, reliability=95.0)

        # Verify result is positive and reasonable
        assert k1 > 0
        assert k1 < 10  # Sanity check - should be reasonable value

    def test_known_value(self):
        """Test against a known statistical reference value."""
        # For n=10, C=95%, R=95%, k1 should be approximately 2.911
        k1 = calculate_one_sided_tolerance_factor(n=10, confidence=95.0, reliability=95.0)

        # Allow some tolerance for numerical precision
        assert abs(k1 - 2.911) < 0.01

    def test_increasing_sample_size_decreases_factor(self):
        """Test that larger sample sizes produce smaller tolerance factors."""
        k1_small = calculate_one_sided_tolerance_factor(n=10, confidence=95.0, reliability=95.0)
        k1_large = calculate_one_sided_tolerance_factor(n=100, confidence=95.0, reliability=95.0)

        assert k1_large < k1_small

    def test_increasing_confidence_increases_factor(self):
        """Test that higher confidence produces larger tolerance factors."""
        k1_low = calculate_one_sided_tolerance_factor(n=30, confidence=90.0, reliability=95.0)
        k1_high = calculate_one_sided_tolerance_factor(n=30, confidence=99.0, reliability=95.0)

        assert k1_high > k1_low

    def test_increasing_reliability_increases_factor(self):
        """Test that higher reliability produces larger tolerance factors."""
        k1_low = calculate_one_sided_tolerance_factor(n=30, confidence=95.0, reliability=90.0)
        k1_high = calculate_one_sided_tolerance_factor(n=30, confidence=95.0, reliability=99.0)

        assert k1_high > k1_low

    def test_invalid_sample_size(self):
        """Test that sample size <= 1 raises ValueError."""
        with pytest.raises(ValueError, match="Sample size must be greater than 1"):
            calculate_one_sided_tolerance_factor(n=1, confidence=95.0, reliability=95.0)

        with pytest.raises(ValueError, match="Sample size must be greater than 1"):
            calculate_one_sided_tolerance_factor(n=0, confidence=95.0, reliability=95.0)

    def test_edge_case_high_values(self):
        """Test with very high confidence and reliability."""
        k1 = calculate_one_sided_tolerance_factor(n=50, confidence=99.9, reliability=99.9)

        # Should produce a large but finite value
        assert k1 > 0
        assert np.isfinite(k1)


class TestTwoSidedToleranceFactor:
    """Tests for two-sided tolerance factor calculation."""

    def test_basic_calculation(self):
        """Test two-sided tolerance factor with standard inputs."""
        # Standard case: n=30, C=95%, R=95%
        k2 = calculate_two_sided_tolerance_factor(n=30, confidence=95.0, reliability=95.0)

        # Verify result is positive and reasonable
        assert k2 > 0
        assert k2 < 10  # Sanity check

    def test_known_value(self):
        """Test against a known statistical reference value."""
        # For n=10, C=95%, R=95%, k2 should be approximately 3.379
        k2 = calculate_two_sided_tolerance_factor(n=10, confidence=95.0, reliability=95.0)

        # Allow some tolerance for numerical precision
        assert abs(k2 - 3.379) < 0.01

    def test_two_sided_larger_than_one_sided(self):
        """Test that two-sided factors are larger than one-sided for same inputs."""
        n, c, r = 30, 95.0, 95.0
        k1 = calculate_one_sided_tolerance_factor(n, c, r)
        k2 = calculate_two_sided_tolerance_factor(n, c, r)

        # Two-sided should be larger because it covers both tails
        assert k2 > k1

    def test_increasing_sample_size_decreases_factor(self):
        """Test that larger sample sizes produce smaller tolerance factors."""
        k2_small = calculate_two_sided_tolerance_factor(n=10, confidence=95.0, reliability=95.0)
        k2_large = calculate_two_sided_tolerance_factor(n=100, confidence=95.0, reliability=95.0)

        assert k2_large < k2_small

    def test_increasing_confidence_increases_factor(self):
        """Test that higher confidence produces larger tolerance factors."""
        k2_low = calculate_two_sided_tolerance_factor(n=30, confidence=90.0, reliability=95.0)
        k2_high = calculate_two_sided_tolerance_factor(n=30, confidence=99.0, reliability=95.0)

        assert k2_high > k2_low

    def test_increasing_reliability_increases_factor(self):
        """Test that higher reliability produces larger tolerance factors."""
        k2_low = calculate_two_sided_tolerance_factor(n=30, confidence=95.0, reliability=90.0)
        k2_high = calculate_two_sided_tolerance_factor(n=30, confidence=95.0, reliability=99.0)

        assert k2_high > k2_low

    def test_invalid_sample_size(self):
        """Test that sample size <= 1 raises ValueError."""
        with pytest.raises(ValueError, match="Sample size must be greater than 1"):
            calculate_two_sided_tolerance_factor(n=1, confidence=95.0, reliability=95.0)

        with pytest.raises(ValueError, match="Sample size must be greater than 1"):
            calculate_two_sided_tolerance_factor(n=0, confidence=95.0, reliability=95.0)

    def test_edge_case_high_values(self):
        """Test with very high confidence and reliability."""
        k2 = calculate_two_sided_tolerance_factor(n=50, confidence=99.9, reliability=99.9)

        # Should produce a large but finite value
        assert k2 > 0
        assert np.isfinite(k2)

    def test_formula_components(self):
        """Test that the formula components are calculated correctly."""
        n, c, r = 20, 95.0, 95.0

        # Calculate manually
        c_decimal = c / 100.0
        r_decimal = r / 100.0
        z_val = stats.norm.ppf((1 + r_decimal) / 2)
        chi2_val = stats.chi2.ppf(1 - c_decimal, df=n-1)  # Use 1-C for lower tail
        expected_k2 = np.sqrt((1 + 1/n) * z_val**2 * (n - 1) / chi2_val)

        # Calculate using function
        k2 = calculate_two_sided_tolerance_factor(n, c, r)

        # Should match within numerical precision
        assert abs(k2 - expected_k2) < 1e-10


class TestToleranceFactorComparison:
    """Tests comparing one-sided and two-sided tolerance factors."""

    def test_consistent_behavior_across_sample_sizes(self):
        """Test that both methods behave consistently as sample size changes."""
        sample_sizes = [10, 20, 50, 100]
        k1_values = []
        k2_values = []

        for n in sample_sizes:
            k1 = calculate_one_sided_tolerance_factor(n, 95.0, 95.0)
            k2 = calculate_two_sided_tolerance_factor(n, 95.0, 95.0)
            k1_values.append(k1)
            k2_values.append(k2)

        # Both should decrease monotonically
        assert all(k1_values[i] > k1_values[i+1] for i in range(len(k1_values)-1))
        assert all(k2_values[i] > k2_values[i+1] for i in range(len(k2_values)-1))

        # Two-sided should always be larger
        assert all(k2 > k1 for k1, k2 in zip(k1_values, k2_values))


class TestOneSidedToleranceFactorProperty:
    """Property-based tests for one-sided tolerance factor calculation.
    
    Feature: sample-size-estimator
    Property 6: One-Sided Tolerance Factor Correctness
    Validates: Requirements 4.1
    
    For any sample size n > 1, confidence C, and reliability R,
    the one-sided tolerance factor k1 should equal t_{n-1, 1-C/100}(delta)/sqrt(n)
    where delta = z_R * sqrt(n)
    """

    @given(
        n=st.integers(min_value=2, max_value=200),
        confidence=st.floats(min_value=80.0, max_value=99.9),
        reliability=st.floats(min_value=80.0, max_value=99.9)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_one_sided_tolerance_factor_correctness(
        self, n: int, confidence: float, reliability: float
    ):
        """**Validates: Requirements 4.1**
        
        Property 6: For any sample size n > 1, confidence C, and reliability R,
        the one-sided tolerance factor k1 should equal t_{n-1, 1-C/100}(delta)/sqrt(n)
        where delta = z_R * sqrt(n)
        """
        # Calculate using the function
        k1 = calculate_one_sided_tolerance_factor(n, confidence, reliability)

        # Calculate expected value using the formula directly
        c_decimal = confidence / 100.0
        r_decimal = reliability / 100.0

        # Calculate z-score for reliability level
        z_r = stats.norm.ppf(r_decimal)

        # Calculate non-centrality parameter
        delta = z_r * np.sqrt(n)

        # Calculate expected tolerance factor using non-central t-distribution
        expected_k1 = stats.nct.ppf(c_decimal, df=n-1, nc=delta) / np.sqrt(n)

        # Verify the result matches the formula (within numerical precision)
        assert np.isclose(k1, expected_k1, rtol=1e-10, atol=1e-10), (
            f"One-sided tolerance factor mismatch for n={n}, C={confidence}%, R={reliability}%: "
            f"got {k1}, expected {expected_k1}"
        )

        # Verify result is positive and finite
        assert k1 > 0, f"Tolerance factor must be positive, got {k1}"
        assert np.isfinite(k1), f"Tolerance factor must be finite, got {k1}"


class TestTwoSidedToleranceFactorProperty:
    """Property-based tests for two-sided tolerance factor calculation.
    
    Feature: sample-size-estimator
    Property 7: Two-Sided Tolerance Factor Correctness
    Validates: Requirements 4.2
    
    For any sample size n > 1, confidence C, and reliability R,
    the two-sided tolerance factor k2 should equal
    sqrt((1 + 1/n) * z^2_{(1+R/100)/2} * (n-1) / chi^2_{1-C/100, n-1})
    """

    @given(
        n=st.integers(min_value=2, max_value=200),
        confidence=st.floats(min_value=80.0, max_value=99.9),
        reliability=st.floats(min_value=80.0, max_value=99.9)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_two_sided_tolerance_factor_correctness(
        self, n: int, confidence: float, reliability: float
    ):
        """**Validates: Requirements 4.2**
        
        Property 7: For any sample size n > 1, confidence C, and reliability R,
        the two-sided tolerance factor k2 should equal
        sqrt((1 + 1/n) * z^2_{(1+R/100)/2} * (n-1) / chi^2_{1-C/100, n-1})
        """
        # Calculate using the function
        k2 = calculate_two_sided_tolerance_factor(n, confidence, reliability)

        # Calculate expected value using the formula directly
        c_decimal = confidence / 100.0
        r_decimal = reliability / 100.0

        # Calculate z-score for two-sided reliability
        z_val = stats.norm.ppf((1 + r_decimal) / 2)

        # Calculate chi-squared value at 1-C level (lower tail)
        chi2_val = stats.chi2.ppf(1 - c_decimal, df=n-1)

        # Calculate expected tolerance factor using Howe-Guenther approximation
        expected_k2 = np.sqrt((1 + 1/n) * z_val**2 * (n - 1) / chi2_val)

        # Verify the result matches the formula (within numerical precision)
        assert np.isclose(k2, expected_k2, rtol=1e-10, atol=1e-10), (
            f"Two-sided tolerance factor mismatch for n={n}, C={confidence}%, R={reliability}%: "
            f"got {k2}, expected {expected_k2}"
        )

        # Verify result is positive and finite
        assert k2 > 0, f"Tolerance factor must be positive, got {k2}"
        assert np.isfinite(k2), f"Tolerance factor must be finite, got {k2}"

        # Verify two-sided factor is larger than one-sided for same inputs
        k1 = calculate_one_sided_tolerance_factor(n, confidence, reliability)
        assert k2 > k1, (
            f"Two-sided tolerance factor should be larger than one-sided: "
            f"k2={k2} <= k1={k1} for n={n}, C={confidence}%, R={reliability}%"
        )



class TestToleranceLimits:
    """Tests for tolerance limit calculation."""

    def test_two_sided_limits(self):
        """Test two-sided tolerance limit calculation."""
        mean = 100.0
        std = 10.0
        k = 2.0

        lower, upper = calculate_tolerance_limits(mean, std, k, "two")

        # Verify formula: mean ± k*std
        assert lower == mean - k * std
        assert upper == mean + k * std
        assert lower == 80.0
        assert upper == 120.0

    def test_one_sided_limits(self):
        """Test one-sided tolerance limit calculation."""
        mean = 100.0
        std = 10.0
        k = 2.0

        lower, upper = calculate_tolerance_limits(mean, std, k, "one")

        # One-sided: only upper limit
        assert lower is None
        assert upper == mean + k * std
        assert upper == 120.0


    def test_negative_mean(self):
        """Test with negative mean value."""
        mean = -50.0
        std = 5.0
        k = 1.5

        lower, upper = calculate_tolerance_limits(mean, std, k, "two")

        assert lower == mean - k * std
        assert upper == mean + k * std
        assert lower == -57.5
        assert upper == -42.5

    def test_large_tolerance_factor(self):
        """Test with large tolerance factor."""
        mean = 100.0
        std = 10.0
        k = 5.0

        lower, upper = calculate_tolerance_limits(mean, std, k, "two")

        assert lower == 50.0
        assert upper == 150.0

    def test_small_std(self):
        """Test with small standard deviation."""
        mean = 100.0
        std = 0.1
        k = 2.0

        lower, upper = calculate_tolerance_limits(mean, std, k, "two")

        assert abs(lower - 99.8) < 1e-10
        assert abs(upper - 100.2) < 1e-10

    def test_invalid_std_zero(self):
        """Test that zero standard deviation raises ValueError."""
        with pytest.raises(ValueError, match="Standard deviation must be greater than 0"):
            calculate_tolerance_limits(100.0, 0.0, 2.0, "two")

    def test_invalid_std_negative(self):
        """Test that negative standard deviation raises ValueError."""
        with pytest.raises(ValueError, match="Standard deviation must be greater than 0"):
            calculate_tolerance_limits(100.0, -1.0, 2.0, "two")

    def test_invalid_sided_parameter(self):
        """Test that invalid sided parameter raises ValueError."""
        with pytest.raises(ValueError, match="sided parameter must be 'one' or 'two'"):
            calculate_tolerance_limits(100.0, 10.0, 2.0, "three")

        with pytest.raises(ValueError, match="sided parameter must be 'one' or 'two'"):
            calculate_tolerance_limits(100.0, 10.0, 2.0, "both")



class TestToleranceLimitsProperty:
    """Property-based tests for tolerance limit calculation.
    
    Feature: sample-size-estimator
    Property 8: Tolerance Limit Calculation Correctness
    Validates: Requirements 5.1, 5.2
    
    For any sample mean μ, standard deviation σ > 0, and tolerance factor k,
    the upper tolerance limit should equal μ + k*σ and the lower tolerance
    limit should equal μ - k*σ
    """

    @given(
        mean=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        std=st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False),
        k=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False),
        sided=st.sampled_from(["one", "two"])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_tolerance_limit_calculation_correctness(
        self, mean: float, std: float, k: float, sided: str
    ):
        """**Validates: Requirements 5.1, 5.2**
        
        Property 8: For any sample mean μ, standard deviation σ > 0, and
        tolerance factor k, the upper tolerance limit should equal μ + k*σ
        and the lower tolerance limit should equal μ - k*σ
        """
        # Calculate tolerance limits
        lower, upper = calculate_tolerance_limits(mean, std, k, sided)

        # Verify upper limit formula
        expected_upper = mean + k * std
        assert upper is not None, "Upper limit should always be calculated"
        assert np.isclose(upper, expected_upper, rtol=1e-10, atol=1e-10), (
            f"Upper tolerance limit mismatch: got {upper}, expected {expected_upper} "
            f"for mean={mean}, std={std}, k={k}"
        )

        # Verify lower limit based on sided parameter
        if sided == "two":
            expected_lower = mean - k * std
            assert lower is not None, "Lower limit should be calculated for two-sided"
            assert np.isclose(lower, expected_lower, rtol=1e-10, atol=1e-10), (
                f"Lower tolerance limit mismatch: got {lower}, expected {expected_lower} "
                f"for mean={mean}, std={std}, k={k}"
            )
            # Verify lower < upper
            assert lower < upper, (
                f"Lower limit should be less than upper limit: "
                f"lower={lower}, upper={upper}"
            )
        else:  # sided == "one"
            assert lower is None, "Lower limit should be None for one-sided"

        # Verify results are finite
        assert np.isfinite(upper), f"Upper limit must be finite, got {upper}"
        if lower is not None:
            assert np.isfinite(lower), f"Lower limit must be finite, got {lower}"



class TestPpkCalculation:
    """Tests for Ppk (process performance index) calculation."""

    def test_two_sided_ppk(self):
        """Test Ppk calculation with both specification limits."""
        mean = 100.0
        std = 5.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Calculate expected values
        # Ppk_upper = (USL - mean) / (3 * std) = (115 - 100) / 15 = 1.0
        # Ppk_lower = (mean - LSL) / (3 * std) = (100 - 85) / 15 = 1.0
        # Ppk = min(1.0, 1.0) = 1.0
        assert ppk == 1.0

    def test_ppk_upper_limiting(self):
        """Test Ppk when upper spec is the limiting factor."""
        mean = 105.0
        std = 5.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (115 - 105) / 15 = 0.667
        # Ppk_lower = (105 - 85) / 15 = 1.333
        # Ppk = min(0.667, 1.333) = 0.667
        expected_ppk = (usl - mean) / (3 * std)
        assert abs(ppk - expected_ppk) < 1e-10

    def test_ppk_lower_limiting(self):
        """Test Ppk when lower spec is the limiting factor."""
        mean = 90.0
        std = 5.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (115 - 90) / 15 = 1.667
        # Ppk_lower = (90 - 85) / 15 = 0.333
        # Ppk = min(1.667, 0.333) = 0.333
        expected_ppk = (mean - lsl) / (3 * std)
        assert abs(ppk - expected_ppk) < 1e-10

    def test_ppk_only_usl(self):
        """Test Ppk calculation with only upper specification limit."""
        mean = 100.0
        std = 5.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, None, usl)

        # Only upper term: (115 - 100) / 15 = 1.0
        expected_ppk = (usl - mean) / (3 * std)
        assert ppk == expected_ppk

    def test_ppk_only_lsl(self):
        """Test Ppk calculation with only lower specification limit."""
        mean = 100.0
        std = 5.0
        lsl = 85.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, None)

        # Only lower term: (100 - 85) / 15 = 1.0
        expected_ppk = (mean - lsl) / (3 * std)
        assert ppk == expected_ppk

    def test_ppk_no_spec_limits(self):
        """Test that Ppk returns None when no spec limits provided."""
        mean = 100.0
        std = 5.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, None, None)

        assert ppk is None

    def test_ppk_negative_values(self):
        """Test Ppk calculation with negative mean and spec limits."""
        mean = -50.0
        std = 10.0
        lsl = -80.0
        usl = -20.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (-20 - (-50)) / 30 = 30 / 30 = 1.0
        # Ppk_lower = (-50 - (-80)) / 30 = 30 / 30 = 1.0
        assert ppk == 1.0

    def test_ppk_high_capability(self):
        """Test Ppk with high process capability (Ppk > 2)."""
        mean = 100.0
        std = 2.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (115 - 100) / 6 = 2.5
        # Ppk_lower = (100 - 85) / 6 = 2.5
        assert ppk == 2.5

    def test_ppk_low_capability(self):
        """Test Ppk with low process capability (Ppk < 1)."""
        mean = 100.0
        std = 10.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (115 - 100) / 30 = 0.5
        # Ppk_lower = (100 - 85) / 30 = 0.5
        assert ppk == 0.5

    def test_ppk_invalid_std_zero(self):
        """Test that zero standard deviation raises ValueError."""
        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        
        with pytest.raises(ValueError, match="Standard deviation must be greater than 0"):
            calculate_ppk(100.0, 0.0, 85.0, 115.0)

    def test_ppk_invalid_std_negative(self):
        """Test that negative standard deviation raises ValueError."""
        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        
        with pytest.raises(ValueError, match="Standard deviation must be greater than 0"):
            calculate_ppk(100.0, -1.0, 85.0, 115.0)

    def test_ppk_mean_at_usl(self):
        """Test Ppk when mean equals upper spec limit."""
        mean = 115.0
        std = 5.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (115 - 115) / 15 = 0
        # Ppk_lower = (115 - 85) / 15 = 2.0
        # Ppk = min(0, 2.0) = 0
        assert ppk == 0.0

    def test_ppk_mean_at_lsl(self):
        """Test Ppk when mean equals lower spec limit."""
        mean = 85.0
        std = 5.0
        lsl = 85.0
        usl = 115.0

        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Ppk_upper = (115 - 85) / 15 = 2.0
        # Ppk_lower = (85 - 85) / 15 = 0
        # Ppk = min(2.0, 0) = 0
        assert ppk == 0.0


class TestPpkCalculationProperty:
    """Property-based tests for Ppk calculation.
    
    Feature: sample-size-estimator
    Property 10: Ppk Calculation Correctness
    Validates: Requirements 7.1, 7.2
    
    For any mean μ, standard deviation σ > 0, and specification limits (LSL, USL),
    Ppk should equal min((USL-μ)/(3σ), (μ-LSL)/(3σ)) when both limits exist,
    or the single relevant term when only one limit exists.
    """

    @given(
        mean=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        std=st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False),
        lsl_offset=st.floats(min_value=-50.0, max_value=-0.1, allow_nan=False, allow_infinity=False),
        usl_offset=st.floats(min_value=0.1, max_value=50.0, allow_nan=False, allow_infinity=False),
        spec_type=st.sampled_from(["both", "lsl_only", "usl_only", "none"])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_ppk_calculation_correctness(
        self, mean: float, std: float, lsl_offset: float, usl_offset: float, spec_type: str
    ):
        """**Validates: Requirements 7.1, 7.2**
        
        Property 10: For any mean μ, standard deviation σ > 0, and specification
        limits (LSL, USL), Ppk should equal min((USL-μ)/(3σ), (μ-LSL)/(3σ))
        when both limits exist, or the single relevant term when only one limit exists.
        """
        from sample_size_estimator.calculations.variables_calcs import calculate_ppk
        
        # Set up specification limits based on spec_type
        if spec_type == "both":
            lsl = mean + lsl_offset
            usl = mean + usl_offset
        elif spec_type == "lsl_only":
            lsl = mean + lsl_offset
            usl = None
        elif spec_type == "usl_only":
            lsl = None
            usl = mean + usl_offset
        else:  # none
            lsl = None
            usl = None

        # Calculate Ppk
        ppk = calculate_ppk(mean, std, lsl, usl)

        # Verify result based on spec_type
        if spec_type == "none":
            # No spec limits: should return None
            assert ppk is None, "Ppk should be None when no spec limits provided"
        else:
            # Calculate expected Ppk
            ppk_values = []
            
            if usl is not None:
                ppk_upper = (usl - mean) / (3 * std)
                ppk_values.append(ppk_upper)
            
            if lsl is not None:
                ppk_lower = (mean - lsl) / (3 * std)
                ppk_values.append(ppk_lower)
            
            expected_ppk = min(ppk_values)
            
            # Verify Ppk matches expected value
            assert ppk is not None, "Ppk should not be None when spec limits provided"
            assert np.isclose(ppk, expected_ppk, rtol=1e-10, atol=1e-10), (
                f"Ppk mismatch: got {ppk}, expected {expected_ppk} "
                f"for mean={mean}, std={std}, lsl={lsl}, usl={usl}"
            )
            
            # Verify Ppk is finite
            assert np.isfinite(ppk), f"Ppk must be finite, got {ppk}"
            
            # Verify Ppk formula components
            if spec_type == "both":
                ppk_upper = (usl - mean) / (3 * std)
                ppk_lower = (mean - lsl) / (3 * std)
                assert ppk == min(ppk_upper, ppk_lower), (
                    f"Ppk should be minimum of upper and lower terms: "
                    f"ppk={ppk}, ppk_upper={ppk_upper}, ppk_lower={ppk_lower}"
                )
            elif spec_type == "usl_only":
                ppk_upper = (usl - mean) / (3 * std)
                assert np.isclose(ppk, ppk_upper, rtol=1e-10, atol=1e-10), (
                    f"Ppk should equal upper term when only USL provided: "
                    f"ppk={ppk}, ppk_upper={ppk_upper}"
                )
            elif spec_type == "lsl_only":
                ppk_lower = (mean - lsl) / (3 * std)
                assert np.isclose(ppk, ppk_lower, rtol=1e-10, atol=1e-10), (
                    f"Ppk should equal lower term when only LSL provided: "
                    f"ppk={ppk}, ppk_lower={ppk_lower}"
                )



class TestCompareToSpecLimits:
    """Tests for specification limit comparison."""

    def test_pass_both_limits_within_spec(self):
        """Test PASS when both tolerance limits are within spec limits."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 90.0
        upper_tol = 110.0
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "PASS"
        assert margin_lower == 5.0  # 90 - 85
        assert margin_upper == 5.0  # 115 - 110

    def test_fail_lower_limit_violation(self):
        """Test FAIL when lower tolerance limit violates LSL."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 80.0  # Below LSL
        upper_tol = 110.0
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "FAIL"
        assert margin_lower == -5.0  # 80 - 85 (negative = failing)
        assert margin_upper == 5.0  # 115 - 110

    def test_fail_upper_limit_violation(self):
        """Test FAIL when upper tolerance limit violates USL."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 90.0
        upper_tol = 120.0  # Above USL
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "FAIL"
        assert margin_lower == 5.0  # 90 - 85
        assert margin_upper == -5.0  # 115 - 120 (negative = failing)

    def test_fail_both_limits_violation(self):
        """Test FAIL when both tolerance limits violate spec limits."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 80.0  # Below LSL
        upper_tol = 120.0  # Above USL
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "FAIL"
        assert margin_lower == -5.0  # 80 - 85
        assert margin_upper == -5.0  # 115 - 120

    def test_pass_at_boundary(self):
        """Test PASS when tolerance limits exactly equal spec limits."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 85.0  # Exactly at LSL
        upper_tol = 115.0  # Exactly at USL
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "PASS"
        assert margin_lower == 0.0
        assert margin_upper == 0.0

    def test_only_usl_pass(self):
        """Test comparison with only upper spec limit (PASS)."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = None
        upper_tol = 110.0
        lsl = None
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "PASS"
        assert margin_lower is None
        assert margin_upper == 5.0  # 115 - 110

    def test_only_usl_fail(self):
        """Test comparison with only upper spec limit (FAIL)."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = None
        upper_tol = 120.0  # Above USL
        lsl = None
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "FAIL"
        assert margin_lower is None
        assert margin_upper == -5.0  # 115 - 120

    def test_only_lsl_pass(self):
        """Test comparison with only lower spec limit (PASS)."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 90.0
        upper_tol = None
        lsl = 85.0
        usl = None

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "PASS"
        assert margin_lower == 5.0  # 90 - 85
        assert margin_upper is None

    def test_only_lsl_fail(self):
        """Test comparison with only lower spec limit (FAIL)."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 80.0  # Below LSL
        upper_tol = None
        lsl = 85.0
        usl = None

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "FAIL"
        assert margin_lower == -5.0  # 80 - 85
        assert margin_upper is None

    def test_no_spec_limits(self):
        """Test that None is returned when no spec limits provided."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 90.0
        upper_tol = 110.0
        lsl = None
        usl = None

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail is None
        assert margin_lower is None
        assert margin_upper is None

    def test_negative_values(self):
        """Test comparison with negative values."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = -60.0
        upper_tol = -40.0
        lsl = -65.0
        usl = -35.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "PASS"
        assert margin_lower == 5.0  # -60 - (-65)
        assert margin_upper == 5.0  # -35 - (-40)

    def test_very_small_margins(self):
        """Test with very small positive margins."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 85.001
        upper_tol = 114.999
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "PASS"
        assert abs(margin_lower - 0.001) < 1e-10
        assert abs(margin_upper - 0.001) < 1e-10

    def test_very_small_negative_margins(self):
        """Test with very small negative margins (just failing)."""
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        lower_tol = 84.999
        upper_tol = 115.001
        lsl = 85.0
        usl = 115.0

        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, lsl, usl
        )

        assert pass_fail == "FAIL"
        assert abs(margin_lower - (-0.001)) < 1e-10
        assert abs(margin_upper - (-0.001)) < 1e-10



class TestSpecificationComparisonProperty:
    """Property-based tests for specification limit comparison logic.
    
    Feature: sample-size-estimator
    Property 9: Specification Comparison Logic
    Validates: Requirements 6.2, 6.3, 6.4
    
    For any tolerance limits (L_tol, U_tol) and specification limits (LSL, USL),
    the result should be PASS if and only if L_tol >= LSL AND U_tol <= USL
    """

    @given(
        # Generate tolerance limits
        lower_tol=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        upper_tol=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        # Generate spec limit offsets to ensure LSL < USL
        lsl_offset=st.floats(min_value=-100.0, max_value=-0.1, allow_nan=False, allow_infinity=False),
        usl_offset=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        # Determine which spec limits to provide
        spec_config=st.sampled_from(["both", "lsl_only", "usl_only", "none"])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_specification_comparison_logic(
        self, 
        lower_tol: float, 
        upper_tol: float, 
        lsl_offset: float, 
        usl_offset: float,
        spec_config: str
    ):
        """**Validates: Requirements 6.2, 6.3, 6.4**
        
        Property 9: For any tolerance limits (L_tol, U_tol) and specification
        limits (LSL, USL), the result should be PASS if and only if
        L_tol >= LSL AND U_tol <= USL
        """
        from sample_size_estimator.calculations.variables_calcs import compare_to_spec_limits
        
        # Ensure lower_tol < upper_tol for valid tolerance limits
        if lower_tol >= upper_tol:
            lower_tol, upper_tol = upper_tol - 1.0, lower_tol + 1.0
        
        # Calculate spec limits based on tolerance limits to ensure variety
        # Use the middle point between tolerance limits as reference
        mid_point = (lower_tol + upper_tol) / 2.0
        
        # Set up specification limits based on config
        if spec_config == "both":
            lsl = mid_point + lsl_offset
            usl = mid_point + usl_offset
            lower_tol_input = lower_tol
            upper_tol_input = upper_tol
        elif spec_config == "lsl_only":
            lsl = mid_point + lsl_offset
            usl = None
            lower_tol_input = lower_tol
            upper_tol_input = None
        elif spec_config == "usl_only":
            lsl = None
            usl = mid_point + usl_offset
            lower_tol_input = None
            upper_tol_input = upper_tol
        else:  # none
            lsl = None
            usl = None
            lower_tol_input = lower_tol
            upper_tol_input = upper_tol
        
        # Call the comparison function
        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol_input, upper_tol_input, lsl, usl
        )
        
        # Verify the logic based on spec_config
        if spec_config == "none":
            # No spec limits: should return None
            assert pass_fail is None, (
                "pass_fail should be None when no spec limits provided"
            )
            assert margin_lower is None, (
                "margin_lower should be None when no spec limits provided"
            )
            assert margin_upper is None, (
                "margin_upper should be None when no spec limits provided"
            )
        
        elif spec_config == "both":
            # Both spec limits: verify PASS/FAIL logic
            lower_passes = lower_tol >= lsl
            upper_passes = upper_tol <= usl
            expected_pass_fail = "PASS" if (lower_passes and upper_passes) else "FAIL"
            
            assert pass_fail == expected_pass_fail, (
                f"Comparison logic mismatch: got {pass_fail}, expected {expected_pass_fail} "
                f"for lower_tol={lower_tol}, upper_tol={upper_tol}, lsl={lsl}, usl={usl}"
            )
            
            # Verify margins
            expected_margin_lower = lower_tol - lsl
            expected_margin_upper = usl - upper_tol
            
            assert margin_lower is not None, "margin_lower should not be None when LSL provided"
            assert margin_upper is not None, "margin_upper should not be None when USL provided"
            
            assert np.isclose(margin_lower, expected_margin_lower, rtol=1e-10, atol=1e-10), (
                f"Lower margin mismatch: got {margin_lower}, expected {expected_margin_lower}"
            )
            assert np.isclose(margin_upper, expected_margin_upper, rtol=1e-10, atol=1e-10), (
                f"Upper margin mismatch: got {margin_upper}, expected {expected_margin_upper}"
            )
            
            # Verify margin signs match pass/fail status
            if pass_fail == "PASS":
                assert margin_lower >= 0, (
                    f"PASS status requires non-negative lower margin, got {margin_lower}"
                )
                assert margin_upper >= 0, (
                    f"PASS status requires non-negative upper margin, got {margin_upper}"
                )
            else:  # FAIL
                assert margin_lower < 0 or margin_upper < 0, (
                    f"FAIL status requires at least one negative margin, "
                    f"got margin_lower={margin_lower}, margin_upper={margin_upper}"
                )
        
        elif spec_config == "lsl_only":
            # Only LSL: verify lower limit logic
            lower_passes = lower_tol >= lsl
            expected_pass_fail = "PASS" if lower_passes else "FAIL"
            
            assert pass_fail == expected_pass_fail, (
                f"Comparison logic mismatch (LSL only): got {pass_fail}, expected {expected_pass_fail} "
                f"for lower_tol={lower_tol}, lsl={lsl}"
            )
            
            # Verify margins
            expected_margin_lower = lower_tol - lsl
            
            assert margin_lower is not None, "margin_lower should not be None when LSL provided"
            assert margin_upper is None, "margin_upper should be None when USL not provided"
            
            assert np.isclose(margin_lower, expected_margin_lower, rtol=1e-10, atol=1e-10), (
                f"Lower margin mismatch: got {margin_lower}, expected {expected_margin_lower}"
            )
            
            # Verify margin sign matches pass/fail status
            if pass_fail == "PASS":
                assert margin_lower >= 0, (
                    f"PASS status requires non-negative lower margin, got {margin_lower}"
                )
            else:  # FAIL
                assert margin_lower < 0, (
                    f"FAIL status requires negative lower margin, got {margin_lower}"
                )
        
        elif spec_config == "usl_only":
            # Only USL: verify upper limit logic
            upper_passes = upper_tol <= usl
            expected_pass_fail = "PASS" if upper_passes else "FAIL"
            
            assert pass_fail == expected_pass_fail, (
                f"Comparison logic mismatch (USL only): got {pass_fail}, expected {expected_pass_fail} "
                f"for upper_tol={upper_tol}, usl={usl}"
            )
            
            # Verify margins
            expected_margin_upper = usl - upper_tol
            
            assert margin_lower is None, "margin_lower should be None when LSL not provided"
            assert margin_upper is not None, "margin_upper should not be None when USL provided"
            
            assert np.isclose(margin_upper, expected_margin_upper, rtol=1e-10, atol=1e-10), (
                f"Upper margin mismatch: got {margin_upper}, expected {expected_margin_upper}"
            )
            
            # Verify margin sign matches pass/fail status
            if pass_fail == "PASS":
                assert margin_upper >= 0, (
                    f"PASS status requires non-negative upper margin, got {margin_upper}"
                )
            else:  # FAIL
                assert margin_upper < 0, (
                    f"FAIL status requires negative upper margin, got {margin_upper}"
                )



class TestCalculateVariables:
    """Tests for the main calculate_variables() entry point.
    
    Tests the integration of all variables calculations:
    - Tolerance factor calculation
    - Tolerance limit calculation
    - Ppk calculation
    - Specification limit comparison
    
    Requirements: REQ-4, REQ-5, REQ-6, REQ-7
    """

    def test_two_sided_with_spec_limits_pass(self):
        """Test complete two-sided calculation with spec limits (PASS case)."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # Create input with well-centered process
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=5.0,
            lsl=85.0,
            usl=115.0,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Verify all fields are populated
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit is not None
        assert result.upper_tolerance_limit is not None
        assert result.ppk is not None
        assert result.pass_fail == "PASS"
        assert result.margin_lower is not None
        assert result.margin_upper is not None
        
        # Verify tolerance limits are within spec limits
        assert result.lower_tolerance_limit >= input_data.lsl
        assert result.upper_tolerance_limit <= input_data.usl
        
        # Verify margins are positive (PASS)
        assert result.margin_lower > 0
        assert result.margin_upper > 0

    def test_two_sided_with_spec_limits_fail(self):
        """Test complete two-sided calculation with spec limits (FAIL case)."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # Create input with poor process capability (high variation)
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=15.0,  # Large std causes tolerance limits to exceed spec
            lsl=85.0,
            usl=115.0,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Verify all fields are populated
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit is not None
        assert result.upper_tolerance_limit is not None
        assert result.ppk is not None
        assert result.pass_fail == "FAIL"
        assert result.margin_lower is not None
        assert result.margin_upper is not None
        
        # Verify at least one tolerance limit violates spec
        assert (result.lower_tolerance_limit < input_data.lsl or 
                result.upper_tolerance_limit > input_data.usl)
        
        # Verify at least one margin is negative (FAIL)
        assert result.margin_lower < 0 or result.margin_upper < 0

    def test_one_sided_with_usl_only(self):
        """Test one-sided calculation with only upper spec limit."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=50,
            sample_mean=100.0,
            sample_std=8.0,
            lsl=None,
            usl=120.0,
            sided="one"
        )
        
        result = calculate_variables(input_data)
        
        # Verify one-sided behavior
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit is None  # One-sided: no lower limit
        assert result.upper_tolerance_limit is not None
        assert result.ppk is not None  # Ppk calculated with USL only
        assert result.pass_fail == "PASS"
        assert result.margin_lower is None  # No LSL
        assert result.margin_upper is not None

    def test_two_sided_without_spec_limits(self):
        """Test two-sided calculation without specification limits."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=20,
            sample_mean=50.0,
            sample_std=10.0,
            lsl=None,
            usl=None,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Verify tolerance calculations work without spec limits
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit is not None
        assert result.upper_tolerance_limit is not None
        
        # Verify no comparison performed
        assert result.ppk is None  # No spec limits
        assert result.pass_fail is None  # No comparison
        assert result.margin_lower is None
        assert result.margin_upper is None

    def test_known_statistical_values(self):
        """Test with known statistical reference values."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # Use n=10, C=95%, R=95% which has known k2 ≈ 3.379
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=10,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=None,
            usl=None,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Verify tolerance factor is close to known value
        assert abs(result.tolerance_factor - 3.379) < 0.01
        
        # Verify tolerance limits
        expected_lower = 100.0 - 3.379 * 10.0
        expected_upper = 100.0 + 3.379 * 10.0
        assert abs(result.lower_tolerance_limit - expected_lower) < 0.1
        assert abs(result.upper_tolerance_limit - expected_upper) < 0.1

    def test_ppk_calculation_integration(self):
        """Test that Ppk is correctly calculated and integrated."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=5.0,
            lsl=85.0,
            usl=115.0,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Calculate expected Ppk manually
        ppk_upper = (115.0 - 100.0) / (3 * 5.0)  # = 1.0
        ppk_lower = (100.0 - 85.0) / (3 * 5.0)   # = 1.0
        expected_ppk = min(ppk_upper, ppk_lower)  # = 1.0
        
        assert result.ppk is not None
        assert abs(result.ppk - expected_ppk) < 1e-10

    def test_tolerance_factor_differs_by_sided(self):
        """Test that one-sided and two-sided produce different tolerance factors."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        # One-sided calculation
        input_one = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=None,
            usl=None,
            sided="one"
        )
        
        # Two-sided calculation (same parameters)
        input_two = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=None,
            usl=None,
            sided="two"
        )
        
        result_one = calculate_variables(input_one)
        result_two = calculate_variables(input_two)
        
        # Two-sided tolerance factor should be larger
        assert result_two.tolerance_factor > result_one.tolerance_factor

    def test_negative_mean_and_spec_limits(self):
        """Test with negative mean and specification limits."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=25,
            sample_mean=-50.0,
            sample_std=5.0,
            lsl=-65.0,
            usl=-35.0,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Verify calculations work with negative values
        assert result.tolerance_factor > 0
        assert result.lower_tolerance_limit < result.upper_tolerance_limit
        assert result.ppk is not None
        assert result.pass_fail in ["PASS", "FAIL"]

    def test_high_confidence_high_reliability(self):
        """Test with very high confidence and reliability levels."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=99.9,
            reliability=99.9,
            sample_size=100,
            sample_mean=100.0,
            sample_std=5.0,
            lsl=None,
            usl=None,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # High confidence/reliability should produce large tolerance factor
        assert result.tolerance_factor > 3.0
        assert np.isfinite(result.tolerance_factor)
        assert np.isfinite(result.lower_tolerance_limit)
        assert np.isfinite(result.upper_tolerance_limit)

    def test_small_sample_size(self):
        """Test with minimum valid sample size (n=2)."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=2,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=None,
            usl=None,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Small sample size should produce large tolerance factor
        assert result.tolerance_factor > 10.0
        assert np.isfinite(result.tolerance_factor)

    def test_large_sample_size(self):
        """Test with large sample size."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=200,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=None,
            usl=None,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Large sample size should produce smaller tolerance factor
        assert result.tolerance_factor < 3.0
        assert result.tolerance_factor > 0

    def test_result_model_structure(self):
        """Test that result follows VariablesResult model structure."""
        from sample_size_estimator.models import VariablesInput, VariablesResult
        from sample_size_estimator.calculations.variables_calcs import calculate_variables
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=85.0,
            usl=115.0,
            sided="two"
        )
        
        result = calculate_variables(input_data)
        
        # Verify result is correct type
        assert isinstance(result, VariablesResult)
        
        # Verify all expected fields exist
        assert hasattr(result, 'tolerance_factor')
        assert hasattr(result, 'lower_tolerance_limit')
        assert hasattr(result, 'upper_tolerance_limit')
        assert hasattr(result, 'ppk')
        assert hasattr(result, 'pass_fail')
        assert hasattr(result, 'margin_lower')
        assert hasattr(result, 'margin_upper')

    def test_consistency_with_individual_functions(self):
        """Test that calculate_variables produces same results as calling functions individually."""
        from sample_size_estimator.models import VariablesInput
        from sample_size_estimator.calculations.variables_calcs import (
            calculate_variables,
            calculate_two_sided_tolerance_factor,
            calculate_tolerance_limits,
            calculate_ppk,
            compare_to_spec_limits
        )
        
        input_data = VariablesInput(
            confidence=95.0,
            reliability=95.0,
            sample_size=30,
            sample_mean=100.0,
            sample_std=10.0,
            lsl=85.0,
            usl=115.0,
            sided="two"
        )
        
        # Calculate using integrated function
        result = calculate_variables(input_data)
        
        # Calculate using individual functions
        k = calculate_two_sided_tolerance_factor(30, 95.0, 95.0)
        lower_tol, upper_tol = calculate_tolerance_limits(100.0, 10.0, k, "two")
        ppk = calculate_ppk(100.0, 10.0, 85.0, 115.0)
        pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
            lower_tol, upper_tol, 85.0, 115.0
        )
        
        # Verify results match
        assert np.isclose(result.tolerance_factor, k, rtol=1e-10)
        assert np.isclose(result.lower_tolerance_limit, lower_tol, rtol=1e-10)
        assert np.isclose(result.upper_tolerance_limit, upper_tol, rtol=1e-10)
        assert np.isclose(result.ppk, ppk, rtol=1e-10)
        assert result.pass_fail == pass_fail
        assert np.isclose(result.margin_lower, margin_lower, rtol=1e-10)
        assert np.isclose(result.margin_upper, margin_upper, rtol=1e-10)
