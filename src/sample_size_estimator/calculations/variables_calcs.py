"""
Variables calculations module for normally distributed data.

This module implements tolerance factor and limit calculations for continuous
measurements following a normal distribution.
"""

from typing import TYPE_CHECKING

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from ..models import VariablesInput, VariablesResult


def calculate_one_sided_tolerance_factor(
    n: int,
    confidence: float,
    reliability: float
) -> float:
    """
    Calculate one-sided tolerance factor using non-central t-distribution.

    Args:
        n: Sample size (must be > 1)
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)

    Returns:
        Tolerance factor k1

    Formula: k1 = t_{n-1, 1-alpha}(delta) / sqrt(n)
    where delta = z_R * sqrt(n)

    Requirements: REQ-4.1
    """
    if n <= 1:
        raise ValueError("Sample size must be greater than 1")

    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0

    # Calculate z-score for reliability level
    z_r = stats.norm.ppf(r_decimal)

    # Calculate non-centrality parameter
    delta = z_r * np.sqrt(n)

    # Calculate tolerance factor using non-central t-distribution
    k1 = stats.nct.ppf(c_decimal, df=n-1, nc=delta) / np.sqrt(n)

    return float(k1)


def calculate_two_sided_tolerance_factor(
    n: int,
    confidence: float,
    reliability: float
) -> float:
    """
    Calculate two-sided tolerance factor using Howe-Guenther approximation.

    Args:
        n: Sample size (must be > 1)
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)

    Returns:
        Tolerance factor k2

    Formula: k2 = sqrt((1 + 1/n) * z^2_{(1+R)/2} * (n-1) / chi^2_{1-C, n-1})

    Requirements: REQ-4.2
    """
    if n <= 1:
        raise ValueError("Sample size must be greater than 1")

    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0

    # Calculate z-score for two-sided reliability
    z_val = stats.norm.ppf((1 + r_decimal) / 2)

    # Calculate chi-squared value at 1-C level (lower tail)
    chi2_val = stats.chi2.ppf(1 - c_decimal, df=n-1)

    # Calculate tolerance factor using Howe-Guenther approximation
    k2 = np.sqrt((1 + 1/n) * z_val**2 * (n - 1) / chi2_val)

    return float(k2)


def calculate_tolerance_limits(
    mean: float,
    std: float,
    k: float,
    sided: str
) -> tuple[float | None, float | None]:
    """
    Calculate tolerance limits from sample statistics.

    Args:
        mean: Sample mean
        std: Sample standard deviation (must be > 0)
        k: Tolerance factor
        sided: "one" or "two" (one-sided or two-sided limits)

    Returns:
        Tuple of (lower_limit, upper_limit). None for limits not calculated.
        - For two-sided: both limits are calculated
        - For one-sided: only upper limit is calculated (lower is None)

    Formula:
        - Upper limit: mean + k * std
        - Lower limit: mean - k * std (two-sided only)

    Requirements: REQ-5.1, REQ-5.2, REQ-5.3
    """
    if std <= 0:
        raise ValueError("Standard deviation must be greater than 0")

    if sided not in ["one", "two"]:
        raise ValueError("sided parameter must be 'one' or 'two'")

    if sided == "two":
        # Two-sided: calculate both limits
        lower = mean - k * std
        upper = mean + k * std
        return (lower, upper)
    else:
        # One-sided: only upper limit (assuming upper specification)
        upper = mean + k * std
        return (None, upper)



def calculate_ppk(
    mean: float,
    std: float,
    lsl: float | None,
    usl: float | None
) -> float | None:
    """
    Calculate process performance index (Ppk).

    Args:
        mean: Sample mean
        std: Sample standard deviation (must be > 0)
        lsl: Lower specification limit (optional)
        usl: Upper specification limit (optional)

    Returns:
        Ppk value, or None if no spec limits provided

    Formula: Ppk = min((USL - mean)/(3*std), (mean - LSL)/(3*std))
    - For two-sided specs: minimum of both terms
    - For one-sided specs: only the relevant term

    Requirements: REQ-7.1, REQ-7.2
    """
    if std <= 0:
        raise ValueError("Standard deviation must be greater than 0")

    # If no specification limits provided, cannot calculate Ppk
    if lsl is None and usl is None:
        return None

    ppk_values = []

    # Calculate upper Ppk if USL is provided
    if usl is not None:
        ppk_upper = (usl - mean) / (3 * std)
        ppk_values.append(ppk_upper)

    # Calculate lower Ppk if LSL is provided
    if lsl is not None:
        ppk_lower = (mean - lsl) / (3 * std)
        ppk_values.append(ppk_lower)

    # Return minimum of calculated values
    return float(min(ppk_values))



