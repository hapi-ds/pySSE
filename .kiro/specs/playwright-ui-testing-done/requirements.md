# Requirements Document: Playwright UI Testing

## Introduction

This document specifies the requirements for implementing end-to-end UI testing using Playwright browser automation for the Sample Size Estimator Streamlit application. The current UI tests use Streamlit AppTest framework but face technical limitations with import scope and isolated execution contexts. This feature will provide true browser-based automated testing to achieve full compliance with REQ-25 (Performance Qualification UI Testing).

## Glossary

- **Playwright**: Browser automation library for end-to-end testing
- **Streamlit_App**: The Sample Size Estimator web application built with Streamlit
- **Test_Runner**: The pytest test execution framework
- **Browser_Instance**: Automated browser (Chromium/Firefox/WebKit) controlled by Playwright
- **Subprocess_Manager**: Component that starts and stops the Streamlit application
- **UI_Element**: Interactive widget in the Streamlit application (input, button, tab, etc.)
- **Test_Isolation**: Ensuring each test runs independently without side effects
- **Headless_Mode**: Browser execution without visible GUI (for CI/CD)
- **REQ-25**: URS requirement mandating automated UI testing for Performance Qualification

## Requirements

### Requirement 1: Subprocess Management

**User Story:** As a test engineer, I want the Streamlit application to start automatically before tests and stop after tests, so that I can run UI tests without manual intervention.

#### Acceptance Criteria

1. WHEN the test suite begins, THE Subprocess_Manager SHALL start the Streamlit_App in a subprocess
2. WHEN the Streamlit_App starts, THE Subprocess_Manager SHALL wait until the application is ready to accept connections
3. WHEN the test suite completes, THE Subprocess_Manager SHALL terminate the Streamlit_App subprocess
4. IF the Streamlit_App fails to start within 30 seconds, THEN THE Subprocess_Manager SHALL raise a timeout error
5. WHEN the subprocess terminates, THE Subprocess_Manager SHALL ensure all resources are cleaned up

### Requirement 2: Browser Automation Setup

**User Story:** As a test engineer, I want Playwright to control a browser instance, so that I can interact with the Streamlit UI programmatically.

#### Acceptance Criteria

1. WHEN tests execute, THE Test_Runner SHALL launch a Browser_Instance using Playwright
2. THE Browser_Instance SHALL support headless mode for CI/CD environments
3. THE Browser_Instance SHALL support visible mode for local debugging
4. WHEN a test completes, THE Test_Runner SHALL close the Browser_Instance
5. THE Test_Runner SHALL configure appropriate timeouts for element interactions (default 30 seconds)

### Requirement 3: Attribute Tab Testing

**User Story:** As a test engineer, I want to test the Attribute (Binomial) tab workflows, so that I can verify calculations display correctly in the browser.

#### Acceptance Criteria

1. WHEN the test navigates to the Attribute tab, THE Browser_Instance SHALL click the "Attribute (Binomial)" tab element
2. WHEN entering confidence level, THE Test_Runner SHALL input a numeric value into the confidence field
3. WHEN entering reliability level, THE Test_Runner SHALL input a numeric value into the reliability field
4. WHEN clicking the calculate button, THE Browser_Instance SHALL trigger the calculation
5. WHEN results are calculated, THE Test_Runner SHALL verify the results table is visible in the page
6. FOR zero-failure calculations (c=0), THE Test_Runner SHALL verify the sample size matches expected value (n=29 for C=95%, R=90%)
7. FOR sensitivity analysis, THE Test_Runner SHALL verify results display for c=0,1,2,3
8. WHEN allowable failures are specified, THE Test_Runner SHALL verify only the single result displays

### Requirement 4: Variables Tab Testing

**User Story:** As a test engineer, I want to test the Variables (Normal) tab workflows, so that I can verify tolerance limit calculations display correctly.

#### Acceptance Criteria

1. WHEN the test navigates to the Variables tab, THE Browser_Instance SHALL click the "Variables (Normal)" tab element
2. WHEN entering sample parameters, THE Test_Runner SHALL input confidence, reliability, sample size, mean, and standard deviation
3. WHEN entering specification limits, THE Test_Runner SHALL input LSL and USL values
4. WHEN clicking calculate, THE Browser_Instance SHALL trigger the tolerance limit calculation
5. WHEN results are calculated, THE Test_Runner SHALL verify tolerance factor displays
6. WHEN results are calculated, THE Test_Runner SHALL verify upper and lower tolerance limits display
7. WHEN results are calculated, THE Test_Runner SHALL verify Ppk value displays
8. WHEN specification limits are provided, THE Test_Runner SHALL verify PASS/FAIL status displays

### Requirement 5: Non-Normal Tab Testing

**User Story:** As a test engineer, I want to test the Non-Normal Distribution tab workflows, so that I can verify data transformation and normality testing work correctly.

#### Acceptance Criteria

