# Design Document: Sample Size Estimator

## Overview

The Sample Size Estimator is a Python-based web application built with Streamlit that provides statistical calculations for medical device validation. The system implements four distinct statistical analysis modules using a functional programming approach with strong type safety via Pydantic.

### Design Principles

1. **Functional Programming**: Pure functions for all calculations, avoiding classes except for data models
2. **Type Safety**: Pydantic models for all data structures with runtime validation
3. **Modularity**: Each statistical method in a separate module for easy extension
4. **Testability**: All calculation functions are pure and easily testable
5. **Auditability**: Comprehensive logging and hash-based validation state tracking
6. **Regulatory Compliance**: Full traceability and validation documentation per ISO/TR 80002-2

### Technology Stack

- **Framework**: Streamlit 1.x (latest stable)
- **Validation**: Pydantic 2.x for settings and data models
- **Statistics**: SciPy 1.x for statistical distributions and tests
- **Numerical**: NumPy 1.x for array operations
- **Plotting**: Matplotlib 3.x for Q-Q plots
- **PDF Generation**: ReportLab 4.x for report generation
- **Testing**: pytest 8.x with property-based testing support
- **Package Management**: uv for dependency management
- **Type Checking**: mypy for static type analysis

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Attribute │ │Variables │ │Non-Normal│ │Reliability│      │
│  │   Tab    │ │   Tab    │ │   Tab    │ │   Tab    │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
└───────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │
┌───────┼────────────┼────────────┼────────────┼─────────────┐
│       │            │            │            │              │
│  ┌────▼─────┐ ┌───▼──────┐ ┌──▼───────┐ ┌──▼────────┐    │
│  │attribute │ │variables │ │non_normal│ │reliability│    │
│  │_calcs.py │ │_calcs.py │ │_calcs.py │ │_calcs.py  │    │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘    │
│                                                             │
│                  Calculation Engine Layer                   │
└─────────────────────────────────────────────────────────────┘
        │            │            │            │
┌───────┼────────────┼────────────┼────────────┼─────────────┐
│  ┌────▼────────────▼────────────▼────────────▼──────┐      │
│  │           models.py (Pydantic Models)            │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │         config.py (Settings Management)          │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │         validation.py (Hash Verification)        │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │         reports.py (PDF Generation)              │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │         logger.py (Audit Trail Logging)          │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
│                    Core Services Layer                      │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
sample-size-estimator/
├── src/
│   └── sample_size_estimator/
│       ├── __init__.py
│       ├── app.py                    # Main Streamlit application
│       ├── config.py                 # Pydantic settings
│       ├── models.py                 # Data models
│       ├── logger.py                 # Logging configuration
│       ├── validation.py             # Hash verification
│       ├── reports.py                # PDF report generation
│       ├── calculations/
│       │   ├── __init__.py
│       │   ├── attribute_calcs.py   # Binomial calculations
│       │   ├── variables_calcs.py   # Normal distribution calculations
│       │   ├── non_normal_calcs.py  # Transformations and non-parametric
│       │   └── reliability_calcs.py # Life testing calculations
│       └── ui/
│           ├── __init__.py
│           ├── attribute_tab.py     # Attribute analysis UI
│           ├── variables_tab.py     # Variables analysis UI
│           ├── non_normal_tab.py    # Non-normal analysis UI
│           └── reliability_tab.py   # Reliability analysis UI
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_attribute_calcs.py
│   ├── test_variables_calcs.py
│   ├── test_non_normal_calcs.py
│   ├── test_reliability_calcs.py
│   ├── test_validation.py
│   ├── test_ui_playwright_attribute.py    # Playwright UI tests
│   ├── test_ui_playwright_variables.py
│   ├── test_ui_playwright_non_normal.py
│   └── test_ui_playwright_reliability.py
├── docs/
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── VALIDATION_PROTOCOL.md
├── pyproject.toml                   # uv project configuration
├── uv.lock                          # Locked dependencies
├── README.md
└── .env.example                     # Example configuration
```


## Components and Interfaces

### 1. Configuration Management (config.py)

**Purpose**: Centralized configuration using Pydantic Settings for environment-based configuration.

**Interface**:
```python
from pydantic_settings import BaseSettings
from typing import Optional

class AppSettings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Application settings
    app_title: str = "Sample Size Estimator"
    app_version: str = "1.0.0"
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_format: str = "json"
    
    # Validation settings
    validated_hash: Optional[str] = None
    calculations_file: str = "src/sample_size_estimator/calculations/__init__.py"
    
    # Report settings
    report_output_dir: str = "reports"
    report_author: str = "Sample Size Estimator System"
    
    # Statistical defaults
    default_confidence: float = 95.0
    default_reliability: float = 90.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> AppSettings:
    """Get application settings singleton."""
    return AppSettings()
