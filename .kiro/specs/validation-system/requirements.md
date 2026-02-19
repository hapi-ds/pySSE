# Requirements Document

## Introduction

The Validation System is an enhancement to the Sample Size Estimator application that implements a comprehensive IQ/OQ/PQ (Installation Qualification, Operational Qualification, Performance Qualification) validation workflow. This system provides visual validation status indicators, automated validation testing, and generates detailed validation certificates that trace back to the User Requirements Specification (URS) defined in the sample-size-estimator spec.

The validation system ensures regulatory compliance by tracking code changes, dependency versions, validation expiry, and test results. It provides quality managers and validation specialists with clear evidence that the application remains in a validated state and meets all specified requirements.

## Glossary

- **System**: The Validation System module within the Sample Size Estimator application
- **Validation_Button**: A prominent GUI element that displays validation status and initiates validation workflows
- **Validation_State**: The current status of the system (VALIDATED or NOT_VALIDATED)
- **IQ**: Installation Qualification - verification that dependencies and environment are correctly configured
- **OQ**: Operational Qualification - verification that all mathematical models and calculations produce correct results
- **PQ**: Performance Qualification - verification that the user interface functions correctly in realistic usage scenarios
- **Validation_Hash**: SHA-256 cryptographic hash of all calculation engine files
- **Validation_Expiry**: Configurable time period after which validation must be renewed
- **Validation_Certificate**: Comprehensive PDF document containing IQ/OQ/PQ test results and traceability to URS requirements
- **URS**: User Requirements Specification - the requirements defined in .kiro/specs/sample-size-estimator/requirements.md
- **Environment_Fingerprint**: Snapshot of Python version and key dependency versions
- **Validation_Persistence**: Storage mechanism for validation state across application restarts

## Requirements

### Requirement 1: Validation Status Button Display

**User Story:** As a quality manager, I want to see a prominent validation status indicator in the GUI, so that I can immediately know if the system is in a validated state.

#### Acceptance Criteria

1. THE System SHALL display a large validation button in the main application interface
2. WHEN the Validation_State is NOT_VALIDATED, THE System SHALL render the button with a red background color
3. WHEN the Validation_State is VALIDATED, THE System SHALL render the button with a green background color
4. THE System SHALL display the text "VALIDATION STATUS" on the button
5. THE System SHALL display the current validation state text (VALIDATED or NOT VALIDATED) on the button
6. THE System SHALL position the button prominently so it is visible without scrolling

### Requirement 2: Validation Status Determination

**User Story:** As a validation specialist, I want the system to automatically determine validation status based on multiple criteria, so that I can ensure the system remains compliant.

#### Acceptance Criteria

1. THE System SHALL check if the Validation_Hash of the calculation engine matches the stored validated hash
2. THE System SHALL check if the validation age is less than the configured Validation_Expiry period (in days)
3. THE System SHALL check if the Environment_Fingerprint (Python version and key dependencies) matches the validated environment
4. THE System SHALL check if all IQ/OQ/PQ tests passed in the last validation run
5. WHEN all four criteria are met, THE System SHALL set Validation_State to VALIDATED
6. WHEN any criterion fails, THE System SHALL set Validation_State to NOT_VALIDATED
7. THE System SHALL provide detailed information about which criteria failed

### Requirement 3: Validation Hash Calculation

**User Story:** As a validation specialist, I want the system to calculate a hash of all calculation engine files, so that any code changes are detected.

#### Acceptance Criteria

1. THE System SHALL calculate SHA-256 hashes for all Python files in the calculations directory
2. THE System SHALL combine individual file hashes into a single Validation_Hash
3. THE System SHALL exclude __pycache__ directories and non-Python files from hash calculation
4. THE System SHALL sort files alphabetically before hashing to ensure consistent results
5. WHEN any calculation file is modified, THE System SHALL produce a different Validation_Hash

### Requirement 4: Environment Fingerprint Tracking

**User Story:** As a validation specialist, I want to track the system environment, so that I can detect when dependencies or Python versions change.

#### Acceptance Criteria

