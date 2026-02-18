# Implementation Plan: Sample Size Estimator

## Overview

This implementation plan breaks down the Sample Size Estimator application into discrete, testable tasks. The application uses functional programming with Pydantic for type safety, Streamlit for the UI, and comprehensive testing with pytest, hypothesis for property-based testing, and Playwright for UI testing.

## Tasks

- [x] 1. Project Setup and Configuration
  - Initialize uv project with pyproject.toml
  - Configure dependencies: streamlit, pydantic, pydantic-settings, scipy, numpy, matplotlib, reportlab, pytest, hypothesis, mypy, ruff
  - Create directory structure: src/sample_size_estimator/, tests/, docs/
  - Set up .env.example with configuration parameters
  - Create .gitignore for Python projects
  - _Requirements: REQ-23, REQ-27_

- [ ] 2. Core Configuration and Models
  - [x] 2.1 Implement configuration management (config.py)
    - Create AppSettings class with Pydantic BaseSettings
    - Define all configuration parameters (log_level, validated_hash, report_output_dir, etc.)
    - Implement get_settings() singleton function
    - _Requirements: REQ-27_
  
  - [x] 2.2 Implement data models (models.py)
    - Create input models: AttributeInput, VariablesInput, ReliabilityInput
    - Create result models: AttributeResult, VariablesResult, ReliabilityResult, SensitivityResult
    - Create normality and transformation models: NormalityTestResult, TransformationResult
    - Create report model: CalculationReport
    - Add field validators for percentage ranges, positive values, LSL < USL
    - _Requirements: REQ-1, REQ-2, REQ-4, REQ-6, REQ-7, REQ-15, REQ-16, REQ-19_
  
  - [x] 2.3 Write unit tests for data models
    - Test validation for valid inputs
    - Test rejection of invalid inputs (negative values, out-of-range percentages)
    - Test LSL < USL validation
    - _Requirements: REQ-19_

- [ ] 3. Attribute Calculations Module
  - [x] 3.1 Implement Success Run Theorem calculation (attribute_calcs.py)
    - Implement calculate_sample_size_zero_failures() function
    - Use formula: n = ceil(ln(1-C/100) / ln(R/100))
    - _Requirements: REQ-1.2_
  
  - [x] 3.2 Write property test for Success Run Theorem
    - **Property 1: Success Run Theorem Correctness**
    - **Validates: Requirements 1.2**
    - Use hypothesis to generate random C and R values
    - Verify formula produces correct results
    - _Requirements: REQ-1, REQ-24_
  
  - [x] 3.3 Implement binomial sample size calculation
    - Implement calculate_sample_size_with_failures() function
    - Use iterative approach with scipy.stats.binom
    - Find smallest n where cumulative probability ≤ (1-C)
    - _Requirements: REQ-2.2, REQ-2.3_
  
  - [x] 3.4 Write property tests for binomial calculation
    - **Property 2: Binomial Sample Size Correctness**
    - **Property 3: Binomial Sample Size Minimality**
    - **Validates: Requirements 2.2, 2.3**
    - Verify formula correctness and minimality of n
    - _Requirements: REQ-2, REQ-24_
  
  - [x] 3.5 Implement sensitivity analysis
    - Implement calculate_sensitivity_analysis() function
    - Calculate for c=0, 1, 2, 3
    - Return SensitivityResult with list of results
    - _Requirements: REQ-3.1_
  
  - [x] 3.6 Write property test for sensitivity analysis
    - **Property 4: Sensitivity Analysis Completeness**
    - **Validates: Requirements 3.1**
    - Verify exactly 4 results with correct c values
    - _Requirements: REQ-3, REQ-24_
  
  - [x] 3.7 Implement main entry point calculate_attribute()
    - Handle None for c (sensitivity analysis)
    - Handle c=0 (Success Run)
    - Handle c>0 (binomial)
    - _Requirements: REQ-1, REQ-2, REQ-3_
  
  - [x] 3.8 Write unit tests for attribute module
    - Test with known statistical values (C=95%, R=90% → n=29)
    - Test edge cases (very high/low confidence)
    - Test error conditions
    - _Requirements: REQ-1, REQ-2, REQ-3_