```

### 2. Data Models (models.py)

**Purpose**: Type-safe data structures for all inputs, outputs, and intermediate calculations.

**Interface**:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime

class AttributeInput(BaseModel):
    """Input parameters for attribute data analysis."""
    confidence: float = Field(ge=0.0, le=100.0, description="Confidence level (%)")
    reliability: float = Field(ge=0.0, le=100.0, description="Reliability (%)")
    allowable_failures: Optional[int] = Field(None, ge=0, description="Allowable failures (c)")
    
    @field_validator('confidence', 'reliability')
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v

class AttributeResult(BaseModel):
    """Output from attribute data analysis."""
    sample_size: int = Field(description="Minimum required sample size")
    allowable_failures: int = Field(description="Number of allowable failures")
    confidence: float = Field(description="Confidence level used (%)")
    reliability: float = Field(description="Reliability level used (%)")
    method: Literal["success_run", "binomial"] = Field(description="Calculation method")

class SensitivityResult(BaseModel):
    """Sensitivity analysis results for multiple failure scenarios."""
    results: List[AttributeResult] = Field(description="Results for c=0,1,2,3")

class VariablesInput(BaseModel):
    """Input parameters for variables data analysis."""
    confidence: float = Field(ge=0.0, le=100.0, description="Confidence level (%)")
    reliability: float = Field(ge=0.0, le=100.0, description="Reliability (%)")
    sample_size: int = Field(gt=1, description="Sample size")
    sample_mean: float = Field(description="Sample mean")
    sample_std: float = Field(gt=0.0, description="Sample standard deviation")
    lsl: Optional[float] = Field(None, description="Lower specification limit")
    usl: Optional[float] = Field(None, description="Upper specification limit")
    sided: Literal["one", "two"] = Field(description="One-sided or two-sided limits")

class VariablesResult(BaseModel):
    """Output from variables data analysis."""
    tolerance_factor: float = Field(description="Calculated tolerance factor (k)")
    lower_tolerance_limit: Optional[float] = Field(None, description="Lower tolerance limit")
    upper_tolerance_limit: Optional[float] = Field(None, description="Upper tolerance limit")
    ppk: Optional[float] = Field(None, description="Process performance index")
    pass_fail: Optional[Literal["PASS", "FAIL"]] = Field(None, description="Comparison result")
    margin_lower: Optional[float] = Field(None, description="Margin to LSL")
    margin_upper: Optional[float] = Field(None, description="Margin to USL")

class NormalityTestResult(BaseModel):
    """Results from normality testing."""
    shapiro_wilk_statistic: float
    shapiro_wilk_pvalue: float
    anderson_darling_statistic: float
    anderson_darling_critical_values: List[float]
    is_normal: bool = Field(description="True if data passes normality tests")
    interpretation: str = Field(description="Human-readable interpretation")

class TransformationResult(BaseModel):
    """Results from data transformation."""
    method: Literal["boxcox", "log", "sqrt"] = Field(description="Transformation method")
    lambda_param: Optional[float] = Field(None, description="Box-Cox lambda parameter")
    transformed_data: List[float] = Field(description="Transformed dataset")
    normality_after: NormalityTestResult = Field(description="Normality test after transformation")

class ReliabilityInput(BaseModel):
    """Input parameters for reliability life testing."""
    confidence: float = Field(ge=0.0, le=100.0, description="Confidence level (%)")
    reliability: float = Field(ge=0.0, le=100.0, description="Reliability (%)")
    failures: int = Field(ge=0, description="Number of failures")
    activation_energy: Optional[float] = Field(None, gt=0.0, description="Activation energy (eV)")
    use_temperature: Optional[float] = Field(None, gt=0.0, description="Use temperature (K)")
    test_temperature: Optional[float] = Field(None, gt=0.0, description="Test temperature (K)")

class ReliabilityResult(BaseModel):
    """Output from reliability life testing."""
    test_duration: float = Field(description="Required test duration or units")
    acceleration_factor: Optional[float] = Field(None, description="Acceleration factor")
    method: str = Field(description="Calculation method used")

class CalculationReport(BaseModel):
    """Complete calculation report for PDF generation."""
    timestamp: datetime = Field(default_factory=datetime.now)
    module: Literal["attribute", "variables", "non_normal", "reliability"]
    inputs: dict = Field(description="All input parameters")
    results: dict = Field(description="All calculated results")
    engine_hash: str = Field(description="SHA-256 hash of calculation engine")
    validated_state: bool = Field(description="True if hash matches validated hash")
    app_version: str = Field(description="Application version")
```


### 3. Calculation Modules

#### 3.1 Attribute Calculations (attribute_calcs.py)

**Purpose**: Implement binomial-based sample size calculations for attribute data.

**Interface**:
```python
from typing import Union
import math
from scipy import stats
from ..models import AttributeInput, AttributeResult, SensitivityResult

def calculate_sample_size_zero_failures(
    confidence: float,
    reliability: float
) -> int:
    """
    Calculate minimum sample size using Success Run Theorem (c=0).
    
    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
    
    Returns:
        Minimum sample size (integer)
    
    Formula: n = ceil(ln(1-C/100) / ln(R/100))
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
    """
    Calculate minimum sample size using cumulative binomial distribution (c>0).
    
    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
        allowable_failures: Maximum allowable failures (c)
    
    Returns:
        Minimum sample size (integer)
    
    Iteratively solves for smallest n where:
    sum(binom(n,k) * (1-R)^k * R^(n-k) for k=0 to c) <= 1-C
    """
    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0
    p_fail = 1 - r_decimal
    
    # Start with a reasonable initial guess
    n = allowable_failures + 10
    
    while n < 10000:  # Safety limit
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
    """
    Calculate sample sizes for c=0, 1, 2, 3.
    
    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
    
    Returns:
        SensitivityResult containing results for all c values
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

def calculate_attribute(input_data: AttributeInput) -> Union[AttributeResult, SensitivityResult]:
    """
    Main entry point for attribute calculations.
    
    Args:
        input_data: Validated input parameters
    
    Returns:
        Single result if c specified, sensitivity analysis if c is None
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
```

#### 3.2 Variables Calculations (variables_calcs.py)

**Purpose**: Implement tolerance factor and limit calculations for normally distributed data.