1. THE System SHALL capture the Python version (major.minor.patch format)
2. THE System SHALL capture versions of key dependencies: scipy, numpy, streamlit, pydantic, reportlab, pytest, playwright
3. THE System SHALL store the Environment_Fingerprint as a JSON structure
4. WHEN comparing environments, THE System SHALL flag differences in Python version or any key dependency version
5. THE System SHALL allow configuration of which dependencies are considered "key" for validation purposes

### Requirement 5: Validation Expiry Tracking

**User Story:** As a quality manager, I want validation to expire after a configurable period, so that we perform regular revalidation as required by our quality system.

#### Acceptance Criteria

1. THE System SHALL store the timestamp of the last successful validation
2. THE System SHALL calculate the age of the validation in days
3. THE System SHALL compare the validation age against a configurable Validation_Expiry value (default: 365 days)
4. WHEN the validation age exceeds Validation_Expiry, THE System SHALL set Validation_State to NOT_VALIDATED
5. THE System SHALL display the validation date and days remaining until expiry

### Requirement 6: Validation Workflow Initiation

**User Story:** As a validation specialist, I want to start the full validation process by clicking the validation button, so that I can execute IQ/OQ/PQ testing.

#### Acceptance Criteria

1. WHEN a user clicks the validation button, THE System SHALL initiate the complete validation workflow
2. THE System SHALL display a progress indicator showing the current validation phase (IQ, OQ, or PQ)
3. THE System SHALL execute IQ tests first, then OQ tests, then PQ tests in sequence
4. WHEN any phase fails, THE System SHALL stop the workflow and display the failure details
5. WHEN all phases pass, THE System SHALL update the Validation_State to VALIDATED

### Requirement 7: Installation Qualification (IQ) Tests

**User Story:** As a validation specialist, I want automated IQ tests to verify the installation, so that I can confirm all dependencies are correctly configured.

#### Acceptance Criteria

1. THE System SHALL verify that all required Python packages are installed
2. THE System SHALL verify that package versions match the locked versions in uv.lock or requirements.txt
3. THE System SHALL verify that the Python version meets minimum requirements
4. THE System SHALL verify that all calculation engine files are present and readable
5. THE System SHALL verify that configuration files (.env) are present and valid
6. WHEN all IQ checks pass, THE System SHALL record IQ status as PASS
7. WHEN any IQ check fails, THE System SHALL record IQ status as FAIL with specific failure details

### Requirement 8: Operational Qualification (OQ) Tests

**User Story:** As a validation specialist, I want automated OQ tests to verify calculations, so that I can confirm all mathematical models produce correct results.

#### Acceptance Criteria

1. THE System SHALL execute all pytest tests that verify calculation functions
2. THE System SHALL map each OQ test to its corresponding URS requirement ID
3. THE System SHALL verify attribute data calculations (zero failures and with failures)
4. THE System SHALL verify variable data calculations (tolerance factors, tolerance limits, Ppk)
5. THE System SHALL verify non-normal data handling (transformations, normality tests)
6. THE System SHALL verify reliability calculations (zero-failure demonstration, acceleration factors)
7. WHEN all OQ tests pass, THE System SHALL record OQ status as PASS
8. WHEN any OQ test fails, THE System SHALL record OQ status as FAIL with specific test failures

### Requirement 9: Performance Qualification (PQ) Tests

**User Story:** As a validation specialist, I want automated PQ tests to verify the user interface, so that I can confirm the application functions correctly in realistic usage scenarios.

#### Acceptance Criteria

1. THE System SHALL execute all Playwright UI tests that simulate user workflows
2. THE System SHALL verify that each analysis module tab (Attribute, Variables, Non-Normal, Reliability) is accessible
3. THE System SHALL verify that users can enter data, click calculate buttons, and see results
4. THE System SHALL verify that error messages display correctly for invalid inputs
5. THE System SHALL verify that PDF reports can be generated
6. WHEN all PQ tests pass, THE System SHALL record PQ status as PASS
7. WHEN any PQ test fails, THE System SHALL record PQ status as FAIL with specific test failures

### Requirement 10: Validation Certificate Generation