- [ ] 4. Variables Calculations Module
  - [x] 4.1 Implement tolerance factor calculations (variables_calcs.py)
    - Implement calculate_one_sided_tolerance_factor() using non-central t-distribution
    - Implement calculate_two_sided_tolerance_factor() using Howe-Guenther approximation
    - Use scipy.stats.nct and scipy.stats.chi2
    - _Requirements: REQ-4.1, REQ-4.2_
  
  - [x] 4.2 Write property tests for tolerance factors
    - **Property 6: One-Sided Tolerance Factor Correctness**
    - **Property 7: Two-Sided Tolerance Factor Correctness**
    - **Validates: Requirements 4.1, 4.2**
    - Verify formulas with random inputs
    - _Requirements: REQ-4, REQ-24_
  
  - [x] 4.3 Implement tolerance limit calculations
    - Implement calculate_tolerance_limits() function
    - Calculate upper and lower limits based on sided parameter
    - _Requirements: REQ-5.1, REQ-5.2, REQ-5.3_
  
  - [x] 4.4 Write property test for tolerance limits
    - **Property 8: Tolerance Limit Calculation Correctness**
    - **Validates: Requirements 5.1, 5.2**
    - Verify arithmetic: μ ± k*σ
    - _Requirements: REQ-5, REQ-24_
  
  - [x] 4.5 Implement Ppk calculation
    - Implement calculate_ppk() function
    - Handle one-sided and two-sided specifications
    - _Requirements: REQ-7.1, REQ-7.2_
  
  - [-] 4.6 Write property test for Ppk
    - **Property 10: Ppk Calculation Correctness**
    - **Validates: Requirements 7.1, 7.2**
    - Verify formula with random inputs
    - _Requirements: REQ-7, REQ-24_
  
  - [x] 4.7 Implement specification limit comparison
    - Implement compare_to_spec_limits() function
    - Determine PASS/FAIL status
    - Calculate margins
    - _Requirements: REQ-6.2, REQ-6.3, REQ-6.4, REQ-6.5_
  
  - [x] 4.8 Write property test for comparison logic
    - **Property 9: Specification Comparison Logic**
    - **Validates: Requirements 6.2, 6.3, 6.4**
    - Verify PASS/FAIL logic with random limits
    - _Requirements: REQ-6, REQ-24_
  
  - [x] 4.9 Implement main entry point calculate_variables()
    - Integrate all calculations
    - Return complete VariablesResult
    - _Requirements: REQ-4, REQ-5, REQ-6, REQ-7_
  
  - [x] 4.10 Write unit tests for variables module
    - Test with known capability examples
    - Test one-sided vs two-sided
    - Test PASS/FAIL scenarios
    - _Requirements: REQ-4, REQ-5, REQ-6, REQ-7_

- [x] 5. Checkpoint - Core Calculations Complete
  - Ensure all tests pass for attribute and variables modules
  - Verify property tests run with 100+ iterations
  - Ask user if questions arise