**Interface**:
```python
from scipy import stats
import numpy as np
from ..models import VariablesInput, VariablesResult

def calculate_one_sided_tolerance_factor(
    n: int,
    confidence: float,
    reliability: float
) -> float:
    """
    Calculate one-sided tolerance factor using non-central t-distribution.
    
    Args:
        n: Sample size
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
    
    Returns:
        Tolerance factor k1
    
    Formula: k1 = t_{n-1, 1-alpha}(delta) / sqrt(n)
    where delta = z_R * sqrt(n)
    """
    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0
    
    z_r = stats.norm.ppf(r_decimal)
    delta = z_r * np.sqrt(n)
    
    # Non-central t-distribution
    k1 = stats.nct.ppf(c_decimal, df=n-1, nc=delta) / np.sqrt(n)
    
    return k1

def calculate_two_sided_tolerance_factor(
    n: int,
    confidence: float,
    reliability: float
) -> float:
    """
    Calculate two-sided tolerance factor using Howe-Guenther approximation.
    
    Args:
        n: Sample size
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
    
    Returns:
        Tolerance factor k2
    
    Formula: k2 = sqrt((1 + 1/n) * z^2_{(1+R)/2} * (n-1) / chi^2_{1-C, n-1})
    """
    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0
    
    z_val = stats.norm.ppf((1 + r_decimal) / 2)
    chi2_val = stats.chi2.ppf(c_decimal, df=n-1)
    
    k2 = np.sqrt((1 + 1/n) * z_val**2 * (n - 1) / chi2_val)
    
    return k2

def calculate_tolerance_limits(
    mean: float,
    std: float,
    k: float,
    sided: str
) -> tuple[Optional[float], Optional[float]]:
    """
    Calculate tolerance limits from sample statistics.
    
    Args:
        mean: Sample mean
        std: Sample standard deviation
        k: Tolerance factor
        sided: "one" or "two"
    
    Returns:
        Tuple of (lower_limit, upper_limit). None for limits not calculated.
    """
    if sided == "two":
        lower = mean - k * std
        upper = mean + k * std
        return (lower, upper)
    else:
        # For one-sided, assume upper limit (can be parameterized)
        upper = mean + k * std
        return (None, upper)

def calculate_ppk(
    mean: float,
    std: float,
    lsl: Optional[float],
    usl: Optional[float]
) -> Optional[float]:
    """
    Calculate process performance index (Ppk).
    
    Args:
        mean: Sample mean
        std: Sample standard deviation
        lsl: Lower specification limit (optional)
        usl: Upper specification limit (optional)
    
    Returns:
        Ppk value, or None if no spec limits provided
    
    Formula: Ppk = min((USL - mean)/(3*std), (mean - LSL)/(3*std))
    """
    if lsl is None and usl is None:
        return None
    
    ppk_values = []
    
    if usl is not None:
        ppk_upper = (usl - mean) / (3 * std)
        ppk_values.append(ppk_upper)
    
    if lsl is not None:
        ppk_lower = (mean - lsl) / (3 * std)
        ppk_values.append(ppk_lower)
    
    return min(ppk_values)

def compare_to_spec_limits(
    lower_tol: Optional[float],
    upper_tol: Optional[float],
    lsl: Optional[float],
    usl: Optional[float]
) -> tuple[Optional[str], Optional[float], Optional[float]]:
    """
    Compare tolerance limits to specification limits.
    
    Args:
        lower_tol: Lower tolerance limit
        upper_tol: Upper tolerance limit
        lsl: Lower specification limit
        usl: Upper specification limit
    
    Returns:
        Tuple of (pass_fail, margin_lower, margin_upper)
    """
    if lsl is None and usl is None:
        return (None, None, None)
    
    pass_fail = "PASS"
    margin_lower = None
    margin_upper = None
    
    if lsl is not None and lower_tol is not None:
        margin_lower = lower_tol - lsl
        if margin_lower < 0:
            pass_fail = "FAIL"
    
    if usl is not None and upper_tol is not None:
        margin_upper = usl - upper_tol
        if margin_upper < 0:
            pass_fail = "FAIL"
    
    return (pass_fail, margin_lower, margin_upper)

def calculate_variables(input_data: VariablesInput) -> VariablesResult:
    """
    Main entry point for variables calculations.
    
    Args:
        input_data: Validated input parameters
    
    Returns:
        Complete variables analysis results
    """
    # Calculate tolerance factor
    if input_data.sided == "one":
        k = calculate_one_sided_tolerance_factor(
            input_data.sample_size,
            input_data.confidence,
            input_data.reliability
        )
    else:
        k = calculate_two_sided_tolerance_factor(
            input_data.sample_size,
            input_data.confidence,
            input_data.reliability
        )
    
    # Calculate tolerance limits
    lower_tol, upper_tol = calculate_tolerance_limits(
        input_data.sample_mean,
        input_data.sample_std,
        k,
        input_data.sided
    )
    
    # Calculate Ppk
    ppk = calculate_ppk(
        input_data.sample_mean,
        input_data.sample_std,
        input_data.lsl,
        input_data.usl
    )
    
    # Compare to spec limits
    pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
        lower_tol,
        upper_tol,
        input_data.lsl,
        input_data.usl
    )
    
    return VariablesResult(
        tolerance_factor=k,
        lower_tolerance_limit=lower_tol,
        upper_tolerance_limit=upper_tol,
        ppk=ppk,
        pass_fail=pass_fail,
        margin_lower=margin_lower,
        margin_upper=margin_upper
    )
```


#### 3.3 Non-Normal Calculations (non_normal_calcs.py)

**Purpose**: Handle non-normal data through outlier detection, normality testing, transformations, and non-parametric methods.

**Interface**:
```python
from scipy import stats
import numpy as np
from typing import List, Tuple
import matplotlib.pyplot as plt
from ..models import NormalityTestResult, TransformationResult

def detect_outliers(data: List[float]) -> Tuple[List[float], List[int]]:
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

def test_normality(data: List[float]) -> NormalityTestResult:
    """
    Perform Shapiro-Wilk and Anderson-Darling normality tests.
    
    Args:
        data: Dataset to test
    
    Returns:
        NormalityTestResult with test statistics and interpretation
    """
    arr = np.array(data)
    
    # Shapiro-Wilk test
    sw_stat, sw_pval = stats.shapiro(arr)
    
    # Anderson-Darling test
    ad_result = stats.anderson(arr, dist='norm')
    ad_stat = ad_result.statistic
    ad_critical = ad_result.critical_values.tolist()
    
    # Determine if normal (using alpha=0.05)
    is_normal = (sw_pval > 0.05) and (ad_stat < ad_critical[2])  # Index 2 is 5% level
    
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

def generate_qq_plot(data: List[float]) -> plt.Figure:
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

def transform_boxcox(data: List[float]) -> Tuple[List[float], float]:
    """
    Apply Box-Cox transformation with automatic lambda optimization.
    
    Args:
        data: Raw dataset (must be positive)
    
    Returns:
        Tuple of (transformed_data, lambda_parameter)
    
    Raises:
        ValueError: If data contains non-positive values
    """
    arr = np.array(data)
    
    if np.any(arr <= 0):
        raise ValueError("Box-Cox transformation requires all positive values")
    
    transformed, lambda_param = stats.boxcox(arr)
    
    return (transformed.tolist(), float(lambda_param))

def transform_log(data: List[float]) -> List[float]:
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
    
    return np.log(arr).tolist()

def transform_sqrt(data: List[float]) -> List[float]:
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
    
    return np.sqrt(arr).tolist()

def back_transform_log(transformed_value: float) -> float:
    """Back-transform from log scale to original scale."""
    return np.exp(transformed_value)

def back_transform_boxcox(transformed_value: float, lambda_param: float) -> float:
    """
    Back-transform from Box-Cox scale to original scale.
    
    Formula: original = (lambda * transformed + 1)^(1/lambda)
    """
    if abs(lambda_param) < 1e-10:  # lambda ≈ 0 means log transform
        return np.exp(transformed_value)
    else:
        return np.power(lambda_param * transformed_value + 1, 1 / lambda_param)

def back_transform_sqrt(transformed_value: float) -> float:
    """Back-transform from square root scale to original scale."""
    return transformed_value ** 2

def apply_transformation(
    data: List[float],
    method: str
) -> TransformationResult:
    """
    Apply specified transformation and re-test normality.
    
    Args:
        data: Raw dataset
        method: "boxcox", "log", or "sqrt"
    
    Returns:
        TransformationResult with transformed data and normality test
    """
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
    data: List[float],
    confidence: float,
    reliability: float
) -> Tuple[float, float]:
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
```