**User Story:** As a validation specialist, I want a comprehensive validation certificate PDF, so that I can document IQ/OQ/PQ completion for regulatory submissions.

#### Acceptance Criteria

1. WHEN validation completes successfully, THE System SHALL generate a Validation_Certificate PDF
2. THE Validation_Certificate SHALL include a title page with validation date, tester name, and overall status
3. THE Validation_Certificate SHALL include a system information section with OS, Python version, and dependency versions
4. THE Validation_Certificate SHALL include a separate chapter for IQ results
5. THE Validation_Certificate SHALL include a separate chapter for OQ results
6. THE Validation_Certificate SHALL include a separate chapter for PQ results
7. THE Validation_Certificate SHALL include the Validation_Hash and validation expiry date
8. THE System SHALL save the certificate to a reports directory with a timestamped filename

### Requirement 11: IQ Chapter Content

**User Story:** As a validation specialist, I want the IQ chapter to show installation verification details, so that I can document that the system is correctly installed.

#### Acceptance Criteria

1. THE IQ chapter SHALL list all required dependencies with their expected and actual versions
2. THE IQ chapter SHALL show PASS or FAIL status for each dependency check
3. THE IQ chapter SHALL display the Python version verification result
4. THE IQ chapter SHALL display the configuration file verification result
5. THE IQ chapter SHALL display the calculation engine file verification result
6. THE IQ chapter SHALL include a summary showing total checks, passed checks, and failed checks

### Requirement 12: OQ Chapter Content

**User Story:** As a validation specialist, I want the OQ chapter to show calculation verification details, so that I can document that all mathematical models are correct.

#### Acceptance Criteria

1. THE OQ chapter SHALL list all OQ tests with their corresponding URS requirement IDs
2. THE OQ chapter SHALL show PASS or FAIL status for each test
3. THE OQ chapter SHALL group tests by functional area (Attribute, Variables, Non-Normal, Reliability)
4. THE OQ chapter SHALL reference the specific URS requirement being validated by each test
5. THE OQ chapter SHALL include a summary showing total tests, passed tests, and failed tests
6. THE OQ chapter SHALL display the test execution timestamp

### Requirement 13: PQ Chapter Content

**User Story:** As a validation specialist, I want the PQ chapter to show UI verification details, so that I can document that the user interface functions correctly.

#### Acceptance Criteria

1. THE PQ chapter SHALL list all PQ tests with their corresponding URS requirement IDs
2. THE PQ chapter SHALL show PASS or FAIL status for each UI test
3. THE PQ chapter SHALL group tests by analysis module (Attribute, Variables, Non-Normal, Reliability)
4. THE PQ chapter SHALL describe the user workflow being tested
5. THE PQ chapter SHALL include a summary showing total tests, passed tests, and failed tests
6. THE PQ chapter SHALL display the test execution timestamp

### Requirement 14: URS Traceability

**User Story:** As a quality manager, I want each test to reference its URS requirement, so that I can demonstrate complete traceability from requirements to verification.

#### Acceptance Criteria

1. THE System SHALL use pytest markers to tag each test with its URS requirement ID (e.g., @pytest.mark.urs("URS-FUNC_A-02"))
2. THE System SHALL extract URS markers from test results
3. THE Validation_Certificate SHALL display the URS requirement ID next to each test result
4. THE System SHALL verify that all URS requirements have at least one corresponding test
5. THE System SHALL generate a traceability matrix showing which tests validate which requirements

### Requirement 15: Validation State Persistence

**User Story:** As a user, I want the validation state to persist across application restarts, so that I don't need to revalidate every time I start the application.

#### Acceptance Criteria

1. THE System SHALL store validation state in a JSON file in a .validation directory
2. THE Validation_Persistence file SHALL include: validation timestamp, Validation_Hash, Environment_Fingerprint, IQ/OQ/PQ status, and expiry date
3. THE System SHALL load validation state from the persistence file on application startup
4. WHEN the persistence file does not exist, THE System SHALL set Validation_State to NOT_VALIDATED
5. THE System SHALL validate the integrity of the persistence file (check for corruption or tampering)
6. WHEN the persistence file is invalid, THE System SHALL set Validation_State to NOT_VALIDATED

