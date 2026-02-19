# Implementation Plan: Validation System

## Overview

This implementation plan breaks down the validation system into discrete coding tasks. The approach follows a bottom-up strategy: first implementing core data models and utilities, then building the state management and persistence layers, followed by orchestration logic, UI components, and finally integration with the main application.

Each task builds on previous tasks to ensure incremental progress with testable milestones. Property-based tests are included as optional sub-tasks to validate correctness properties while allowing for faster MVP delivery.

## Tasks

- [ ] 1. Set up validation module structure and data models
  - Create `src/sample_size_estimator/validation/` directory
  - Create `__init__.py` with module exports
  - Create `models.py` with all data classes: ValidationState, EnvironmentFingerprint, ValidationStatus, ValidationResult, IQResult, OQResult, PQResult, ValidationEvent, IQCheck, OQTest, PQTest
  - Add Pydantic ValidationConfig class with environment variable support
  - _Requirements: 15.1, 15.2, 4.2, 4.3, 17.1_

- [ ] 2. Implement ValidationStateManager core functionality
  - [ ] 2.1 Create `state_manager.py` with ValidationStateManager class
    - Implement `calculate_validation_hash()` method to hash all calculation files
    - Implement `get_environment_fingerprint()` to capture Python and dependency versions
    - Implement `compare_environments()` to detect environment changes
    - Implement `is_validation_expired()` to check expiry
    - Implement `check_validation_status()` to determine overall validation state
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ] 2.2 Write property test for hash calculation idempotence
    - **Property 5: Hash Calculation Idempotence**
    - **Validates: Requirements 3.4**

  - [ ] 2.3 Write property test for hash sensitivity to file changes
    - **Property 6: Hash Sensitivity to File Changes**
    - **Validates: Requirements 3.5**

  - [ ] 2.4 Write property test for hash file filtering
    - **Property 7: Hash Excludes Non-Python Files**
    - **Validates: Requirements 3.3**

  - [ ] 2.5 Write property test for environment fingerprint completeness
    - **Property 8: Environment Fingerprint Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [ ] 2.6 Write property test for environment comparison
    - **Property 9: Environment Comparison Detects All Differences**
    - **Validates: Requirements 4.4**

  - [ ] 2.7 Write property test for validation expiry calculation
    - **Property 10: Validation Expiry Calculation Correctness**
    - **Validates: Requirements 5.2, 5.3, 5.4**

  - [ ] 2.8 Write property test for validation state determination
    - **Property 3: Validation State Determination Correctness**
    - **Validates: Requirements 2.5, 2.6**

  - [ ] 2.9 Write unit tests for state manager edge cases
    - Test missing calculation files
    - Test permission errors
    - Test missing dependencies
    - _Requirements: 3.1, 4.2_

- [ ] 3. Implement ValidationPersistence for state storage
  - [ ] 3.1 Create `persistence.py` with ValidationPersistence class
    - Implement `save_validation_state()` to write JSON file
    - Implement `load_validation_state()` to read JSON file
    - Implement `verify_state_integrity()` to check for corruption
    - Implement `append_to_history()` to add events to JSONL log
    - Implement `get_validation_history()` to retrieve history
    - Add history log size limiting logic
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7_

  - [ ] 3.2 Write property test for persistence round trip
    - **Property 11: Validation State Persistence Round Trip**
    - **Validates: Requirements 15.3**

  - [ ] 3.3 Write property test for persisted state completeness
    - **Property 12: Persisted State Completeness**
    - **Validates: Requirements 15.2**

  - [ ] 3.4 Write property test for corrupted persistence detection
    - **Property 13: Corrupted Persistence Detection**
    - **Validates: Requirements 15.5**

  - [ ] 3.5 Write property test for history event completeness
    - **Property 14: History Event Completeness**
    - **Validates: Requirements 20.2, 20.3, 20.4, 20.5**

  - [ ] 3.6 Write property test for history retrieval ordering
    - **Property 15: History Retrieval Ordering**
    - **Validates: Requirements 20.6**

  - [ ] 3.7 Write property test for history log size limiting
    - **Property 16: History Log Size Limiting**
    - **Validates: Requirements 20.7**

  - [ ] 3.8 Write unit tests for persistence edge cases
    - Test missing persistence directory
    - Test file write failures
    - Test corrupted JSON
    - Test missing required fields
    - _Requirements: 15.4, 15.5, 15.6_

