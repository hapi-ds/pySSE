# Sample Data Files for Testing

This directory contains sample datasets for testing and demonstrating the Sample Size Estimator application. Each file is designed to illustrate specific statistical scenarios and analysis methods.

## File Descriptions

### 1. sample_data_normal.csv
**Distribution Type:** Normal (Gaussian)  
**Use Case:** Variables (Normal) tab  
**Characteristics:**
- Mean ≈ 10.0 mm
- Standard Deviation ≈ 0.5 mm
- Sample Size: 30 measurements
- No outliers
- Passes normality tests

**How to Use:**
1. Navigate to the "Variables (Normal)" tab
2. Copy the data values (excluding comments)
3. Calculate mean and standard deviation in Excel or similar tool
4. Enter the statistics into the Variables tab
5. Set specification limits (e.g., LSL=8.5, USL=11.5) to test process capability

**Expected Results:**
- Tolerance Factor (k) ≈ 2.14 (for 95% confidence, 90% reliability, n=30, two-sided)
- Lower Tolerance Limit ≈ 8.93 mm
- Upper Tolerance Limit ≈ 11.07 mm
- Ppk ≈ 1.67 (if LSL=8.5, USL=11.5)
- Result: PASS

---

### 2. sample_data_skewed.csv
**Distribution Type:** Right-Skewed (Log-Normal)  
**Use Case:** Non-Normal Distribution tab  
**Characteristics:**
- Right-skewed distribution (long tail to the right)
- Typical of cycle times, response times, or failure times
- Sample Size: 40 measurements
- Fails normality tests in original form

**How to Use:**
1. Navigate to the "Non-Normal Distribution" tab
2. Copy and paste the data values (comma-separated or one per line)
3. Click "Test Normality" - should show p-value < 0.05 (non-normal)
4. Select "Logarithmic" transformation
5. Click "Apply Transformation"
6. Verify transformed data passes normality tests
7. Calculate tolerance limits on transformed data
8. View back-transformed limits in original units

**Expected Results:**
- Original data: Shapiro-Wilk p-value < 0.05 (fails normality)
- After log transformation: p-value > 0.05 (passes normality)
- Back-transformed limits provide valid tolerance intervals

**Statistical Note:**
Log transformation is ideal for data where:
- Values are strictly positive
- Distribution is right-skewed
- Variance increases with the mean

---

### 3. sample_data_with_outliers.csv
**Distribution Type:** Normal with Outliers  
**Use Case:** Non-Normal Distribution tab (Outlier Detection)  
**Characteristics:**
- Mostly normal distribution (mean ≈ 10.0)
- Contains 2 obvious outliers: 25.5 and 0.2
- Sample Size: 40 measurements
- Demonstrates IQR-based outlier detection

**How to Use:**
1. Navigate to the "Non-Normal Distribution" tab
2. Copy and paste the data values
3. Click "Detect Outliers"
4. Review the outlier detection results

**Expected Results:**
- Outlier Count: 2
- Outlier Values: 0.2 and 25.5
- Q1 ≈ 9.8, Q3 ≈ 10.2, IQR ≈ 0.4
- Lower Bound: Q1 - 1.5×IQR ≈ 9.2
- Upper Bound: Q3 + 1.5×IQR ≈ 10.8
- Values outside these bounds are flagged as outliers

**Decision Points:**
- Investigate outliers: Are they measurement errors or real phenomena?
- If errors: Remove and recalculate
- If real: Consider robust statistical methods or non-parametric approaches

---