### Requirement 16: Validation Status Check on Startup

**User Story:** As a quality manager, I want the system to check validation status when it starts, so that users are immediately informed if revalidation is needed.

#### Acceptance Criteria

1. WHEN the application starts, THE System SHALL load the persisted validation state
2. THE System SHALL recalculate the current Validation_Hash and compare it to the stored hash
3. THE System SHALL check if the validation has expired
4. THE System SHALL check if the Environment_Fingerprint has changed
5. WHEN any check fails, THE System SHALL update Validation_State to NOT_VALIDATED
6. THE System SHALL display a warning message if validation is required

### Requirement 17: Validation Configuration

**User Story:** As a system administrator, I want to configure validation parameters, so that I can adapt the system to our quality system requirements.

#### Acceptance Criteria

1. THE System SHALL support configuration of Validation_Expiry in days via environment variable or config file
2. THE System SHALL support configuration of which dependencies are tracked in Environment_Fingerprint
3. THE System SHALL support configuration of the validation persistence file location
4. THE System SHALL support configuration of the validation certificate output directory
5. THE System SHALL provide default values for all configuration parameters
6. THE System SHALL validate configuration values and display errors for invalid settings

### Requirement 18: Validation Failure Details

**User Story:** As a validation specialist, I want detailed information about validation failures, so that I can quickly identify and resolve issues.

#### Acceptance Criteria

1. WHEN Validation_Hash does not match, THE System SHALL display both the current hash and the expected hash
2. WHEN validation has expired, THE System SHALL display the validation date and the expiry date
3. WHEN Environment_Fingerprint has changed, THE System SHALL display which dependencies or Python version changed
4. WHEN tests fail, THE System SHALL display the test name, URS requirement ID, and failure reason
5. THE System SHALL provide actionable guidance for resolving each type of validation failure

### Requirement 19: Manual Validation Trigger

**User Story:** As a validation specialist, I want to manually trigger validation from the command line, so that I can run validation as part of CI/CD pipelines or scheduled tasks.

#### Acceptance Criteria

1. THE System SHALL provide a command-line script to execute the full validation workflow
2. THE script SHALL accept command-line arguments for configuration (output directory, expiry days)
3. THE script SHALL return exit code 0 when validation passes and non-zero when validation fails
4. THE script SHALL display progress information during execution
5. THE script SHALL generate the Validation_Certificate PDF upon completion
6. THE script SHALL update the Validation_Persistence file upon successful validation

### Requirement 20: Validation History Tracking

**User Story:** As a quality manager, I want to maintain a history of validation events, so that I can demonstrate ongoing compliance over time.

#### Acceptance Criteria

1. THE System SHALL maintain a validation history log file
2. THE history log SHALL record each validation attempt with timestamp, result, and Validation_Hash
3. THE history log SHALL record validation expiry events
4. THE history log SHALL record detected code changes (hash mismatches)
5. THE history log SHALL record detected environment changes
6. THE System SHALL provide a command to display validation history
7. THE System SHALL limit history log size (e.g., keep last 100 entries or 2 years of data)

### Requirement 21: Validation Button Interaction Feedback

**User Story:** As a user, I want clear feedback when I click the validation button, so that I understand what is happening during the validation process.

#### Acceptance Criteria

1. WHEN a user clicks the validation button, THE System SHALL disable the button to prevent multiple simultaneous validations
2. THE System SHALL display a progress spinner or animation during validation
3. THE System SHALL display the current phase (IQ, OQ, PQ) being executed
4. THE System SHALL display a progress percentage or step counter (e.g., "Step 2 of 3")
5. WHEN validation completes, THE System SHALL display a success message with the validation date
6. WHEN validation fails, THE System SHALL display an error message with failure details
7. THE System SHALL re-enable the button after validation completes

### Requirement 22: Validation Certificate Accessibility

**User Story:** As a quality manager, I want to easily access the latest validation certificate, so that I can provide it for audits or regulatory submissions.