- [ ] 6. Non-Normal Calculations Module
  - [x] 6.1 Implement outlier detection (non_normal_calcs.py)
    - Implement detect_outliers() using IQR method
    - Calculate Q1, Q3, IQR
    - Flag values outside Q1-1.5*IQR to Q3+1.5*IQR
    - _Requirements: REQ-8.1, REQ-8.2_
  
  - [x] 6.2 Write property tests for outlier detection
    - **Property 13: Outlier Detection Correctness**
    - **Property 14: Outlier Count Consistency**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
    - Verify IQR calculation and flagging logic
    - _Requirements: REQ-8, REQ-24_
  
  - [x] 6.3 Implement normality testing
    - Implement test_normality() function
    - Perform Shapiro-Wilk test using scipy.stats.shapiro
    - Perform Anderson-Darling test using scipy.stats.anderson
    - Determine is_normal based on p-value and critical values
    - Generate interpretation text
    - _Requirements: REQ-9.1, REQ-9.2, REQ-9.5, REQ-9.6_
  
  - [x] 6.4 Write property tests for normality testing
    - **Property 15: Normality Test Execution**
    - **Property 16: Normality Rejection Logic**
    - **Validates: Requirements 9.1-9.7**
    - Verify tests execute and logic is correct
    - _Requirements: REQ-9, REQ-24_
  
  - [x] 6.5 Implement Q-Q plot generation
    - Implement generate_qq_plot() function
    - Use scipy.stats.probplot and matplotlib
    - Return matplotlib figure object
    - _Requirements: REQ-10.1, REQ-10.2, REQ-10.3_
  
  - [x] 6.6 Implement data transformations
    - Implement transform_boxcox() with automatic lambda optimization
    - Implement transform_log() for natural logarithm
    - Implement transform_sqrt() for square root
    - Validate data suitability (positive for log/boxcox, non-negative for sqrt)
    - _Requirements: REQ-11.1, REQ-11.2, REQ-11.3, REQ-11.4, REQ-11.6_
  
  - [x] 6.7 Write property tests for transformations (round-trip)
    - **Property 17: Logarithmic Transformation Round-Trip**
    - **Property 18: Box-Cox Transformation Round-Trip**
    - **Property 19: Square Root Transformation Round-Trip**
    - **Validates: Requirements 13.1, 13.2, 13.3**
    - Verify transform → back-transform returns original (within precision)
    - _Requirements: REQ-13, REQ-24_
  
  - [x] 6.8 Implement back-transformations
    - Implement back_transform_log(), back_transform_boxcox(), back_transform_sqrt()
    - Use inverse formulas
    - _Requirements: REQ-13.1, REQ-13.2, REQ-13.3_
  
  - [x] 6.9 Implement apply_transformation() with normality re-testing
    - Apply selected transformation
    - Re-run normality tests on transformed data
    - Return TransformationResult with both datasets and normality results
    - _Requirements: REQ-11, REQ-12_
  
  - [x] 6.10 Write property test for post-transformation normality
    - **Property 21: Post-Transformation Normality Testing**
    - **Validates: Requirements 12.1, 12.2**
    - Verify normality tests run on transformed data
    - _Requirements: REQ-12, REQ-24_
  
  - [x] 6.11 Implement Wilks' non-parametric method
    - Implement calculate_wilks_limits() function
    - Use min/max of dataset as limits
    - _Requirements: REQ-14.2_
  
  - [x] 6.12 Write property test for Wilks' method
    - **Property 22: Wilks' Limits Correctness**
    - **Validates: Requirements 14.2**
    - Verify limits equal min/max
    - _Requirements: REQ-14, REQ-24_
  
  - [x] 6.13 Write unit tests for non-normal module
    - Test outlier detection with known datasets
    - Test normality tests with normal and non-normal data
    - Test transformation error conditions (negative data for log)
    - _Requirements: REQ-8, REQ-9, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14_

- [ ] 7. Reliability Calculations Module
  - [x] 7.1 Implement zero-failure duration calculation (reliability_calcs.py)
    - Implement calculate_zero_failure_duration() function
    - Use scipy.stats.chi2.ppf
    - Formula: chi^2_{1-C, 2(r+1)}
    - _Requirements: REQ-15.1, REQ-15.2_
  
  - [x] 7.2 Write property test for zero-failure duration
    - **Property 23: Zero-Failure Duration Correctness**
    - **Validates: Requirements 15.1, 15.2**
    - Verify chi-squared formula
    - _Requirements: REQ-15, REQ-24_
  
  - [x] 7.3 Implement Arrhenius acceleration factor
    - Implement calculate_acceleration_factor() function
    - Use Arrhenius equation with Boltzmann constant
    - Validate T_test > T_use
    - _Requirements: REQ-16.1, REQ-16.2, REQ-16.4_
  
  - [x] 7.4 Write property test for acceleration factor
    - **Property 24: Arrhenius Acceleration Factor Correctness**
    - **Property 25: Temperature Validation**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4**
    - Verify Arrhenius formula and temperature validation
    - _Requirements: REQ-16, REQ-24_
  
  - [x] 7.5 Implement temperature conversion helper
    - Implement celsius_to_kelvin() function
    - _Requirements: REQ-16.3_
  
  - [x] 7.6 Implement main entry point calculate_reliability()
    - Integrate duration and acceleration factor calculations
    - Return ReliabilityResult
    - _Requirements: REQ-15, REQ-16_
  
  - [x] 7.7 Write unit tests for reliability module
    - Test with known reliability values
    - Test temperature validation
    - Test acceleration factor with known examples
    - _Requirements: REQ-15, REQ-16_