#### 3.4 Reliability Calculations (reliability_calcs.py)

**Purpose**: Implement reliability life testing calculations including zero-failure demonstration and acceleration factors.

**Interface**:
```python
from scipy import stats
import numpy as np
from ..models import ReliabilityInput, ReliabilityResult

# Boltzmann constant in eV/K
BOLTZMANN_CONSTANT = 8.617333262e-5

def calculate_zero_failure_duration(
    confidence: float,
    failures: int = 0
) -> float:
    """
    Calculate required test duration for zero-failure demonstration.
    
    Args:
        confidence: Confidence level as percentage (0-100)
        failures: Number of failures (typically 0)
    
    Returns:
        Test duration (proportional to chi-squared value)
    
    Formula: Duration ∝ chi^2_{1-C, 2(r+1)}
    """
    c_decimal = confidence / 100.0
    df = 2 * (failures + 1)
    
    chi2_value = stats.chi2.ppf(c_decimal, df)
    
    return float(chi2_value)

def calculate_acceleration_factor(
    activation_energy: float,
    use_temperature: float,
    test_temperature: float
) -> float:
    """
    Calculate acceleration factor using Arrhenius equation.
    
    Args:
        activation_energy: Activation energy in eV
        use_temperature: Use temperature in Kelvin
        test_temperature: Test temperature in Kelvin
    
    Returns:
        Acceleration factor (AF)
    
    Formula: AF = exp[(Ea/k) * (1/T_use - 1/T_test)]
    
    Raises:
        ValueError: If test temperature <= use temperature
    """
    if test_temperature <= use_temperature:
        raise ValueError("Test temperature must be greater than use temperature")
    
    exponent = (activation_energy / BOLTZMANN_CONSTANT) * (
        1 / use_temperature - 1 / test_temperature
    )
    
    af = np.exp(exponent)
    
    return float(af)

def celsius_to_kelvin(celsius: float) -> float:
    """Convert temperature from Celsius to Kelvin."""
    return celsius + 273.15

def calculate_reliability(input_data: ReliabilityInput) -> ReliabilityResult:
    """
    Main entry point for reliability calculations.
    
    Args:
        input_data: Validated input parameters
    
    Returns:
        Complete reliability analysis results
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
        af = calculate_acceleration_factor(
            input_data.activation_energy,
            input_data.use_temperature,
            input_data.test_temperature
        )
    
    method = "Chi-squared zero-failure demonstration"
    if af is not None:
        method += " with Arrhenius acceleration"
    
    return ReliabilityResult(
        test_duration=duration,
        acceleration_factor=af,
        method=method
    )
```


### 4. Validation and Reporting

#### 4.1 Hash Verification (validation.py)

**Purpose**: Calculate and verify SHA-256 hash of calculation engine for validation state tracking.

**Interface**:
```python
import hashlib
from pathlib import Path
from typing import Tuple

def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to file to hash
    
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()

def verify_validation_state(
    current_hash: str,
    validated_hash: str | None
) -> Tuple[bool, str]:
    """
    Compare current hash against validated hash.
    
    Args:
        current_hash: Current file hash
        validated_hash: Expected validated hash (or None if not set)
    
    Returns:
        Tuple of (is_validated, status_message)
    """
    if validated_hash is None:
        return (False, "VALIDATED STATE: NO - No validated hash configured")
    
    if current_hash == validated_hash:
        return (True, "VALIDATED STATE: YES")
    else:
        return (False, "VALIDATED STATE: NO - UNVERIFIED CHANGE")

def get_engine_validation_info(calculations_file: str, validated_hash: str | None) -> dict:
    """
    Get complete validation information for calculation engine.
    
    Args:
        calculations_file: Path to calculations module
        validated_hash: Expected validated hash
    
    Returns:
        Dictionary with hash and validation state
    """
    current_hash = calculate_file_hash(calculations_file)
    is_validated, status_message = verify_validation_state(current_hash, validated_hash)
    
    return {
        "current_hash": current_hash,
        "validated_hash": validated_hash,
        "is_validated": is_validated,
        "status_message": status_message
    }
```

#### 4.2 PDF Report Generation (reports.py)

**Purpose**: Generate PDF reports for user calculations and validation certificates.

