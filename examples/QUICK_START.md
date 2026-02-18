# Quick Start Guide - Sample Data Examples

This guide provides quick copy-paste examples for testing each module of the Sample Size Estimator.

## Attribute Data (Binomial) Tab

### Example 1: Zero-Failure Demonstration
**Copy these values:**
```
Confidence Level: 95
Reliability: 90
Allowable Failures: 0
```
**Expected Result:** Sample Size = 29

### Example 2: Sensitivity Analysis
**Copy these values:**
```
Confidence Level: 95
Reliability: 90
Allowable Failures: (leave empty)
```
**Expected Result:** Table showing n for c=0,1,2,3

### Example 3: Acceptance Sampling
**Copy these values:**
```
Confidence Level: 95
Reliability: 95
Allowable Failures: 2
```
**Expected Result:** Sample Size = 93

---

## Variables (Normal) Tab

### Example 1: Basic Tolerance Limits
**Copy these values:**
```
Confidence Level: 95
Reliability: 90
Sample Size: 30
Sample Mean: 10.0
Sample Standard Deviation: 0.5
Sided: Two-sided
LSL: (leave empty)
USL: (leave empty)
```
**Expected Results:**
- Tolerance Factor (k) ≈ 2.14
- Lower Tolerance Limit ≈ 8.93
- Upper Tolerance Limit ≈ 11.07

### Example 2: Process Capability
**Copy these values:**
```
Confidence Level: 95
Reliability: 90
Sample Size: 30
Sample Mean: 10.0
Sample Standard Deviation: 0.5
Sided: Two-sided
LSL: 8.5
USL: 11.5
```
**Expected Results:**
- Ppk ≈ 1.67
- Result: PASS
- Margin to LSL ≈ 0.43
- Margin to USL ≈ 0.43

---

## Non-Normal Distribution Tab

### Example 1: Normal Data (Baseline)
**Copy this data:**
```
9.8,10.2,9.9,10.1,10.0,9.7,10.3,10.1,9.9,10.2,10.0,9.8,10.1,10.0,9.9,10.2,10.1,9.8,10.0,10.1,9.9,10.0,10.2,9.8,10.1,10.0,9.9,10.1,10.0,9.8
```
**Steps:**
1. Paste data
2. Click "Test Normality"
3. Should show p-value > 0.05 (normal)

### Example 2: Outlier Detection
**Copy this data:**
```
9.8,10.2,9.9,10.1,10.0,9.7,10.3,10.1,9.9,10.2,10.0,9.8,10.1,10.0,9.9,10.2,10.1,9.8,10.0,10.1,9.9,10.0,10.2,9.8,10.1,10.0,9.9,10.1,10.0,9.8,25.5,10.1,9.9,10.0,10.2,9.8,10.1,10.0,0.2,10.1
```
**Steps:**
1. Paste data
2. Click "Detect Outliers"
3. Should detect 2 outliers: 0.2 and 25.5

### Example 3: Log Transformation
**Copy this data:**
```
1.2,1.5,1.8,2.1,2.3,2.5,2.8,3.1,3.5,4.2,4.8,5.5,6.2,7.1,8.5,9.8,11.2,13.5,16.8,21.3,1.4,1.7,2.0,2.4,2.7,3.0,3.3,3.8,4.5,5.2,6.0,7.5,9.2,11.5,14.2,18.5,24.1,32.5,45.2,62.8
```
**Steps:**
1. Paste data
2. Click "Test Normality" - should fail (p < 0.05)
3. Select "Logarithmic" transformation
4. Click "Apply Transformation"
5. Should show improved normality

### Example 4: Box-Cox Transformation
**Copy this data:**
```
1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,1.2,2.2,3.2,4.2,5.2,6.2,7.2,8.2,9.2,10.2,1.8,2.8,3.8,4.8,5.8,6.8,7.8,8.8,9.8,10.8
```
**Steps:**
1. Paste data
2. Click "Test Normality" - should fail
3. Select "Box-Cox" transformation
4. Click "Apply Transformation"
5. Review optimal lambda parameter

---

## Reliability Tab

### Example 1: Zero-Failure Demonstration
**Copy these values:**
```
Confidence Level: 90
Reliability: 90
Failures: 0
```
**Expected Result:** Test Duration ≈ 4.61

### Example 2: Accelerated Life Testing
**Copy these values:**
```
Confidence Level: 90
Reliability: 90
Failures: 0
Activation Energy: 0.7
Use Temperature: 298.15 (25°C in Kelvin)
Test Temperature: 358.15 (85°C in Kelvin)
```
**Expected Results:**
- Test Duration ≈ 4.61
- Acceleration Factor ≈ 54.6
- Equivalent test time at use conditions

### Temperature Conversion Reference
```
Celsius to Kelvin: K = °C + 273.15

Common temperatures:
25°C = 298.15 K (room temperature)
37°C = 310.15 K (body temperature)
60°C = 333.15 K (accelerated test)
85°C = 358.15 K (high accelerated test)
```

---

## Tips for Testing

### Data Entry
- Remove comments (lines starting with #) before pasting
- Data can be comma-separated, space-separated, or one per line
- Decimal points use period (.) not comma (,)

### Verification
- Compare your results to expected values
- Small differences (< 1%) are normal due to rounding
- Large differences indicate potential input errors

### Troubleshooting
- **"Invalid input"**: Check value ranges (0-100 for percentages)
- **"Must be positive"**: Ensure no negative values for std dev
- **"Transformation failed"**: Check data is positive (for log/Box-Cox)
- **"Sample size too large"**: Adjust confidence/reliability parameters

### Report Generation
- After any calculation, click "Generate Report"
- PDF includes all inputs, results, and validation status
- Reports saved to `reports/` directory

---

## Next Steps

1. **Try the examples above** to familiarize yourself with each module
2. **Read the User Guide** (`docs/USER_GUIDE.md`) for detailed explanations
3. **Use your own data** following the same format
4. **Generate reports** for documentation and compliance

## Need Help?

- **User Guide:** Detailed usage instructions and interpretations
- **Validation Protocol:** Testing and validation procedures
- **Developer Guide:** Technical details and architecture
- **Sample Data README:** Detailed explanation of each sample file
