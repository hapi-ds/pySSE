# Sample Size Estimator - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Tab 1: Attribute (Binomial) Analysis](#tab-1-attribute-binomial-analysis)
4. [Tab 2: Variables (Normal) Analysis](#tab-2-variables-normal-analysis)
5. [Tab 3: Non-Normal Distribution Analysis](#tab-3-non-normal-distribution-analysis)
6. [Tab 4: Reliability Life Testing](#tab-4-reliability-life-testing)
7. [Understanding Reports](#understanding-reports)
8. [Validation State and Hash Verification](#validation-state-and-hash-verification)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

The Sample Size Estimator is a statistical tool designed for medical device validation and quality management. It helps you determine statistically valid sample sizes and analyze measurement data for design verification and process validation activities.

### When to Use This Tool

- **Design Verification**: Determine how many units to test to demonstrate reliability
- **Process Validation**: Calculate sample sizes for process capability studies
- **Non-Normal Data**: Transform and analyze data that doesn't follow a normal distribution
- **Reliability Testing**: Plan time-dependent reliability demonstrations

### Key Features

- Four specialized analysis modules for different statistical scenarios
- Built-in validation state tracking for regulatory compliance
- PDF report generation with complete calculation documentation
- Comprehensive input validation and error checking

---

## Getting Started

### Launching the Application

1. Open your terminal or command prompt
2. Navigate to the project directory
3. Run: `uv run streamlit run src/sample_size_estimator/app.py`
4. The application will open in your web browser

### Interface Overview

The application has four tabs at the top:
- **Attribute (Binomial)**: For pass/fail testing
- **Variables (Normal)**: For continuous measurements
- **Non-Normal Distribution**: For data that isn't normally distributed
- **Reliability**: For time-dependent reliability testing

Each tab has:
- Input fields with tooltips (hover over labels for help)
- A Calculate button to run the analysis
- Results display area
- Download Report button (appears after calculation)

---

## Tab 1: Attribute (Binomial) Analysis

### Purpose

Use this tab when you have **binary outcomes** (pass/fail, good/bad, conforming/non-conforming) and need to determine how many units to test.

### When to Use

- Acceptance testing with pass/fail criteria
- Demonstrating reliability with zero or few failures
- Planning sampling plans for lot acceptance

### Input Parameters

**Confidence Level (%)**: The statistical confidence you want in your result
- Typical value: 95%
- Range: 0.01 to 99.99
- Higher confidence requires larger sample sizes

**Reliability (%)**: The minimum acceptable proportion of conforming units
- Typical value: 90% or 95%
- Range: 0.01 to 99.99
- Higher reliability requires larger sample sizes

**Allowable Failures (c)**: Maximum number of failures permitted in the sample
- Leave empty for sensitivity analysis (shows c=0, 1, 2, 3)
- Enter 0 for zero-failure demonstration
- Enter a specific number (1, 2, 3, etc.) for acceptance sampling plans

### Example 1: Zero-Failure Demonstration

**Scenario**: You want to demonstrate 90% reliability with 95% confidence, allowing no failures.

**Inputs**:
- Confidence Level: 95
- Reliability: 90
- Allowable Failures: 0

**Result**: Sample Size = 29 units

**Interpretation**: Test 29 units. If all pass (zero failures), you have demonstrated 90% reliability with 95% confidence.

### Example 2: Sensitivity Analysis

**Scenario**: You want to see how sample size changes with different failure allowances.

**Inputs**:
- Confidence Level: 95
- Reliability: 90
- Allowable Failures: (leave empty)

**Result**: 
| Allowable Failures | Sample Size |
|--------------------|-------------|
| 0                  | 29          |
| 1                  | 47          |
| 2                  | 64          |
| 3                  | 80          |

**Interpretation**: If you allow 1 failure, you need 47 units. If you allow 2 failures, you need 64 units, etc.

### Example 3: Acceptance Sampling

**Scenario**: You want a sampling plan that allows up to 2 failures.

**Inputs**:
- Confidence Level: 95
- Reliability: 95
- Allowable Failures: 2

**Result**: Sample Size = 93 units

**Interpretation**: Test 93 units. If 2 or fewer fail, you have demonstrated 95% reliability with 95% confidence.

---

## Tab 2: Variables (Normal) Analysis

### Purpose

Use this tab when you have **continuous measurements** (dimensions, weights, temperatures) that follow a normal distribution and need to calculate tolerance limits or assess process capability.

### When to Use

- Process capability studies
- Tolerance limit calculations
- Comparing process performance to specifications
- Demonstrating that a process meets requirements

### Input Parameters

**Confidence Level (%)**: Statistical confidence in the tolerance limits
- Typical value: 95%
- Range: 0.01 to 99.99

**Reliability (%)**: Proportion of population contained within tolerance limits
- Typical value: 90% or 95%
- Range: 0.01 to 99.99

**Sample Size (n)**: Number of measurements in your sample
- Must be greater than 1
- Larger samples give tighter tolerance limits

**Sample Mean (μ)**: Average of your measurements
- Enter the calculated mean from your data

**Sample Standard Deviation (σ)**: Spread of your measurements
- Must be greater than 0
- Enter the calculated standard deviation from your data

**Sided**: Choose one-sided or two-sided limits
- **Two-sided**: Use when you have both upper and lower specification limits
- **One-sided**: Use when you only care about one direction (e.g., only maximum)

**Lower Specification Limit (LSL)**: Minimum acceptable value (optional)
- Leave empty if not applicable
- Must be less than USL if both are provided

**Upper Specification Limit (USL)**: Maximum acceptable value (optional)
- Leave empty if not applicable
- Must be greater than LSL if both are provided

### Example 1: Basic Tolerance Limits

**Scenario**: You measured 30 parts. Mean = 10.0 mm, Std Dev = 0.5 mm. Calculate 95% confidence, 90% reliability tolerance limits.

**Inputs**:
- Confidence Level: 95
- Reliability: 90
- Sample Size: 30
- Sample Mean: 10.0
- Sample Standard Deviation: 0.5
- Sided: Two-sided
- LSL: (leave empty)
- USL: (leave empty)

**Results**:
- Tolerance Factor (k): 2.140
- Lower Tolerance Limit: 8.93 mm
- Upper Tolerance Limit: 11.07 mm

**Interpretation**: With 95% confidence, at least 90% of the population falls between 8.93 and 11.07 mm.

### Example 2: Process Capability Assessment

**Scenario**: Same data as above, but specifications are LSL = 8.5 mm, USL = 11.5 mm.

**Inputs**:
- (Same as Example 1)
- LSL: 8.5
- USL: 11.5

**Results**:
- Tolerance Factor (k): 2.140
- Lower Tolerance Limit: 8.93 mm
- Upper Tolerance Limit: 11.07 mm
- Ppk: 1.00
- Comparison: **PASS**
- Margin to LSL: 0.43 mm
- Margin to USL: 0.43 mm

**Interpretation**: 
- The process is capable (Ppk = 1.00)
- Tolerance limits fall within specifications (PASS)
- There's a 0.43 mm margin on both sides

### Example 3: Process Fails Specification

**Scenario**: Mean = 10.0 mm, Std Dev = 1.0 mm, n = 30, LSL = 8.5 mm, USL = 11.5 mm.

**Inputs**:
- Confidence Level: 95
- Reliability: 90
- Sample Size: 30
- Sample Mean: 10.0
- Sample Standard Deviation: 1.0
- Sided: Two-sided
- LSL: 8.5
- USL: 11.5

**Results**:
- Tolerance Factor (k): 2.140
- Lower Tolerance Limit: 7.86 mm
- Upper Tolerance Limit: 12.14 mm
- Ppk: 0.50
- Comparison: **FAIL**
- Margin to LSL: -0.64 mm
- Margin to USL: -0.64 mm

**Interpretation**: 
- The process is not capable (Ppk = 0.50 < 1.0)
- Tolerance limits exceed specifications (FAIL)
- Negative margins indicate the process is too variable

---

## Tab 3: Non-Normal Distribution Analysis

### Purpose

Use this tab when your data **does not follow a normal distribution** and you need to either transform it to normality or use non-parametric methods.

### When to Use

- Data fails normality tests
- Skewed distributions (e.g., cycle times, failure rates)
- Data with outliers
- When parametric methods aren't appropriate

### Workflow

1. **Enter your data** (comma-separated values or one per line)
2. **Check for outliers** (optional but recommended)
3. **Test for normality** to confirm data is non-normal
4. **View Q-Q plot** for visual assessment
5. **Apply transformation** (Box-Cox, Log, or Square Root)
6. **Verify normality** of transformed data
7. **Calculate tolerance limits** on transformed data
8. **View back-transformed results** in original units

### Input Parameters

**Raw Data**: Your measurement values
- Enter as comma-separated: `1.2, 3.4, 5.6, 7.8`
- Or one per line
- Minimum 3 values required

**Transformation Method**: Choose based on your data
- **Box-Cox**: Automatic optimization (best for most cases)
- **Log**: For right-skewed data (requires all positive values)
- **Square Root**: For count data or mild skewness (requires non-negative values)

**Confidence Level (%)**: For tolerance limit calculation
- Typical value: 95%

**Reliability (%)**: For tolerance limit calculation
- Typical value: 90%

### Example 1: Right-Skewed Data with Log Transformation

**Scenario**: Cycle time data that's right-skewed.

**Data**: `2.1, 2.3, 2.5, 2.8, 3.1, 3.5, 4.2, 5.8, 7.3, 9.1`

**Steps**:

1. **Enter data** in the text area

2. **Click "Detect Outliers"**
   - Result: 2 outliers detected (7.3, 9.1)
   - Interpretation: High values are flagged but may be legitimate

3. **Click "Test Normality"**
   - Shapiro-Wilk p-value: 0.023 (< 0.05)
   - Anderson-Darling: Fails at 5% level
   - Interpretation: Data is NOT normally distributed

4. **View Q-Q Plot**
   - Points deviate from reference line at upper end
   - Confirms right skewness

5. **Select "Log" transformation and click "Apply Transformation"**
   - Transformed data normality: p-value = 0.342 (> 0.05)
   - Interpretation: Transformation successful!

6. **Enter confidence (95) and reliability (90), click "Calculate Tolerance Limits"**
   - Transformed limits: [0.65, 2.45] (in log scale)
   - **Back-transformed limits: [1.92, 11.59]** (in original units)
   - Interpretation: Use the back-transformed limits for reporting

### Example 2: Box-Cox Transformation

**Scenario**: Unknown distribution type, let Box-Cox optimize.

**Data**: `5, 7, 8, 9, 10, 12, 15, 18, 22, 28, 35`

**Steps**:

1. Enter data and test normality (fails)

2. Select "Box-Cox" transformation
   - Optimal lambda: 0.23
   - Post-transformation p-value: 0.156 (> 0.05)
   - Success!

3. Calculate tolerance limits
   - Back-transformed limits provided automatically

**Interpretation**: Box-Cox found the optimal transformation (lambda = 0.23) to achieve normality.

### Example 3: Non-Parametric Fallback (Wilks' Method)

**Scenario**: All transformations fail to achieve normality.

**Steps**:

1. Try Box-Cox, Log, and Square Root transformations
2. All still fail normality tests (p < 0.05)

3. **Click "Use Non-Parametric Method (Wilks)"**
   - Lower limit: Minimum of dataset
   - Upper limit: Maximum of dataset
   - Warning: Conservative method, requires larger sample sizes

**Interpretation**: When transformations fail, Wilks' method provides distribution-free limits using the sample extremes.

---

## Tab 4: Reliability Life Testing

### Purpose

Use this tab for **time-dependent reliability testing**, including zero-failure demonstrations and accelerated life testing.

### When to Use

- Planning reliability demonstration tests
- Calculating test duration for zero-failure tests
- Accelerated life testing with temperature stress
- Arrhenius model applications

### Input Parameters

**Confidence Level (%)**: Statistical confidence in the result
- Typical value: 90% or 95%

**Reliability (%)**: Target reliability to demonstrate
- Typical value: 90% or 95%

**Number of Failures (r)**: Expected failures during test
- Typically 0 for zero-failure demonstration
- Can be > 0 for other test plans

**Activation Energy (Ea)**: For accelerated testing (optional)
- In electron volts (eV)
- Typical range: 0.3 to 1.5 eV
- Leave empty if not using acceleration

**Use Temperature (T_use)**: Normal operating temperature (optional)
- In Kelvin (K)
- Convert from Celsius: K = °C + 273.15
- Required if using acceleration factor

**Test Temperature (T_test)**: Elevated test temperature (optional)
- In Kelvin (K)
- Must be greater than use temperature
- Required if using acceleration factor

### Example 1: Zero-Failure Demonstration

**Scenario**: Demonstrate 90% reliability with 90% confidence, zero failures allowed.

**Inputs**:
- Confidence Level: 90
- Reliability: 90
- Number of Failures: 0
- (Leave acceleration parameters empty)

**Result**:
- Test Duration: 4.61 unit-hours
- Method: Chi-squared zero-failure demonstration

**Interpretation**: 
- Test 1 unit for 4.61 hours, OR
- Test 2 units for 2.3 hours each, OR
- Test 5 units for 0.92 hours each
- If zero failures occur, reliability is demonstrated

### Example 2: Accelerated Life Testing

**Scenario**: Same as above, but use elevated temperature to reduce test time.

**Inputs**:
- Confidence Level: 90
- Reliability: 90
- Number of Failures: 0
- Activation Energy: 0.7 (eV)
- Use Temperature: 298 (K) [25°C]
- Test Temperature: 358 (K) [85°C]

**Results**:
- Test Duration: 4.61 unit-hours
- Acceleration Factor: 54.6
- Method: Chi-squared zero-failure demonstration with Arrhenius acceleration

**Interpretation**:
- At elevated temperature (85°C), test time is reduced by factor of 54.6
- Equivalent test time at use temperature: 4.61 / 54.6 = 0.084 hours
- Test 1 unit for 0.084 hours at 85°C to demonstrate reliability at 25°C

### Example 3: Temperature Conversion

**Converting Celsius to Kelvin**:
- 25°C = 25 + 273.15 = 298.15 K
- 85°C = 85 + 273.15 = 358.15 K
- 125°C = 125 + 273.15 = 398.15 K

**Common Activation Energies**:
- Electronic components: 0.3 - 0.7 eV
- Mechanical wear: 0.5 - 1.0 eV
- Chemical reactions: 0.7 - 1.5 eV

---

## Understanding Reports

### Generating a Report

After completing any calculation:

1. Review your results on screen
2. Click the **"Download Calculation Report"** button
3. A PDF file will be generated and downloaded
4. The report is saved in the `reports/` directory

### Report Contents

Every calculation report includes:

#### 1. Report Information
- Date and time of calculation
- Analysis module used (Attribute, Variables, etc.)
- Application version

#### 2. Input Parameters
- All values you entered
- Clearly labeled with parameter names
- Formatted for easy review

#### 3. Calculated Results
- All output values
- Formulas used (referenced)
- Statistical method applied

#### 4. Validation Information
- **Engine Hash**: SHA-256 hash of the calculation engine
- **Validation Status**: VALIDATED or NOT VALIDATED
- Ensures calculation integrity

### Report Interpretation

**Example Report Section**:

```
Calculated Results
------------------
Sample Size:              29
Allowable Failures:       0
Method:                   Success Run Theorem
Confidence Level:         95%
Reliability:              90%

Validation Information
----------------------
Engine Hash:              a3f5b2c8d1e9f4a7b6c3d2e1f8a9b0c7...
Validation Status:        VALIDATED
```

**What This Means**:
- You need to test 29 units with zero failures
- The calculation used the Success Run Theorem
- The calculation engine is in a validated state (trustworthy)

### Using Reports for Compliance

Reports are designed for regulatory compliance:

- **Traceability**: All inputs and outputs documented
- **Reproducibility**: Anyone can verify the calculation
- **Validation State**: Hash verification ensures integrity
- **Audit Trail**: Timestamp and version tracking

**Best Practices**:
- Generate a report for every calculation used in validation
- Store reports with your validation documentation
- Include reports in Design History Files (DHF)
- Reference report hash in validation protocols

---

## Validation State and Hash Verification

### What is Validation State?

The validation state indicates whether the calculation engine has been verified and remains unchanged since validation.

### How It Works

1. **Hash Calculation**: The system calculates a SHA-256 hash (fingerprint) of the calculation engine code
2. **Comparison**: This hash is compared to a stored "validated hash"
3. **Status Display**: 
   - **VALIDATED**: Hashes match - calculation engine is verified
   - **NOT VALIDATED**: Hashes don't match - code has changed

### Understanding Hash Values

**Example Hash**:
```
a3f5b2c8d1e9f4a7b6c3d2e1f8a9b0c7d4e5f6a1b2c3d4e5f6a7b8c9d0e1f2a3
```

- 64-character hexadecimal string
- Unique fingerprint of the calculation code
- Any code change produces a completely different hash

### Validation State Scenarios

#### Scenario 1: VALIDATED
```
Engine Hash:        a3f5b2c8d1e9f4a7...
Validated Hash:     a3f5b2c8d1e9f4a7...
Status:             VALIDATED
```
**Meaning**: The calculation engine matches the validated version. Results are trustworthy for regulatory use.

#### Scenario 2: NOT VALIDATED - Unverified Change
```
Engine Hash:        b4g6c3d9e2f0g5b8...
Validated Hash:     a3f5b2c8d1e9f4a7...
Status:             NOT VALIDATED - UNVERIFIED CHANGE
```
**Meaning**: The code has changed since validation. Do not use for regulatory submissions until re-validated.

#### Scenario 3: NOT VALIDATED - No Validated Hash
```
Engine Hash:        a3f5b2c8d1e9f4a7...
Validated Hash:     (none configured)
Status:             NOT VALIDATED - No validated hash configured
```
**Meaning**: No validated hash has been set. System is functional but not validated for regulatory use.

### When to Be Concerned

**🔴 Red Flags**:
- Status shows "NOT VALIDATED - UNVERIFIED CHANGE"
- You're preparing regulatory submissions
- You need validated calculations for compliance

**🟢 Acceptable**:
- Status shows "VALIDATED"
- You're doing exploratory calculations (validation not required)
- You're in development/testing phase

### Maintaining Validation State

**For Quality/Regulatory Users**:

1. **Initial Validation**:
   - Run the complete test suite
   - Generate validation certificate
   - Record the validated hash
   - Configure system with validated hash

2. **Ongoing Use**:
   - Check validation status on every report
   - Only use VALIDATED calculations for submissions
   - Report any "NOT VALIDATED" status to IT/Quality

3. **After Updates**:
   - Re-run validation test suite
   - Generate new validation certificate
   - Update validated hash in configuration
   - Document the change in validation records

**For Administrators**:

1. **Setting Validated Hash**:
   ```bash
   # Run validation test suite
   uv run pytest -q
   
   # Generate validation certificate
   uv run python scripts/generate_validation_certificate.py
   
   # Copy validated hash from certificate
   # Update .env file:
   VALIDATED_HASH=a3f5b2c8d1e9f4a7b6c3d2e1f8a9b0c7...
   ```

2. **Verifying Validation State**:
   - Run a test calculation
   - Generate report
   - Confirm "VALIDATED" status appears

### Hash Verification in Validation Protocols

Include this information in your validation protocol:

```
Validation Hash Verification
-----------------------------
Validated Hash:     a3f5b2c8d1e9f4a7b6c3d2e1f8a9b0c7d4e5f6a1b2c3d4e5f6a7b8c9d0e1f2a3
Validation Date:    2024-01-15
Validated By:       John Smith, Quality Engineer
Test Suite:         All tests passed (100%)
Certificate:        validation_certificate_20240115.pdf

Verification Procedure:
1. Generate calculation report
2. Verify "Engine Hash" matches validated hash above
3. Confirm "Validation Status" shows "VALIDATED"
4. If mismatch, do not use for regulatory submissions
```

---

## Troubleshooting

### Common Errors and Solutions

#### Error: "Value must be between 0 and 100"

**Cause**: Confidence or Reliability entered outside valid range

**Solution**: 
- Enter values between 0.01 and 99.99
- Use percentages, not decimals (95, not 0.95)

#### Error: "Sample standard deviation must be greater than zero"

**Cause**: Entered 0 or negative value for standard deviation

**Solution**:
- Recalculate your standard deviation
- Ensure you're using sample standard deviation (not population)
- Check for data entry errors

#### Error: "Lower specification limit must be less than upper specification limit"

**Cause**: LSL ≥ USL

**Solution**:
- Verify your specification limits
- Check for transposed values
- Ensure LSL < USL

#### Error: "Logarithmic transformation requires all positive values"

**Cause**: Your data contains zero or negative values

**Solution**:
- Use Box-Cox transformation instead (handles zeros better)
- Or use Square Root transformation
- Or add a constant to shift all values positive

#### Error: "Test temperature must be greater than use temperature"

**Cause**: T_test ≤ T_use in acceleration factor calculation

**Solution**:
- Verify temperature values
- Ensure both are in Kelvin (not mixed Celsius/Kelvin)
- Test temperature should be elevated (higher than use)

### Data Entry Tips

**For Attribute Tab**:
- Use whole numbers for Allowable Failures
- Leave Allowable Failures empty to see sensitivity analysis
- Higher confidence/reliability = larger sample size

**For Variables Tab**:
- Calculate mean and standard deviation in Excel first
- Use sample standard deviation (STDEV.S in Excel)
- Ensure sample size matches your actual data count

**For Non-Normal Tab**:
- Enter at least 10 data points for reliable results
- Remove obvious data entry errors before analysis
- Try Box-Cox first - it auto-optimizes

**For Reliability Tab**:
- Convert Celsius to Kelvin: K = °C + 273.15
- Typical activation energies: 0.3 - 1.5 eV
- Test temperature should be 20-60°C above use temperature

### Performance Issues

**Slow Calculations**:
- Large sample sizes (> 1000) may take longer
- Non-normal transformations with large datasets may be slow
- This is normal - wait for completion

**Application Not Responding**:
- Refresh the browser page
- Restart the application
- Check for error messages in terminal

### Getting Help

**Before Contacting Support**:
1. Check this user guide
2. Verify your input values are reasonable
3. Try a simpler example to isolate the issue
4. Note any error messages exactly

**When Contacting Support, Provide**:
- Which tab you're using
- Input values you entered
- Error message (exact text)
- Screenshot if possible
- What you expected to happen

**For Validation Issues**:
- Contact your Quality/IT department
- Provide the validation certificate
- Include the engine hash from your report
- Describe when the issue started

---

## Appendix: Statistical Background

### Attribute Analysis

**Success Run Theorem**: For zero failures, the formula n = ln(1-C)/ln(R) comes from the binomial distribution with p = R and k = 0.

**Binomial Distribution**: For c > 0, we solve for the smallest n where the cumulative probability of 0 to c failures is ≤ (1-C).

### Variables Analysis

**Tolerance Factors**: Statistical multipliers that account for sampling uncertainty. Larger samples give smaller k values (tighter limits).

**Ppk**: Process performance index. Values > 1.33 indicate good capability. Values < 1.0 indicate the process may not meet specifications.

### Non-Normal Analysis

**Normality Tests**: 
- Shapiro-Wilk: Tests if data came from a normal distribution
- Anderson-Darling: More sensitive to tails of distribution
- p-value > 0.05 suggests normality

**Transformations**:
- Box-Cox: Finds optimal power transformation
- Log: Good for right-skewed data
- Square Root: Good for count data

### Reliability Testing

**Chi-Squared Distribution**: Used for zero-failure demonstrations. The test duration is proportional to the chi-squared value.

**Arrhenius Equation**: Models temperature acceleration. Higher temperatures accelerate failure mechanisms, reducing test time.

---

## Quick Reference Card

### Attribute Tab
- **Use for**: Pass/fail testing
- **Key inputs**: Confidence, Reliability, Allowable Failures
- **Output**: Sample size
- **Tip**: Leave failures empty for sensitivity analysis

### Variables Tab
- **Use for**: Continuous measurements
- **Key inputs**: Mean, Std Dev, Sample Size, Spec Limits
- **Output**: Tolerance limits, Ppk, Pass/Fail
- **Tip**: Calculate mean/std dev in Excel first

### Non-Normal Tab
- **Use for**: Non-normal data
- **Key inputs**: Raw data, Transformation method
- **Output**: Transformed limits, Back-transformed limits
- **Tip**: Try Box-Cox first

### Reliability Tab
- **Use for**: Time-dependent testing
- **Key inputs**: Confidence, Reliability, Failures, Temperatures
- **Output**: Test duration, Acceleration factor
- **Tip**: Convert °C to K: add 273.15

### Validation Status
- **VALIDATED**: ✅ Safe for regulatory use
- **NOT VALIDATED**: ⚠️ Do not use for submissions
- **Check**: Every report before using for compliance

---

*For technical support or validation questions, contact your Quality Assurance department.*

*Document Version: 1.0*  
*Last Updated: 2024*
