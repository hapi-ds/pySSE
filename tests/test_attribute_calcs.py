"""Unit tests for attribute calculations module.

Tests the Success Run Theorem and binomial sample size calculations
with known statistical values and edge cases.
"""

import math

from hypothesis import given, settings
from hypothesis import strategies as st
from scipy import stats

from src.sample_size_estimator.calculations.attribute_calcs import (
    calculate_sample_size_zero_failures,
)


class TestSuccessRunTheorem:
    """Tests for Success Run Theorem calculation (c=0)."""

    def test_known_value_95_90(self):
        """Test with known statistical value: C=95%, R=90% should give n=29."""
        result = calculate_sample_size_zero_failures(95.0, 90.0)
        assert result == 29

    def test_known_value_90_95(self):
        """Test with C=90%, R=95% should give n=45."""
        result = calculate_sample_size_zero_failures(90.0, 95.0)
        assert result == 45

    def test_high_confidence_high_reliability(self):
        """Test with high confidence and reliability: C=99%, R=99%."""
        result = calculate_sample_size_zero_failures(99.0, 99.0)
        assert result > 0
        assert isinstance(result, int)

    def test_low_confidence_low_reliability(self):
        """Test with lower values: C=80%, R=80%."""
        result = calculate_sample_size_zero_failures(80.0, 80.0)
        assert result > 0
        assert isinstance(result, int)

    def test_result_is_integer(self):
        """Verify result is always an integer."""
        result = calculate_sample_size_zero_failures(95.0, 90.0)
        assert isinstance(result, int)

    def test_result_is_positive(self):
        """Verify result is always positive."""
        result = calculate_sample_size_zero_failures(95.0, 90.0)
        assert result > 0

    def test_increasing_confidence_increases_sample_size(self):
        """Higher confidence should require larger sample size."""
        n1 = calculate_sample_size_zero_failures(90.0, 90.0)
        n2 = calculate_sample_size_zero_failures(95.0, 90.0)
        n3 = calculate_sample_size_zero_failures(99.0, 90.0)
        assert n1 < n2 < n3

    def test_increasing_reliability_increases_sample_size(self):
        """Higher reliability should require larger sample size."""
        n1 = calculate_sample_size_zero_failures(95.0, 80.0)
        n2 = calculate_sample_size_zero_failures(95.0, 90.0)
        n3 = calculate_sample_size_zero_failures(95.0, 95.0)
        assert n1 < n2 < n3


class TestSuccessRunTheoremProperty:
    """Property-based tests for Success Run Theorem calculation.
    
    Feature: sample-size-estimator
    Property 1: Success Run Theorem Correctness
    Validates: Requirements 1.2
    
    For any confidence level C (0 < C < 100) and reliability R (0 < R < 100),
    when calculating sample size with zero allowable failures, the calculated n
    should equal ceiling(ln(1-C/100) / ln(R/100))
    """

    @given(
        confidence=st.floats(min_value=0.01, max_value=99.99),
        reliability=st.floats(min_value=0.01, max_value=99.99)
    )
    @settings(max_examples=100)
    def test_property_success_run_theorem_correctness(
        self, confidence: float, reliability: float
    ):
        """**Validates: Requirements 1.2**
        
        Property: For any confidence C and reliability R in (0, 100),
        the calculated sample size n should equal ceil(ln(1-C/100) / ln(R/100))
        """
        # Calculate using the function
        n = calculate_sample_size_zero_failures(confidence, reliability)

        # Calculate expected value using the formula directly
        c_decimal = confidence / 100.0
        r_decimal = reliability / 100.0
        expected_n = math.ceil(math.log(1 - c_decimal) / math.log(r_decimal))

        # Verify the result matches the formula
        assert n == expected_n, (
            f"Sample size mismatch for C={confidence}%, R={reliability}%: "
            f"got {n}, expected {expected_n}"
        )

        # Verify result is a positive integer
        assert isinstance(n, int), f"Result must be an integer, got {type(n)}"
        assert n > 0, f"Sample size must be positive, got {n}"