**Interface**:
```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from ..models import CalculationReport

def generate_calculation_report(
    report_data: CalculationReport,
    output_path: str
) -> str:
    """
    Generate PDF report for user calculation.
    
    Args:
        report_data: Complete calculation report data
        output_path: Path to save PDF file
    
    Returns:
        Path to generated PDF file
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30
    )
    story.append(Paragraph("Sample Size Estimator - Calculation Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata section
    story.append(Paragraph("<b>Report Information</b>", styles['Heading2']))
    metadata_data = [
        ["Date/Time:", report_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
        ["Module:", report_data.module.capitalize()],
        ["Application Version:", report_data.app_version]
    ]
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Input parameters section
    story.append(Paragraph("<b>Input Parameters</b>", styles['Heading2']))
    input_data = [[k, str(v)] for k, v in report_data.inputs.items()]
    input_table = Table(input_data, colWidths=[2*inch, 4*inch])
    input_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Results section
    story.append(Paragraph("<b>Calculated Results</b>", styles['Heading2']))
    results_data = [[k, str(v)] for k, v in report_data.results.items()]
    results_table = Table(results_data, colWidths=[2*inch, 4*inch])
    results_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Validation section
    story.append(Paragraph("<b>Validation Information</b>", styles['Heading2']))
    validation_color = colors.green if report_data.validated_state else colors.red
    validation_data = [
        ["Engine Hash:", report_data.engine_hash],
        ["Validation Status:", "VALIDATED" if report_data.validated_state else "NOT VALIDATED"]
    ]
    validation_table = Table(validation_data, colWidths=[2*inch, 4*inch])
    validation_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (1, 1), (1, 1), validation_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(validation_table)
    
    # Build PDF
    doc.build(story)
    
    return output_path

def generate_validation_certificate(
    test_results: Dict[str, Any],
    output_path: str
) -> str:
    """
    Generate validation certificate PDF from test suite results.
    
    Args:
        test_results: Dictionary containing test execution results
        output_path: Path to save PDF file
    
    Returns:
        Path to generated PDF file
    
    Expected test_results structure:
    {
        "test_date": datetime,
        "tester": str,
        "system_info": {"os": str, "python_version": str, "dependencies": dict},
        "urs_results": [{"urs_id": str, "status": "PASS"|"FAIL", "test_name": str}],
        "validated_hash": str,
        "all_passed": bool
    }
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30
    )
    story.append(Paragraph("Validation Certificate", title_style))
    story.append(Paragraph("Sample Size Estimator Application", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Test execution info
    story.append(Paragraph("<b>Test Execution Information</b>", styles['Heading2']))
    exec_data = [
        ["Test Date:", test_results["test_date"].strftime("%Y-%m-%d %H:%M:%S")],
        ["Tester:", test_results["tester"]],
        ["Operating System:", test_results["system_info"]["os"]],
        ["Python Version:", test_results["system_info"]["python_version"]]
    ]
    exec_table = Table(exec_data, colWidths=[2*inch, 4*inch])
    exec_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 0.3*inch))
    
    # URS test results
    story.append(Paragraph("<b>URS Requirement Test Results</b>", styles['Heading2']))
    urs_data = [["URS ID", "Test Name", "Status"]]
    for result in test_results["urs_results"]:
        status_color = colors.green if result["status"] == "PASS" else colors.red
        urs_data.append([result["urs_id"], result["test_name"], result["status"]])
    
    urs_table = Table(urs_data, colWidths=[1.5*inch, 3*inch, 1*inch])
    urs_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(urs_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Validation summary
    story.append(Paragraph("<b>Validation Summary</b>", styles['Heading2']))
    overall_status = "PASSED" if test_results["all_passed"] else "FAILED"
    status_color = colors.green if test_results["all_passed"] else colors.red
    summary_data = [
        ["Overall Status:", overall_status],
        ["Validated Hash:", test_results["validated_hash"]]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (1, 0), (1, 0), status_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    
    return output_path
```

#### 4.3 Logging (logger.py)

**Purpose**: Structured logging for audit trail and debugging.

**Interface**:
```python
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'calculation_data'):
            log_data['calculation_data'] = record.calculation_data
        
        if hasattr(record, 'validation_data'):
            log_data['validation_data'] = record.validation_data
        
        return json.dumps(log_data)

def setup_logger(
    name: str,
    log_file: str,
    log_level: str = "INFO",
    log_format: str = "json"
) -> logging.Logger:
    """
    Set up application logger.
    
    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: "json" or "text"
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    
    if log_format == "json":
        file_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    # Console handler for errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console_handler)
    
    return logger

def log_calculation(
    logger: logging.Logger,
    module: str,
    inputs: Dict[str, Any],
    results: Dict[str, Any]
) -> None:
    """
    Log a calculation execution.
    
    Args:
        logger: Logger instance
        module: Calculation module name
        inputs: Input parameters
        results: Calculation results
    """
    logger.info(
        f"Calculation executed: {module}",
        extra={
            'calculation_data': {
                'module': module,
                'inputs': inputs,
                'results': results
            }
        }
    )

def log_validation_check(
    logger: logging.Logger,
    current_hash: str,
    validated_hash: str | None,
    is_validated: bool
) -> None:
    """
    Log a validation state check.
    
    Args:
        logger: Logger instance
        current_hash: Current file hash
        validated_hash: Expected validated hash
        is_validated: Whether validation passed
    """
    logger.info(
        f"Validation check: {'PASSED' if is_validated else 'FAILED'}",
        extra={
            'validation_data': {
                'current_hash': current_hash,
                'validated_hash': validated_hash,
                'is_validated': is_validated
            }
        }
    )
```


## Data Models

### Input/Output Flow

```
User Input (UI) → Pydantic Model Validation → Calculation Function → Result Model → UI Display
                                ↓
                         Validation Errors → User Feedback
```

### Key Data Structures

1. **Configuration Models**: `AppSettings` - Environment-based configuration
2. **Input Models**: `AttributeInput`, `VariablesInput`, `ReliabilityInput`, `NormalityTestInput`
3. **Result Models**: `AttributeResult`, `VariablesResult`, `ReliabilityResult`, `NormalityTestResult`
4. **Report Models**: `CalculationReport`, `ValidationCertificate`

### Data Validation Strategy

All user inputs are validated at the Pydantic model level before reaching calculation functions:

- **Range validation**: Field constraints (ge, le, gt, lt)
- **Type validation**: Automatic type coercion and validation
- **Custom validators**: Complex business rules (e.g., LSL < USL)
- **Error messages**: Clear, user-friendly validation error messages

### State Management

The application is stateless at the calculation level:
- Each calculation is independent
- No shared mutable state between calculations
- Session state managed by Streamlit's session_state for UI persistence
- Calculation history stored in logs, not in memory


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection and Consolidation