- [x] 8. Checkpoint - All Calculation Modules Complete
  - Ensure all calculation tests pass
  - Verify all property tests have 100+ iterations
  - Run full test suite: uv run pytest -q
  - Ask user if questions arise


- [x] 9. Validation and Reporting Services
  - [x] 9.1 Implement hash verification (validation.py)
    - Implement calculate_file_hash() using hashlib.sha256
    - Implement verify_validation_state() for hash comparison
    - Implement get_engine_validation_info() to get complete validation info
    - _Requirements: REQ-21.1, REQ-21.3_
  
  - [x] 9.2 Write property tests for hash verification
    - **Property 26: Hash Calculation Determinism**
    - **Property 27: Hash Comparison Logic**
    - **Validates: Requirements 21.1, 21.3, 21.4, 21.5**
    - Verify hash determinism and comparison logic
    - _Requirements: REQ-21, REQ-24_
  
  - [x] 9.3 Write unit tests for validation module
    - Test hash calculation with test files
    - Test validation state logic (match/mismatch)
    - Test with None validated hash
    - _Requirements: REQ-21_
  
  - [x] 9.4 Implement PDF report generation (reports.py)
    - Implement generate_calculation_report() using reportlab
    - Include all required sections: metadata, inputs, results, validation
    - Format with tables and styling
    - _Requirements: REQ-20.1-20.6_
  
  - [x] 9.5 Implement validation certificate generation
    - Implement generate_validation_certificate() function
    - Include test execution info, URS results table, validation summary
    - Format with colors for PASS/FAIL
    - _Requirements: REQ-22.1-22.7_
  
  - [x] 9.6 Write unit tests for report generation
    - Test PDF creation with sample data
    - Verify all required sections present
    - Test validation state display (YES/NO)
    - _Requirements: REQ-20, REQ-22_

- [x] 10. Logging Infrastructure
  - [x] 10.1 Implement logging configuration (logger.py)
    - Create JSONFormatter class for structured logging
    - Implement setup_logger() function
    - Configure file and console handlers
    - _Requirements: REQ-26.6_
  
  - [x] 10.2 Implement logging helper functions
    - Implement log_calculation() for calculation events
    - Implement log_validation_check() for validation events
    - _Requirements: REQ-26.1, REQ-26.2_
  
  - [x] 10.3 Write property tests for logging
    - **Property 29: Calculation Logging Completeness**
    - **Property 30: Validation Logging Completeness**
    - **Validates: Requirements 26.1, 26.2**
    - Verify log entries contain all required fields
    - _Requirements: REQ-26, REQ-24_
  
  - [x] 10.4 Write unit tests for logging
    - Test JSON formatting
    - Test log file creation
    - Test log levels
    - _Requirements: REQ-26_

- [ ] 11. Streamlit UI - Attribute Tab
  - [x] 11.1 Create attribute tab UI (ui/attribute_tab.py)
    - Create input widgets for confidence, reliability, allowable failures
    - Add tooltips for each input
    - Add calculate button
    - Display results (single or sensitivity table)
    - Add download report button
    - _Requirements: REQ-17, REQ-18, REQ-19, REQ-20_
  
  - [x] 11.2 Integrate attribute calculations
    - Call calculate_attribute() with validated inputs
    - Handle errors and display error messages
    - Log calculation execution
    - _Requirements: REQ-1, REQ-2, REQ-3, REQ-26_
  
  - [x] 11.3 Write UI test for attribute tab workflow
    - Use Playwright browser automation
    - Simulate entering inputs and clicking calculate
    - Verify results display
    - _Requirements: REQ-25, URS-VAL-03_