- [ ] 4. Checkpoint - Ensure core validation logic tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement IQ test execution
  - [ ] 5.1 Create IQ test functions in `tests/test_validation_iq.py`
    - Write test to verify all required packages are installed
    - Write test to verify package versions match uv.lock
    - Write test to verify Python version meets requirements
    - Write test to verify calculation engine files exist
    - Write test to verify configuration files are valid
    - Mark all tests with `@pytest.mark.iq` and appropriate `@pytest.mark.urs()` markers
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ] 5.2 Write unit tests for IQ test execution
    - Test IQ result aggregation
    - Test IQ failure handling
    - _Requirements: 7.6, 7.7_

- [ ] 6. Implement OQ test execution
  - [ ] 6.1 Add URS markers to existing calculation tests
    - Update `tests/test_attribute_calcs.py` with `@pytest.mark.oq` and `@pytest.mark.urs()` markers
    - Update `tests/test_variables_calcs.py` with markers
    - Update `tests/test_non_normal_calcs.py` with markers
    - Update `tests/test_reliability_calcs.py` with markers
    - Map each test to its corresponding URS requirement from sample-size-estimator spec
    - _Requirements: 8.1, 8.2, 14.1, 14.2_

  - [ ] 6.2 Write unit tests for OQ test execution
    - Test OQ result aggregation
    - Test OQ failure handling
    - Test URS marker extraction
    - _Requirements: 8.7, 8.8_

- [ ] 7. Implement PQ test execution
  - [ ] 7.1 Add URS markers to existing Playwright UI tests
    - Update `tests/test_ui_playwright_attribute.py` with `@pytest.mark.pq` and `@pytest.mark.urs()` markers
    - Update `tests/test_ui_playwright_variables.py` with markers
    - Update `tests/test_ui_playwright_non_normal.py` with markers
    - Update `tests/test_ui_playwright_reliability.py` with markers
    - Map each test to its corresponding URS requirement
    - _Requirements: 9.1, 9.2, 14.1, 14.2_

  - [ ] 7.2 Implement PDF validation tests
    - [ ] 7.2.1 Add pdfplumber dependency for PDF text extraction
      - Run `uv add pdfplumber`
      - _Requirements: 29.2_

    - [ ] 7.2.2 Create PDF extraction utility functions
      - Create `tests/utils/pdf_validator.py` with `extract_pdf_text()` function
      - Create parsing functions for each module: `parse_attribute_results()`, `parse_variables_results()`, etc.
      - _Requirements: 29.2, 29.3_

    - [ ] 7.2.3 Write PDF validation tests for Attribute module
      - Create `tests/test_pdf_validation_attribute.py`
      - Test that PDF report shows same sample size as calculation
      - Test that PDF shows correct AQL/RQL values
      - Mark with `@pytest.mark.pq` and `@pytest.mark.urs()` markers
      - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

    - [ ] 7.2.4 Write PDF validation tests for Variables module
      - Create `tests/test_pdf_validation_variables.py`
      - Test that PDF shows correct sample size and tolerance factors
      - Test that PDF shows correct Ppk values
      - Mark with `@pytest.mark.pq` and `@pytest.mark.urs()` markers
      - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

    - [ ] 7.2.5 Write PDF validation tests for Non-Normal module
      - Create `tests/test_pdf_validation_non_normal.py`
      - Test that PDF shows correct transformed sample sizes
      - Test that PDF shows normality test results
      - Mark with `@pytest.mark.pq` and `@pytest.mark.urs()` markers
      - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

    - [ ] 7.2.6 Write PDF validation tests for Reliability module
      - Create `tests/test_pdf_validation_reliability.py`
      - Test that PDF shows correct test duration
      - Test that PDF shows correct acceleration factors
      - Mark with `@pytest.mark.pq` and `@pytest.mark.urs()` markers
      - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5_

    - [ ] 7.2.7 Write property test for PDF report accuracy
      - **Property 21: PDF Report Accuracy**
      - **Validates: Requirements 29.1, 29.2, 29.3, 29.4**

  - [ ] 7.3 Write unit tests for PQ test execution
    - Test PQ result aggregation
    - Test PQ failure handling
    - Test workflow description extraction
    - _Requirements: 9.6, 9.7_