### 4. sample_data_bimodal.csv
**Distribution Type:** Bimodal (Two Peaks)  
**Use Case:** Non-Normal Distribution tab (Wilks' Method)  
**Characteristics:**
- Two distinct modes (peaks) at ~5.0 and ~15.0
- Represents mixed populations (e.g., two different suppliers, shifts, or processes)
- Sample Size: 40 measurements
- Transformations typically fail to achieve normality

**How to Use:**
1. Navigate to the "Non-Normal Distribution" tab
2. Copy and paste the data values
3. Click "Test Normality" - should fail
4. Try transformations (log, Box-Cox, sqrt) - all should fail
5. Use Wilks' non-parametric method as fallback

**Expected Results:**
- Normality tests fail (p-value < 0.05)
- All transformations fail to achieve normality
- Wilks' method provides conservative limits:
  - Lower Limit: min(data) = 5.0
  - Upper Limit: max(data) = 15.3

**Statistical Note:**
Bimodal distributions indicate:
- Mixed populations that should be analyzed separately
- Different operating conditions or sources
- Consider stratifying data by source before analysis

**Recommendation:**
Split the data into two groups (values around 5 and values around 15) and analyze separately for more meaningful results.

---

### 5. sample_data_uniform.csv
**Distribution Type:** Uniform (Rectangular)  
**Use Case:** Non-Normal Distribution tab (Box-Cox Transformation)  
**Characteristics:**
- Uniformly distributed (all values equally likely)
- Flat distribution with no central tendency
- Sample Size: 40 measurements
- Box-Cox may find optimal transformation

**How to Use:**
1. Navigate to the "Non-Normal Distribution" tab
2. Copy and paste the data values
3. Click "Test Normality" - should fail
4. Select "Box-Cox" transformation (automatic lambda optimization)
5. Click "Apply Transformation"
6. Review the optimal lambda parameter and normality results

**Expected Results:**
- Original data fails normality tests
- Box-Cox finds optimal lambda parameter
- Transformed data may achieve normality (depends on lambda)
- If transformation succeeds, calculate tolerance limits on transformed data

**Statistical Note:**
Box-Cox transformation:
- Automatically finds optimal power transformation
- Lambda = 1: No transformation
- Lambda = 0.5: Square root transformation
- Lambda = 0: Logarithmic transformation
- Lambda = -1: Reciprocal transformation

---

## Data Format Guidelines

### CSV Format
- Values can be comma-separated on one line or multiple lines
- Comments start with `#` and are ignored
- No headers required (just raw data values)

### Copying Data into Application
You can enter data in multiple formats:

**Comma-separated (single line):**
```
9.8,10.2,9.9,10.1,10.0,9.7,10.3
```

**Comma-separated (multiple lines):**
```
9.8,10.2,9.9,10.1,10.0
9.7,10.3,10.1,9.9,10.2
```

**One value per line:**
```
9.8
10.2
9.9
10.1
```

**Space-separated:**
```
9.8 10.2 9.9 10.1 10.0
```

## Statistical Analysis Workflow

### For Normal Data (sample_data_normal.csv)
1. Calculate descriptive statistics (mean, std dev)
2. Use Variables (Normal) tab
3. Calculate tolerance factors and limits
4. Compare to specification limits
5. Calculate Ppk for process capability

### For Non-Normal Data (sample_data_skewed.csv, etc.)
1. Enter raw data in Non-Normal Distribution tab
2. Check for outliers (optional but recommended)
3. Test for normality
4. If non-normal:
   - Try appropriate transformation (log, Box-Cox, sqrt)
   - Re-test normality on transformed data
   - If successful: Calculate limits and back-transform
   - If unsuccessful: Use Wilks' non-parametric method

## Creating Your Own Test Data

### Normal Distribution
Use Excel or Python to generate:
```python
import numpy as np
data = np.random.normal(loc=10.0, scale=0.5, size=30)
```

### Log-Normal Distribution (Right-Skewed)
```python
import numpy as np
data = np.random.lognormal(mean=1.0, sigma=0.5, size=40)
```

### With Outliers
```python
import numpy as np
normal_data = np.random.normal(loc=10.0, scale=0.5, size=38)
outliers = np.array([0.2, 25.5])
data = np.concatenate([normal_data, outliers])
```

## Validation Testing

These sample files are also used in automated testing:
- Unit tests verify calculations with known datasets
- Property-based tests use randomly generated data
- UI tests use these samples to verify end-to-end workflows

## Additional Resources

- **User Guide:** `docs/USER_GUIDE.md` - Detailed usage instructions
- **Validation Protocol:** `docs/VALIDATION_PROTOCOL.md` - Testing procedures
- **Developer Guide:** `docs/DEVELOPER_GUIDE.md` - Technical documentation

## Questions or Issues?

If you encounter issues with these sample files or need additional examples:
1. Check the User Guide for detailed instructions
2. Verify data format matches expected input
3. Ensure values are appropriate for the selected analysis method
4. Review error messages for specific guidance

---

**Note:** All sample data files are for demonstration and testing purposes only. For production use, always use your actual measurement data and verify results with appropriate statistical expertise.