After analyzing all acceptance criteria, several properties were identified as redundant or combinable:
- Input validation properties (1.1, 1.4, 2.1, 4.4, 6.1, 7.4, 16.4) can be consolidated into comprehensive validation properties
- Output type properties (1.3, 2.4) are redundant - covered by single output validation property
- Comparison logic properties (6.2, 6.3) can be combined into single comparison correctness property
- Display/formatting properties (4.5, 5.4, 7.3, 16.5) can be consolidated
- Round-trip properties (13.1, 13.2, 13.3) are the key properties for transformation correctness

### Attribute Module Properties

**Property 1: Success Run Theorem Correctness**
*For any* confidence level C (0 < C < 100) and reliability R (0 < R < 100), when calculating sample size with zero allowable failures, the calculated n should equal ceiling(ln(1-C/100) / ln(R/100))
**Validates: Requirements 1.2**

**Property 2: Binomial Sample Size Correctness**
*For any* confidence C, reliability R, and allowable failures c > 0, the calculated sample size n should be the smallest integer where the cumulative binomial probability sum(binom(n,k)*(1-R/100)^k*(R/100)^(n-k) for k=0 to c) ≤ (1-C/100)
**Validates: Requirements 2.2, 2.3**

**Property 3: Binomial Sample Size Minimality**
*For any* valid inputs where c > 0, if n is the calculated sample size, then n-1 should NOT satisfy the binomial criterion (ensuring n is truly minimal)
**Validates: Requirements 2.3**

**Property 4: Sensitivity Analysis Completeness**
*For any* confidence C and reliability R, when allowable failures is not specified, the system should return exactly 4 results with c values of 0, 1, 2, and 3
**Validates: Requirements 3.1**

**Property 5: Input Validation for Percentages**
*For any* input value v, when validating confidence or reliability, the system should accept v if and only if 0 < v < 100
**Validates: Requirements 1.1, 1.4, 19.1**

### Variables Module Properties

**Property 6: One-Sided Tolerance Factor Correctness**
*For any* sample size n > 1, confidence C, and reliability R, the one-sided tolerance factor k1 should equal t_{n-1, 1-C/100}(delta)/sqrt(n) where delta = z_R * sqrt(n)
**Validates: Requirements 4.1**

**Property 7: Two-Sided Tolerance Factor Correctness**
*For any* sample size n > 1, confidence C, and reliability R, the two-sided tolerance factor k2 should equal sqrt((1 + 1/n) * z^2_{(1+R/100)/2} * (n-1) / chi^2_{1-C/100, n-1})
**Validates: Requirements 4.2**

**Property 8: Tolerance Limit Calculation Correctness**
*For any* sample mean μ, standard deviation σ > 0, and tolerance factor k, the upper tolerance limit should equal μ + k*σ and the lower tolerance limit should equal μ - k*σ
**Validates: Requirements 5.1, 5.2**

**Property 9: Specification Comparison Logic**
*For any* tolerance limits (L_tol, U_tol) and specification limits (LSL, USL), the result should be PASS if and only if L_tol ≥ LSL AND U_tol ≤ USL
**Validates: Requirements 6.2, 6.3, 6.4**

**Property 10: Ppk Calculation Correctness**
*For any* mean μ, standard deviation σ > 0, and specification limits (LSL, USL), Ppk should equal min((USL-μ)/(3σ), (μ-LSL)/(3σ)) when both limits exist, or the single relevant term when only one limit exists
**Validates: Requirements 7.1, 7.2**

**Property 11: Specification Limit Ordering**
*For any* specification limits LSL and USL, the system should accept them if and only if LSL < USL
**Validates: Requirements 6.1**

**Property 12: Standard Deviation Positivity**
*For any* calculation requiring standard deviation σ, the system should accept σ if and only if σ > 0
**Validates: Requirements 7.4**

### Non-Normal Module Properties

**Property 13: Outlier Detection Correctness**
*For any* dataset, a value x should be flagged as an outlier if and only if x < Q1 - 1.5*IQR OR x > Q3 + 1.5*IQR, where Q1, Q3, and IQR are correctly calculated from the data
**Validates: Requirements 8.1, 8.2**

**Property 14: Outlier Count Consistency**
*For any* dataset, the count of detected outliers should equal the number of values flagged by the outlier detection algorithm
**Validates: Requirements 8.3, 8.4**

**Property 15: Normality Test Execution**
*For any* dataset with n ≥ 3, both Shapiro-Wilk and Anderson-Darling tests should execute and return valid statistics (p-value for SW, statistic and critical values for AD)
**Validates: Requirements 9.1, 9.2, 9.3, 9.4**

**Property 16: Normality Rejection Logic**
*For any* dataset, normality should be rejected if and only if (Shapiro-Wilk p-value < 0.05) OR (Anderson-Darling statistic > critical value at α=0.05)
**Validates: Requirements 9.5, 9.6**

**Property 17: Logarithmic Transformation Round-Trip**
*For any* dataset with all positive values, applying log transformation followed by exp back-transformation should produce values equal to the original values (within numerical precision)
**Validates: Requirements 13.1**

**Property 18: Box-Cox Transformation Round-Trip**
*For any* dataset with all positive values and calculated lambda λ, applying Box-Cox transformation followed by inverse Box-Cox back-transformation should produce values equal to the original values (within numerical precision)
**Validates: Requirements 13.2**

**Property 19: Square Root Transformation Round-Trip**
*For any* dataset with all non-negative values, applying sqrt transformation followed by squaring should produce values equal to the original values (within numerical precision)
**Validates: Requirements 13.3**

**Property 20: Transformation Data Suitability**
*For any* transformation method, the system should validate data suitability: log and Box-Cox require all positive values, sqrt requires all non-negative values
**Validates: Requirements 11.6**

**Property 21: Post-Transformation Normality Testing**
*For any* transformed dataset, normality tests should be re-executed on the transformed data and results should be available for both original and transformed datasets
**Validates: Requirements 12.1, 12.2**

**Property 22: Wilks' Limits Correctness**
*For any* dataset, when using Wilks' non-parametric method, the lower limit should equal min(data) and the upper limit should equal max(data)
**Validates: Requirements 14.2**

### Reliability Module Properties