- [ ] 12. Streamlit UI - Variables Tab
  - [x] 12.1 Create variables tab UI (ui/variables_tab.py)
    - Create input widgets for all parameters
    - Add sided selection (one/two)
    - Add optional spec limits
    - Display tolerance factor, limits, Ppk, PASS/FAIL
    - _Requirements: REQ-17, REQ-18, REQ-19_
  
  - [x] 12.2 Integrate variables calculations
    - Call calculate_variables() with validated inputs
    - Handle errors and display messages
    - Log calculation execution
    - _Requirements: REQ-4, REQ-5, REQ-6, REQ-7, REQ-26_
  
  - [x] 12.3 Write UI test for variables tab workflow
    - Test complete workflow with spec limits
    - Verify PASS/FAIL display
    - _Requirements: REQ-25, URS-VAL-03_

- [ ] 13. Streamlit UI - Non-Normal Tab
  - [x] 13.1 Create non-normal tab UI (ui/non_normal_tab.py)
    - Create data input widget (text area or file upload)
    - Add outlier detection section
    - Add normality testing section with Q-Q plot
    - Add transformation selection
    - Display transformation results and back-transformed limits
    - _Requirements: REQ-17, REQ-18_
  
  - [x] 13.2 Integrate non-normal calculations
    - Call outlier detection, normality testing, transformations
    - Display Q-Q plot using st.pyplot()
    - Handle transformation errors
    - Log operations
    - _Requirements: REQ-8, REQ-9, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-26_
  
  - [x] 13.3 Write UI test for non-normal tab workflow
    - Test with sample dataset
    - Verify outlier detection display
    - Verify transformation workflow
    - _Requirements: REQ-25, URS-VAL-03_

- [ ] 14. Streamlit UI - Reliability Tab
  - [x] 14.1 Create reliability tab UI (ui/reliability_tab.py)
    - Create input widgets for confidence, failures
    - Add optional acceleration factor inputs
    - Display test duration and acceleration factor
    - _Requirements: REQ-17, REQ-18_
  
  - [x] 14.2 Integrate reliability calculations
    - Call calculate_reliability() with validated inputs
    - Handle errors
    - Log calculation
    - _Requirements: REQ-15, REQ-16, REQ-26_
  
  - [x] 14.3 Write UI test for reliability tab workflow
    - Test zero-failure calculation
    - Test with acceleration factor
    - _Requirements: REQ-25, URS-VAL-03_

- [ ] 15. Main Streamlit Application
  - [x] 15.1 Create main app.py
    - Set up page configuration
    - Load settings from config
    - Create help/instruction expander at top
    - Create tab layout with 4 tabs
    - Import and render each tab
    - _Requirements: REQ-17, REQ-18_
  
  - [x] 15.2 Implement report generation integration
    - Add report generation to each tab
    - Get validation info and include in report
    - Provide download button for PDF
    - _Requirements: REQ-20, REQ-21_
  
  - [x] 15.3 Initialize logging
    - Set up logger at app startup
    - Log app initialization
    - _Requirements: REQ-26_

- [x] 16. Checkpoint - UI Complete
  - Run app locally: uv run streamlit run src/sample_size_estimator/app.py
  - Test all four tabs manually
  - Verify report generation works
  - Verify validation state display
  - Ask user if questions arise

- [ ] 17. Validation Test Suite
  - [x] 17.1 Create pytest configuration (conftest.py)
    - Define pytest markers for URS IDs
    - Create fixtures for common test data
    - Configure hypothesis settings (min 100 iterations)
    - _Requirements: REQ-24_
  
  - [x] 17.2 Create validation certificate generation script
    - Create scripts/generate_validation_certificate.py
    - Collect all test results with URS markers
    - Calculate validated hash of calculation engine
    - Generate validation certificate PDF
    - _Requirements: REQ-22, REQ-24_
  
  - [x] 17.3 Write integration tests
    - Test end-to-end workflows for each module
    - Test report generation with real calculations
    - Test validation state verification
    - _Requirements: REQ-24_
  
  - [x] 17.4 Create environment check script
    - Create scripts/check_environment.py
    - Verify all dependencies at correct versions
    - Display system information
    - _Requirements: REQ-23_