class TestBinomialSampleSize:
    """Tests for binomial sample size calculation (c>0)."""

    def test_known_value_c1(self):
        """Test with c=1: C=95%, R=90% should give n=46."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        result = calculate_sample_size_with_failures(95.0, 90.0, 1)
        assert result == 46

    def test_known_value_c2(self):
        """Test with c=2: C=95%, R=90% should give n=61."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        result = calculate_sample_size_with_failures(95.0, 90.0, 2)
        assert result == 61

    def test_result_is_integer(self):
        """Verify result is always an integer."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        result = calculate_sample_size_with_failures(95.0, 90.0, 1)
        assert isinstance(result, int)

    def test_result_is_positive(self):
        """Verify result is always positive."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        result = calculate_sample_size_with_failures(95.0, 90.0, 1)
        assert result > 0

    def test_increasing_failures_increases_sample_size(self):
        """Higher allowable failures should require larger sample size."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        n0 = calculate_sample_size_zero_failures(95.0, 90.0)
        n1 = calculate_sample_size_with_failures(95.0, 90.0, 1)
        n2 = calculate_sample_size_with_failures(95.0, 90.0, 2)
        n3 = calculate_sample_size_with_failures(95.0, 90.0, 3)
        assert n0 < n1 < n2 < n3

    def test_increasing_confidence_increases_sample_size(self):
        """Higher confidence should require larger sample size."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        n1 = calculate_sample_size_with_failures(90.0, 90.0, 1)
        n2 = calculate_sample_size_with_failures(95.0, 90.0, 1)
        n3 = calculate_sample_size_with_failures(99.0, 90.0, 1)
        assert n1 < n2 < n3

    def test_increasing_reliability_increases_sample_size(self):
        """Higher reliability should require larger sample size."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        n1 = calculate_sample_size_with_failures(95.0, 80.0, 1)
        n2 = calculate_sample_size_with_failures(95.0, 90.0, 1)
        n3 = calculate_sample_size_with_failures(95.0, 95.0, 1)
        assert n1 < n2 < n3

    def test_edge_case_very_high_confidence(self):
        """Test with very high confidence (99.9%)."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        result = calculate_sample_size_with_failures(99.9, 90.0, 1)
        assert result > 0
        assert isinstance(result, int)

    def test_edge_case_very_high_reliability(self):
        """Test with very high reliability (99.9%)."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )
        result = calculate_sample_size_with_failures(95.0, 99.9, 1)
        assert result > 0
        assert isinstance(result, int)


class TestBinomialSampleSizeProperty:
    """Property-based tests for binomial sample size calculation.
    
    Feature: sample-size-estimator
    Property 2: Binomial Sample Size Correctness
    Property 3: Binomial Sample Size Minimality
    Validates: Requirements 2.2, 2.3
    
    For any confidence C, reliability R, and allowable failures c > 0,
    the calculated sample size n should be the smallest integer where
    the cumulative binomial probability satisfies the criterion.
    """

    @given(
        confidence=st.floats(min_value=50.0, max_value=99.9),
        reliability=st.floats(min_value=50.0, max_value=99.9),
        allowable_failures=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_binomial_sample_size_correctness(
        self, confidence: float, reliability: float, allowable_failures: int
    ):
        """**Validates: Requirements 2.2, 2.3**
        
        Property 2: For any confidence C, reliability R, and allowable failures c > 0,
        the calculated sample size n should be the smallest integer where the
        cumulative binomial probability sum(binom(n,k)*(1-R/100)^k*(R/100)^(n-k)
        for k=0 to c) <= (1-C/100)
        """
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )

        # Calculate sample size using the function
        n = calculate_sample_size_with_failures(
            confidence, reliability, allowable_failures
        )

        # Verify result is a positive integer
        assert isinstance(n, int), f"Result must be an integer, got {type(n)}"
        assert n > 0, f"Sample size must be positive, got {n}"

        # Verify the binomial criterion is satisfied
        c_decimal = confidence / 100.0
        r_decimal = reliability / 100.0
        p_fail = 1 - r_decimal

        # Calculate cumulative probability for the returned n
        cumulative_prob = sum(
            stats.binom.pmf(k, n, p_fail)
            for k in range(allowable_failures + 1)
        )

        # The cumulative probability should be <= (1 - confidence)
        threshold = 1 - c_decimal
        assert cumulative_prob <= threshold + 1e-9, (
            f"Binomial criterion not satisfied for C={confidence}%, R={reliability}%, c={allowable_failures}: "
            f"cumulative_prob={cumulative_prob:.10f} > threshold={threshold:.10f}"
        )

    @given(
        confidence=st.floats(min_value=50.0, max_value=99.9),
        reliability=st.floats(min_value=50.0, max_value=99.9),
        allowable_failures=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_binomial_sample_size_minimality(
        self, confidence: float, reliability: float, allowable_failures: int
    ):
        """**Validates: Requirements 2.3**
        
        Property 3: For any valid inputs where c > 0, if n is the calculated
        sample size, then n-1 should NOT satisfy the binomial criterion
        (ensuring n is truly minimal)
        """
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sample_size_with_failures,
        )

        # Calculate sample size using the function
        n = calculate_sample_size_with_failures(
            confidence, reliability, allowable_failures
        )

        # Verify n-1 does NOT satisfy the criterion (proving minimality)
        c_decimal = confidence / 100.0
        r_decimal = reliability / 100.0
        p_fail = 1 - r_decimal

        # Calculate cumulative probability for n-1
        if n > allowable_failures + 1:  # Only test if n-1 is large enough to be meaningful
            cumulative_prob_n_minus_1 = sum(
                stats.binom.pmf(k, n - 1, p_fail)
                for k in range(allowable_failures + 1)
            )

            # The cumulative probability for n-1 should be > (1 - confidence)
            # This proves that n is the smallest value that satisfies the criterion
            threshold = 1 - c_decimal

            # Use a more lenient tolerance for numerical precision issues
            assert cumulative_prob_n_minus_1 > threshold - 1e-9, (
                f"Minimality violated for C={confidence}%, R={reliability}%, c={allowable_failures}: "
                f"n={n}, n-1={n-1} also satisfies criterion with "
                f"cumulative_prob={cumulative_prob_n_minus_1:.10f} <= threshold={threshold:.10f}"
            )



class TestSensitivityAnalysis:
    """Tests for sensitivity analysis calculation."""

    def test_returns_four_results(self):
        """Verify sensitivity analysis returns exactly 4 results."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sensitivity_analysis,
        )
        result = calculate_sensitivity_analysis(95.0, 90.0)
        assert len(result.results) == 4

    def test_correct_c_values(self):
        """Verify results have c values of 0, 1, 2, 3."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sensitivity_analysis,
        )
        result = calculate_sensitivity_analysis(95.0, 90.0)
        c_values = [r.allowable_failures for r in result.results]
        assert c_values == [0, 1, 2, 3]

    def test_known_values(self):
        """Test with known statistical values: C=95%, R=90%."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sensitivity_analysis,
        )
        result = calculate_sensitivity_analysis(95.0, 90.0)
        # Known values for C=95%, R=90%
        assert result.results[0].sample_size == 29  # c=0
        assert result.results[1].sample_size == 46  # c=1
        assert result.results[2].sample_size == 61  # c=2
        assert result.results[3].sample_size == 76  # c=3

    def test_increasing_sample_sizes(self):
        """Verify sample sizes increase with allowable failures."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sensitivity_analysis,
        )
        result = calculate_sensitivity_analysis(95.0, 90.0)
        sample_sizes = [r.sample_size for r in result.results]
        # Each sample size should be larger than the previous
        for i in range(len(sample_sizes) - 1):
            assert sample_sizes[i] < sample_sizes[i + 1]

    def test_correct_methods(self):
        """Verify correct calculation methods are used."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sensitivity_analysis,
        )
        result = calculate_sensitivity_analysis(95.0, 90.0)
        assert result.results[0].method == "success_run"
        assert result.results[1].method == "binomial"
        assert result.results[2].method == "binomial"
        assert result.results[3].method == "binomial"