def compare_to_spec_limits(
    lower_tol: float | None,
    upper_tol: float | None,
    lsl: float | None,
    usl: float | None
) -> tuple[str | None, float | None, float | None]:
    """
    Compare tolerance limits to specification limits.

    Args:
        lower_tol: Lower tolerance limit (can be None for one-sided)
        upper_tol: Upper tolerance limit (can be None for one-sided)
        lsl: Lower specification limit (optional)
        usl: Upper specification limit (optional)

    Returns:
        Tuple of (pass_fail, margin_lower, margin_upper)
        - pass_fail: "PASS" if all tolerance limits are within spec limits,
          "FAIL" otherwise, None if no spec limits
        - margin_lower: lower_tol - lsl (positive means passing),
          None if not applicable
        - margin_upper: usl - upper_tol (positive means passing),
          None if not applicable

    Logic:
        - PASS: lower_tol >= lsl AND upper_tol <= usl (for applicable limits)
        - FAIL: any tolerance limit violates its corresponding specification limit
        - None: no specification limits provided

    Requirements: REQ-6.2, REQ-6.3, REQ-6.4, REQ-6.5
    """
    # If no specification limits provided, cannot perform comparison
    if lsl is None and usl is None:
        return (None, None, None)

    # Initialize as PASS, will change to FAIL if any limit is violated
    pass_fail = "PASS"
    margin_lower = None
    margin_upper = None

    # Check lower specification limit
    if lsl is not None and lower_tol is not None:
        margin_lower = lower_tol - lsl
        if margin_lower < 0:
            pass_fail = "FAIL"

    # Check upper specification limit
    if usl is not None and upper_tol is not None:
        margin_upper = usl - upper_tol
        if margin_upper < 0:
            pass_fail = "FAIL"

    return (pass_fail, margin_lower, margin_upper)


def calculate_variables(input_data: "VariablesInput") -> "VariablesResult":
    """
    Main entry point for variables calculations.

    Integrates all variable data calculations:
    1. Calculate tolerance factor (one-sided or two-sided)
    2. Calculate tolerance limits
    3. Calculate Ppk (if spec limits provided)
    4. Compare tolerance limits to spec limits (if spec limits provided)

    Args:
        input_data: Validated input parameters (VariablesInput model)

    Returns:
        Complete variables analysis results (VariablesResult model)

    Requirements: REQ-4, REQ-5, REQ-6, REQ-7
    """
    # Import here to avoid circular dependency
    from ..models import VariablesResult

    # Step 1: Calculate tolerance factor based on sided parameter
    if input_data.sided == "one":
        k = calculate_one_sided_tolerance_factor(
            input_data.sample_size,
            input_data.confidence,
            input_data.reliability
        )
    else:  # sided == "two"
        k = calculate_two_sided_tolerance_factor(
            input_data.sample_size,
            input_data.confidence,
            input_data.reliability
        )

    # Step 2: Calculate tolerance limits
    lower_tol, upper_tol = calculate_tolerance_limits(
        input_data.sample_mean,
        input_data.sample_std,
        k,
        input_data.sided
    )

    # Step 3: Calculate Ppk (if spec limits provided)
    ppk = calculate_ppk(
        input_data.sample_mean,
        input_data.sample_std,
        input_data.lsl,
        input_data.usl
    )

    # Step 4: Compare to spec limits (if spec limits provided)
    pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
        lower_tol,
        upper_tol,
        input_data.lsl,
        input_data.usl
    )

    # Return complete results
    return VariablesResult(
        tolerance_factor=k,
        lower_tolerance_limit=lower_tol,
        upper_tolerance_limit=upper_tol,
        ppk=ppk,
        pass_fail=pass_fail,
        margin_lower=margin_lower,
        margin_upper=margin_upper
    )