1. WHEN the test navigates to the Non-Normal tab, THE Browser_Instance SHALL click the "Non-Normal Distribution" tab element
2. WHEN entering sample data, THE Test_Runner SHALL input comma-separated values into the data field
3. WHEN clicking detect outliers, THE Browser_Instance SHALL trigger outlier detection
4. WHEN outliers are detected, THE Test_Runner SHALL verify outlier count displays
5. WHEN clicking test normality, THE Browser_Instance SHALL trigger normality tests
6. WHEN normality tests complete, THE Test_Runner SHALL verify Shapiro-Wilk p-value displays
7. WHEN normality tests complete, THE Test_Runner SHALL verify Anderson-Darling results display
8. WHEN selecting a transformation method, THE Test_Runner SHALL select from the transformation dropdown
9. WHEN applying transformation, THE Browser_Instance SHALL trigger the transformation calculation
10. WHEN transformation completes, THE Test_Runner SHALL verify transformed data normality results display

### Requirement 6: Reliability Tab Testing

**User Story:** As a test engineer, I want to test the Reliability tab workflows, so that I can verify accelerated life testing calculations display correctly.

#### Acceptance Criteria

1. WHEN the test navigates to the Reliability tab, THE Browser_Instance SHALL click the "Reliability" tab element
2. WHEN entering test parameters, THE Test_Runner SHALL input confidence level and number of failures
3. WHEN entering Arrhenius parameters, THE Test_Runner SHALL input activation energy, use temperature, and test temperature
4. WHEN clicking calculate, THE Browser_Instance SHALL trigger the test duration calculation
5. WHEN results are calculated, THE Test_Runner SHALL verify test duration displays
6. WHEN results are calculated, THE Test_Runner SHALL verify acceleration factor displays

### Requirement 7: Error Handling Verification

**User Story:** As a test engineer, I want to verify error messages display correctly, so that I can ensure users receive helpful feedback for invalid inputs.

#### Acceptance Criteria

1. WHEN invalid confidence is entered (>100%), THE Test_Runner SHALL verify an error message displays
2. WHEN invalid reliability is entered (>100%), THE Test_Runner SHALL verify an error message displays
3. WHEN LSL >= USL in Variables tab, THE Test_Runner SHALL verify an error message displays
4. WHEN negative standard deviation is entered, THE Test_Runner SHALL verify an error message displays
5. WHEN error messages display, THE Test_Runner SHALL verify they contain clear guidance for correction

### Requirement 8: Test Isolation and Cleanup

**User Story:** As a test engineer, I want each test to run independently, so that test failures don't cascade and results are reliable.

#### Acceptance Criteria

1. WHEN a test completes, THE Test_Runner SHALL reset the browser state for the next test
2. WHEN a test fails, THE Test_Runner SHALL capture a screenshot for debugging
3. WHEN a test fails, THE Test_Runner SHALL capture browser console logs
4. WHEN all tests complete, THE Test_Runner SHALL ensure the Streamlit_App subprocess terminates
5. WHEN all tests complete, THE Test_Runner SHALL ensure all Browser_Instance resources are released

### Requirement 9: CI/CD Integration

**User Story:** As a DevOps engineer, I want UI tests to run in CI/CD pipelines, so that I can catch UI regressions automatically.

#### Acceptance Criteria

1. WHEN tests run in CI/CD, THE Test_Runner SHALL execute in headless mode
2. WHEN tests run in CI/CD, THE Test_Runner SHALL not require display server (X11/Wayland)
3. WHEN tests run in CI/CD, THE Test_Runner SHALL complete within reasonable time (< 10 minutes for full suite)
4. WHEN tests run in CI/CD, THE Test_Runner SHALL generate test reports compatible with CI systems
5. WHEN tests fail in CI/CD, THE Test_Runner SHALL upload screenshots as artifacts

### Requirement 10: URS Traceability

**User Story:** As a validation engineer, I want UI tests to maintain URS traceability, so that I can demonstrate compliance with REQ-25.

#### Acceptance Criteria

1. THE Test_Runner SHALL mark all UI tests with pytest marker `@pytest.mark.urs("REQ-25")`
2. THE Test_Runner SHALL mark all UI tests with pytest marker `@pytest.mark.urs("URS-VAL-03")`
3. WHEN validation certificate is generated, THE Test_Runner SHALL include Playwright UI test results
4. THE Test_Runner SHALL maintain the same traceability format as existing tests
5. THE Test_Runner SHALL enable filtering UI tests using pytest markers

### Requirement 11: Test Configuration

**User Story:** As a test engineer, I want to configure test behavior, so that I can adapt tests to different environments.

#### Acceptance Criteria

1. THE Test_Runner SHALL support configuration of Streamlit application port (default 8501)
2. THE Test_Runner SHALL support configuration of browser type (Chromium/Firefox/WebKit)
3. THE Test_Runner SHALL support configuration of headless mode (default True for CI, False for local)
4. THE Test_Runner SHALL support configuration of timeout values
5. THE Test_Runner SHALL read configuration from environment variables or pytest configuration

### Requirement 12: Existing Test Compatibility

**User Story:** As a test engineer, I want Playwright tests to coexist with existing tests, so that I don't break the current test suite.

#### Acceptance Criteria

1. THE Test_Runner SHALL allow running Playwright tests separately using pytest markers
2. THE Test_Runner SHALL allow running all tests together without conflicts
3. THE Test_Runner SHALL not modify existing test files or fixtures
4. THE Test_Runner SHALL use separate test files with clear naming (test_ui_playwright_*.py)
5. THE Test_Runner SHALL maintain compatibility with existing pytest configuration
