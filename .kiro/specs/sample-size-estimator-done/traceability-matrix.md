# Traceability Matrix

## Requirements to URS Mapping

This document provides bidirectional traceability between the system requirements and the User Requirements Specification (URS) document.

| Requirement ID | Requirement Title | URS ID(s) | Notes |
|----------------|-------------------|-----------|-------|
| REQ-1 | Attribute Data Sample Size Calculation (Zero Failures) | URS-FUNC_A-01, URS-FUNC_A-02, URS-UI-04 | Core binomial calculation with zero failures |
| REQ-2 | Attribute Data Sample Size Calculation (With Failures) | URS-FUNC_A-01, URS-FUNC_A-03, URS-FUNC_A-05 | Binomial calculation allowing failures |
| REQ-3 | Attribute Data Sensitivity Analysis | URS-FUNC_A-04, URS-FUNC_A-05 | Automatic calculation for c=0,1,2,3 |
| REQ-4 | Variable Data Tolerance Factor Calculation | URS-FUNC_B-01, URS-FUNC_B-02 | One-sided and two-sided tolerance factors |
| REQ-5 | Variable Data Tolerance Limit Calculation | URS-FUNC_B-03 | Calculate limits from sample statistics |
| REQ-6 | Specification Limit Comparison | URS-FUNC_B-04 | PASS/FAIL determination |
| REQ-7 | Process Performance Index Calculation | URS-FUNC_B-05 | Ppk calculation |
| REQ-8 | Outlier Detection | URS-FUNC_C-01 | IQR method for outlier detection |
| REQ-9 | Normality Testing | URS-FUNC_C-02, URS-FUNC_C-03 | Shapiro-Wilk and Anderson-Darling tests |
| REQ-10 | Probability Plot Visualization | URS-FUNC_C-04 | Q-Q plot generation |
| REQ-11 | Data Transformation | URS-FUNC_C-05 | Box-Cox, log, and square root transformations |
| REQ-12 | Post-Transformation Normality Verification | URS-FUNC_C-06 | Re-test normality after transformation |
| REQ-13 | Back-Transformation of Results | URS-FUNC_C-07 | Convert transformed results to original scale |
| REQ-14 | Non-Parametric Fallback Analysis | URS-FUNC_C-08 | Wilks' method when transformations fail |
| REQ-15 | Reliability Life Testing (Zero-Failure) | URS-FUNC_D-01 | Chi-squared based duration calculation |
| REQ-16 | Acceleration Factor Calculation | URS-FUNC_D-02 | Arrhenius equation for accelerated testing |
| REQ-17 | Tab-Based User Interface | URS-UI-01 | Four-tab layout for different methods |
| REQ-18 | Contextual Help and Tooltips | URS-UI-02, URS-UI-03, URS-UI-04 | Tooltips and help section |
| REQ-19 | Input Validation and Range Restrictions | URS-UI-04 | Prevent invalid inputs |
| REQ-20 | User Calculation Report Generation | URS-REP-01, URS-REP-02 | PDF report with hash |
| REQ-21 | Validation State Verification | URS-REP-02, URS-REP-03 | Hash comparison and validation state |
| REQ-22 | Automated Validation Report Generation | URS-REP-04 | Validation certificate from test suite |
| REQ-23 | Installation Qualification | URS-VAL-01 | Dependency version locking |
| REQ-24 | Operational Qualification Test Suite | URS-VAL-02 | Automated mathematical verification |
| REQ-25 | Performance Qualification UI Testing | URS-VAL-03 | End-to-end UI workflow testing |
| REQ-26 | Logging for Audit Trail | Derived | QMS compliance requirement |
| REQ-27 | Configuration Management | Derived | Deployment flexibility requirement |
| REQ-28 | Extensibility for Future Modules | Derived | Architecture requirement for AOL and future features |

## URS to Requirements Mapping

