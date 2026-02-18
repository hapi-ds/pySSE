# Developer Guide: Sample Size Estimator

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Design Principles](#design-principles)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Adding New Analysis Modules](#adding-new-analysis-modules)
7. [Testing Approach](#testing-approach)
8. [Configuration Management](#configuration-management)
9. [Development Workflow](#development-workflow)
10. [Code Style and Standards](#code-style-and-standards)

## Introduction

The Sample Size Estimator is a Python-based web application built with Streamlit that provides statistical calculations for medical device validation. This guide is intended for developers who need to understand, maintain, or extend the application.

### Key Technologies

- **Framework**: Streamlit 1.x for web UI
- **Validation**: Pydantic 2.x for data models and settings
- **Statistics**: SciPy 1.x for statistical distributions and tests
- **Numerical**: NumPy 1.x for array operations
- **Plotting**: Matplotlib 3.x for Q-Q plots
- **PDF Generation**: ReportLab 4.x for reports
- **Testing**: pytest 8.x with hypothesis for property-based testing
- **Package Management**: uv for dependency management
- **Type Checking**: mypy for static type analysis

### Design Philosophy

The application follows a **functional programming** approach with strong type safety:
- Pure functions for all calculations (no side effects)
- Pydantic models for all data structures with runtime validation
- Modular architecture for easy extension
- Comprehensive testing (unit + property-based)
- Full auditability through logging and hash verification


## Architecture Overview

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

### Data Flow

```
User Input (UI) → Pydantic Model Validation → Calculation Function → Result Model → UI Display
                                ↓
                         Validation Errors → User Feedback
```

### Key Architectural Decisions

1. **Stateless Calculations**: Each calculation is independent with no shared mutable state
2. **Type Safety First**: Pydantic models validate all inputs before reaching calculation functions
3. **Separation of Concerns**: UI, calculations, and services are cleanly separated
4. **Functional Core, Imperative Shell**: Pure functions for calculations, side effects at boundaries
5. **Configuration as Code**: Environment-based configuration with sensible defaults


## Design Principles

### 1. Functional Programming

All calculation functions are **pure functions**:
- No side effects (no global state modification)
- Deterministic (same inputs always produce same outputs)
- Easy to test and reason about
- Composable and reusable

**Example**:
```python
def calculate_sample_size_zero_failures(confidence: float, reliability: float) -> int:
    """Pure function - no side effects, deterministic output."""
    c_decimal = confidence / 100.0
    r_decimal = reliability / 100.0
    n = math.ceil(math.log(1 - c_decimal) / math.log(r_decimal))
    return n
```

### 2. Type Safety with Pydantic

All data structures use Pydantic models for:
- Runtime validation
- Type checking
- Automatic error messages
- JSON serialization/deserialization

**Example**:
```python
class AttributeInput(BaseModel):
    confidence: float = Field(ge=0.0, le=100.0)
    reliability: float = Field(ge=0.0, le=100.0)
    
    @field_validator("confidence", "reliability")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v
```

### 3. Modularity

Each statistical method is in a separate module:
- `attribute_calcs.py` - Binomial sample size calculations
- `variables_calcs.py` - Normal distribution tolerance calculations
- `non_normal_calcs.py` - Transformations and non-parametric methods
- `reliability_calcs.py` - Life testing calculations

This makes it easy to:
- Test each module independently
- Add new modules without affecting existing code
- Understand and maintain specific functionality

### 4. Testability

The architecture supports comprehensive testing:
- **Unit tests**: Verify specific examples and edge cases
- **Property-based tests**: Verify universal properties across all inputs
- **Integration tests**: Verify complete workflows
- **UI tests**: Verify Streamlit interface behavior

### 5. Auditability

Full traceability for regulatory compliance:
- Structured JSON logging of all calculations
- SHA-256 hash verification of calculation engine
- PDF reports with validation state
- Automated validation certificate generation


## Project Structure

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
│   ├── test_attribute_calcs.py      # Unit + property tests
│   ├── test_variables_calcs.py      # Unit + property tests
│   ├── test_non_normal_calcs.py     # Unit + property tests
│   ├── test_reliability_calcs.py    # Unit + property tests
│   ├── test_validation.py           # Hash verification tests
│   ├── test_reports.py              # PDF generation tests
│   ├── test_logger.py               # Logging tests
│   ├── test_config.py               # Configuration tests
│   ├── test_models.py               # Data model tests
│   └── test_integration.py          # End-to-end workflow tests
├── scripts/
│   ├── check_environment.py         # Dependency verification
│   └── generate_validation_certificate.py  # Validation certificate
├── docs/
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md           # This document
│   └── VALIDATION_PROTOCOL.md
├── logs/                            # Application logs
├── reports/                         # Generated PDF reports
├── pyproject.toml                   # uv project configuration
├── uv.lock                          # Locked dependencies
├── .env.example                     # Example configuration
└── README.md
```

### Key Directories

- **`src/sample_size_estimator/`**: Main application code
  - **`calculations/`**: Pure calculation functions (no UI, no I/O)
  - **`ui/`**: Streamlit UI components (one file per tab)
  
- **`tests/`**: All test files (unit, property, integration)

- **`scripts/`**: Utility scripts for validation and environment checks

- **`docs/`**: User and developer documentation


## Core Components

### Configuration Management (`config.py`)

Centralized configuration using Pydantic Settings:

```python
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    app_title: str = "Sample Size Estimator"
    log_level: str = "INFO"
    validated_hash: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

def get_settings() -> AppSettings:
    """Singleton pattern for settings."""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings
```

**Configuration Sources** (in order of precedence):
1. Environment variables
2. `.env` file
3. Default values in code

**Usage**:
```python
from sample_size_estimator.config import get_settings

settings = get_settings()
print(settings.app_title)
```

### Data Models (`models.py`)

All data structures are Pydantic models with validation:

**Input Models**:
- `AttributeInput` - Binomial analysis inputs
- `VariablesInput` - Normal distribution inputs
- `ReliabilityInput` - Life testing inputs

**Result Models**:
- `AttributeResult` - Single binomial result
- `SensitivityResult` - Multiple failure scenarios
- `VariablesResult` - Tolerance limits and Ppk
- `NormalityTestResult` - Normality test results
- `TransformationResult` - Transformation results
- `ReliabilityResult` - Life testing results

**Report Models**:
- `CalculationReport` - Complete calculation report for PDF

**Key Features**:
- Field validators for complex business rules
- Automatic type coercion and validation
- Clear error messages for invalid inputs
- JSON serialization support

### Calculation Modules

Each calculation module follows the same pattern:

1. **Helper functions**: Small, focused pure functions
2. **Main calculation function**: Orchestrates helpers and returns result model
3. **No side effects**: No logging, no I/O, no global state

**Example Structure** (`attribute_calcs.py`):
```python
def calculate_sample_size_zero_failures(confidence: float, reliability: float) -> int:
    """Helper function - pure calculation."""
    # Implementation
    return n

def calculate_sample_size_with_failures(confidence: float, reliability: float, c: int) -> int:
    """Helper function - pure calculation."""
    # Implementation
    return n

def calculate_attribute(input_data: AttributeInput) -> AttributeResult | SensitivityResult:
    """Main entry point - orchestrates helpers."""
    if input_data.allowable_failures is None:
        return calculate_sensitivity_analysis(...)
    elif input_data.allowable_failures == 0:
        n = calculate_sample_size_zero_failures(...)
        return AttributeResult(...)
    else:
        n = calculate_sample_size_with_failures(...)
        return AttributeResult(...)
```

### Validation and Hash Verification (`validation.py`)

Ensures calculation engine integrity:

```python
def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_validation_state(current_hash: str, validated_hash: str | None) -> tuple[bool, str]:
    """Compare current hash against validated hash."""
    if validated_hash is None:
        return (False, "VALIDATED STATE: NO - No validated hash configured")
    if current_hash == validated_hash:
        return (True, "VALIDATED STATE: YES")
    else:
        return (False, "VALIDATED STATE: NO - UNVERIFIED CHANGE")
```

### Logging (`logger.py`)

Structured JSON logging for audit trail:

```python
class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            # ... additional fields
        }
        return json.dumps(log_data)

def log_calculation(logger: logging.Logger, module: str, inputs: dict, results: dict) -> None:
    """Log a calculation execution."""
    logger.info(
        f"Calculation executed: {module}",
        extra={'calculation_data': {'module': module, 'inputs': inputs, 'results': results}}
    )
```

### PDF Report Generation (`reports.py`)

Uses ReportLab to generate professional PDF reports:

```python
def generate_calculation_report(report_data: CalculationReport, output_path: str) -> str:
    """Generate PDF report for user calculation."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    
    # Add title, metadata, inputs, results, validation info
    # ... ReportLab code
    
    doc.build(story)
    return output_path
```


## Adding New Analysis Modules

This section explains how to extend the application with new statistical analysis methods.

### Step 1: Define Data Models

Add input and result models to `models.py`:

```python
class NewAnalysisInput(BaseModel):
    """Input parameters for new analysis."""
    confidence: float = Field(ge=0.0, le=100.0, description="Confidence level (%)")
    # Add other parameters
    
    @field_validator("confidence")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v

class NewAnalysisResult(BaseModel):
    """Output from new analysis."""
    calculated_value: float = Field(description="Main result")
    # Add other results
```

### Step 2: Create Calculation Module

Create `src/sample_size_estimator/calculations/new_analysis_calcs.py`:

```python
"""New analysis calculations.

This module implements [description of statistical method].
"""

from ..models import NewAnalysisInput, NewAnalysisResult

def helper_calculation(param1: float, param2: float) -> float:
    """Helper function for specific calculation.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Calculated value
    
    Formula: [mathematical formula]
    """
    # Pure function implementation
    result = param1 * param2  # Example
    return result

def calculate_new_analysis(input_data: NewAnalysisInput) -> NewAnalysisResult:
    """Main entry point for new analysis.
    
    Args:
        input_data: Validated input parameters
    
    Returns:
        Complete analysis results
    """
    # Orchestrate helper functions
    value = helper_calculation(input_data.param1, input_data.param2)
    
    return NewAnalysisResult(
        calculated_value=value
    )
```

**Key Guidelines**:
- All functions must be pure (no side effects)
- Use type hints for all parameters and return values
- Include docstrings with Args, Returns, and Formula sections
- Break complex calculations into small helper functions
- Return Pydantic models, not dictionaries

### Step 3: Export from Calculations Package

Update `src/sample_size_estimator/calculations/__init__.py`:

```python
from .new_analysis_calcs import calculate_new_analysis

__all__ = [
    # ... existing exports
    "calculate_new_analysis",
]
```

### Step 4: Create UI Tab

Create `src/sample_size_estimator/ui/new_analysis_tab.py`:

```python
"""UI for new analysis module."""

import streamlit as st
from ..calculations import calculate_new_analysis
from ..models import NewAnalysisInput
from ..logger import setup_logger, log_calculation
from ..config import get_settings

def render_new_analysis_tab():
    """Render the new analysis tab."""
    st.header("New Analysis")
    
    # Help text
    with st.expander("ℹ️ How to use this module"):
        st.markdown("""
        This module calculates [description].
        
        **When to use**: [use cases]
        **Inputs**: [input descriptions]
        """)
    
    # Input widgets
    col1, col2 = st.columns(2)
    with col1:
        confidence = st.number_input(
            "Confidence Level (%)",
            min_value=0.01,
            max_value=99.99,
            value=95.0,
            help="Statistical confidence level"
        )
    
    with col2:
        param2 = st.number_input(
            "Parameter 2",
            min_value=0.0,
            value=10.0,
            help="Description of parameter"
        )
    
    # Calculate button
    if st.button("Calculate", key="new_analysis_calculate"):
        try:
            # Validate inputs
            input_data = NewAnalysisInput(
                confidence=confidence,
                param2=param2
            )
            
            # Perform calculation
            result = calculate_new_analysis(input_data)
            
            # Log calculation
            settings = get_settings()
            logger = setup_logger("new_analysis", settings.log_file, settings.log_level)
            log_calculation(
                logger,
                "new_analysis",
                input_data.model_dump(),
                result.model_dump()
            )
            
            # Display results
            st.success("Calculation Complete!")
            st.metric("Calculated Value", f"{result.calculated_value:.2f}")
            
        except ValueError as e:
            st.error(f"Input Error: {str(e)}")
        except Exception as e:
            st.error(f"Calculation Error: {str(e)}")
```

### Step 5: Integrate into Main App

Update `src/sample_size_estimator/app.py`:

```python
from .ui.new_analysis_tab import render_new_analysis_tab

# In main():
tabs = st.tabs([
    "Attribute (Binomial)",
    "Variables (Normal)",
    "Non-Normal Distribution",
    "Reliability",
    "New Analysis"  # Add new tab
])

with tabs[4]:
    render_new_analysis_tab()
```

### Step 6: Write Tests

Create `tests/test_new_analysis_calcs.py`:

```python
"""Tests for new analysis calculations."""

import pytest
from hypothesis import given, strategies as st
from sample_size_estimator.calculations import calculate_new_analysis
from sample_size_estimator.models import NewAnalysisInput

# Unit tests
@pytest.mark.urs("URS-NEW-01")
def test_new_analysis_known_value():
    """Test with known reference value."""
    input_data = NewAnalysisInput(confidence=95.0, param2=10.0)
    result = calculate_new_analysis(input_data)
    assert result.calculated_value == pytest.approx(expected_value, rel=1e-6)

@pytest.mark.urs("URS-NEW-01")
def test_new_analysis_edge_case():
    """Test edge case behavior."""
    input_data = NewAnalysisInput(confidence=99.99, param2=0.01)
    result = calculate_new_analysis(input_data)
    assert result.calculated_value > 0

# Property-based tests
@pytest.mark.urs("URS-NEW-01")
@given(
    confidence=st.floats(min_value=0.01, max_value=99.99),
    param2=st.floats(min_value=0.01, max_value=1000.0)
)
def test_new_analysis_property(confidence, param2):
    """
    Property: [Description of universal property that should hold]
    Validates: Requirements X.Y
    """
    input_data = NewAnalysisInput(confidence=confidence, param2=param2)
    result = calculate_new_analysis(input_data)
    
    # Verify property holds
    assert result.calculated_value > 0  # Example property
```

### Step 7: Update Documentation

1. Add requirement to `requirements.md`
2. Add design details to `design.md`
3. Add correctness properties to design document
4. Update `USER_GUIDE.md` with usage instructions
5. Update `README.md` feature list

### Checklist for New Modules

- [ ] Data models defined in `models.py`
- [ ] Calculation module created with pure functions
- [ ] Module exported from `calculations/__init__.py`
- [ ] UI tab created with input validation and error handling
- [ ] Tab integrated into main app
- [ ] Unit tests written (>90% coverage)
- [ ] Property-based tests written for key properties
- [ ] Integration test added to `test_integration.py`
- [ ] Documentation updated
- [ ] All tests passing


## Testing Approach

The application uses a **dual testing strategy**: unit tests + property-based tests.

### Testing Philosophy

1. **Unit Tests**: Verify specific examples, edge cases, and error conditions
2. **Property-Based Tests**: Verify universal properties hold across all inputs
3. **Integration Tests**: Verify complete workflows end-to-end
4. **UI Tests**: Verify Streamlit interface behavior

Together, these provide comprehensive coverage:
- Unit tests catch concrete bugs
- Property tests verify general correctness
- Integration tests verify system behavior
- UI tests verify user experience

### Unit Testing

**Purpose**: Test specific scenarios with known values

**Example**:
```python
@pytest.mark.urs("URS-FUNC_A-02")
def test_success_run_known_value():
    """Test with known statistical reference value."""
    # C=95%, R=90% should give n=29
    result = calculate_sample_size_zero_failures(95.0, 90.0)
    assert result == 29

@pytest.mark.urs("URS-FUNC_A-01")
def test_invalid_confidence_rejected():
    """Test that confidence > 100 is rejected."""
    with pytest.raises(ValueError):
        AttributeInput(confidence=150.0, reliability=90.0)
```

**Guidelines**:
- Test with known reference values from statistical tables
- Test boundary conditions (min/max values)
- Test error conditions (invalid inputs)
- Use descriptive test names that explain what is being tested
- Mark tests with URS requirement IDs using `@pytest.mark.urs()`

### Property-Based Testing

**Purpose**: Verify universal properties across randomly generated inputs

**Library**: Hypothesis for Python

**Configuration** (in `conftest.py`):
```python
from hypothesis import settings

settings.register_profile("default", max_examples=100)
settings.load_profile("default")
```

**Example**:
```python
from hypothesis import given, strategies as st

@pytest.mark.urs("URS-FUNC_A-02")
@given(
    confidence=st.floats(min_value=0.01, max_value=99.99),
    reliability=st.floats(min_value=0.01, max_value=99.99)
)
def test_success_run_theorem_correctness(confidence, reliability):
    """
    Property 1: For any C and R, sample size should equal 
    ceiling(ln(1-C/100) / ln(R/100))
    
    Validates: Requirements 1.2
    """
    result = calculate_sample_size_zero_failures(confidence, reliability)
    
    expected = math.ceil(
        math.log(1 - confidence/100) / math.log(reliability/100)
    )
    
    assert result == expected
```

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
   ```python
   @given(inputs)
   def test_formula_correctness(inputs):
       result = calculate(inputs)
       expected = reference_formula(inputs)
       assert result == pytest.approx(expected)
   ```

2. **Round-Trip Properties**: Transformation followed by inverse returns original
   ```python
   @given(data=positive_datasets)
   def test_log_transformation_round_trip(data):
       transformed = transform_log(data)
       back_transformed = [back_transform_log(x) for x in transformed]
       assert back_transformed == pytest.approx(data, rel=1e-6)
   ```

3. **Invariants**: Properties that must hold regardless of inputs
   ```python
   @given(confidence=percentages, reliability=percentages)
   def test_sample_size_positive(confidence, reliability):
       result = calculate_sample_size(confidence, reliability)
       assert result > 0
   ```

4. **Comparison Properties**: Relationships between related calculations
   ```python
   @given(c=st.integers(min_value=0, max_value=3))
   def test_sample_size_increases_with_failures(c):
       n1 = calculate_sample_size(95.0, 90.0, c)
       n2 = calculate_sample_size(95.0, 90.0, c + 1)
       assert n2 > n1  # More failures allowed = larger sample needed
   ```

### Adding New Properties

When adding new functionality, define correctness properties in the design document first:

**Template**:
```
**Property N: [Property Name]**
*For any* [input conditions], [the system behavior should be...]
**Validates: Requirements X.Y**
```

**Example**:
```
**Property 1: Success Run Theorem Correctness**
*For any* confidence level C (0 < C < 100) and reliability R (0 < R < 100), 
when calculating sample size with zero allowable failures, the calculated n 
should equal ceiling(ln(1-C/100) / ln(R/100))
**Validates: Requirements 1.2**
```

Then implement the property test:
```python
@pytest.mark.urs("URS-FUNC_A-02")
@given(
    confidence=st.floats(min_value=0.01, max_value=99.99),
    reliability=st.floats(min_value=0.01, max_value=99.99)
)
def test_success_run_theorem_correctness(confidence, reliability):
    """Property 1: Success Run Theorem Correctness
    
    Validates: Requirements 1.2
    """
    result = calculate_sample_size_zero_failures(confidence, reliability)
    expected = math.ceil(math.log(1 - confidence/100) / math.log(reliability/100))
    assert result == expected
```

### Integration Testing

**Purpose**: Test complete workflows end-to-end

**Example**:
```python
def test_attribute_workflow_complete():
    """Test complete attribute analysis workflow."""
    # Create input
    input_data = AttributeInput(
        confidence=95.0,
        reliability=90.0,
        allowable_failures=None
    )
    
    # Perform calculation
    result = calculate_attribute(input_data)
    
    # Verify result structure
    assert isinstance(result, SensitivityResult)
    assert len(result.results) == 4
    
    # Verify results are ordered by c
    for i, r in enumerate(result.results):
        assert r.allowable_failures == i
        assert r.sample_size > 0
```

### Test Execution

**Run all tests**:
```bash
uv run pytest -q
```

**Run specific test file**:
```bash
uv run pytest tests/test_attribute_calcs.py -q
```

**Run tests for specific URS requirement**:
```bash
uv run pytest -m urs -k "URS-FUNC_A-02" -v
```

**Run property tests only**:
```bash
uv run pytest -k "property" -q
```

**Run with coverage**:
```bash
uv run pytest --cov=src/sample_size_estimator --cov-report=html -q
```

**Run specific test**:
```bash
uv run pytest tests/test_attribute_calcs.py::test_success_run_known_value -v
```

### Test Coverage Requirements

| Module | Unit Test Coverage | Property Tests | Integration Tests |
|--------|-------------------|----------------|-------------------|
| attribute_calcs.py | > 90% | Properties 1-5 | 2 workflows |
| variables_calcs.py | > 90% | Properties 6-12 | 2 workflows |
| non_normal_calcs.py | > 90% | Properties 13-22 | 2 workflows |
| reliability_calcs.py | > 90% | Properties 23-25 | 1 workflow |
| validation.py | > 95% | Properties 26-27 | 1 workflow |
| reports.py | > 85% | N/A | 2 workflows |
| config.py | > 90% | Property 28 | 1 workflow |
| logger.py | > 85% | Properties 29-30 | 1 workflow |

### Debugging Failed Tests

**View detailed output**:
```bash
uv run pytest tests/test_attribute_calcs.py -v --tb=long
```

**Run with print statements**:
```bash
uv run pytest tests/test_attribute_calcs.py -s
```

**Stop on first failure**:
```bash
uv run pytest --maxfail=1
```

**Run last failed tests**:
```bash
uv run pytest --lf
```


## Configuration Management

### Configuration Sources

The application uses **Pydantic Settings** for configuration management with the following precedence:

1. **Environment variables** (highest priority)
2. **`.env` file** in project root
3. **Default values** in code (lowest priority)

### Available Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `APP_TITLE` | str | "Sample Size Estimator" | Application title |
| `APP_VERSION` | str | "0.0.1" | Application version |
| `LOG_LEVEL` | str | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | str | "logs/app.log" | Path to log file |
| `LOG_FORMAT` | str | "json" | Log format (json or text) |
| `VALIDATED_HASH` | str | None | SHA-256 hash of validated calculation engine |
| `CALCULATIONS_FILE` | str | "src/sample_size_estimator/calculations/__init__.py" | Path to calculation engine file |
| `REPORT_OUTPUT_DIR` | str | "reports" | Directory for generated reports |
| `REPORT_AUTHOR` | str | "Sample Size Estimator System" | Author name in reports |
| `DEFAULT_CONFIDENCE` | float | 95.0 | Default confidence level (%) |
| `DEFAULT_RELIABILITY` | float | 90.0 | Default reliability level (%) |

### Configuration Files

**`.env.example`** (template):
```bash
# Application Settings
APP_TITLE=Sample Size Estimator
APP_VERSION=0.0.1

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=json

# Validation Settings
VALIDATED_HASH=abc123...  # SHA-256 hash from validation certificate
CALCULATIONS_FILE=src/sample_size_estimator/calculations/__init__.py

# Report Settings
REPORT_OUTPUT_DIR=reports
REPORT_AUTHOR=Sample Size Estimator System

# Statistical Defaults
DEFAULT_CONFIDENCE=95.0
DEFAULT_RELIABILITY=90.0
```

**`.env`** (actual configuration - not in version control):
```bash
# Copy from .env.example and customize
LOG_LEVEL=DEBUG
VALIDATED_HASH=your_actual_hash_here
```

### Using Configuration in Code

```python
from sample_size_estimator.config import get_settings

# Get settings singleton
settings = get_settings()

# Access settings
print(settings.app_title)
print(settings.log_level)

# Settings are validated by Pydantic
# Invalid values will raise ValidationError at startup
```

### Environment-Specific Configuration

**Development**:
```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

**Production**:
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
VALIDATED_HASH=<hash_from_validation_certificate>
```

**Testing**:
```bash
LOG_LEVEL=WARNING
REPORT_OUTPUT_DIR=test_reports
```

### Validation Hash Management

The `VALIDATED_HASH` setting is critical for regulatory compliance:

1. **Initial Setup**: Leave as `None` during development
2. **After Validation**: Run validation test suite
3. **Update Hash**: Copy hash from validation certificate to `.env`
4. **Verification**: Application checks hash on startup and in reports

**Updating Validated Hash**:
```bash
# 1. Run validation test suite
uv run python scripts/generate_validation_certificate.py

# 2. Copy hash from generated certificate
# 3. Update .env file
VALIDATED_HASH=abc123def456...

# 4. Restart application
```

### Adding New Configuration Parameters

1. **Add to `AppSettings` class** in `config.py`:
   ```python
   class AppSettings(BaseSettings):
       # ... existing settings
       new_parameter: str = "default_value"
   ```

2. **Add to `.env.example`**:
   ```bash
   # New Feature
   NEW_PARAMETER=default_value
   ```

3. **Document in this guide** (update table above)

4. **Use in code**:
   ```python
   settings = get_settings()
   value = settings.new_parameter
   ```


## Development Workflow

### Initial Setup

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd sample-size-estimator
   ```

2. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies**:
   ```bash
   uv sync
   ```

4. **Create `.env` file**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Verify installation**:
   ```bash
   uv run python scripts/check_environment.py
   ```

### Daily Development Workflow

1. **Activate virtual environment** (optional, uv handles this):
   ```bash
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

2. **Run application**:
   ```bash
   uv run streamlit run src/sample_size_estimator/app.py
   ```

3. **Make code changes**

4. **Run tests**:
   ```bash
   uv run pytest -q
   ```

5. **Check code quality**:
   ```bash
   # Linting
   uv run ruff check src/ tests/
   
   # Type checking
   uvx mypy src/sample_size_estimator
   
   # Fix auto-fixable issues
   uv run ruff check --fix src/ tests/
   ```

6. **Commit changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

### Adding Dependencies

**Add new dependency**:
```bash
uv add package-name
```

**Add development dependency**:
```bash
uv add --dev package-name
```

**Remove dependency**:
```bash
uv remove package-name
```

**Update all dependencies**:
```bash
uv sync --upgrade
```

### Running the Application

**Development mode**:
```bash
uv run streamlit run src/sample_size_estimator/app.py
```

**With specific configuration**:
```bash
LOG_LEVEL=DEBUG uv run streamlit run src/sample_size_estimator/app.py
```

**Access application**:
- Open browser to `http://localhost:8501`

### Testing Workflow

**Run all tests**:
```bash
uv run pytest -q
```

**Run specific module tests**:
```bash
uv run pytest tests/test_attribute_calcs.py -q
```

**Run with coverage**:
```bash
uv run pytest --cov=src/sample_size_estimator --cov-report=html -q
open htmlcov/index.html  # View coverage report
```

**Run property tests with more examples**:
```bash
uv run pytest -k "property" --hypothesis-show-statistics
```

**Run integration tests only**:
```bash
uv run pytest tests/test_integration.py -v
```

### Code Quality Checks

**Linting with ruff**:
```bash
# Check for issues
uv run ruff check src/ tests/

# Fix auto-fixable issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/
```

**Type checking with mypy**:
```bash
uvx mypy src/sample_size_estimator
```

**Run all quality checks**:
```bash
# Create a script: scripts/check_quality.sh
#!/bin/bash
echo "Running linter..."
uv run ruff check src/ tests/

echo "Running type checker..."
uvx mypy src/sample_size_estimator

echo "Running tests..."
uv run pytest -q

echo "All checks complete!"
```

### Validation Workflow

**Generate validation certificate**:
```bash
uv run python scripts/generate_validation_certificate.py
```

**Check environment**:
```bash
uv run python scripts/check_environment.py
```

**Update validated hash**:
1. Run validation certificate generation
2. Copy hash from `reports/validation_certificate_*.pdf`
3. Update `VALIDATED_HASH` in `.env`
4. Restart application

### Debugging

**Debug with print statements**:
```python
# In calculation function
print(f"Debug: confidence={confidence}, reliability={reliability}")
```

**Run tests with output**:
```bash
uv run pytest tests/test_attribute_calcs.py -s
```

**Debug Streamlit app**:
```python
# In UI code
st.write("Debug:", variable_name)
st.json(data_structure)
```

**Check logs**:
```bash
tail -f logs/app.log
```

**Python debugger**:
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

### Common Tasks

**Add new statistical method**:
1. Define models in `models.py`
2. Create calculation module in `calculations/`
3. Create UI tab in `ui/`
4. Write tests in `tests/`
5. Update documentation

**Fix a bug**:
1. Write failing test that reproduces bug
2. Fix the bug
3. Verify test passes
4. Run full test suite
5. Commit with descriptive message

**Update dependencies**:
1. Update `pyproject.toml` or use `uv add package@version`
2. Run `uv sync`
3. Run full test suite
4. Update documentation if needed
5. Regenerate validation certificate

**Prepare for release**:
1. Run full test suite: `uv run pytest`
2. Run quality checks: `ruff`, `mypy`
3. Generate validation certificate
4. Update `APP_VERSION` in `config.py`
5. Update `CHANGELOG.md`
6. Tag release: `git tag v1.0.0`
7. Push: `git push --tags`


## Code Style and Standards

### Python Style Guide

Follow **PEP 8** with these specific guidelines:

**Naming Conventions**:
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Descriptive names (avoid abbreviations)

**Example**:
```python
# Good
def calculate_sample_size_zero_failures(confidence: float, reliability: float) -> int:
    MAX_ITERATIONS = 10000
    c_decimal = confidence / 100.0
    return result

# Bad
def calcSS(c: float, r: float) -> int:
    maxIter = 10000
    cd = c / 100.0
    return res
```

**Line Length**:
- Maximum 88 characters (Black formatter default)
- Break long lines logically

**Imports**:
```python
# Standard library
import math
from pathlib import Path

# Third-party
import numpy as np
from scipy import stats
from pydantic import BaseModel

# Local
from ..models import AttributeInput
from ..config import get_settings
```

### Type Hints

**Always use type hints** for function signatures:

```python
# Good
def calculate_tolerance_factor(
    n: int,
    confidence: float,
    reliability: float
) -> float:
    """Calculate tolerance factor."""
    return k

# Bad
def calculate_tolerance_factor(n, confidence, reliability):
    return k
```

**Use modern type hint syntax** (Python 3.10+):
```python
# Good
def process_data(data: list[float]) -> dict[str, float]:
    return {"mean": np.mean(data)}

# Old style (avoid)
from typing import List, Dict
def process_data(data: List[float]) -> Dict[str, float]:
    return {"mean": np.mean(data)}
```

**Use `None` for optional types**:
```python
# Good
def get_value(key: str) -> float | None:
    return value if exists else None

# Old style (avoid)
from typing import Optional
def get_value(key: str) -> Optional[float]:
    return value if exists else None
```

### Docstrings

Use **Google-style docstrings** for all public functions:

```python
def calculate_sample_size_with_failures(
    confidence: float,
    reliability: float,
    allowable_failures: int
) -> int:
    """Calculate minimum sample size using cumulative binomial distribution.
    
    This function iteratively solves for the smallest sample size where
    the cumulative probability of observing c or fewer failures is less
    than or equal to (1 - confidence level).
    
    Args:
        confidence: Confidence level as percentage (0-100)
        reliability: Reliability level as percentage (0-100)
        allowable_failures: Maximum allowable failures (c)
    
    Returns:
        Minimum sample size (integer)
    
    Raises:
        ValueError: If no valid sample size found within reasonable range
    
    Formula:
        sum(binom(n,k) * (1-R)^k * R^(n-k) for k=0 to c) <= 1-C
    
    Example:
        >>> calculate_sample_size_with_failures(95.0, 90.0, 1)
        46
    """
    # Implementation
```

**Docstring sections**:
- Brief description (one line)
- Detailed description (optional)
- `Args:` - Parameter descriptions
- `Returns:` - Return value description
- `Raises:` - Exceptions that may be raised
- `Formula:` - Mathematical formula (for calculation functions)
- `Example:` - Usage example (optional)

### Error Handling

**Use specific exception types**:
```python
# Good
if value <= 0:
    raise ValueError("Value must be positive")

# Bad
if value <= 0:
    raise Exception("Error")
```

**Handle exceptions at appropriate level**:
```python
# In calculation function - let exceptions propagate
def calculate(value: float) -> float:
    if value <= 0:
        raise ValueError("Value must be positive")
    return math.log(value)

# In UI layer - catch and display to user
try:
    result = calculate(user_input)
    st.success(f"Result: {result}")
except ValueError as e:
    st.error(f"Input Error: {str(e)}")
```

### Code Organization

**Keep functions small and focused**:
```python
# Good - single responsibility
def calculate_tolerance_factor(n: int, confidence: float, reliability: float) -> float:
    """Calculate tolerance factor only."""
    return k

def calculate_tolerance_limits(mean: float, std: float, k: float) -> tuple[float, float]:
    """Calculate limits only."""
    return (lower, upper)

# Bad - doing too much
def calculate_everything(n, confidence, reliability, mean, std, lsl, usl):
    # Calculates factor, limits, ppk, comparison all in one function
    pass
```

**Use helper functions**:
```python
def calculate_attribute(input_data: AttributeInput) -> AttributeResult | SensitivityResult:
    """Main entry point - orchestrates helpers."""
    if input_data.allowable_failures is None:
        return _calculate_sensitivity_analysis(input_data)
    elif input_data.allowable_failures == 0:
        return _calculate_zero_failures(input_data)
    else:
        return _calculate_with_failures(input_data)

def _calculate_zero_failures(input_data: AttributeInput) -> AttributeResult:
    """Helper for zero failures case."""
    n = calculate_sample_size_zero_failures(
        input_data.confidence,
        input_data.reliability
    )
    return AttributeResult(...)
```

### Testing Standards

**Test naming**:
```python
# Good - descriptive names
def test_success_run_theorem_with_known_value():
    """Test Success Run Theorem with C=95%, R=90% expecting n=29."""
    pass

def test_invalid_confidence_raises_value_error():
    """Test that confidence > 100 raises ValueError."""
    pass

# Bad - unclear names
def test_1():
    pass

def test_calc():
    pass
```

**Test structure** (Arrange-Act-Assert):
```python
def test_tolerance_factor_calculation():
    """Test tolerance factor calculation for known values."""
    # Arrange
    n = 10
    confidence = 95.0
    reliability = 90.0
    
    # Act
    result = calculate_one_sided_tolerance_factor(n, confidence, reliability)
    
    # Assert
    assert result > 0
    assert isinstance(result, float)
```

### Comments

**Use comments for complex logic**:
```python
# Good - explains why
# Use iterative approach because closed-form solution doesn't exist
# for binomial with failures > 0
while n < MAX_ITERATIONS:
    cumulative_prob = sum(stats.binom.pmf(k, n, p_fail) for k in range(c + 1))
    if cumulative_prob <= (1 - c_decimal):
        return n
    n += 1

# Bad - states the obvious
# Increment n
n += 1
```

**Avoid commented-out code**:
```python
# Bad - delete instead of commenting
# def old_calculation(x):
#     return x * 2

# Good - just delete it (version control preserves history)
```

### Constants

**Define constants at module level**:
```python
# At top of module
MAX_ITERATIONS = 10000
BOLTZMANN_CONSTANT = 8.617333262e-5  # eV/K
DEFAULT_ALPHA = 0.05

def calculate(value: float) -> float:
    """Use module-level constants."""
    if value > MAX_ITERATIONS:
        raise ValueError(f"Value exceeds maximum of {MAX_ITERATIONS}")
    return value * BOLTZMANN_CONSTANT
```

### Validation

**Validate at model level, not in calculations**:
```python
# Good - validation in Pydantic model
class AttributeInput(BaseModel):
    confidence: float = Field(ge=0.0, le=100.0)
    
    @field_validator("confidence")
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        if v <= 0 or v >= 100:
            raise ValueError("Value must be between 0 and 100 (exclusive)")
        return v

# Calculation function assumes valid input
def calculate(confidence: float) -> int:
    """Assumes confidence is already validated."""
    return math.ceil(math.log(1 - confidence/100))

# Bad - validation in calculation function
def calculate(confidence: float) -> int:
    if confidence <= 0 or confidence >= 100:
        raise ValueError("Invalid confidence")
    return math.ceil(math.log(1 - confidence/100))
```

### Code Review Checklist

Before submitting code for review:

- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Code follows PEP 8 style guide
- [ ] No commented-out code
- [ ] No hardcoded values (use constants or configuration)
- [ ] Error handling is appropriate
- [ ] Tests are written and passing
- [ ] No duplicate code
- [ ] Variable names are descriptive
- [ ] Functions are small and focused
- [ ] Imports are organized correctly
- [ ] Linter passes (`ruff check`)
- [ ] Type checker passes (`mypy`)


## Appendix: Property Examples

This section provides detailed examples of property-based tests for reference when adding new properties.

### Example 1: Mathematical Correctness Property

**Property**: Success Run Theorem formula correctness

```python
from hypothesis import given, strategies as st
import math
import pytest

@pytest.mark.urs("URS-FUNC_A-02")
@given(
    confidence=st.floats(min_value=0.01, max_value=99.99),
    reliability=st.floats(min_value=0.01, max_value=99.99)
)
def test_success_run_theorem_correctness(confidence, reliability):
    """
    Property 1: Success Run Theorem Correctness
    
    For any confidence level C (0 < C < 100) and reliability R (0 < R < 100),
    when calculating sample size with zero allowable failures, the calculated n
    should equal ceiling(ln(1-C/100) / ln(R/100))
    
    Validates: Requirements 1.2
    """
    result = calculate_sample_size_zero_failures(confidence, reliability)
    
    expected = math.ceil(
        math.log(1 - confidence/100) / math.log(reliability/100)
    )
    
    assert result == expected, (
        f"Sample size mismatch for C={confidence}, R={reliability}: "
        f"got {result}, expected {expected}"
    )
```

### Example 2: Round-Trip Property

**Property**: Logarithmic transformation round-trip

```python
@pytest.mark.urs("URS-FUNC_C-06")
@given(
    data=st.lists(
        st.floats(min_value=0.01, max_value=1000.0),
        min_size=3,
        max_size=50
    )
)
def test_log_transformation_round_trip(data):
    """
    Property 17: Logarithmic Transformation Round-Trip
    
    For any dataset with all positive values, applying log transformation
    followed by exp back-transformation should produce values equal to the
    original values (within numerical precision)
    
    Validates: Requirements 13.1
    """
    # Transform
    transformed = transform_log(data)
    
    # Back-transform
    back_transformed = [back_transform_log(x) for x in transformed]
    
    # Verify round-trip
    for original, recovered in zip(data, back_transformed):
        assert original == pytest.approx(recovered, rel=1e-6), (
            f"Round-trip failed: {original} != {recovered}"
        )
```

### Example 3: Invariant Property

**Property**: Sample size is always positive

```python
@pytest.mark.urs("URS-FUNC_A-02")
@given(
    confidence=st.floats(min_value=0.01, max_value=99.99),
    reliability=st.floats(min_value=0.01, max_value=99.99),
    allowable_failures=st.integers(min_value=0, max_value=10)
)
def test_sample_size_always_positive(confidence, reliability, allowable_failures):
    """
    Property: Sample size is always positive
    
    For any valid inputs, the calculated sample size must be a positive integer.
    
    Validates: Requirements 1.3, 2.4
    """
    if allowable_failures == 0:
        result = calculate_sample_size_zero_failures(confidence, reliability)
    else:
        result = calculate_sample_size_with_failures(
            confidence, reliability, allowable_failures
        )
    
    assert result > 0, f"Sample size must be positive, got {result}"
    assert isinstance(result, int), f"Sample size must be integer, got {type(result)}"
```

### Example 4: Comparison Property

**Property**: Specification comparison logic

```python
@pytest.mark.urs("URS-FUNC_B-03")
@given(
    lower_tol=st.floats(min_value=-100.0, max_value=100.0),
    upper_tol=st.floats(min_value=-100.0, max_value=100.0),
    lsl=st.floats(min_value=-100.0, max_value=100.0),
    usl=st.floats(min_value=-100.0, max_value=100.0)
)
def test_specification_comparison_logic(lower_tol, upper_tol, lsl, usl):
    """
    Property 9: Specification Comparison Logic
    
    For any tolerance limits (L_tol, U_tol) and specification limits (LSL, USL),
    the result should be PASS if and only if L_tol >= LSL AND U_tol <= USL
    
    Validates: Requirements 6.2, 6.3, 6.4
    """
    # Ensure valid ordering
    if lower_tol > upper_tol:
        lower_tol, upper_tol = upper_tol, lower_tol
    if lsl > usl:
        lsl, usl = usl, lsl
    
    pass_fail, margin_lower, margin_upper = compare_to_spec_limits(
        lower_tol, upper_tol, lsl, usl
    )
    
    # Verify logic
    expected_pass = (lower_tol >= lsl) and (upper_tol <= usl)
    
    if expected_pass:
        assert pass_fail == "PASS", (
            f"Expected PASS but got {pass_fail} for "
            f"tol=[{lower_tol}, {upper_tol}], spec=[{lsl}, {usl}]"
        )
    else:
        assert pass_fail == "FAIL", (
            f"Expected FAIL but got {pass_fail} for "
            f"tol=[{lower_tol}, {upper_tol}], spec=[{lsl}, {usl}]"
        )
```

### Example 5: Validation Property

**Property**: Input validation rejects invalid values

```python
@pytest.mark.urs("URS-FUNC_A-01")
@given(
    confidence=st.one_of(
        st.floats(max_value=0.0),  # Too low
        st.floats(min_value=100.0, max_value=200.0)  # Too high
    )
)
def test_invalid_confidence_rejected(confidence):
    """
    Property 5: Input Validation for Percentages
    
    For any input value v, when validating confidence or reliability,
    the system should accept v if and only if 0 < v < 100
    
    Validates: Requirements 1.1, 1.4, 19.1
    """
    with pytest.raises(ValueError) as exc_info:
        AttributeInput(confidence=confidence, reliability=90.0)
    
    assert "between 0 and 100" in str(exc_info.value).lower(), (
        f"Expected validation error message for confidence={confidence}"
    )
```

### Example 6: Determinism Property

**Property**: Hash calculation is deterministic

```python
@pytest.mark.urs("URS-VAL-01")
@given(
    content=st.text(min_size=1, max_size=1000)
)
def test_hash_calculation_determinism(content, tmp_path):
    """
    Property 26: Hash Calculation Determinism
    
    For any file, calculating the SHA-256 hash multiple times should
    produce identical hash values
    
    Validates: Requirements 21.1
    """
    # Create temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)
    
    # Calculate hash multiple times
    hash1 = calculate_file_hash(str(test_file))
    hash2 = calculate_file_hash(str(test_file))
    hash3 = calculate_file_hash(str(test_file))
    
    # Verify determinism
    assert hash1 == hash2 == hash3, (
        f"Hash calculation not deterministic: {hash1}, {hash2}, {hash3}"
    )
```

### Tips for Writing Good Properties

1. **Start with the property statement**: Write the property in plain English first
2. **Use appropriate strategies**: Choose input generators that match your domain
3. **Add constraints**: Use `assume()` or filter strategies to ensure valid inputs
4. **Provide clear error messages**: Include context in assertion messages
5. **Test edge cases**: Include boundary values in your strategies
6. **Keep properties simple**: One property per test function
7. **Document thoroughly**: Explain what property is being tested and why

### Common Hypothesis Strategies

```python
# Percentages (0-100 exclusive)
percentages = st.floats(min_value=0.01, max_value=99.99)

# Positive integers
positive_ints = st.integers(min_value=1, max_value=1000)

# Positive floats
positive_floats = st.floats(min_value=0.01, max_value=1000.0)

# Non-negative floats
non_negative_floats = st.floats(min_value=0.0, max_value=1000.0)

# Small datasets
small_datasets = st.lists(
    st.floats(min_value=-100.0, max_value=100.0),
    min_size=3,
    max_size=20
)

# Positive datasets (for transformations)
positive_datasets = st.lists(
    st.floats(min_value=0.01, max_value=1000.0),
    min_size=3,
    max_size=50
)

# Ordered pairs (LSL < USL)
@st.composite
def ordered_spec_limits(draw):
    lsl = draw(st.floats(min_value=-100.0, max_value=100.0))
    usl = draw(st.floats(min_value=lsl + 0.01, max_value=200.0))
    return (lsl, usl)
```

## Conclusion

This developer guide provides the foundation for understanding, maintaining, and extending the Sample Size Estimator application. Key takeaways:

- **Functional architecture** with pure functions and strong type safety
- **Modular design** makes it easy to add new statistical methods
- **Comprehensive testing** with unit and property-based tests
- **Configuration management** supports multiple environments
- **Code quality standards** ensure maintainability

For additional information:
- **User Guide**: See `docs/USER_GUIDE.md` for end-user documentation
- **Validation Protocol**: See `docs/VALIDATION_PROTOCOL.md` for validation procedures
- **Requirements**: See `.kiro/specs/sample-size-estimator/requirements.md`
- **Design**: See `.kiro/specs/sample-size-estimator/design.md`

Questions or issues? Contact the development team or open an issue in the repository.