**Property 23: Zero-Failure Duration Correctness**
*For any* confidence level C and failures r=0, the calculated test duration should equal chi^2_{1-C/100, 2(r+1)}
**Validates: Requirements 15.1, 15.2**

**Property 24: Arrhenius Acceleration Factor Correctness**
*For any* activation energy Ea, use temperature T_use, and test temperature T_test (where T_test > T_use), the acceleration factor should equal exp[(Ea/k_B) * (1/T_use - 1/T_test)] where k_B is Boltzmann's constant
**Validates: Requirements 16.1, 16.2**

**Property 25: Temperature Validation**
*For any* acceleration factor calculation, the system should accept temperatures if and only if T_test > T_use and both are positive (in Kelvin)
**Validates: Requirements 16.3, 16.4**

### Validation and Integrity Properties

**Property 26: Hash Calculation Determinism**
*For any* file, calculating the SHA-256 hash multiple times should produce identical hash values
**Validates: Requirements 21.1**

**Property 27: Hash Comparison Logic**
*For any* current hash H_current and validated hash H_validated, the validation state should be TRUE if and only if H_current == H_validated
**Validates: Requirements 21.3, 21.4, 21.5**

**Property 28: Configuration Validation**
*For any* configuration parameter, the system should validate the value at startup and reject invalid configurations with clear error messages
**Validates: Requirements 27.4**

### Logging Properties

**Property 29: Calculation Logging Completeness**
*For any* calculation execution, the log entry should contain timestamp, module name, all input parameters, and all calculated results
**Validates: Requirements 26.1**

**Property 30: Validation Logging Completeness**
*For any* validation check, the log entry should contain timestamp, current hash, validated hash, and validation outcome
**Validates: Requirements 26.2**


## Error Handling

### Error Handling Strategy

The application uses a layered error handling approach:

1. **Input Validation Layer** (Pydantic Models)
   - Automatic validation of types, ranges, and constraints
   - Clear validation error messages
   - Prevents invalid data from reaching calculation functions

2. **Calculation Layer** (Pure Functions)
   - Explicit error handling for mathematical edge cases
   - Custom exceptions for domain-specific errors
   - Graceful degradation when possible

3. **UI Layer** (Streamlit)
   - User-friendly error messages
   - Error state visualization
   - Guidance for correcting errors

### Exception Hierarchy

```python
class SampleSizeEstimatorError(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(SampleSizeEstimatorError):
    """Raised when input validation fails."""
    pass

class CalculationError(SampleSizeEstimatorError):
    """Raised when calculation cannot be completed."""
    pass

class TransformationError(SampleSizeEstimatorError):
    """Raised when data transformation fails."""
    pass

class ConfigurationError(SampleSizeEstimatorError):
    """Raised when configuration is invalid."""
    pass
```

### Error Scenarios and Handling

| Scenario | Error Type | Handling Strategy |
|----------|-----------|-------------------|
| Invalid percentage (< 0 or > 100) | ValidationError | Display range error, highlight field |
| Negative standard deviation | ValidationError | Display error, require positive value |
| LSL ≥ USL | ValidationError | Display ordering error, suggest correction |
| Non-positive data for log transform | TransformationError | Display error, suggest alternative transformation |
| Sample size too large (> 10000) | CalculationError | Display warning, suggest parameter adjustment |
| File not found for hash calculation | ConfigurationError | Display error, check file path |
| Missing validated hash | ConfigurationError | Display warning, allow operation with unvalidated state |
| Test suite failure | ValidationError | Display failed tests, prevent certificate generation |

### Logging Error Details

All errors are logged with:
- Error type and message
- Stack trace (for unexpected errors)
- Input parameters that caused the error
- Timestamp and module context
- User session identifier (if applicable)


## Testing Strategy

### Dual Testing Approach

The application requires both unit testing and property-based testing for comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, and error conditions
- **Property Tests**: Verify universal properties across all inputs
- Together they provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: sample-size-estimator, Property {number}: {property_text}`

**Example Property Test**:
```python
from hypothesis import given, strategies as st
import pytest

# Feature: sample-size-estimator, Property 1: Success Run Theorem Correctness
@pytest.mark.urs("URS-FUNC_A-02")
@given(
    confidence=st.floats(min_value=0.01, max_value=99.99),
    reliability=st.floats(min_value=0.01, max_value=99.99)
)
def test_success_run_theorem_correctness(confidence, reliability):
    """
    Property 1: For any C and R, sample size should equal 
    ceiling(ln(1-C/100) / ln(R/100))
    """
    result = calculate_sample_size_zero_failures(confidence, reliability)
    
    expected = math.ceil(
        math.log(1 - confidence/100) / math.log(reliability/100)
    )
    
    assert result == expected
```

### Test Organization

```
tests/
├── unit/
│   ├── test_attribute_calcs.py      # Unit tests for attribute module
│   ├── test_variables_calcs.py      # Unit tests for variables module
│   ├── test_non_normal_calcs.py     # Unit tests for non-normal module
│   ├── test_reliability_calcs.py    # Unit tests for reliability module
│   ├── test_validation.py           # Unit tests for hash verification
│   └── test_reports.py              # Unit tests for PDF generation
├── properties/
│   ├── test_attribute_properties.py  # Property tests for attribute module
│   ├── test_variables_properties.py  # Property tests for variables module
│   ├── test_non_normal_properties.py # Property tests for non-normal module
│   └── test_reliability_properties.py # Property tests for reliability module
├── integration/
│   ├── test_end_to_end_workflows.py  # Complete calculation workflows
│   └── test_report_generation.py     # Report generation integration
└── ui/
    ├── test_ui_playwright_attribute.py    # Playwright UI tests for attribute tab
    ├── test_ui_playwright_variables.py    # Playwright UI tests for variables tab
    ├── test_ui_playwright_non_normal.py   # Playwright UI tests for non-normal tab
    └── test_ui_playwright_reliability.py  # Playwright UI tests for reliability tab