class TestSensitivityAnalysisProperty:
    """Property-based tests for sensitivity analysis.
    
    Feature: sample-size-estimator
    Property 4: Sensitivity Analysis Completeness
    Validates: Requirements 3.1
    
    For any confidence C and reliability R, when allowable failures is not specified,
    the system should return exactly 4 results with c values of 0, 1, 2, and 3.
    """

    @given(
        confidence=st.floats(min_value=50.0, max_value=99.9),
        reliability=st.floats(min_value=50.0, max_value=99.9)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_sensitivity_analysis_completeness(
        self, confidence: float, reliability: float
    ):
        """**Validates: Requirements 3.1**
        
        Property 4: For any confidence C and reliability R, when allowable failures
        is not specified, the system should return exactly 4 results with c values
        of 0, 1, 2, and 3.
        """
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_sensitivity_analysis,
        )

        # Calculate sensitivity analysis
        result = calculate_sensitivity_analysis(confidence, reliability)

        # Verify exactly 4 results
        assert len(result.results) == 4, (
            f"Expected exactly 4 results, got {len(result.results)}"
        )

        # Verify c values are 0, 1, 2, 3
        c_values = [r.allowable_failures for r in result.results]
        assert c_values == [0, 1, 2, 3], (
            f"Expected c values [0, 1, 2, 3], got {c_values}"
        )

        # Verify all results have correct confidence and reliability
        for i, r in enumerate(result.results):
            assert r.confidence == confidence, (
                f"Result {i} has incorrect confidence: {r.confidence} != {confidence}"
            )
            assert r.reliability == reliability, (
                f"Result {i} has incorrect reliability: {r.reliability} != {reliability}"
            )
            assert r.sample_size > 0, (
                f"Result {i} has non-positive sample size: {r.sample_size}"
            )

        # Verify sample sizes are increasing
        sample_sizes = [r.sample_size for r in result.results]
        for i in range(len(sample_sizes) - 1):
            assert sample_sizes[i] < sample_sizes[i + 1], (
                f"Sample sizes not increasing: {sample_sizes[i]} >= {sample_sizes[i + 1]} "
                f"at position {i}"
            )

        # Verify correct methods
        assert result.results[0].method == "success_run", (
            f"First result should use success_run method, got {result.results[0].method}"
        )
        for i in range(1, 4):
            assert result.results[i].method == "binomial", (
                f"Result {i} should use binomial method, got {result.results[i].method}"
            )


