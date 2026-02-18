"""Data models for Sample Size Estimator application.

This module defines all Pydantic models for input validation, calculation results,
and report generation. All models include field validators for data integrity.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class AttributeInput(BaseModel):
    """Input parameters for attribute data analysis.

    Validates:
    - Confidence and reliability are percentages between 0 and 100 (exclusive)
    - Allowable failures is a non-negative integer
    """

    confidence: float = Field(
        ge=0.0, le=100.0, description="Confidence level (%)"
    )
    reliability: float = Field(
        ge=0.0, le=100.0, description="Reliability (%)"
    )
    allowable_failures: int | None = Field(
        None, ge=0, description="Allowable failures (c)"
    )

    @field_validator("confidence", "reliability")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate that percentage values are in valid range (0, 100)."""
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v


class AttributeResult(BaseModel):
    """Output from attribute data analysis."""

    sample_size: int = Field(description="Minimum required sample size")
    allowable_failures: int = Field(description="Number of allowable failures")
    confidence: float = Field(description="Confidence level used (%)")
    reliability: float = Field(description="Reliability level used (%)")
    method: Literal["success_run", "binomial"] = Field(
        description="Calculation method"
    )


class SensitivityResult(BaseModel):
    """Sensitivity analysis results for multiple failure scenarios."""

    results: list[AttributeResult] = Field(
        description="Results for c=0,1,2,3"
    )


class VariablesInput(BaseModel):
    """Input parameters for variables data analysis.

    Validates:
    - Confidence and reliability are percentages between 0 and 100 (exclusive)
    - Sample size is greater than 1
    - Sample standard deviation is positive
    - LSL < USL when both are provided
    """

    confidence: float = Field(
        ge=0.0, le=100.0, description="Confidence level (%)"
    )
    reliability: float = Field(
        ge=0.0, le=100.0, description="Reliability (%)"
    )
    sample_size: int = Field(gt=1, description="Sample size")
    sample_mean: float = Field(description="Sample mean")
    sample_std: float = Field(gt=0.0, description="Sample standard deviation")
    lsl: float | None = Field(None, description="Lower specification limit")
    usl: float | None = Field(None, description="Upper specification limit")
    sided: Literal["one", "two"] = Field(
        description="One-sided or two-sided limits"
    )

    @field_validator("confidence", "reliability")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate that percentage values are in valid range (0, 100)."""
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v

    @field_validator("sample_std")
    @classmethod
    def validate_positive_std(cls, v: float) -> float:
        """Validate that standard deviation is positive."""
        if v <= 0:
            raise ValueError("Sample standard deviation must be greater than zero")
        return v

    def model_post_init(self, __context: object) -> None:
        """Validate that LSL < USL when both are provided."""
        if self.lsl is not None and self.usl is not None:
            if self.lsl >= self.usl:
                raise ValueError(
                    "Lower specification limit (LSL) must be less than "
                    "upper specification limit (USL)"
                )


class VariablesResult(BaseModel):
    """Output from variables data analysis."""

    tolerance_factor: float = Field(
        description="Calculated tolerance factor (k)"
    )
    lower_tolerance_limit: float | None = Field(
        None, description="Lower tolerance limit"
    )
    upper_tolerance_limit: float | None = Field(
        None, description="Upper tolerance limit"
    )
    ppk: float | None = Field(None, description="Process performance index")
    pass_fail: Literal["PASS", "FAIL"] | None = Field(
        None, description="Comparison result"
    )
    margin_lower: float | None = Field(None, description="Margin to LSL")
    margin_upper: float | None = Field(None, description="Margin to USL")


class NormalityTestResult(BaseModel):
    """Results from normality testing."""

    shapiro_wilk_statistic: float
    shapiro_wilk_pvalue: float
    anderson_darling_statistic: float
    anderson_darling_critical_values: list[float]
    is_normal: bool = Field(
        description="True if data passes normality tests"
    )
    interpretation: str = Field(
        description="Human-readable interpretation"
    )


class TransformationResult(BaseModel):
    """Results from data transformation."""

    method: Literal["boxcox", "log", "sqrt"] = Field(
        description="Transformation method"
    )
    lambda_param: float | None = Field(
        None, description="Box-Cox lambda parameter"
    )
    transformed_data: list[float] = Field(description="Transformed dataset")
    normality_after: NormalityTestResult = Field(
        description="Normality test after transformation"
    )


class ReliabilityInput(BaseModel):
    """Input parameters for reliability life testing.

    Validates:
    - Confidence and reliability are percentages between 0 and 100 (exclusive)
    - Failures is a non-negative integer
    - Activation energy, temperatures are positive when provided
    - Test temperature > use temperature when both provided
    """

    confidence: float = Field(
        ge=0.0, le=100.0, description="Confidence level (%)"
    )
    reliability: float = Field(
        ge=0.0, le=100.0, description="Reliability (%)"
    )
    failures: int = Field(ge=0, description="Number of failures")
    activation_energy: float | None = Field(
        None, gt=0.0, description="Activation energy (eV)"
    )
    use_temperature: float | None = Field(
        None, gt=0.0, description="Use temperature (K)"
    )
    test_temperature: float | None = Field(
        None, gt=0.0, description="Test temperature (K)"
    )

    @field_validator("confidence", "reliability")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate that percentage values are in valid range (0, 100)."""
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v

    def model_post_init(self, __context: object) -> None:
        """Validate that test temperature > use temperature when both provided."""
        if (
            self.test_temperature is not None
            and self.use_temperature is not None
        ):
            if self.test_temperature <= self.use_temperature:
                raise ValueError(
                    "Test temperature must be greater than use temperature"
                )


class ReliabilityResult(BaseModel):
    """Output from reliability life testing."""

    test_duration: float = Field(
        description="Required test duration or units"
    )
    acceleration_factor: float | None = Field(
        None, description="Acceleration factor"
    )
    method: str = Field(description="Calculation method used")


class CalculationReport(BaseModel):
    """Complete calculation report for PDF generation."""

    timestamp: datetime = Field(default_factory=datetime.now)
    module: Literal["attribute", "variables", "non_normal", "reliability"]
    inputs: dict[str, Any] = Field(description="All input parameters")
    results: dict[str, Any] = Field(description="All calculated results")
    engine_hash: str = Field(description="SHA-256 hash of calculation engine")
    validated_state: bool = Field(
        description="True if hash matches validated hash"
    )
    app_version: str = Field(description="Application version")
