# Implementation Plan: Playwright UI Testing

## Overview

This implementation plan breaks down the Playwright UI testing feature into incremental, testable steps. Each task builds on previous work, with testing integrated throughout to catch issues early. The implementation will add true browser-based end-to-end testing to achieve full compliance with REQ-25.

## Tasks

- [x] 1. Install Playwright dependencies and verify setup
  - Add playwright and pytest-playwright to dev dependencies using `uv add --dev`
  - Install Chromium browser binaries using `uv run playwright install chromium`
  - Verify installation by running `uv run playwright --version`
  - Create `reports/screenshots/` directory for test artifacts
  - _Requirements: 2.1, 2.2, 11.2_

- [ ] 2. Create configuration model and environment variable support
  - [x] 2.1 Create `tests/playwright_config.py` with PlaywrightTestConfig Pydantic model
    - Define fields: streamlit_port, streamlit_host, browser_type, headless, timeout, screenshot_dir
    - Add app_url property method
    - Add validation for port range (1024-65535)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 2.2 Write unit tests for configuration model
    - Test default values load correctly
    - Test environment variable override
    - Test port validation
    - Test app_url property
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 2.3 Write property test for configuration
    - **Property 14: Configuration from Environment**
    - **Validates: Requirements 11.5**

- [ ] 3. Implement subprocess manager fixture
  - [x] 3.1 Add streamlit_app fixture to `tests/conftest.py`
    - Use session scope for fixture
    - Start Streamlit subprocess with appropriate arguments
    - Implement health check polling (30 second timeout)
    - Yield app URL when ready
    - Terminate subprocess in cleanup
    - Capture stdout/stderr for debugging
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 3.2 Write tests for subprocess manager
    - Test subprocess starts successfully
    - Test health check waits for app readiness
    - Test subprocess terminates after session
    - Test timeout error when app doesn't start
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 3.3 Write property test for subprocess health check
    - **Property 1: Subprocess Health Check**
    - **Validates: Requirements 1.2**
  
  - [x] 3.4 Write property test for resource cleanup
    - **Property 2: Resource Cleanup**
    - **Validates: Requirements 1.5, 8.5**

- [ ] 4. Checkpoint - Verify subprocess management works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement browser manager fixtures
  - [x] 5.1 Add browser fixture to `tests/conftest.py`
    - Use session scope for fixture
    - Launch Playwright browser (Chromium by default)
    - Read headless mode from environment variable
    - Configure default timeout
    - Close browser in cleanup
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 5.2 Add page fixture to `tests/conftest.py`
    - Use function scope for fixture
    - Create new page from browser
    - Navigate to streamlit_app URL
    - Wait for page load
    - Yield page to test
    - Capture screenshot on test failure
    - Capture console logs on test failure
    - Close page in cleanup
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x] 5.3 Write tests for browser fixtures
    - Test browser launches successfully
    - Test headless mode configuration
    - Test page creation and cleanup
    - Test screenshot capture on failure
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.2_
  
  - [x] 5.4 Write property test for test isolation
    - **Property 10: Test Isolation**
    - **Validates: Requirements 8.1**
  
  - [x] 5.5 Write property test for screenshot capture
    - **Property 11: Screenshot Capture on Failure**
    - **Validates: Requirements 8.2**
  
  - [x] 5.6 Write property test for console log capture
    - **Property 12: Console Log Capture on Failure**
    - **Validates: Requirements 8.3**

- [ ] 6. Create UI interaction helper functions
  - [x] 6.1 Add helper functions to `tests/conftest.py`
    - Implement click_tab(page, tab_name)
    - Implement fill_number_input(page, label, value)
    - Implement click_button(page, button_text)
    - Implement get_text_content(page, selector)
    - Implement wait_for_element(page, selector, timeout)
    - Use Playwright's get_by_role() and get_by_label() for accessibility
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 6.2 Write unit tests for helper functions
    - Test each helper function with mocked Page object
    - Test error handling for missing elements
    - Test timeout behavior
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 7. Checkpoint - Verify fixtures and helpers work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Attribute tab E2E tests
  - [x] 8.1 Create `tests/test_ui_playwright_attribute.py`
    - Add pytest markers: @pytest.mark.urs("REQ-25"), @pytest.mark.urs("URS-VAL-03"), @pytest.mark.playwright, @pytest.mark.e2e
    - Implement test_attribute_tab_renders()
    - Implement test_attribute_zero_failure_calculation() - verify n=29 for C=95%, R=90%
    - Implement test_attribute_sensitivity_analysis() - verify c=0,1,2,3 results display
    - Implement test_attribute_with_failures() - verify single result when c specified
    - Implement test_attribute_invalid_confidence() - verify error message for C>100%
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 7.1_
  
  - [x] 8.2 Write property test for tab navigation
    - **Property 3: Tab Navigation**
    - **Validates: Requirements 3.1, 4.1, 5.1, 6.1**
  
  - [x] 8.3 Write property test for numeric input interaction
    - **Property 4: Numeric Input Interaction**
    - **Validates: Requirements 3.2, 3.3, 4.2, 4.3, 6.2, 6.3**
  
  - [x] 8.4 Write property test for calculate button
    - **Property 5: Calculate Button Triggers Computation**
    - **Validates: Requirements 3.4, 4.4, 6.4**
  
  - [x] 8.5 Write property test for results display
    - **Property 6: Results Display After Calculation**
    - **Validates: Requirements 3.5, 4.5, 4.6, 4.7, 4.8, 5.4, 5.6, 5.7, 6.5, 6.6**

