"""Non-normal data calculations module.

This module handles non-normal data through outlier detection, normality testing,
transformations, and non-parametric methods.
"""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from ..models import NormalityTestResult, TransformationResult


def detect_outliers(data: list[float]) -> tuple[list[float], list[int]]:
    """
    Detect outliers using IQR method.

    Args:
        data: Raw dataset

    Returns:
        Tuple of (outlier_values, outlier_indices)

    Method: Flag points < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
    """
    arr = np.array(data)
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (arr < lower_bound) | (arr > upper_bound)
    outlier_indices = np.where(outlier_mask)[0].tolist()
    outlier_values = arr[outlier_mask].tolist()

    return (outlier_values, outlier_indices)



def test_normality(data: list[float]) -> "NormalityTestResult":
    """
    Perform Shapiro-Wilk and Anderson-Darling normality tests.

    Args:
        data: Dataset to test

    Returns:
        NormalityTestResult with test statistics and interpretation
    """
    from ..models import NormalityTestResult

    arr = np.array(data)

    # Check for constant data (zero variance)
    if np.std(arr) == 0:
        # Constant data is not normal (degenerate case)
        return NormalityTestResult(
            shapiro_wilk_statistic=1.0,
            shapiro_wilk_pvalue=1.0,
            anderson_darling_statistic=0.0,
            anderson_darling_critical_values=[0.576, 0.656, 0.787, 0.918, 1.092],
            is_normal=False,
            interpretation="Data has zero variance (constant values) - not normally distributed"
        )

    # Shapiro-Wilk test
    sw_stat, sw_pval = stats.shapiro(arr)

    # Anderson-Darling test
    ad_result = stats.anderson(arr, dist='norm', method='interpolate')
    ad_stat = ad_result.statistic
    ad_pval = ad_result.pvalue

    # For backward compatibility, get critical values if available
    if hasattr(ad_result, 'critical_values'):
        ad_critical = ad_result.critical_values.tolist()
    else:
        # Use standard critical values for normal distribution at different significance levels
        ad_critical = [0.576, 0.656, 0.787, 0.918, 1.092]  # 15%, 10%, 5%, 2.5%, 1%

    # Determine if normal (using alpha=0.05)
    is_normal = (sw_pval > 0.05) and (ad_pval > 0.05)

    # Generate interpretation
    if is_normal:
        interpretation = "Data appears to follow a normal distribution (p > 0.05)"
    else:
        interpretation = "Data does not follow a normal distribution (p <= 0.05 or AD statistic exceeds critical value)"

    return NormalityTestResult(
        shapiro_wilk_statistic=float(sw_stat),
        shapiro_wilk_pvalue=float(sw_pval),
        anderson_darling_statistic=float(ad_stat),
        anderson_darling_critical_values=ad_critical,
        is_normal=is_normal,
        interpretation=interpretation
    )


def generate_qq_plot(data: list[float]) -> plt.Figure:
    """
    Generate Q-Q probability plot for normality assessment.

    Args:
        data: Dataset to plot

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    stats.probplot(data, dist="norm", plot=ax)
    ax.set_title("Q-Q Plot for Normality Assessment")
    ax.set_xlabel("Theoretical Quantiles")
    ax.set_ylabel("Sample Quantiles")
    ax.grid(True, alpha=0.3)
    return fig



def transform_boxcox(data: list[float]) -> tuple[list[float], float]:
    """
    Apply Box-Cox transformation with automatic lambda optimization.

    Args:
        data: Raw dataset (must be positive)

    Returns:
        Tuple of (transformed_data, lambda_parameter)

    Raises:
        ValueError: If data contains non-positive values or is constant
    """
    arr = np.array(data)

    if np.any(arr <= 0):
        raise ValueError("Box-Cox transformation requires all positive values")

    # Check for constant data (zero variance)
    if np.std(arr) == 0:
        raise ValueError("Box-Cox transformation requires non-constant data")

    transformed, lambda_param = stats.boxcox(arr)

    return (transformed.tolist(), float(lambda_param))


def transform_log(data: list[float]) -> list[float]:
    """
    Apply natural logarithm transformation.

    Args:
        data: Raw dataset (must be positive)

    Returns:
        Transformed dataset

    Raises:
        ValueError: If data contains non-positive values
    """
    arr = np.array(data)

    if np.any(arr <= 0):
        raise ValueError("Logarithmic transformation requires all positive values")

    result: list[float] = np.log(arr).tolist()
    return result


def transform_sqrt(data: list[float]) -> list[float]:
    """
    Apply square root transformation.

    Args:
        data: Raw dataset (must be non-negative)

    Returns:
        Transformed dataset

    Raises:
        ValueError: If data contains negative values
    """
    arr = np.array(data)

    if np.any(arr < 0):
        raise ValueError("Square root transformation requires non-negative values")

    result: list[float] = np.sqrt(arr).tolist()
    return result



def back_transform_log(transformed_value: float) -> float:
    """Back-transform from log scale to original scale."""
    result: float = float(np.exp(transformed_value))
    return result


def back_transform_boxcox(transformed_value: float, lambda_param: float) -> float:
    """
    Back-transform from Box-Cox scale to original scale.

    Formula: original = (lambda * transformed + 1)^(1/lambda)
    """
    if abs(lambda_param) < 1e-10:  # lambda ≈ 0 means log transform
        result_log: float = float(np.exp(transformed_value))
        return result_log
    else:
        # Protect against numerical overflow
        try:
            result_val = np.power(lambda_param * transformed_value + 1, 1 / lambda_param)
            if np.isinf(result_val) or np.isnan(result_val):
                # Numerical overflow, return a large value
                return 1e100 if transformed_value > 0 else 0.0
            result_bc: float = float(result_val)
            return result_bc
        except (OverflowError, RuntimeWarning):
            return 1e100 if transformed_value > 0 else 0.0


def back_transform_sqrt(transformed_value: float) -> float:
    """Back-transform from square root scale to original scale."""
    result: float = float(transformed_value ** 2)
    return result
    return transformed_value ** 2



def apply_transformation(data: list[float], method: str) -> "TransformationResult":
    """
    Apply specified transformation and re-test normality.

    Args:
        data: Raw dataset
        method: "boxcox", "log", or "sqrt"

    Returns:
        TransformationResult with transformed data and normality test
    """
    from ..models import TransformationResult

    lambda_param = None

    if method == "boxcox":
        transformed_data, lambda_param = transform_boxcox(data)
    elif method == "log":
        transformed_data = transform_log(data)
    elif method == "sqrt":
        transformed_data = transform_sqrt(data)
    else:
        raise ValueError(f"Unknown transformation method: {method}")

    # Re-test normality on transformed data
    normality_result = test_normality(transformed_data)

    return TransformationResult(
        method=method,
        lambda_param=lambda_param,
        transformed_data=transformed_data,
        normality_after=normality_result
    )


def calculate_wilks_limits(
    data: list[float],
    confidence: float,
    reliability: float
) -> tuple[float, float]:
    """
    Calculate non-parametric tolerance limits using Wilks' method.

    Args:
        data: Raw dataset
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)

    Returns:
        Tuple of (lower_limit, upper_limit) using min/max of sample

    Note: This is a simplified implementation. Full Wilks' method
    requires specific sample size calculations.
    """
    arr = np.array(data)
    return (float(np.min(arr)), float(np.max(arr)))
