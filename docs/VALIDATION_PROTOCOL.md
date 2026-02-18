# Validation Protocol

## Document Information

**Document Title:** Validation Protocol for Sample Size Estimator Application  
**Version:** 0.1  
**Date:** 2026  
**Purpose:** This document describes the validation procedures for the Sample Size Estimator application, including Installation Qualification (IQ), Operational Qualification (OQ), and Performance Qualification (PQ) protocols.

**Regulatory Context:** This validation protocol supports compliance with ISO/TR 80002-2 for medical device software validation and 21 CFR Part 11 for electronic records.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Validation Overview](#validation-overview)
3. [Installation Qualification (IQ)](#installation-qualification-iq)
4. [Operational Qualification (OQ)](#operational-qualification-oq)
5. [Performance Qualification (PQ)](#performance-qualification-pq)
6. [Validation Test Suite](#validation-test-suite)
7. [Validation Certificate Generation](#validation-certificate-generation)
8. [URS Requirements and Test Coverage](#urs-requirements-and-test-coverage)
9. [Validation Maintenance](#validation-maintenance)
10. [Appendices](#appendices)

---

## 1. Introduction

### 1.1 Purpose

The Sample Size Estimator is a Python-based web application designed to determine statistically valid sample sizes for medical device design verification and process validation. This validation protocol ensures that the application:

- Performs calculations correctly according to established statistical methods
- Meets all User Requirements Specification (URS) requirements
- Operates reliably in the intended environment
- Maintains data integrity and traceability
- Complies with regulatory requirements for software validation

### 1.2 Scope

This validation protocol covers:


- **Installation Qualification (IQ):** Verification that the software and all dependencies are correctly installed
- **Operational Qualification (OQ):** Verification that all calculation functions produce correct results
- **Performance Qualification (PQ):** Verification that the complete system functions correctly in realistic usage scenarios

### 1.3 Validation Approach

The validation follows a risk-based approach with three qualification phases:

1. **IQ Phase:** Automated environment checks verify correct installation
2. **OQ Phase:** Comprehensive automated test suite validates all calculations
3. **PQ Phase:** UI workflow tests simulate real user interactions

### 1.4 Validation Team Roles

| Role | Responsibilities |
|------|------------------|
| Validation Lead | Overall validation planning and execution |
| Test Engineer | Execute test protocols and document results |
| Quality Assurance | Review validation documentation and approve |
| Subject Matter Expert | Verify statistical correctness of calculations |
| IT Administrator | Manage system installation and configuration |

---

## 2. Validation Overview

### 2.1 Validation Strategy

The Sample Size Estimator uses a **dual testing approach** combining:

1. **Unit Tests:** Verify specific examples, edge cases, and error conditions
2. **Property-Based Tests:** Verify universal properties hold across all inputs

This comprehensive approach ensures both concrete correctness (unit tests) and general correctness (property tests).

### 2.2 Validation Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Validation Lifecycle                      │
└─────────────────────────────────────────────────────────────┘

         ┌──────────────┐
         │  IQ Phase    │  Verify Installation
         │  (REQ-23)    │
         └──────┬───────┘
                │
         ┌──────▼───────┐
         │  OQ Phase    │  Verify Calculations
         │  (REQ-24)    │
         └──────┬───────┘
                │
         ┌──────▼───────┐
         │  PQ Phase    │  Verify UI Workflows
         │  (REQ-25)    │
         └──────┬───────┘
                │
         ┌──────▼───────┐
         │ Certificate  │  Generate Validation
         │ Generation   │  Certificate (REQ-22)
         │  (REQ-22)    │
         └──────────────┘
```

### 2.3 Validation Deliverables

| Deliverable | Description | Requirements |
|-------------|-------------|--------------|
| Environment Check Report | IQ verification results | REQ-23 |
| OQ Test Results | Automated test suite results | REQ-24 |
| PQ Test Results | UI workflow test results | REQ-25 |
| Validation Certificate | Final validation summary PDF | REQ-22 |
| Validated Hash | SHA-256 hash of calculation engine | REQ-21 |
| Validation Protocol | This document | REQ-22, REQ-23, REQ-24, REQ-25 |

### 2.4 Acceptance Criteria

The system is considered validated when:

1. ✓ All IQ checks pass (100% of dependencies installed correctly)
2. ✓ All OQ tests pass (100% of calculation tests pass)
3. ✓ All PQ tests pass (100% of UI workflow tests pass)
4. ✓ Validation certificate is generated successfully
5. ✓ Validated hash is documented and stored

---

## 3. Installation Qualification (IQ)

**Requirement:** REQ-23 - Installation Qualification

### 3.1 IQ Objectives

Verify that:
- Python version meets requirements (≥ 3.11)
- All required dependencies are installed with correct versions
- Project structure is complete and correct
- Configuration files are present


### 3.2 IQ Procedure

**Script:** `scripts/check_environment.py`

**Execution:**
```bash
uv run python scripts/check_environment.py
```

**Expected Output:**
- ✓ Python version ≥ 3.11
- ✓ All core dependencies installed with correct versions
- ✓ All development dependencies installed
- ✓ Project structure complete

### 3.3 IQ Checklist

| Check Item | Requirement | Pass Criteria | Status |
|------------|-------------|---------------|--------|
| Python Version | Python ≥ 3.11 | Version check passes | [ ] |
| Streamlit | ≥ 1.30.0 | Package installed and version verified | [ ] |
| Pydantic | ≥ 2.5.0 | Package installed and version verified | [ ] |
| Pydantic Settings | ≥ 2.1.0 | Package installed and version verified | [ ] |
| SciPy | ≥ 1.11.0 | Package installed and version verified | [ ] |
| NumPy | ≥ 1.26.0 | Package installed and version verified | [ ] |
| Matplotlib | ≥ 3.8.0 | Package installed and version verified | [ ] |
| ReportLab | ≥ 4.0.0 | Package installed and version verified | [ ] |
| Pytest | ≥ 8.0.0 | Package installed and version verified | [ ] |
| Hypothesis | ≥ 6.92.0 | Package installed and version verified | [ ] |
| Project Structure | All directories present | src/, tests/, docs/, scripts/ exist | [ ] |
| Configuration Files | pyproject.toml, uv.lock | Files exist and valid | [ ] |
| Lock File | uv.lock present | Dependency versions locked | [ ] |

### 3.4 IQ Dependencies

**Core Dependencies (Required for Operation):**
- **streamlit:** Web application framework
- **pydantic:** Data validation and settings management
- **pydantic-settings:** Environment-based configuration
- **scipy:** Statistical distributions and tests
- **numpy:** Numerical computations
- **matplotlib:** Q-Q plot generation
- **reportlab:** PDF report generation

**Development Dependencies (Required for Validation):**
- **pytest:** Test framework
- **hypothesis:** Property-based testing
- **mypy:** Static type checking
- **ruff:** Code linting and formatting

### 3.5 IQ Acceptance Criteria

**Pass Criteria:**
- All core dependencies installed with versions meeting minimum requirements
- Python version ≥ 3.11
- Project structure complete
- Lock file present and valid

**Fail Criteria:**
- Any core dependency missing or below minimum version
- Python version < 3.11
- Missing critical project files

### 3.6 IQ Documentation

**Record the following information:**
- Date and time of installation
- System information (OS, hostname, processor)
- Python version
- All dependency versions
- Installation performed by (name/role)
- IQ test results (pass/fail for each check)

---

## 4. Operational Qualification (OQ)

**Requirement:** REQ-24 - Operational Qualification Test Suite

### 4.1 OQ Objectives

Verify that all calculation functions produce mathematically correct results by:
- Testing against known statistical reference values
- Verifying formulas with property-based tests (100+ iterations)
- Testing edge cases and boundary conditions
- Verifying error handling for invalid inputs


### 4.2 OQ Test Suite Structure

```
tests/
├── test_attribute_calcs.py          # Attribute calculations (REQ-1, REQ-2, REQ-3)
├── test_variables_calcs.py          # Variables calculations (REQ-4, REQ-5, REQ-6, REQ-7)
├── test_non_normal_calcs.py         # Non-normal calculations (REQ-8-14)
├── test_reliability_calcs.py        # Reliability calculations (REQ-15, REQ-16)
├── test_validation.py               # Hash verification (REQ-21)
├── test_reports.py                  # PDF generation (REQ-20, REQ-22)
├── test_config.py                   # Configuration (REQ-27)
├── test_logger.py                   # Logging (REQ-26)
└── test_integration.py              # End-to-end workflows
```

### 4.3 OQ Test Execution

**Run all OQ tests:**
```bash
uv run pytest -q --tb=short
```

**Run specific module tests:**
```bash
# Attribute calculations
uv run pytest tests/test_attribute_calcs.py -q

# Variables calculations
uv run pytest tests/test_variables_calcs.py -q

# Non-normal calculations
uv run pytest tests/test_non_normal_calcs.py -q

# Reliability calculations
uv run pytest tests/test_reliability_calcs.py -q
```

**Run tests for specific URS requirement:**
```bash
uv run pytest -m urs -k "URS-FUNC_A-02" -v
```

### 4.4 OQ Test Categories

#### 4.4.1 Unit Tests

**Purpose:** Verify specific examples with known correct answers

**Example Test Cases:**
- Success Run Theorem: C=95%, R=90% → n=29 (known reference value)
- Binomial: C=95%, R=90%, c=1 → n=46 (known reference value)
- Ppk Calculation: Mean=10, Std=1, LSL=7, USL=13 → Ppk=1.0
- Outlier Detection: Dataset [1,2,3,4,5,100,200] → 2 outliers detected

**Coverage:** Each calculation function tested with at least 3 known values

#### 4.4.2 Property-Based Tests

**Purpose:** Verify universal properties hold across all valid inputs

**Configuration:**
- Minimum 100 iterations per property test (configured in conftest.py)
- Uses Hypothesis library for input generation
- Tests mathematical properties that must always be true

**Example Properties:**
- **Property 1:** Success Run Theorem formula correctness
- **Property 2:** Binomial sample size correctness
- **Property 8:** Tolerance limit arithmetic (μ ± k*σ)
- **Property 17:** Log transformation round-trip accuracy

**Coverage:** All 30 properties defined in design document tested

#### 4.4.3 Edge Case Tests

**Purpose:** Verify behavior at boundaries and extreme values

**Test Cases:**
- Very high confidence (99.9%)
- Very low confidence (0.1%)
- Very high reliability (99.9%)
- Very low reliability (50%)
- Large sample sizes (n > 1000)
- Small sample sizes (n = 2)
- Empty datasets
- Single-value datasets

#### 4.4.4 Error Handling Tests

**Purpose:** Verify proper rejection of invalid inputs

**Test Cases:**
- Confidence > 100% → ValidationError
- Confidence ≤ 0% → ValidationError
- Negative standard deviation → ValidationError
- LSL ≥ USL → ValidationError
- Negative data for log transformation → TransformationError
- Non-positive data for Box-Cox → TransformationError


### 4.5 OQ Test Coverage Requirements

| Module | Unit Tests | Property Tests | Edge Cases | Error Tests | Target Coverage |
|--------|-----------|----------------|------------|-------------|-----------------|
| attribute_calcs.py | ≥ 5 | Properties 1-5 | ≥ 3 | ≥ 2 | > 90% |
| variables_calcs.py | ≥ 8 | Properties 6-12 | ≥ 4 | ≥ 3 | > 90% |
| non_normal_calcs.py | ≥ 10 | Properties 13-22 | ≥ 5 | ≥ 4 | > 90% |
| reliability_calcs.py | ≥ 4 | Properties 23-25 | ≥ 2 | ≥ 2 | > 90% |
| validation.py | ≥ 3 | Properties 26-27 | ≥ 2 | ≥ 1 | > 95% |
| reports.py | ≥ 4 | N/A | ≥ 2 | ≥ 2 | > 85% |
| config.py | ≥ 3 | Property 28 | ≥ 2 | ≥ 2 | > 90% |
| logger.py | ≥ 3 | Properties 29-30 | ≥ 1 | ≥ 1 | > 85% |

### 4.6 OQ Acceptance Criteria

**Pass Criteria:**
- 100% of unit tests pass
- 100% of property tests pass (with ≥ 100 iterations each)
- 100% of edge case tests pass
- 100% of error handling tests pass
- Overall code coverage > 85%
- No critical or high-severity linting errors

**Fail Criteria:**
- Any test fails
- Property test fails with counterexample
- Code coverage < 85%
- Critical calculation errors detected

### 4.7 OQ Test Traceability

Each test is marked with the URS requirement it validates using pytest markers:

```python
@pytest.mark.urs("URS-FUNC_A-02")
def test_success_run_theorem_correctness():
    """Validates REQ-1.2: Success Run Theorem calculation"""
    # Test implementation
```

This enables traceability from requirements → tests → results.

### 4.8 OQ Known Reference Values

**Attribute Calculations:**
- C=95%, R=90%, c=0 → n=29 (Success Run Theorem)
- C=95%, R=90%, c=1 → n=46 (Binomial)
- C=95%, R=90%, c=2 → n=61 (Binomial)
- C=95%, R=90%, c=3 → n=76 (Binomial)
- C=90%, R=95%, c=0 → n=45 (Success Run Theorem)

**Variables Calculations:**
- Mean=10, Std=1, LSL=7, USL=13 → Ppk=1.0
- Mean=10, Std=0.5, LSL=8, USL=12 → Ppk≈1.33

**Reliability Calculations:**
- C=95%, r=0 → χ²=5.991 (Chi-squared value)
- Ea=0.7eV, T_use=298K, T_test=358K → AF≈10 (Arrhenius)

---

## 5. Performance Qualification (PQ)

**Requirement:** REQ-25 - Performance Qualification UI Testing

### 5.1 PQ Objectives

Verify that the complete system functions correctly in realistic usage scenarios by:
- Testing complete user workflows through the UI
- Verifying data flows from input → calculation → display
- Testing report generation from each module
- Verifying error messages display correctly
- Testing tab navigation and state management

### 5.2 PQ Test Framework

**Framework:** Playwright browser automation (playwright.sync_api)

**Approach:** Simulate user interactions in a real browser environment

**Test Structure:**
```python
from playwright.sync_api import Page, expect

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
```
    # Select tab
    at.tabs[0].select()
    
    # Enter inputs
    at.number_input[0].set_value(95.0)  # Confidence
    at.number_input[1].set_value(90.0)  # Reliability
    
    # Click calculate
    at.button[0].click()
    
    # Verify results
    assert "Sample Size" in at.text[0].value
    assert at.run().success
```


### 5.3 PQ Test Scenarios

#### 5.3.1 Attribute Tab Workflow

**Test Case:** PQ-ATTR-01  
**Objective:** Verify complete attribute calculation workflow  
**Steps:**
1. Launch application
2. Navigate to "Attribute (Binomial)" tab
3. Enter Confidence = 95%
4. Enter Reliability = 90%
5. Leave Allowable Failures empty (sensitivity analysis)
6. Click "Calculate Sample Size"
7. Verify results table displays with c=0,1,2,3
8. Verify sample sizes match expected values
9. Click "Generate Report"
10. Verify PDF downloads successfully

**Expected Results:**
- Results display correctly in table format
- Sample sizes: n=29 (c=0), n=46 (c=1), n=61 (c=2), n=76 (c=3)
- Report generates without errors

#### 5.3.2 Variables Tab Workflow

**Test Case:** PQ-VAR-01  
**Objective:** Verify complete variables calculation workflow  
**Steps:**
1. Navigate to "Variables (Normal)" tab
2. Enter Confidence = 95%
3. Enter Reliability = 90%
4. Enter Sample Size = 30
5. Enter Sample Mean = 10.0
6. Enter Sample Std Dev = 1.0
7. Enter LSL = 7.0
8. Enter USL = 13.0
9. Select "Two-sided" limits
10. Click "Calculate Tolerance Limits"
11. Verify tolerance factor, limits, Ppk, and PASS/FAIL display
12. Generate report

**Expected Results:**
- Tolerance factor calculated
- Upper and lower tolerance limits displayed
- Ppk ≈ 1.0
- PASS/FAIL status shown
- Report generates successfully

#### 5.3.3 Non-Normal Tab Workflow

**Test Case:** PQ-NONNORM-01  
**Objective:** Verify complete non-normal data workflow  
**Steps:**
1. Navigate to "Non-Normal Distribution" tab
2. Enter sample dataset (comma-separated or upload)
3. Click "Detect Outliers"
4. Verify outlier count and values display
5. Click "Test Normality"
6. Verify Shapiro-Wilk and Anderson-Darling results display
7. View Q-Q plot
8. Select transformation method (e.g., "Box-Cox")
9. Click "Apply Transformation"
10. Verify transformed data normality results
11. Verify back-transformed limits display

**Expected Results:**
- Outliers detected correctly
- Normality tests execute and display results
- Q-Q plot renders
- Transformation applies successfully
- Back-transformed results shown

#### 5.3.4 Reliability Tab Workflow

**Test Case:** PQ-REL-01  
**Objective:** Verify complete reliability calculation workflow  
**Steps:**
1. Navigate to "Reliability" tab
2. Enter Confidence = 95%
3. Enter Failures = 0
4. Enter Activation Energy = 0.7 eV
5. Enter Use Temperature = 298 K
6. Enter Test Temperature = 358 K
7. Click "Calculate Test Duration"
8. Verify test duration and acceleration factor display
9. Generate report

**Expected Results:**
- Test duration calculated
- Acceleration factor ≈ 10
- Report generates successfully

#### 5.3.5 Error Handling Workflow

**Test Case:** PQ-ERROR-01  
**Objective:** Verify error messages display correctly  
**Steps:**
1. Navigate to Attribute tab
2. Enter Confidence = 150% (invalid)
3. Click Calculate
4. Verify error message displays
5. Enter valid Confidence = 95%
6. Navigate to Variables tab
7. Enter LSL = 10, USL = 5 (invalid order)
8. Click Calculate
9. Verify error message displays

**Expected Results:**
- Clear error messages for invalid inputs
- Calculation prevented until inputs valid
- Error messages guide user to correction

### 5.4 PQ Test Execution

**Run PQ tests:**
```bash
uv run pytest tests/test_ui_playwright_*.py -v
```

**Manual PQ testing (optional for exploratory testing):**
```bash
# Start application
uv run streamlit run src/sample_size_estimator/app.py

# Follow test scenarios manually
# Document results in PQ test log
```

### 5.5 PQ Acceptance Criteria

**Pass Criteria:**
- All automated UI tests pass
- Results display correctly in UI
- Reports generate without errors
- Error messages display for invalid inputs
- Error messages clear and helpful
- Navigation between tabs works correctly

**Fail Criteria:**
- Any UI test fails
- Results do not display
- Reports fail to generate
- Error messages unclear or missing
- UI navigation broken

---

## 6. Validation Test Suite

### 6.1 Complete Test Execution

**Run all validation tests:**
```bash
# Run complete test suite
uv run pytest -q --tb=short

# Run with coverage report
uv run pytest --cov=src/sample_size_estimator --cov-report=html -q

# Run only tests with URS markers
uv run pytest -m urs -v
```

### 6.2 Test Suite Organization

**Test Markers:**
- `@pytest.mark.urs("URS-ID")` - Links test to URS requirement
- `@pytest.mark.attribute` - Attribute calculation tests
- `@pytest.mark.variables` - Variables calculation tests
- `@pytest.mark.non_normal` - Non-normal calculation tests
- `@pytest.mark.reliability` - Reliability calculation tests
- `@pytest.mark.property` - Property-based tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.ui` - UI workflow tests

### 6.3 Test Configuration

**File:** `tests/conftest.py`

**Key Configurations:**
- Hypothesis settings: min_examples=100 (property tests)
- Pytest markers registered
- Common fixtures defined
- Test data generators

### 6.4 Test Fixtures

**Common fixtures available:**
- `valid_confidence_values` - Standard confidence levels
- `valid_reliability_values` - Standard reliability levels
- `sample_attribute_input` - Sample attribute input data
- `sample_variables_input` - Sample variables input data
- `sample_normal_data` - Normally distributed dataset
- `sample_non_normal_data` - Non-normal dataset
- `known_statistical_values` - Reference values for validation


---

## 7. Validation Certificate Generation

**Requirement:** REQ-22 - Automated Validation Report Generation

### 7.1 Certificate Generation Process

The validation certificate is automatically generated after successful completion of all validation tests.

**Script:** `scripts/generate_validation_certificate.py`

**Execution:**
```bash
uv run python scripts/generate_validation_certificate.py
```

### 7.2 Certificate Generation Steps

The script performs the following steps:

1. **Collect System Information**
   - Operating system and version
   - Python version
   - All dependency versions

2. **Run Test Suite**
   - Execute all tests with pytest
   - Collect test results with URS markers
   - Parse pass/fail status for each test

3. **Calculate Validated Hash**
   - Calculate SHA-256 hash of all calculation module files
   - Combine hashes for complete calculation engine
   - Store validated hash for future verification

4. **Generate Certificate PDF**
   - Create professional PDF document
   - Include all test results with URS traceability
   - Display system information
   - Show validated hash
   - Indicate overall PASS/FAIL status

5. **Save Certificate**
   - Save to `reports/validation_certificate_YYYYMMDD_HHMMSS.pdf`
   - Display validated hash for configuration

### 7.3 Certificate Contents

The validation certificate includes:

**Header Section:**
- Document title: "Validation Certificate"
- Application name: "Sample Size Estimator Application"
- Generation date and time

**Test Execution Information:**
- Test execution date/time
- Tester name/system identifier
- Operating system
- Python version
- Key dependency versions (scipy, numpy, streamlit, pydantic, reportlab)

**URS Test Results Table:**
| URS ID | Test Name | Status |
|--------|-----------|--------|
| URS-FUNC_A-01 | Input validation | PASS/FAIL |
| URS-FUNC_A-02 | Success Run Theorem | PASS/FAIL |
| ... | ... | ... |

**Validation Summary:**
- Overall Status: PASSED / FAILED
- Validated Hash: [SHA-256 hash value]
- Total tests executed
- Tests passed / failed

### 7.4 Validated Hash

**Purpose:** The validated hash ensures calculation engine integrity

**Calculation:**
```python
# Hash all calculation module files
calc_files = [
    "attribute_calcs.py",
    "variables_calcs.py", 
    "non_normal_calcs.py",
    "reliability_calcs.py"
]

# Combine individual file hashes
combined_hash = hashlib.sha256()
for file in calc_files:
    file_hash = calculate_file_hash(file)
    combined_hash.update(file_hash.encode())

validated_hash = combined_hash.hexdigest()
```

**Usage:**
1. After successful validation, copy the validated hash
2. Update `.env` file: `VALIDATED_HASH=<hash_value>`
3. Application will verify hash on startup
4. Reports will show validation state (VALIDATED / NOT VALIDATED)

### 7.5 Certificate Approval

**Approval Process:**
1. Review certificate PDF
2. Verify all tests passed
3. Verify system information correct
4. Sign and date certificate (manual or electronic signature)
5. Store in quality records
6. Update validated hash in configuration

**Approval Signatures:**
- Validation Lead: _________________ Date: _______
- Quality Assurance: _________________ Date: _______
- Subject Matter Expert: _________________ Date: _______

### 7.6 Certificate Storage

**Location:** `reports/validation_certificate_YYYYMMDD_HHMMSS.pdf`

**Retention:** Maintain per regulatory requirements (typically 7+ years)

**Access Control:** Restrict access to quality records system

---

## 8. URS Requirements and Test Coverage

### 8.1 Requirements Traceability Matrix

This section maps each URS requirement to its validation tests.


#### 8.1.1 Attribute Data Requirements (REQ-1, REQ-2, REQ-3)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-1.1 | Validate confidence and reliability ranges | Unit tests, Property 5 | test_attribute_calcs.py |
| REQ-1.2 | Success Run Theorem formula | Unit tests, Property 1 | test_attribute_calcs.py |
| REQ-1.3 | Display sample size as integer | Unit tests | test_attribute_calcs.py |
| REQ-1.4 | Error messages for invalid inputs | Error handling tests | test_attribute_calcs.py |
| REQ-2.1 | Validate allowable failures ≥ 0 | Unit tests, Property 5 | test_attribute_calcs.py |
| REQ-2.2 | Binomial distribution formula | Unit tests, Property 2 | test_attribute_calcs.py |
| REQ-2.3 | Iterative solution for minimal n | Unit tests, Property 3 | test_attribute_calcs.py |
| REQ-2.4 | Display sample size as integer | Unit tests | test_attribute_calcs.py |
| REQ-3.1 | Sensitivity analysis for c=0,1,2,3 | Unit tests, Property 4 | test_attribute_calcs.py |
| REQ-3.2 | Display results in table format | UI tests | test_ui_workflows.py |
| REQ-3.3 | Single value when c specified | Unit tests | test_attribute_calcs.py |
| REQ-3.4 | Display all results simultaneously | UI tests | test_ui_workflows.py |

#### 8.1.2 Variables Data Requirements (REQ-4, REQ-5, REQ-6, REQ-7)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-4.1 | One-sided tolerance factor | Unit tests, Property 6 | test_variables_calcs.py |
| REQ-4.2 | Two-sided tolerance factor | Unit tests, Property 7 | test_variables_calcs.py |
| REQ-4.3 | Accept valid inputs | Unit tests | test_variables_calcs.py |
| REQ-4.4 | Validate sample size > 1 | Unit tests, Property 12 | test_variables_calcs.py |
| REQ-4.5 | Display with 4 decimal places | Unit tests | test_variables_calcs.py |
| REQ-5.1 | Upper tolerance limit calculation | Unit tests, Property 8 | test_variables_calcs.py |
| REQ-5.2 | Lower tolerance limit calculation | Unit tests, Property 8 | test_variables_calcs.py |
| REQ-5.3 | One-sided limit calculation | Unit tests | test_variables_calcs.py |
| REQ-5.4 | Display with appropriate precision | Unit tests | test_variables_calcs.py |
| REQ-6.1 | Validate LSL < USL | Unit tests, Property 11 | test_variables_calcs.py |
| REQ-6.2 | PASS when limits within spec | Unit tests, Property 9 | test_variables_calcs.py |
| REQ-6.3 | FAIL when limits violate spec | Unit tests, Property 9 | test_variables_calcs.py |
| REQ-6.4 | Display PASS/FAIL indicator | UI tests | test_ui_workflows.py |
| REQ-6.5 | Display margins | Unit tests | test_variables_calcs.py |
| REQ-7.1 | Ppk calculation formula | Unit tests, Property 10 | test_variables_calcs.py |
| REQ-7.2 | One-sided Ppk | Unit tests, Property 10 | test_variables_calcs.py |
| REQ-7.3 | Display with 2 decimal places | Unit tests | test_variables_calcs.py |
| REQ-7.4 | Validate std dev > 0 | Unit tests, Property 12 | test_variables_calcs.py |

#### 8.1.3 Non-Normal Data Requirements (REQ-8 through REQ-14)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-8.1 | Calculate Q1, Q3, IQR | Unit tests, Property 13 | test_non_normal_calcs.py |
| REQ-8.2 | Flag outliers using IQR method | Unit tests, Property 13 | test_non_normal_calcs.py |
| REQ-8.3 | Display outlier count | Unit tests, Property 14 | test_non_normal_calcs.py |
| REQ-8.4 | Display outlier values | Unit tests, Property 14 | test_non_normal_calcs.py |
| REQ-8.5 | Allow analysis to proceed | UI tests | test_ui_workflows.py |
| REQ-9.1 | Shapiro-Wilk test | Unit tests, Property 15 | test_non_normal_calcs.py |
| REQ-9.2 | Anderson-Darling test | Unit tests, Property 15 | test_non_normal_calcs.py |
| REQ-9.3 | Display Shapiro-Wilk p-value | Unit tests | test_non_normal_calcs.py |
| REQ-9.4 | Display Anderson-Darling results | Unit tests | test_non_normal_calcs.py |
| REQ-9.5 | Reject normality when p < 0.05 | Unit tests, Property 16 | test_non_normal_calcs.py |
| REQ-9.6 | Reject normality when AD exceeds critical | Unit tests, Property 16 | test_non_normal_calcs.py |
| REQ-9.7 | Provide clear interpretation | Unit tests | test_non_normal_calcs.py |
| REQ-10.1 | Generate Q-Q plot | Unit tests | test_non_normal_calcs.py |
| REQ-10.2 | Label axes clearly | UI tests | test_ui_workflows.py |
| REQ-10.3 | Include reference line | Unit tests | test_non_normal_calcs.py |
| REQ-10.4 | Render in application | UI tests | test_ui_workflows.py |
| REQ-11.1 | Box-Cox transformation | Unit tests, Property 18 | test_non_normal_calcs.py |
| REQ-11.2 | Logarithmic transformation | Unit tests, Property 17 | test_non_normal_calcs.py |
| REQ-11.3 | Square root transformation | Unit tests, Property 19 | test_non_normal_calcs.py |
| REQ-11.4 | Automatic lambda optimization | Unit tests | test_non_normal_calcs.py |
| REQ-11.5 | Store original and transformed | Unit tests | test_non_normal_calcs.py |
| REQ-11.6 | Validate data suitability | Unit tests, Property 20 | test_non_normal_calcs.py |
| REQ-12.1 | Re-run normality tests | Unit tests, Property 21 | test_non_normal_calcs.py |
| REQ-12.2 | Display both results | UI tests | test_ui_workflows.py |
| REQ-12.3 | Indicate when parametric OK | Unit tests | test_non_normal_calcs.py |
| REQ-12.4 | Recommend non-parametric if needed | Unit tests | test_non_normal_calcs.py |
| REQ-13.1 | Log back-transformation | Unit tests, Property 17 | test_non_normal_calcs.py |
| REQ-13.2 | Box-Cox back-transformation | Unit tests, Property 18 | test_non_normal_calcs.py |
| REQ-13.3 | Square root back-transformation | Unit tests, Property 19 | test_non_normal_calcs.py |
| REQ-13.4 | Display both transformed and original | UI tests | test_ui_workflows.py |
| REQ-13.5 | Label units clearly | UI tests | test_ui_workflows.py |
| REQ-14.1 | Offer Wilks' method | Unit tests | test_non_normal_calcs.py |
| REQ-14.2 | Use min/max as limits | Unit tests, Property 22 | test_non_normal_calcs.py |
| REQ-14.3 | Indicate non-parametric use | UI tests | test_ui_workflows.py |
| REQ-14.4 | Explain limitations | UI tests | test_ui_workflows.py |

#### 8.1.4 Reliability Requirements (REQ-15, REQ-16)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-15.1 | Chi-squared distribution | Unit tests, Property 23 | test_reliability_calcs.py |
| REQ-15.2 | Duration formula | Unit tests, Property 23 | test_reliability_calcs.py |
| REQ-15.3 | Display test duration | UI tests | test_ui_workflows.py |
| REQ-15.4 | Validate r=0 | Unit tests | test_reliability_calcs.py |
| REQ-16.1 | Arrhenius equation | Unit tests, Property 24 | test_reliability_calcs.py |
| REQ-16.2 | Acceleration factor formula | Unit tests, Property 24 | test_reliability_calcs.py |
| REQ-16.3 | Temperature conversion | Unit tests | test_reliability_calcs.py |
| REQ-16.4 | Validate T_test > T_use | Unit tests, Property 25 | test_reliability_calcs.py |
| REQ-16.5 | Display acceleration factor | UI tests | test_ui_workflows.py |

#### 8.1.5 User Interface Requirements (REQ-17, REQ-18, REQ-19)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-17.1 | Four-tab layout | UI tests | test_ui_workflows.py |
| REQ-17.2 | Display appropriate inputs per tab | UI tests | test_ui_workflows.py |
| REQ-17.3 | Maintain state between tabs | UI tests | test_ui_workflows.py |
| REQ-17.4 | Indicate active tab | UI tests | test_ui_workflows.py |
| REQ-18.1 | Provide tooltips | UI tests | test_ui_workflows.py |
| REQ-18.2 | Display on hover | UI tests | test_ui_workflows.py |
| REQ-18.3 | Help section at top | UI tests | test_ui_workflows.py |
| REQ-18.4 | Use clear language | Manual review | N/A |
| REQ-18.5 | Display % symbol | UI tests | test_ui_workflows.py |
| REQ-19.1 | Restrict percentage ranges | Unit tests, Property 5 | test_attribute_calcs.py |
| REQ-19.2 | Validate positive integers | Unit tests | test_variables_calcs.py |
| REQ-19.3 | Validate std dev > 0 | Unit tests, Property 12 | test_variables_calcs.py |
| REQ-19.4 | Display error messages | UI tests | test_ui_workflows.py |
| REQ-19.5 | Prevent invalid calculation | UI tests | test_ui_workflows.py |


#### 8.1.6 Reporting Requirements (REQ-20, REQ-21, REQ-22)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-20.1 | Provide PDF generation button | UI tests | test_ui_workflows.py |
| REQ-20.2 | Include date and time | Unit tests | test_reports.py |
| REQ-20.3 | Include all inputs | Unit tests | test_reports.py |
| REQ-20.4 | Include all results | Unit tests | test_reports.py |
| REQ-20.5 | Include statistical method | Unit tests | test_reports.py |
| REQ-20.6 | Include validation hash | Unit tests | test_reports.py |
| REQ-21.1 | Calculate SHA-256 hash | Unit tests, Property 26 | test_validation.py |
| REQ-21.2 | Display current hash | Unit tests | test_reports.py |
| REQ-21.3 | Compare against validated hash | Unit tests, Property 27 | test_validation.py |
| REQ-21.4 | Display "VALIDATED STATE: YES" | Unit tests | test_reports.py |
| REQ-21.5 | Display "VALIDATED STATE: NO" | Unit tests | test_reports.py |
| REQ-21.6 | Store validated hash securely | Unit tests | test_config.py |
| REQ-22.1 | Generate certificate after tests | Integration test | test_integration.py |
| REQ-22.2 | Include test execution date | Unit tests | test_reports.py |
| REQ-22.3 | Include tester name | Unit tests | test_reports.py |
| REQ-22.4 | Include system information | Unit tests | test_reports.py |
| REQ-22.5 | List all URS requirements | Unit tests | test_reports.py |
| REQ-22.6 | Display PASS/FAIL per requirement | Unit tests | test_reports.py |
| REQ-22.7 | Include validated hash | Unit tests | test_reports.py |

#### 8.1.7 Validation Requirements (REQ-23, REQ-24, REQ-25)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-23.1 | Use hash-based lockfile | IQ check | check_environment.py |
| REQ-23.2 | Verify locked versions | IQ check | check_environment.py |
| REQ-23.3 | Environment check script | IQ check | check_environment.py |
| REQ-23.4 | Display version mismatch errors | IQ check | check_environment.py |
| REQ-24.1 | Pytest test suite | All OQ tests | tests/* |
| REQ-24.2 | Mark tests with URS IDs | All OQ tests | tests/* |
| REQ-24.3 | Verify against known values | Unit tests | tests/* |
| REQ-24.4 | Report URS pass/fail | Integration test | test_integration.py |
| REQ-24.5 | Require 100% pass rate | Integration test | test_integration.py |
| REQ-25.1 | Automated UI tests | PQ tests | test_ui_workflows.py |
| REQ-25.2 | Simulate user workflows | PQ tests | test_ui_workflows.py |
| REQ-25.3 | Verify results display | PQ tests | test_ui_workflows.py |
| REQ-25.4 | Verify error messages | PQ tests | test_ui_workflows.py |
| REQ-25.5 | End-to-end tests for all modules | PQ tests | test_ui_workflows.py |

#### 8.1.8 System Requirements (REQ-26, REQ-27, REQ-28)

| Requirement | Description | Test Coverage | Test Files |
|-------------|-------------|---------------|------------|
| REQ-26.1 | Log calculation executions | Unit tests, Property 29 | test_logger.py |
| REQ-26.2 | Log validation checks | Unit tests, Property 30 | test_logger.py |
| REQ-26.3 | Log report generation | Unit tests | test_logger.py |
| REQ-26.4 | Log errors and exceptions | Unit tests | test_logger.py |
| REQ-26.5 | Structured log format | Unit tests | test_logger.py |
| REQ-26.6 | Configurable log level | Unit tests | test_logger.py |
| REQ-27.1 | Use Pydantic Settings | Unit tests | test_config.py |
| REQ-27.2 | Support configuration parameters | Unit tests, Property 28 | test_config.py |
| REQ-27.3 | Provide default values | Unit tests | test_config.py |
| REQ-27.4 | Validate configuration | Unit tests, Property 28 | test_config.py |
| REQ-27.5 | Document configuration | Manual review | N/A |
| REQ-28.1 | Modular architecture | Code review | N/A |
| REQ-28.2 | Clear interfaces | Code review | N/A |
| REQ-28.3 | Plugin-like structure | Code review | N/A |
| REQ-28.4 | Document extension process | Manual review | DEVELOPER_GUIDE.md |
| REQ-28.5 | Consistent patterns | Code review | N/A |

### 8.2 Test Coverage Summary

**Total Requirements:** 28 major requirements, 100+ acceptance criteria

**Test Coverage:**
- **Unit Tests:** 50+ test functions covering specific examples
- **Property Tests:** 30 properties covering universal correctness
- **Integration Tests:** 10+ end-to-end workflow tests
- **UI Tests:** 15+ user interaction scenarios
- **Total Test Cases:** 100+ automated tests

**Coverage Metrics:**
- Code coverage target: > 85%
- Requirement coverage: 100% (all requirements have tests)
- Property test iterations: ≥ 100 per property

---

## 9. Validation Maintenance

### 9.1 Revalidation Triggers

Revalidation is required when:

1. **Code Changes:**
   - Any modification to calculation modules
   - Changes to validation logic
   - Updates to data models affecting calculations

2. **Dependency Updates:**
   - Major version updates to scipy, numpy, or other calculation libraries
   - Python version upgrade

3. **Configuration Changes:**
   - Changes to validated hash
   - Modifications to calculation parameters

4. **Regulatory Requirements:**
   - New regulatory guidance
   - Audit findings requiring revalidation

### 9.2 Revalidation Process

**Partial Revalidation (for minor changes):**
1. Run affected test modules
2. Verify no regression in other modules
3. Update validated hash if calculation code changed
4. Generate new validation certificate
5. Document changes in validation log

**Full Revalidation (for major changes):**
1. Execute complete IQ/OQ/PQ protocol
2. Run all test suites
3. Generate new validation certificate
4. Update all validation documentation
5. Obtain new approval signatures

### 9.3 Validation Change Control

**Change Control Process:**
1. Document proposed change
2. Assess impact on validation status
3. Determine revalidation scope (partial/full)
4. Execute revalidation tests
5. Update validated hash if needed
6. Generate new certificate
7. Update validation records

### 9.4 Validated Hash Update Procedure

**Purpose:** The validated hash ensures the calculation engine has not been modified since validation. This procedure documents how to update the validated hash after successful validation testing.

**When to Update:**
- After initial validation (all tests pass)
- After revalidation following code changes
- After dependency updates that affect calculations

**Update Procedure:**

1. **Generate Validation Certificate:**
   ```bash
   uv run python scripts/generate_validation_certificate.py
   ```
   
   This script will:
   - Run the complete test suite
   - Calculate the SHA-256 hash of all calculation modules
   - Generate a validation certificate PDF
   - Display the validated hash in the output

2. **Verify Test Results:**
   - Review the console output to confirm all tests passed
   - Check that no tests failed or were skipped
   - Note the validated hash displayed in the output
   - Example output:
     ```
     Overall Status: PASSED
     Validated Hash: a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e
     ```

3. **Review Validation Certificate:**
   - Open the generated PDF in `reports/validation_certificate_YYYYMMDD_HHMMSS.pdf`
   - Verify all URS requirements show PASS status
   - Confirm system information is correct
   - Note the validated hash in the certificate

4. **Update Configuration File:**
   - Copy the validated hash from the certificate or console output
   - Open `.env.example` file
   - Update the `VALIDATED_HASH` value:
     ```bash
     VALIDATED_HASH="a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e"
     ```
   - Add a comment with the validation date:
     ```bash
     # This hash was generated from validation certificate on YYYY-MM-DD
     # All XXX tests passed - calculation engine is validated
     ```

5. **Update Environment File:**
   - If using a `.env` file (not tracked in version control):
     ```bash
     cp .env.example .env
     ```
   - Or manually update the `VALIDATED_HASH` in your existing `.env` file

6. **Verify Hash Configuration:**
   - Run the application
   - Generate a calculation report
   - Verify the report shows "VALIDATED STATE: YES"
   - If it shows "NO", check that the hash in `.env` matches the certificate

7. **Document the Update:**
   - Record the validation date in validation records
   - Store the validation certificate in quality records
   - Update the validated hash history log
   - Note any changes that triggered revalidation

**Hash Calculation Details:**

The validated hash is a combined SHA-256 hash of all calculation module files:
- `src/sample_size_estimator/calculations/__init__.py`
- `src/sample_size_estimator/calculations/attribute_calcs.py`
- `src/sample_size_estimator/calculations/variables_calcs.py`
- `src/sample_size_estimator/calculations/non_normal_calcs.py`
- `src/sample_size_estimator/calculations/reliability_calcs.py`

Any change to these files will result in a different hash, triggering the "UNVERIFIED CHANGE" warning in reports.

**Troubleshooting:**

| Issue | Solution |
|-------|----------|
| Hash mismatch after update | Verify you copied the complete hash string (64 characters) |
| "NO - No validated hash configured" | Check that VALIDATED_HASH is not empty in .env file |
| Tests fail during certificate generation | Fix failing tests before updating hash |
| Certificate not generated | Check write permissions in reports/ directory |

### 9.5 Validation Records

**Maintain the following records:**
- Initial validation certificate
- All revalidation certificates
- Test execution logs
- Change control documentation
- Validated hash history
- Approval signatures

**Retention Period:** Per regulatory requirements (typically 7+ years)

### 9.6 Periodic Review

**Annual Review:**
- Verify validated hash matches current code
- Review test suite for completeness
- Check for new regulatory requirements
- Update validation protocol if needed
- Document review in quality records

---

## 10. Appendices

### Appendix A: Validation Checklist

**Pre-Validation Checklist:**
- [ ] All code development complete
- [ ] All tests written and passing
- [ ] Code reviewed and approved
- [ ] Documentation complete
- [ ] Environment prepared for validation

**IQ Checklist:**
- [ ] Python version verified (≥ 3.11)
- [ ] All dependencies installed
- [ ] Dependency versions verified
- [ ] Project structure complete
- [ ] Lock file present
- [ ] IQ results documented

**OQ Checklist:**
- [ ] All unit tests pass
- [ ] All property tests pass (≥ 100 iterations)
- [ ] All edge case tests pass
- [ ] All error handling tests pass
- [ ] Code coverage > 85%
- [ ] No critical linting errors
- [ ] OQ results documented

**PQ Checklist:**
- [ ] All UI tests pass
- [ ] Reports generate successfully
- [ ] Error messages verified
- [ ] All four tabs tested
- [ ] Navigation tested
- [ ] PQ results documented

**Certificate Generation Checklist:**
- [ ] All tests passed
- [ ] System information collected
- [ ] Validated hash calculated
- [ ] Certificate PDF generated
- [ ] Certificate reviewed
- [ ] Signatures obtained
- [ ] Hash updated in configuration


### Appendix B: Test Execution Commands

**Installation Qualification:**
```bash
# Run environment check
uv run python scripts/check_environment.py
```

**Operational Qualification:**
```bash
# Run all OQ tests
uv run pytest -q --tb=short

# Run specific module tests
uv run pytest tests/test_attribute_calcs.py -q
uv run pytest tests/test_variables_calcs.py -q
uv run pytest tests/test_non_normal_calcs.py -q
uv run pytest tests/test_reliability_calcs.py -q

# Run with coverage
uv run pytest --cov=src/sample_size_estimator --cov-report=html -q

# Run property tests only
uv run pytest -m property -q

# Run tests for specific URS requirement
uv run pytest -m urs -k "URS-FUNC_A-02" -v
```

**Performance Qualification:**
```bash
# Run UI tests
uv run pytest tests/test_ui_workflows.py -v

# Run integration tests
uv run pytest tests/test_integration.py -v

# Run UI tests with Playwright
uv run pytest tests/test_ui_playwright_*.py -v

# Start application for manual exploration (optional)
uv run streamlit run src/sample_size_estimator/app.py
```

**Validation Certificate:**
```bash
# Generate validation certificate
uv run python scripts/generate_validation_certificate.py
```

**Code Quality Checks:**
```bash
# Run linter
uv run ruff check src/

# Run type checker
uvx mypy src/sample_size_estimator
```

### Appendix C: Known Statistical Reference Values

These values are used to verify calculation correctness:

**Attribute Calculations (Success Run Theorem):**
- C=95%, R=90% → n=29
- C=90%, R=95% → n=45
- C=99%, R=90% → n=44
- C=95%, R=95% → n=59

**Attribute Calculations (Binomial):**
- C=95%, R=90%, c=1 → n=46
- C=95%, R=90%, c=2 → n=61
- C=95%, R=90%, c=3 → n=76
- C=90%, R=90%, c=1 → n=38

**Variables Calculations (Ppk):**
- Mean=10, Std=1, LSL=7, USL=13 → Ppk=1.0
- Mean=10, Std=0.5, LSL=8, USL=12 → Ppk≈1.33
- Mean=100, Std=5, LSL=85, USL=115 → Ppk=1.0

**Reliability Calculations:**
- C=95%, r=0 → χ²(0.95, 2) = 5.991
- C=90%, r=0 → χ²(0.90, 2) = 4.605
- Ea=0.7eV, T_use=298K, T_test=358K → AF≈10

### Appendix D: Validation Roles and Responsibilities

| Role | Responsibilities | Qualifications |
|------|------------------|----------------|
| **Validation Lead** | - Overall validation planning<br>- Coordinate validation activities<br>- Review and approve validation documents<br>- Ensure regulatory compliance | - Experience with software validation<br>- Knowledge of regulatory requirements<br>- Project management skills |
| **Test Engineer** | - Execute test protocols<br>- Document test results<br>- Report issues and deviations<br>- Maintain test environment | - Software testing experience<br>- Familiarity with Python and pytest<br>- Attention to detail |
| **Quality Assurance** | - Review validation documentation<br>- Verify compliance with procedures<br>- Approve validation completion<br>- Maintain quality records | - QA experience in regulated industry<br>- Knowledge of quality systems<br>- Audit experience |
| **Subject Matter Expert** | - Verify statistical correctness<br>- Review calculation methods<br>- Approve test cases<br>- Interpret results | - Advanced statistics knowledge<br>- Medical device experience<br>- Regulatory expertise |
| **IT Administrator** | - Manage system installation<br>- Configure environment<br>- Maintain infrastructure<br>- Support validation activities | - System administration experience<br>- Python environment management<br>- Security knowledge |
| **Developer** | - Implement fixes if needed<br>- Support test execution<br>- Explain technical details<br>- Update documentation | - Python development experience<br>- Knowledge of application architecture<br>- Testing experience |

### Appendix E: Validation Terminology

**Acceptance Criteria:** Predetermined requirements that must be met for validation to be considered successful.

**Calculation Engine:** The core calculation modules (attribute_calcs.py, variables_calcs.py, non_normal_calcs.py, reliability_calcs.py) that perform statistical computations.

**Hash Verification:** Process of calculating and comparing SHA-256 hashes to ensure code integrity.

**Installation Qualification (IQ):** Documented verification that the software and all dependencies are correctly installed.

**Operational Qualification (OQ):** Documented verification that the system performs according to specifications across all anticipated operating ranges.

**Performance Qualification (PQ):** Documented verification that the system consistently performs according to specifications under actual or simulated use conditions.

**Property-Based Testing:** Testing approach that verifies universal properties hold across all valid inputs using randomized test data generation.

**Traceability Matrix:** Document linking requirements to test cases and test results.

**Unit Testing:** Testing individual functions or components in isolation.

**URS (User Requirements Specification):** Document defining what the system must do from the user's perspective.

**Validated Hash:** SHA-256 hash value of the calculation engine after successful validation, used to verify code integrity.

**Validation Certificate:** PDF document generated after successful validation containing test results, system information, and validated hash.

### Appendix F: Validation Protocol Approval

**Document Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Validation Lead | _________________ | _________________ | _______ |
| Quality Assurance | _________________ | _________________ | _______ |
| Subject Matter Expert | _________________ | _________________ | _______ |

**Revision History:**

| Version | Date | Author | Description of Changes |
|---------|------|--------|------------------------|
| 1.0 | 2024 | Validation Team | Initial validation protocol |

---

## Document Control

**Document Number:** VAL-PROTO-SSE-001  
**Effective Date:** Upon approval  
**Review Frequency:** Annually or upon significant changes  
**Next Review Date:** [Date + 1 year]

**Distribution List:**
- Validation Lead
- Quality Assurance Manager
- Regulatory Affairs
- IT Department
- Project Team

---

**END OF VALIDATION PROTOCOL**