- [ ] 9. Implement Variables tab E2E tests
  - [x] 9.1 Create `tests/test_ui_playwright_variables.py`
    - Add pytest markers: @pytest.mark.urs("REQ-25"), @pytest.mark.urs("URS-VAL-03"), @pytest.mark.playwright, @pytest.mark.e2e
    - Implement test_variables_tab_renders()
    - Implement test_variables_basic_calculation() - verify tolerance factor, limits, Ppk display
    - Implement test_variables_with_spec_limits() - verify PASS/FAIL status displays
    - Implement test_variables_invalid_spec_limits() - verify error for LSL>=USL
    - Implement test_variables_negative_std_dev() - verify error message
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 7.3, 7.4_

- [ ] 10. Implement Non-Normal tab E2E tests
  - [x] 10.1 Create `tests/test_ui_playwright_non_normal.py`
    - Add pytest markers: @pytest.mark.urs("REQ-25"), @pytest.mark.urs("URS-VAL-03"), @pytest.mark.playwright, @pytest.mark.e2e
    - Implement test_non_normal_tab_renders()
    - Implement test_non_normal_outlier_detection() - verify outlier count displays
    - Implement test_non_normal_normality_tests() - verify Shapiro-Wilk and Anderson-Darling results
    - Implement test_non_normal_transformation() - verify transformation and results display
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_
  
  - [x] 10.2 Write property test for data input interaction
    - **Property 7: Data Input Interaction**
    - **Validates: Requirements 5.2**
  
  - [x] 10.3 Write property test for dropdown selection
    - **Property 8: Dropdown Selection**
    - **Validates: Requirements 5.8**

- [ ] 11. Implement Reliability tab E2E tests
  - [x] 11.1 Create `tests/test_ui_playwright_reliability.py`
    - Add pytest markers: @pytest.mark.urs("REQ-25"), @pytest.mark.urs("URS-VAL-03"), @pytest.mark.playwright, @pytest.mark.e2e
    - Implement test_reliability_tab_renders()
    - Implement test_reliability_calculation() - verify test duration and acceleration factor display
    - Implement test_reliability_invalid_reliability() - verify error message for R>100%
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.2_
  
  - [x] 11.2 Write property test for error messages
    - **Property 9: Error Messages for Invalid Inputs**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [ ] 12. Checkpoint - Verify all E2E tests work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Add pytest configuration and markers
  - [x] 13.1 Update `pyproject.toml` pytest configuration
    - Add playwright marker definition
    - Add e2e marker definition
    - Add slow marker definition
    - Document marker usage in comments
    - _Requirements: 10.5, 12.1_
  
  - [x] 13.2 Write property test for URS marker presence
    - **Property 13: URS Marker Presence**
    - **Validates: Requirements 10.1, 10.2, 10.4**

- [ ] 14. Update validation certificate generation
  - [x] 14.1 Verify `scripts/generate_validation_certificate.py` includes Playwright tests
    - Check that pytest collects tests with @pytest.mark.urs markers
    - Verify Playwright tests appear in certificate
    - Test certificate generation with Playwright tests
    - _Requirements: 10.3_

- [ ] 15. Create documentation and CI/CD examples
  - [x] 15.1 Update `tests/UI_TESTS_README.md`
    - Document Playwright test approach
    - Add installation instructions
    - Add usage examples (running tests, debugging)
    - Document environment variables
    - Add troubleshooting section
    - Mark AppTest approach as deprecated/alternative
    - _Requirements: 9.1, 9.2, 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [~] 15.2 Create `.github/workflows/playwright-tests.yml` example (optional)
    - Add workflow for running Playwright tests in CI
    - Include browser installation step
    - Configure headless mode
    - Add screenshot artifact upload on failure
    - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [ ] 16. Verify compatibility with existing tests
  - [x] 16.1 Run all tests together to verify no conflicts
    - Run `uv run pytest -q` to execute all tests
    - Verify Playwright tests can be filtered with markers
    - Verify existing tests still pass
    - Verify test count increases appropriately
    - _Requirements: 12.1, 12.2, 12.5_

- [ ] 17. Final checkpoint - Complete test suite validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test-related sub-tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- E2E tests validate complete user workflows through real browser
- All Playwright tests must include URS markers for REQ-25 compliance
- Tests should run in both headless (CI) and visible (local debugging) modes
- Screenshot and console log capture on failure aids debugging