class TestCalculateAttribute:
    """Tests for main entry point calculate_attribute()."""

    def test_with_c_none_returns_sensitivity(self):
        """Test that c=None returns sensitivity analysis."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_attribute,
        )
        from src.sample_size_estimator.models import AttributeInput, SensitivityResult

        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=None
        )
        result = calculate_attribute(input_data)

        assert isinstance(result, SensitivityResult)
        assert len(result.results) == 4

    def test_with_c_zero_returns_single_result(self):
        """Test that c=0 returns single AttributeResult."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_attribute,
        )
        from src.sample_size_estimator.models import AttributeInput, AttributeResult

        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=0
        )
        result = calculate_attribute(input_data)

        assert isinstance(result, AttributeResult)
        assert result.sample_size == 29
        assert result.allowable_failures == 0
        assert result.method == "success_run"

    def test_with_c_positive_returns_single_result(self):
        """Test that c>0 returns single AttributeResult."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_attribute,
        )
        from src.sample_size_estimator.models import AttributeInput, AttributeResult

        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=2
        )
        result = calculate_attribute(input_data)

        assert isinstance(result, AttributeResult)
        assert result.sample_size == 61
        assert result.allowable_failures == 2
        assert result.method == "binomial"

    def test_known_value_c95_r90(self):
        """Test with known statistical value: C=95%, R=90% → n=29."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_attribute,
        )
        from src.sample_size_estimator.models import AttributeInput

        input_data = AttributeInput(
            confidence=95.0,
            reliability=90.0,
            allowable_failures=0
        )
        result = calculate_attribute(input_data)
        assert result.sample_size == 29

    def test_edge_case_very_high_confidence(self):
        """Test with very high confidence (99.9%)."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_attribute,
        )
        from src.sample_size_estimator.models import AttributeInput

        input_data = AttributeInput(
            confidence=99.9,
            reliability=90.0,
            allowable_failures=0
        )
        result = calculate_attribute(input_data)
        assert result.sample_size > 0
        assert isinstance(result.sample_size, int)

    def test_edge_case_very_low_confidence(self):
        """Test with very low confidence (50.1%)."""
        from src.sample_size_estimator.calculations.attribute_calcs import (
            calculate_attribute,
        )
        from src.sample_size_estimator.models import AttributeInput

        input_data = AttributeInput(
            confidence=50.1,
            reliability=90.0,
            allowable_failures=0
        )
        result = calculate_attribute(input_data)
        assert result.sample_size > 0
        assert isinstance(result.sample_size, int)