| URS ID | URS Description | Requirement ID(s) | Acceptance Criteria |
|--------|-----------------|-------------------|---------------------|
| URS-FUNC_A-01 | Accept and validate C, R, c inputs | REQ-1, REQ-2 | 1.1, 2.1 |
| URS-FUNC_A-02 | Calculate n using Success Run Theorem (c=0) | REQ-1 | 1.2, 1.3 |
| URS-FUNC_A-03 | Calculate n using cumulative binomial (c>0) | REQ-2 | 2.2, 2.3 |
| URS-FUNC_A-04 | Sensitivity analysis for c=0,1,2,3 | REQ-3 | 3.1, 3.2, 3.4 |
| URS-FUNC_A-05 | Calculate n for specific c value | REQ-2, REQ-3 | 2.4, 3.3 |
| URS-FUNC_B-01 | Calculate one-sided tolerance factor k1 | REQ-4 | 4.1, 4.3, 4.4, 4.5 |
| URS-FUNC_B-02 | Calculate two-sided tolerance factor k2 | REQ-4 | 4.2, 4.3, 4.4, 4.5 |
| URS-FUNC_B-03 | Calculate tolerance limits from statistics | REQ-5 | 5.1, 5.2, 5.3, 5.4 |
| URS-FUNC_B-04 | Compare tolerance limits to spec limits | REQ-6 | 6.1, 6.2, 6.3, 6.4, 6.5 |
| URS-FUNC_B-05 | Calculate Ppk index | REQ-7 | 7.1, 7.2, 7.3, 7.4 |
| URS-FUNC_C-01 | Detect outliers using IQR method | REQ-8 | 8.1, 8.2, 8.3, 8.4, 8.5 |
| URS-FUNC_C-02 | Perform Shapiro-Wilk normality test | REQ-9 | 9.1, 9.3, 9.5, 9.7 |
| URS-FUNC_C-03 | Perform Anderson-Darling normality test | REQ-9 | 9.2, 9.4, 9.6, 9.7 |
| URS-FUNC_C-04 | Generate Q-Q probability plot | REQ-10 | 10.1, 10.2, 10.3, 10.4 |
| URS-FUNC_C-05 | Offer transformation modes | REQ-11 | 11.1, 11.2, 11.3, 11.4, 11.5, 11.6 |
| URS-FUNC_C-06 | Re-evaluate normality after transformation | REQ-12 | 12.1, 12.2, 12.3, 12.4 |
| URS-FUNC_C-07 | Back-transform results to original scale | REQ-13 | 13.1, 13.2, 13.3, 13.4, 13.5 |
| URS-FUNC_C-08 | Non-parametric fallback (Wilks' method) | REQ-14 | 14.1, 14.2, 14.3, 14.4 |
| URS-FUNC_D-01 | Calculate test duration for zero-failure | REQ-15 | 15.1, 15.2, 15.3, 15.4 |
| URS-FUNC_D-02 | Calculate acceleration factor (Arrhenius) | REQ-16 | 16.1, 16.2, 16.3, 16.4, 16.5 |
| URS-UI-01 | Tab-based layout for methods | REQ-17 | 17.1, 17.2, 17.3, 17.4 |
| URS-UI-02 | Contextual tooltips for inputs | REQ-18 | 18.1, 18.2, 18.4 |
| URS-UI-03 | Help/instruction section | REQ-18 | 18.3 |
| URS-UI-04 | Numeric input widgets with validation | REQ-1, REQ-18, REQ-19 | 1.1, 18.5, 19.1-19.5 |
| URS-REP-01 | Generate user calculation report PDF | REQ-20 | 20.1-20.6 |
| URS-REP-02 | Display SHA-256 hash in report | REQ-20, REQ-21 | 20.6, 21.1, 21.2 |
| URS-REP-03 | Compare hash and display validation state | REQ-21 | 21.3, 21.4, 21.5, 21.6 |
| URS-REP-04 | Generate validation certificate PDF | REQ-22 | 22.1-22.7 |
| URS-VAL-01 | Installation qualification (IQ) | REQ-23 | 23.1-23.4 |
| URS-VAL-02 | Operational qualification (OQ) tests | REQ-24 | 24.1-24.5 |
| URS-VAL-03 | Performance qualification (PQ) UI tests | REQ-25 | 25.1-25.5 |

## Test Coverage Matrix

This section will be populated during the design phase with specific test cases mapped to requirements and URS IDs.

### Attribute Module Tests
- Test case for URS-FUNC_A-02: Success Run Theorem with C=95%, R=90%
- Test case for URS-FUNC_A-03: Binomial with c=2, C=95%, R=90%
- Test case for URS-FUNC_A-04: Sensitivity table generation

### Variable Module Tests
- Test case for URS-FUNC_B-01: One-sided tolerance factor calculation
- Test case for URS-FUNC_B-02: Two-sided tolerance factor calculation
- Test case for URS-FUNC_B-04: PASS/FAIL comparison logic
- Test case for URS-FUNC_B-05: Ppk calculation with known values

### Non-Normal Module Tests
- Test case for URS-FUNC_C-01: Outlier detection with known dataset
- Test case for URS-FUNC_C-02: Shapiro-Wilk test with normal and non-normal data
- Test case for URS-FUNC_C-05: Box-Cox transformation with lambda optimization
- Test case for URS-FUNC_C-07: Back-transformation accuracy verification

### Reliability Module Tests
- Test case for URS-FUNC_D-01: Zero-failure test duration calculation
- Test case for URS-FUNC_D-02: Arrhenius acceleration factor calculation

### Validation Tests
- Test case for URS-VAL-01: Dependency version verification
- Test case for URS-VAL-02: All OQ tests with pytest markers
- Test case for URS-VAL-03: UI workflow simulation for each tab

## Notes

- All test cases must include the @pytest.mark.urs("URS-ID") marker for automated traceability
- Each requirement must have at least one test case that verifies all acceptance criteria
- The validation certificate will automatically generate this matrix from test execution results
- Derived requirements (REQ-26, REQ-27, REQ-28) support the overall QMS compliance but don't map directly to URS functional requirements