#### Acceptance Criteria

1. THE System SHALL save the latest validation certificate with a consistent filename (e.g., validation_certificate_latest.pdf)
2. THE System SHALL also save timestamped copies of all validation certificates
3. THE System SHALL provide a button or link in the GUI to open the latest validation certificate
4. THE System SHALL display the validation certificate generation date in the GUI
5. WHEN no validation certificate exists, THE System SHALL display a message indicating validation is required

### Requirement 23: Test Execution Logging

**User Story:** As a validation specialist, I want detailed logs of test execution, so that I can troubleshoot test failures and understand test behavior.

#### Acceptance Criteria

1. THE System SHALL log the start and end time of each validation phase (IQ, OQ, PQ)
2. THE System SHALL log each individual test execution with test name, URS ID, and result
3. THE System SHALL log any exceptions or errors that occur during testing
4. THE System SHALL log the final validation result and Validation_Hash
5. THE System SHALL store test execution logs in a structured format (JSON or similar)
6. THE System SHALL provide a configuration option to set log verbosity level

### Requirement 24: Validation System Self-Test

**User Story:** As a developer, I want the validation system itself to be tested, so that I can ensure the validation logic is correct.

#### Acceptance Criteria

1. THE System SHALL include unit tests for validation hash calculation
2. THE System SHALL include unit tests for environment fingerprint comparison
3. THE System SHALL include unit tests for validation expiry calculation
4. THE System SHALL include unit tests for validation state determination logic
5. THE System SHALL include unit tests for validation persistence (save/load)
6. THE System SHALL include integration tests for the complete validation workflow
7. THE validation system tests SHALL achieve at least 90% code coverage

### Requirement 25: Graceful Degradation

**User Story:** As a user, I want the application to remain usable even when validation fails, so that I can still perform calculations while addressing validation issues.

#### Acceptance Criteria

1. WHEN Validation_State is NOT_VALIDATED, THE System SHALL still allow users to access all calculation functions
2. THE System SHALL display a persistent warning banner when not validated
3. THE System SHALL include a disclaimer in generated reports when the system is not validated
4. THE System SHALL log all calculations performed in a non-validated state
5. THE System SHALL allow users to acknowledge the non-validated state and proceed

### Requirement 26: Validation Certificate Signing

**User Story:** As a quality manager, I want validation certificates to include digital signatures or checksums, so that I can verify certificate authenticity and detect tampering.

#### Acceptance Criteria

1. THE System SHALL calculate a SHA-256 hash of the validation certificate PDF
2. THE System SHALL include the certificate hash in the validation persistence file
3. THE System SHALL provide a command-line tool to verify certificate integrity
4. WHEN verifying a certificate, THE System SHALL recalculate the hash and compare it to the stored hash
5. THE System SHALL display VALID or TAMPERED status when verifying certificates

### Requirement 27: Validation Metrics Dashboard

**User Story:** As a quality manager, I want to see validation metrics at a glance, so that I can monitor validation health without reading detailed reports.

#### Acceptance Criteria

1. THE System SHALL display the current Validation_State (VALIDATED or NOT_VALIDATED)
2. THE System SHALL display the validation date and days until expiry
3. THE System SHALL display the number of IQ/OQ/PQ tests passed and failed
4. THE System SHALL display the current Validation_Hash (truncated for display)
5. THE System SHALL display the Environment_Fingerprint status (MATCH or CHANGED)
6. THE System SHALL provide a visual indicator (icon or color) for each metric

### Requirement 28: Validation Reminder Notifications

**User Story:** As a quality manager, I want to receive reminders before validation expires, so that I can plan revalidation activities proactively.

#### Acceptance Criteria

1. WHEN validation will expire within 30 days, THE System SHALL display a warning message on startup
2. WHEN validation will expire within 7 days, THE System SHALL display a prominent warning banner
3. THE System SHALL include the expiry date and days remaining in warning messages
4. THE System SHALL provide a configuration option to set reminder thresholds (e.g., 30 days, 7 days)
5. THE System SHALL log validation reminder events to the validation history