- [ ] 8. Implement ValidationOrchestrator
  - [ ] 8.1 Create `orchestrator.py` with ValidationOrchestrator class
    - Implement `execute_validation_workflow()` to run IQ/OQ/PQ in sequence
    - Implement `execute_iq_tests()` to run pytest with `-m iq` marker
    - Implement `execute_oq_tests()` to run pytest with `-m oq` marker
    - Implement `execute_pq_tests()` to run pytest with `-m pq` marker
    - Add progress callback support for UI updates
    - Add subprocess management for test execution
    - Parse pytest output to extract test results and URS markers
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ] 8.2 Write integration tests for validation orchestrator
    - Test complete IQ/OQ/PQ workflow
    - Test workflow stops on failure
    - Test progress callback invocation
    - _Requirements: 6.3, 6.4, 6.5_

- [ ] 9. Checkpoint - Ensure orchestration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement ValidationCertificateGenerator
  - [ ] 10.1 Create `certificate.py` with ValidationCertificateGenerator class
    - Implement `generate_certificate()` main method
    - Implement `generate_title_page()` with validation date and status
    - Implement `generate_system_info_section()` with OS, Python, dependencies
    - Implement `generate_iq_chapter()` with IQ test results table
    - Implement `generate_oq_chapter()` with OQ test results grouped by functional area
    - Implement `generate_pq_chapter()` with PQ test results grouped by module
    - Implement `generate_traceability_matrix()` showing URS to test mapping
    - Calculate and return certificate SHA-256 hash
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 14.2, 14.3, 14.4, 14.5, 26.1, 26.2_

  - [ ] 10.2 Write unit tests for certificate generation
    - Test PDF generation with mock data
    - Test chapter formatting
    - Test traceability matrix generation
    - Test certificate hash calculation
    - _Requirements: 10.1, 10.8, 26.1, 26.2_

- [ ] 11. Implement ValidationUI components
  - [ ] 11.1 Create `ui.py` with ValidationUI class
    - Implement `render_validation_button()` with red/green color based on state
    - Implement `render_validation_metrics_dashboard()` showing status, expiry, test counts
    - Implement `render_validation_progress()` with phase and percentage
    - Implement `render_validation_result()` with success/failure message
    - Implement `render_validation_failure_details()` with specific failure reasons
    - Implement `render_expiry_warning()` for 30-day and 7-day thresholds
    - Implement `render_non_validated_banner()` for persistent warning
    - Use Streamlit components: st.button, st.progress, st.metric, st.warning, st.error, st.success
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 18.1, 18.2, 18.3, 18.4, 18.5, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 25.2, 27.1, 27.2, 27.3, 27.4, 27.5, 27.6, 28.1, 28.2, 28.3, 28.4_

  - [ ] 11.2 Write property test for button color
    - **Property 1: Button Color Reflects Validation State**
    - **Validates: Requirements 1.2, 1.3**

  - [ ] 11.3 Write property test for button text
    - **Property 2: Button Text Reflects Validation State**
    - **Validates: Requirements 1.5**

  - [ ] 11.4 Write unit tests for UI components
    - Test button rendering with various states
    - Test metrics dashboard display
    - Test progress indicator updates
    - Test warning message display
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 21.1, 21.2, 21.3, 28.1, 28.2_

- [ ] 12. Integrate validation system into main application
  - [ ] 12.1 Update `main.py` to add validation UI
    - Import ValidationUI and related components
    - Initialize ValidationStateManager, ValidationPersistence, ValidationOrchestrator
    - Add validation button to sidebar
    - Add validation metrics dashboard to sidebar
    - Check validation status on startup
    - Display expiry warnings if applicable
    - Display non-validated banner if not validated
    - Handle validation button click to trigger workflow
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 25.1, 25.2, 28.1, 28.2_

  - [ ] 12.2 Add validation disclaimer to report generation
    - Update report generation functions to check validation status
    - Add disclaimer text to reports when not validated
    - Include validation hash in reports
    - _Requirements: 25.3_

  - [ ] 12.3 Write integration tests for main application
    - Test validation button appears in UI
    - Test validation status check on startup
    - Test validation workflow execution from UI
    - Test report disclaimer when not validated
    - _Requirements: 1.1, 16.1, 25.1, 25.3_

