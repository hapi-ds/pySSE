"""Attribute data calculations for binomial sample size estimation.

This module implements sample size calculations for attribute (pass/fail) testing
using the Success Run Theorem and cumulative binomial distribution methods.
"""

import math

from scipy import stats

from ..models import AttributeInput, AttributeResult, SensitivityResult


def calculate_sample_size_zero_failures(
    confidence: float,
    reliability: float
) -> int:
    """Calculate minimum sample size using Success Run Theorem (c=0).

    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)

    Returns:
        Minimum sample size (integer)

    Formula: n = ceil(ln(1-C/100) / ln(R/100))

    Example:
        >>> calculate_sample_size_zero_failures(95.0, 90.0)
        29
    """
    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0
    n = math.ceil(math.log(1 - c_decimal) / math.log(r_decimal))
    return n


def calculate_sample_size_with_failures(
    confidence: float,
    reliability: float,
    allowable_failures: int
) -> int:
    """Calculate minimum sample size using cumulative binomial distribution (c>0).

    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
        allowable_failures: Maximum allowable failures (c)

    Returns:
        Minimum sample size (integer)

    Iteratively solves for smallest n where:
    sum(binom(n,k) * (1-R)^k * R^(n-k) for k=0 to c) <= 1-C

    Example:
        >>> calculate_sample_size_with_failures(95.0, 90.0, 1)
        46

    Raises:
        ValueError: If no valid sample size found within reasonable range
    """
    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0
    p_fail = 1 - r_decimal

    # Start from a reasonable minimum - must be at least c+1 to allow c failures
    n = allowable_failures + 1

    while n < 100000:  # Increased safety limit for extreme cases
        cumulative_prob = sum(
            stats.binom.pmf(k, n, p_fail)
            for k in range(allowable_failures + 1)
        )

        if cumulative_prob <= (1 - c_decimal):
            return n
        n += 1

    raise ValueError("Could not find valid sample size within reasonable range")


def calculate_sensitivity_analysis(
    confidence: float,
    reliability: float
) -> SensitivityResult:
    """Calculate sample sizes for c=0, 1, 2, 3.

    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)

    Returns:
        SensitivityResult containing results for all c values

    Example:
        >>> result = calculate_sensitivity_analysis(95.0, 90.0)
        >>> len(result.results)
        4
        >>> result.results[0].allowable_failures
        0
    """
    results = []

    for c in range(4):
        if c == 0:
            n = calculate_sample_size_zero_failures(confidence, reliability)
            method = "success_run"
        else:
            n = calculate_sample_size_with_failures(confidence, reliability, c)
            method = "binomial"

        results.append(AttributeResult(
            sample_size=n,
            allowable_failures=c,
            confidence=confidence,
            reliability=reliability,
            method=method
        ))

    return SensitivityResult(results=results)


def calculate_attribute(input_data: AttributeInput) -> AttributeResult | SensitivityResult:
    """Main entry point for attribute calculations.

    Args:
        input_data: Validated input parameters

    Returns:
        Single result if c specified, sensitivity analysis if c is None

    Example:
        >>> from src.sample_size_estimator.models import AttributeInput
        >>> # Single calculation with c=0
        >>> input_data = AttributeInput(confidence=95.0, reliability=90.0, allowable_failures=0)
        >>> result = calculate_attribute(input_data)
        >>> result.sample_size
        29
        >>> # Sensitivity analysis (c=None)
        >>> input_data = AttributeInput(confidence=95.0, reliability=90.0, allowable_failures=None)
        >>> result = calculate_attribute(input_data)
        >>> len(result.results)
        4
    """
    if input_data.allowable_failures is None:
        return calculate_sensitivity_analysis(
            input_data.confidence,
            input_data.reliability
        )
    elif input_data.allowable_failures == 0:
        n = calculate_sample_size_zero_failures(
            input_data.confidence,
            input_data.reliability
        )
        return AttributeResult(
            sample_size=n,
            allowable_failures=0,
            confidence=input_data.confidence,
            reliability=input_data.reliability,
            method="success_run"
        )
    else:
        n = calculate_sample_size_with_failures(
            input_data.confidence,
            input_data.reliability,
            input_data.allowable_failures
        )
        return AttributeResult(
            sample_size=n,
            allowable_failures=input_data.allowable_failures,
            confidence=input_data.confidence,
            reliability=input_data.reliability,
            method="binomial"
        )