```

### Test Coverage Requirements

| Module | Unit Test Coverage | Property Test Coverage | Integration Tests |
|--------|-------------------|----------------------|-------------------|
| attribute_calcs.py | > 90% | All properties 1-5 | 2 workflows |
| variables_calcs.py | > 90% | All properties 6-12 | 2 workflows |
| non_normal_calcs.py | > 90% | All properties 13-22 | 2 workflows |
| reliability_calcs.py | > 90% | All properties 23-25 | 1 workflow |
| validation.py | > 95% | Properties 26-27 | 1 workflow |
| reports.py | > 85% | N/A | 2 workflows |
| config.py | > 90% | Property 28 | 1 workflow |
| logger.py | > 85% | Properties 29-30 | 1 workflow |

### Unit Test Examples

**Specific Value Tests**:
```python
@pytest.mark.urs("URS-FUNC_A-02")
def test_success_run_known_value():
    """Test with known statistical reference value."""
    # C=95%, R=90% should give n=29
    result = calculate_sample_size_zero_failures(95.0, 90.0)
    assert result == 29

@pytest.mark.urs("URS-FUNC_B-05")
def test_ppk_calculation_known_value():
    """Test Ppk with known process capability example."""
    # Mean=10, Std=1, LSL=7, USL=13 should give Ppk=1.0
    ppk = calculate_ppk(mean=10.0, std=1.0, lsl=7.0, usl=13.0)
    assert abs(ppk - 1.0) < 0.01
```

**Edge Case Tests**:
```python
@pytest.mark.urs("URS-FUNC_C-01")
def test_outlier_detection_no_outliers():
    """Test outlier detection with perfectly normal data."""
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    outliers, indices = detect_outliers(data)
    assert len(outliers) == 0

@pytest.mark.urs("URS-FUNC_C-01")
def test_outlier_detection_all_outliers():
    """Test outlier detection with extreme values."""
    data = [1.0, 1.0, 1.0, 100.0, 200.0]
    outliers, indices = detect_outliers(data)
    assert len(outliers) == 2
    assert 100.0 in outliers
    assert 200.0 in outliers
```

**Error Condition Tests**:
```python
@pytest.mark.urs("URS-FUNC_A-01")
def test_invalid_confidence_rejected():
    """Test that confidence > 100 is rejected."""
    with pytest.raises(ValidationError):
        AttributeInput(confidence=150.0, reliability=90.0)

@pytest.mark.urs("URS-FUNC_C-05")
def test_log_transform_negative_data_rejected():
    """Test that log transformation rejects negative data."""
    data = [1.0, 2.0, -1.0, 3.0]
    with pytest.raises(TransformationError):
        transform_log(data)
```

### Property Test Strategy

**Input Generation Strategies**:
```python
# Valid percentage values
percentages = st.floats(min_value=0.01, max_value=99.99)

# Positive integers for sample size
sample_sizes = st.integers(min_value=2, max_value=1000)

# Positive floats for standard deviation
positive_floats = st.floats(min_value=0.01, max_value=1000.0)

# Datasets for normality testing
datasets = st.lists(
    st.floats(min_value=-1000.0, max_value=1000.0),
    min_size=3,
    max_size=100
)

# Positive datasets for transformations
positive_datasets = st.lists(
    st.floats(min_value=0.01, max_value=1000.0),
    min_size=3,
    max_size=100
)
```

**Property Test Patterns**:

1. **Mathematical Correctness**: Verify formulas produce correct results
2. **Round-Trip Properties**: Transformation followed by inverse returns original
3. **Invariants**: Properties that must hold regardless of inputs
4. **Comparison Properties**: Relationships between related calculations
5. **Boundary Behavior**: Behavior at extreme values

### UI Testing with Playwright

```python
from playwright.sync_api import Page, expect

@pytest.mark.urs("URS-VAL-03")
def test_attribute_tab_workflow(page: Page, streamlit_app: str):
    """Test complete workflow in attribute tab."""
    page.goto(streamlit_app)
    
    # Wait for app to load
    expect(page.locator("text=Attribute (Binomial)")).to_be_visible()
    
    # Click attribute tab
    page.click("text=Attribute (Binomial)")
    
    # Enter inputs
    page.fill("input[aria-label='Confidence Level (%)']", "95")
    page.fill("input[aria-label='Reliability (%)']", "90")
    
    # Click calculate
    page.click("button:has-text('Calculate')")
    
    # Verify output appears
    expect(page.locator("text=Sample Size")).to_be_visible()

@pytest.mark.urs("URS-VAL-03")
def test_invalid_input_error_display(page: Page, streamlit_app: str):
    """Test that invalid inputs show error messages."""
    page.goto(streamlit_app)
    
    # Click attribute tab
    page.click("text=Attribute (Binomial)")
    
    # Enter invalid confidence (out of range)
    page.fill("input[aria-label='Confidence Level (%)']", "150")
    page.click("button:has-text('Calculate')")
    
    # Verify error message appears
    expect(page.locator("text=error")).to_be_visible()
```

### Validation Test Suite

The validation test suite generates the validation certificate and must:

1. **Execute all OQ tests** with pytest markers
2. **Collect test results** with URS ID mapping
3. **Calculate validated hash** of calculation engine
4. **Generate validation certificate PDF** with all results
5. **Verify 100% pass rate** before issuing certificate

**Validation Test Execution**:
```bash
# Run all tests with URS markers
uv run pytest -v -m urs --tb=short

# Generate validation certificate
uv run python scripts/generate_validation_certificate.py
```

### Continuous Integration

**Pre-commit Checks**:
- Run ruff linter
- Run mypy type checker
- Run unit tests (fast subset)

**CI Pipeline**:
1. Install dependencies with uv
2. Run full test suite (unit + property + integration)
3. Generate coverage report (require > 85%)
4. Run UI tests
5. Build validation certificate
6. Archive test artifacts

### Test Execution Commands

```bash
# Run all tests quietly
uv run pytest -q

# Run specific test file
uv run pytest tests/unit/test_attribute_calcs.py -q

# Run tests for specific URS requirement
uv run pytest -m urs -k "URS-FUNC_A-02" -v

# Run property tests only
uv run pytest tests/properties/ -q

# Run with coverage
uv run pytest --cov=src/sample_size_estimator --cov-report=html

# Run UI tests (Playwright)
uv run pytest tests/test_ui_playwright_*.py -v
```