- [ ] 13. Checkpoint - Ensure UI integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement command-line validation script
  - [ ] 14.1 Create `scripts/validate.py` CLI script
    - Accept command-line arguments: --output-dir, --expiry-days
    - Initialize validation components
    - Execute validation workflow
    - Display progress to console
    - Generate validation certificate
    - Update validation persistence
    - Return exit code 0 on success, non-zero on failure
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6_

  - [ ] 14.2 Write unit tests for CLI script
    - Test argument parsing
    - Test exit codes
    - Test output directory creation
    - _Requirements: 19.2, 19.3_

- [ ] 15. Implement certificate verification tool
  - [ ] 15.1 Create `scripts/verify_certificate.py` CLI script
    - Accept certificate path as argument
    - Calculate certificate hash
    - Load validation persistence to get stored hash
    - Compare hashes and display VALID or TAMPERED status
    - _Requirements: 26.3, 26.4, 26.5_

  - [ ] 15.2 Write unit tests for certificate verification
    - Test valid certificate verification
    - Test tampered certificate detection
    - _Requirements: 26.4, 26.5_

- [ ] 16. Add validation configuration to environment
  - [ ] 16.1 Update `.env.example` with validation configuration
    - Add VALIDATION_EXPIRY_DAYS with default 365
    - Add VALIDATION_TRACKED_DEPENDENCIES with default list
    - Add VALIDATION_PERSISTENCE_DIR with default .validation
    - Add VALIDATION_CERTIFICATE_OUTPUT_DIR with default reports
    - Add VALIDATION_REMINDER_THRESHOLDS with default [30, 7]
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 28.4_

  - [ ] 16.2 Update configuration documentation
    - Document all validation configuration parameters in README or docs
    - Provide examples of configuration values
    - _Requirements: 17.5_

- [ ] 17. Implement validation history display command
  - [ ] 17.1 Create `scripts/show_validation_history.py` CLI script
    - Load validation history from persistence
    - Display events in reverse chronological order
    - Format output as readable table
    - Support --limit argument to control number of entries
    - _Requirements: 20.6_

  - [ ] 17.2 Write unit tests for history display
    - Test history retrieval
    - Test output formatting
    - Test limit parameter
    - _Requirements: 20.6_

- [ ] 18. Add validation logging
  - [ ] 18.1 Update validation components to use logging
    - Add log statements for validation workflow start/end
    - Add log statements for each test phase execution
    - Add log statements for validation state changes
    - Add log statements for hash mismatches
    - Add log statements for environment changes
    - Add log statements for expiry events
    - Configure log level from environment variable
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 25.4_

  - [ ] 18.2 Write unit tests for logging
    - Test log messages are generated
    - Test log level configuration
    - _Requirements: 23.6_

- [ ] 19. Add certificate access from UI
  - [ ] 19.1 Update ValidationUI to add certificate access
    - Add button to open latest validation certificate
    - Display certificate generation date
    - Display message when no certificate exists
    - Use Streamlit file download or link to open PDF
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_

  - [ ] 19.2 Write unit tests for certificate access UI
    - Test button rendering
    - Test date display
    - Test missing certificate message
    - _Requirements: 22.3, 22.5_

- [ ] 20. Implement graceful degradation for non-validated state
  - [ ] 20.1 Update main application to allow calculations when not validated
    - Ensure all calculation functions work regardless of validation state
    - Add logging for calculations performed in non-validated state
    - Add acknowledgment mechanism for users to proceed
    - _Requirements: 25.1, 25.4, 25.5_

  - [ ] 20.2 Write integration tests for graceful degradation
    - Test calculations work when not validated
    - Test logging of non-validated calculations
    - Test user acknowledgment flow
    - _Requirements: 25.1, 25.4, 25.5_

- [ ] 21. Final checkpoint - Complete validation system testing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 22. Update documentation
  - [ ] 22.1 Update README with validation system information
    - Add section explaining validation system
    - Document how to run validation
    - Document how to check validation status
    - Document validation certificate location
    - _Requirements: All_

  - [ ] 22.2 Create validation system user guide
    - Document validation workflow
    - Document validation status indicators
    - Document validation expiry and renewal
    - Document troubleshooting common validation issues
    - _Requirements: All_

  - [ ] 22.3 Create validation system developer guide
    - Document validation architecture
    - Document how to add new validation checks
    - Document how to extend IQ/OQ/PQ tests
    - Document validation persistence format
    - _Requirements: All_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The validation system leverages existing test infrastructure (pytest, Playwright)
- New dependency: hypothesis (for property-based testing)
- All validation state is persisted to survive application restarts
- The system is designed to be non-blocking - validation runs in background