- [ ] 18. Documentation
  - [x] 18.1 Write USER_GUIDE.md
    - Explain how to use each tab
    - Provide examples for each analysis type
    - Explain report interpretati
on
    - Explain validation state and hash verification
    - _Requirements: REQ-20, REQ-21_
  
  - [x] 18.2 Write DEVELOPER_GUIDE.md
    - Document architecture and design decisions
    - Explain how to add new analysis modules
    - Document testing approach (unit + property tests)
    - Provide examples of adding new properties
    - Document configuration management
    - _Requirements: REQ-28_
  
  - [x] 18.3 Write VALIDATION_PROTOCOL.md
    - Document IQ/OQ/PQ procedures
    - Explain validation test suite
    - Document how to generate validation certificate
    - List all URS requirements and test coverage
    - _Requirements: REQ-22, REQ-23, REQ-24, REQ-25_
  
  - [x] 18.4 Create comprehensive README.md
    - Project overview and features
    - Installation instructions with uv
    - Quick start guide
    - Configuration options
    - Running tests
    - Deployment instructions
    - Link to user and developer guides
    - _Requirements: All_

- [ ] 19. Final Integration and Testing
  - [x] 19.1 Run complete test suite
    - Execute: uv run pytest -q --cov=src/sample_size_estimator
    - Verify > 85% coverage
    - Ensure all property tests pass with 100+ iterations
    - _Requirements: REQ-24_
  
  - [x] 19.2 Run type checking
    - Execute: uvx mypy src/sample_size_estimator
    - Fix any type errors
    - _Requirements: REQ-27_
  
  - [x] 19.3 Run linting
    - Execute: uv run ruff check src/
    - Fix all errors and warnings
    - _Requirements: REQ-27_
  
  - [x] 19.4 Generate validation certificate
    - Execute: uv run python scripts/generate_validation_certificate.py
    - Verify all URS requirements show PASS
    - Verify validated hash is calculated
    - Store certificate in docs/
    - _Requirements: REQ-22_
  
  - [x] 19.5 Manual UI testing
    - Test all four tabs with various inputs
    - Test error handling with invalid inputs
    - Test report generation from each tab
    - Verify validation state display in reports
    - Test with edge cases (very large/small values)
    - _Requirements: REQ-25_
  
  - [x] 19.6 Update validated hash in configuration
    - Copy validated hash from certificate
    - Update .env.example with validated hash
    - Document hash update procedure
    - _Requirements: REQ-21_

- [ ] 20. Deployment Preparation
  - [~] 20.1 Create Docker configuration (optional)
    - Create Dockerfile with multi-stage build
    - Create docker-compose.yml
    - Create .dockerignore
    - Test Docker build and run
    - _Requirements: Deployment_
  
  - [~] 20.2 Create deployment documentation
    - Document local deployment
    - Document Docker deployment
    - Document environment variable configuration
    - Document backup and recovery procedures
    - _Requirements: Deployment_
  
  - [x] 20.3 Create example configuration files
    - Ensure .env.example has all parameters documented
    - Create sample data files for testing
    - _Requirements: REQ-27_

- [ ] 21. Final Checkpoint
  - All tests passing (unit, property, integration, UI)
  - All documentation complete
  - Validation certificate generated
  - Application runs successfully
  - Ready for user acceptance testing

## Notes

- Tasks marked with `*` are optional test-related sub-tasks that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests must run with minimum 100 iterations
- All calculation functions must be pure functions (no side effects)
- Use Pydantic for all data validation
- Use functional programming approach (avoid classes except for data models)
- Log all important operations for audit trail
- Maintain validated hash for regulatory compliance
