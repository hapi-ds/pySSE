# Design Document: Validation System

## Overview

The Validation System is a comprehensive IQ/OQ/PQ validation framework integrated into the Sample Size Estimator application. It provides automated validation testing, persistent validation state tracking, visual status indicators, and detailed validation certificate generation with full traceability to URS requirements.

The system follows a layered architecture with clear separation between validation logic, persistence, UI components, and certificate generation. It leverages existing pytest and Playwright test infrastructure while adding validation-specific orchestration, state management, and reporting capabilities.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │ Validation Button│  │  Validation Metrics Dashboard   │ │
│  │  (Red/Green)     │  │  (Status, Expiry, Test Results) │ │
│  └──────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Validation Orchestration Layer                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ValidationOrchestrator                               │  │
│  │  - Execute IQ/OQ/PQ workflow                          │  │
│  │  - Coordinate test execution                          │  │
│  │  - Update validation state                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│  IQ Tests    │  │   OQ Tests       │  │  PQ Tests    │
│  (pytest)    │  │   (pytest)       │  │  (Playwright)│
└──────────────┘  └──────────────────┘  └──────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Validation State Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ValidationStateManager                               │  │
│  │  - Calculate validation hash                          │  │
│  │  - Check environment fingerprint                      │  │
│  │  - Check expiry                                       │  │
│  │  - Determine validation status                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Persistence Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ValidationPersistence                                │  │
│  │  - Save/load validation state (JSON)                  │  │
│  │  - Maintain validation history log                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Certificate Generation Layer                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ValidationCertificateGenerator                       │  │
│  │  - Generate PDF with IQ/OQ/PQ chapters               │  │
│  │  - Include URS traceability                          │  │
│  │  - Calculate certificate hash                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Validation logic, persistence, UI, and reporting are cleanly separated
2. **Testability**: All components are unit-testable with clear interfaces
3. **Extensibility**: New validation checks can be added without modifying core logic
4. **Reliability**: Validation state is persisted and verified on every startup
5. **Traceability**: Every test is linked to URS requirements through pytest markers

## Components and Interfaces

### 1. ValidationStateManager

Manages validation state determination and hash calculation.

```python
class ValidationStateManager:
    """
    Manages validation state determination based on multiple criteria.
    """
    
    def __init__(self, config: ValidationConfig):
        """
        Initialize with validation configuration.
        
        Args:
            config: Configuration including expiry days, tracked dependencies
        """
        self.config = config
    
    def calculate_validation_hash(self) -> str:
        """
        Calculate combined SHA-256 hash of all calculation engine files.
        
        Returns:
            Hexadecimal hash string
        
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
        """
        pass
    
    def get_environment_fingerprint(self) -> EnvironmentFingerprint:
        """
        Capture current Python version and dependency versions.
        
        Returns:
            EnvironmentFingerprint object with version information
        
        Validates: Requirements 4.1, 4.2, 4.3
        """
        pass
    
    def check_validation_status(
        self,
        persisted_state: ValidationState | None
    ) -> ValidationStatus:
        """
        Determine current validation status based on all criteria.
        
        Args:
            persisted_state: Previously saved validation state (or None)
        
        Returns:
            ValidationStatus with overall status and failure details
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
        """
        pass
    
    def is_validation_expired(
        self,
        validation_date: datetime
    ) -> tuple[bool, int]:
        """
        Check if validation has expired.
        
        Args:
            validation_date: Date of last successful validation
        
        Returns:
            Tuple of (is_expired, days_since_validation)
        
        Validates: Requirements 5.1, 5.2, 5.3, 5.4
        """
        pass
    
    def compare_environments(
        self,
        env1: EnvironmentFingerprint,
        env2: EnvironmentFingerprint
    ) -> tuple[bool, list[str]]:
        """
        Compare two environment fingerprints.
        
        Args:
            env1: First environment fingerprint
            env2: Second environment fingerprint
        
        Returns:
            Tuple of (environments_match, list_of_differences)
        
        Validates: Requirements 4.4, 4.5
        """
        pass
```

### 2. ValidationOrchestrator

Orchestrates the complete IQ/OQ/PQ validation workflow.

```python
class ValidationOrchestrator:
    """
    Orchestrates the complete validation workflow including IQ/OQ/PQ phases.
    """
    
    def __init__(
        self,
        state_manager: ValidationStateManager,
        persistence: ValidationPersistence,
        certificate_generator: ValidationCertificateGenerator
    ):
        """
        Initialize with required dependencies.
        
        Args:
            state_manager: Validation state manager
            persistence: Validation persistence handler
            certificate_generator: Certificate generator
        """
        self.state_manager = state_manager
        self.persistence = persistence
        self.certificate_generator = certificate_generator
    
    def execute_validation_workflow(
        self,
        progress_callback: Callable[[str, int], None] | None = None
    ) -> ValidationResult:
        """
        Execute complete IQ/OQ/PQ validation workflow.
        
        Args:
            progress_callback: Optional callback for progress updates
                              (phase_name, progress_percentage)
        
        Returns:
            ValidationResult with overall status and detailed results
        
        Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5
        """
        pass
    
    def execute_iq_tests(self) -> IQResult:
        """
        Execute Installation Qualification tests.
        
        Returns:
            IQResult with test results and status
        
        Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
        """
        pass
    
    def execute_oq_tests(self) -> OQResult:
        """
        Execute Operational Qualification tests.
        
        Returns:
            OQResult with test results and URS traceability
        
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
        """
        pass
    
    def execute_pq_tests(self) -> PQResult:
        """
        Execute Performance Qualification tests.
        
        Returns:
            PQResult with UI test results and URS traceability
        
        Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
        """
        pass
```

### 3. ValidationPersistence

Handles saving and loading validation state.

```python
class ValidationPersistence:
    """
    Handles persistence of validation state and history.
    """
    
    def __init__(self, persistence_dir: Path):
        """
        Initialize with persistence directory.
        
        Args:
            persistence_dir: Directory for validation state files
        """
        self.persistence_dir = persistence_dir
        self.state_file = persistence_dir / "validation_state.json"
        self.history_file = persistence_dir / "validation_history.jsonl"
    
    def save_validation_state(self, state: ValidationState) -> None:
        """
        Save validation state to JSON file.
        
        Args:
            state: Validation state to save
        
        Validates: Requirements 15.1, 15.2, 15.3
        """
        pass
    
    def load_validation_state(self) -> ValidationState | None:
        """
        Load validation state from JSON file.
        
        Returns:
            ValidationState if file exists and is valid, None otherwise
        
        Validates: Requirements 15.3, 15.4, 15.5, 15.6
        """
        pass
    
    def append_to_history(self, event: ValidationEvent) -> None:
        """
        Append validation event to history log.
        
        Args:
            event: Validation event to log
        
        Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5
        """
        pass
    
    def get_validation_history(
        self,
        limit: int = 100
    ) -> list[ValidationEvent]:
        """
        Retrieve validation history.
        
        Args:
            limit: Maximum number of events to return
        
        Returns:
            List of validation events (most recent first)
        
        Validates: Requirements 20.6, 20.7
        """
        pass
    
    def verify_state_integrity(self, state_data: dict) -> bool:
        """
        Verify integrity of loaded state data.
        
        Args:
            state_data: Raw state data from JSON file
        
        Returns:
            True if state is valid, False if corrupted
        
        Validates: Requirements 15.5, 15.6
        """
        pass
```

### 4. ValidationCertificateGenerator

Generates comprehensive validation certificate PDFs.

```python
class ValidationCertificateGenerator:
    """
    Generates validation certificate PDFs with IQ/OQ/PQ chapters.
    """
    
    def __init__(self, urs_requirements: dict[str, str]):
        """
        Initialize with URS requirements mapping.
        
        Args:
            urs_requirements: Mapping of URS IDs to requirement text
        """
        self.urs_requirements = urs_requirements
    
    def generate_certificate(
        self,
        validation_result: ValidationResult,
        output_path: Path
    ) -> str:
        """
        Generate complete validation certificate PDF.
        
        Args:
            validation_result: Complete validation results
            output_path: Path for output PDF file
        
        Returns:
            SHA-256 hash of generated certificate
        
        Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8
        """
        pass
    
    def generate_title_page(
        self,
        pdf: Canvas,
        validation_result: ValidationResult
    ) -> None:
        """
        Generate certificate title page.
        
        Args:
            pdf: ReportLab canvas
            validation_result: Validation results
        
        Validates: Requirements 10.2
        """
        pass
    
    def generate_system_info_section(
        self,
        pdf: Canvas,
        system_info: SystemInfo
    ) -> None:
        """
        Generate system information section.
        
        Args:
            pdf: ReportLab canvas
            system_info: System information
        
        Validates: Requirements 10.3
        """
        pass
    
    def generate_iq_chapter(
        self,
        pdf: Canvas,
        iq_result: IQResult
    ) -> None:
        """
        Generate IQ chapter with installation verification details.
        
        Args:
            pdf: ReportLab canvas
            iq_result: IQ test results
        
        Validates: Requirements 10.4, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
        """
        pass
    
    def generate_oq_chapter(
        self,
        pdf: Canvas,
        oq_result: OQResult
    ) -> None:
        """
        Generate OQ chapter with calculation verification details.
        
        Args:
            pdf: ReportLab canvas
            oq_result: OQ test results
        
        Validates: Requirements 10.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6
        """
        pass
    
    def generate_pq_chapter(
        self,
        pdf: Canvas,
        pq_result: PQResult
    ) -> None:
        """
        Generate PQ chapter with UI verification details.
        
        Args:
            pdf: ReportLab canvas
            pq_result: PQ test results
        
        Validates: Requirements 10.6, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
        """
        pass
    
    def generate_traceability_matrix(
        self,
        pdf: Canvas,
        test_results: list[TestResult]
    ) -> None:
        """
        Generate URS traceability matrix.
        
        Args:
            pdf: ReportLab canvas
            test_results: All test results with URS markers
        
        Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
        """
        pass
```

### 5. ValidationUI

Streamlit UI components for validation system.

```python
class ValidationUI:
    """
    Streamlit UI components for validation system.
    """
    
    def __init__(
        self,
        orchestrator: ValidationOrchestrator,
        state_manager: ValidationStateManager
    ):
        """
        Initialize with validation components.
        
        Args:
            orchestrator: Validation orchestrator
            state_manager: State manager
        """
        self.orchestrator = orchestrator
        self.state_manager = state_manager
    
    def render_validation_button(
        self,
        validation_status: ValidationStatus
    ) -> bool:
        """
        Render validation status button.
        
        Args:
            validation_status: Current validation status
        
        Returns:
            True if button was clicked, False otherwise
        
        Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
        """
        pass
    
    def render_validation_metrics_dashboard(
        self,
        validation_status: ValidationStatus
    ) -> None:
        """
        Render validation metrics dashboard.
        
        Args:
            validation_status: Current validation status
        
        Validates: Requirements 27.1, 27.2, 27.3, 27.4, 27.5, 27.6
        """
        pass
    
    def render_validation_progress(
        self,
        phase: str,
        progress: int
    ) -> None:
        """
        Render validation progress indicator.
        
        Args:
            phase: Current phase name (IQ, OQ, PQ)
            progress: Progress percentage (0-100)
        
        Validates: Requirements 21.1, 21.2, 21.3, 21.4
        """
        pass
    
    def render_validation_result(
        self,
        result: ValidationResult
    ) -> None:
        """
        Render validation result message.
        
        Args:
            result: Validation result
        
        Validates: Requirements 21.5, 21.6, 21.7
        """
        pass
    
    def render_validation_failure_details(
        self,
        status: ValidationStatus
    ) -> None:
        """
        Render detailed validation failure information.
        
        Args:
            status: Validation status with failure details
        
        Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5
        """
        pass
    
    def render_expiry_warning(
        self,
        days_until_expiry: int
    ) -> None:
        """
        Render validation expiry warning.
        
        Args:
            days_until_expiry: Days until validation expires
        
        Validates: Requirements 28.1, 28.2, 28.3, 28.4
        """
        pass
    
    def render_non_validated_banner(self) -> None:
        """
        Render persistent warning banner for non-validated state.
        
        Validates: Requirements 25.2
        """
        pass
```

## Data Models

### ValidationState

```python
@dataclass
class ValidationState:
    """Complete validation state for persistence."""
    validation_date: datetime
    validation_hash: str
    environment_fingerprint: EnvironmentFingerprint
    iq_status: str  # "PASS" or "FAIL"
    oq_status: str  # "PASS" or "FAIL"
    pq_status: str  # "PASS" or "FAIL"
    expiry_date: datetime
    certificate_hash: str | None
```

### EnvironmentFingerprint

```python
@dataclass
class EnvironmentFingerprint:
    """Snapshot of system environment."""
    python_version: str  # e.g., "3.11.5"
    dependencies: dict[str, str]  # package_name -> version
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentFingerprint":
        """Create from dictionary."""
        pass
```

### ValidationStatus

```python
@dataclass
class ValidationStatus:
    """Current validation status with detailed information."""
    is_validated: bool
    validation_date: datetime | None
    days_until_expiry: int | None
    hash_match: bool
    environment_match: bool
    tests_passed: bool
    failure_reasons: list[str]
    
    def get_button_color(self) -> str:
        """Get button color based on validation status."""
        return "green" if self.is_validated else "red"
    
    def get_status_text(self) -> str:
        """Get status text for display."""
        return "VALIDATED" if self.is_validated else "NOT VALIDATED"
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    """Complete validation workflow result."""
    success: bool
    validation_date: datetime
    validation_hash: str
    environment_fingerprint: EnvironmentFingerprint
    iq_result: IQResult
    oq_result: OQResult
    pq_result: PQResult
    system_info: SystemInfo
    certificate_path: Path | None
    certificate_hash: str | None
```

### IQResult

```python
@dataclass
class IQResult:
    """Installation Qualification test results."""
    passed: bool
    checks: list[IQCheck]
    timestamp: datetime
    
    def get_summary(self) -> dict[str, int]:
        """Get summary statistics."""
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.passed)
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}

@dataclass
class IQCheck:
    """Individual IQ check result."""
    name: str
    description: str
    passed: bool
    expected_value: str | None
    actual_value: str | None
    failure_reason: str | None
```

### OQResult

```python
@dataclass
class OQResult:
    """Operational Qualification test results."""
    passed: bool
    tests: list[OQTest]
    timestamp: datetime
    
    def get_summary(self) -> dict[str, int]:
        """Get summary statistics."""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t.passed)
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}
    
    def group_by_functional_area(self) -> dict[str, list[OQTest]]:
        """Group tests by functional area."""
        pass

@dataclass
class OQTest:
    """Individual OQ test result."""
    test_name: str
    urs_id: str
    urs_requirement: str
    functional_area: str  # "Attribute", "Variables", "Non-Normal", "Reliability"
    passed: bool
    failure_reason: str | None
```

### PQResult

```python
@dataclass
class PQResult:
    """Performance Qualification test results."""
    passed: bool
    tests: list[PQTest]
    timestamp: datetime
    
    def get_summary(self) -> dict[str, int]:
        """Get summary statistics."""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t.passed)
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}
    
    def group_by_module(self) -> dict[str, list[PQTest]]:
        """Group tests by analysis module."""
        pass

@dataclass
class PQTest:
    """Individual PQ test result."""
    test_name: str
    urs_id: str
    urs_requirement: str
    module: str  # "Attribute", "Variables", "Non-Normal", "Reliability"
    workflow_description: str
    passed: bool
    failure_reason: str | None
```

### ValidationEvent

```python
@dataclass
class ValidationEvent:
    """Validation history event."""
    timestamp: datetime
    event_type: str  # "VALIDATION_ATTEMPT", "EXPIRY", "HASH_MISMATCH", "ENV_CHANGE"
    result: str  # "PASS", "FAIL"
    validation_hash: str | None
    details: dict[str, Any]
    
    def to_json_line(self) -> str:
        """Convert to JSON line for JSONL storage."""
        pass
    
    @classmethod
    def from_json_line(cls, line: str) -> "ValidationEvent":
        """Create from JSON line."""
        pass
```

### ValidationConfig

```python
class ValidationConfig(BaseSettings):
    """Validation system configuration using Pydantic Settings."""
    
    validation_expiry_days: int = 365
    tracked_dependencies: list[str] = [
        "scipy", "numpy", "streamlit", "pydantic", 
        "reportlab", "pytest", "playwright"
    ]
    persistence_dir: Path = Path(".validation")
    certificate_output_dir: Path = Path("reports")
    reminder_thresholds: list[int] = [30, 7]
    
    class Config:
        env_prefix = "VALIDATION_"
        env_file = ".env"
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.


### Property 1: Button Color Reflects Validation State

*For any* validation status, the button color should be green when validated and red when not validated.

**Validates: Requirements 1.2, 1.3**

### Property 2: Button Text Reflects Validation State

*For any* validation status, the button text should display "VALIDATED" when validated and "NOT VALIDATED" when not validated.

**Validates: Requirements 1.5**

### Property 3: Validation State Determination Correctness

*For any* combination of hash match, expiry status, environment match, and test results, the validation state should be VALIDATED if and only if all four criteria pass.

**Validates: Requirements 2.5, 2.6**

### Property 4: Validation Failure Reasons Completeness

*For any* validation status that is NOT_VALIDATED, the failure reasons list should contain at least one reason corresponding to each failed criterion.

**Validates: Requirements 2.7**

### Property 5: Hash Calculation Idempotence

*For any* set of calculation files, calculating the validation hash multiple times should produce the same result regardless of the order files are processed.

**Validates: Requirements 3.4**

### Property 6: Hash Sensitivity to File Changes

*For any* calculation file, if the file content is modified, the validation hash should change.

**Validates: Requirements 3.5**

### Property 7: Hash Excludes Non-Python Files

*For any* directory containing both Python and non-Python files, the validation hash should only include Python files and exclude __pycache__ directories.

**Validates: Requirements 3.3**

### Property 8: Environment Fingerprint Completeness

*For any* system environment, the captured environment fingerprint should include Python version and all configured key dependencies in valid JSON format.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 9: Environment Comparison Detects All Differences

*For any* two environment fingerprints with differences in Python version or dependency versions, the comparison should flag all differences.

**Validates: Requirements 4.4**

### Property 10: Validation Expiry Calculation Correctness

*For any* validation date and expiry configuration, the system should correctly calculate days elapsed and determine if validation has expired.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 11: Validation State Persistence Round Trip

*For any* validation state, saving to JSON and then loading should produce an equivalent validation state with all fields preserved.

**Validates: Requirements 15.3**

### Property 12: Persisted State Completeness

*For any* validation state saved to persistence, the JSON should include validation timestamp, hash, environment fingerprint, IQ/OQ/PQ status, and expiry date.

**Validates: Requirements 15.2**

### Property 13: Corrupted Persistence Detection

*For any* corrupted or invalid persistence file, the integrity validation should detect the corruption and return false.

**Validates: Requirements 15.5**

### Property 14: History Event Completeness

*For any* validation event appended to history, the event should include timestamp, event type, result, and all relevant details for that event type.

**Validates: Requirements 20.2, 20.3, 20.4, 20.5**

### Property 15: History Retrieval Ordering

*For any* validation history log, retrieving history should return events in reverse chronological order (most recent first).

**Validates: Requirements 20.6**

### Property 16: History Log Size Limiting

*For any* validation history log exceeding the configured limit, the oldest entries should be removed while preserving the most recent entries.

**Validates: Requirements 20.7**

### Property 17: Hash Comparison Correctness

*For any* two hash values, the comparison should return true if and only if the hashes are identical strings.

**Validates: Requirements 2.1**

### Property 18: Environment Fingerprint Serialization Round Trip

*For any* environment fingerprint, converting to dictionary and back should produce an equivalent fingerprint.

**Validates: Requirements 4.3**

### Property 19: Validation Date Storage Accuracy

*For any* successful validation, the stored timestamp should accurately reflect the validation completion time within 1 second.

**Validates: Requirements 5.1**

### Property 20: Days Until Expiry Display Accuracy

*For any* validation state with a validation date, the displayed days remaining should equal (expiry_date - current_date) in days.

**Validates: Requirements 5.5**

## Error Handling

### Hash Calculation Errors

- **File Not Found**: When a calculation file is missing, log error and set validation state to NOT_VALIDATED
- **Permission Denied**: When file cannot be read, log error and set validation state to NOT_VALIDATED
- **Hash Calculation Failure**: When hash calculation fails, log exception and set validation state to NOT_VALIDATED

### Persistence Errors

- **File Write Failure**: When persistence file cannot be written, log error but allow application to continue
- **File Read Failure**: When persistence file cannot be read, treat as missing file and set validation state to NOT_VALIDATED
- **JSON Parse Error**: When persistence file contains invalid JSON, log error and set validation state to NOT_VALIDATED
- **Schema Validation Error**: When persistence file is missing required fields, log error and set validation state to NOT_VALIDATED

### Test Execution Errors

- **Test Framework Failure**: When pytest or Playwright fails to execute, log error and mark corresponding phase (IQ/OQ/PQ) as FAIL
- **Test Timeout**: When tests exceed timeout threshold, terminate tests and mark phase as FAIL
- **Test Collection Error**: When tests cannot be collected, log error and mark phase as FAIL

### Environment Errors

- **Dependency Not Found**: When a tracked dependency is not installed, include in environment fingerprint as "NOT_INSTALLED"
- **Version Detection Failure**: When dependency version cannot be determined, include as "VERSION_UNKNOWN"
- **Python Version Detection Failure**: When Python version cannot be determined, log error and set validation state to NOT_VALIDATED

### Certificate Generation Errors

- **PDF Generation Failure**: When certificate PDF cannot be generated, log error but still update validation state if tests passed
- **File Write Failure**: When certificate cannot be written to disk, log error but still update validation state
- **Hash Calculation Failure**: When certificate hash cannot be calculated, log error and set certificate_hash to None

### UI Errors

- **Button Click During Validation**: When user clicks validation button while validation is running, ignore click and display message
- **Display Rendering Error**: When UI component fails to render, log error and display fallback message
- **Progress Update Failure**: When progress callback fails, log error but continue validation

### Configuration Errors

- **Invalid Expiry Days**: When expiry days is negative or zero, use default value (365) and log warning
- **Invalid Persistence Directory**: When persistence directory cannot be created, log error and use temporary directory
- **Invalid Certificate Directory**: When certificate directory cannot be created, log error and use temporary directory
- **Invalid Dependency List**: When tracked dependencies list is empty, use default list and log warning

## Testing Strategy

### Dual Testing Approach

The validation system will be tested using both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases (missing files, corrupted data), and error conditions
- **Property tests**: Verify universal properties across all inputs (hash idempotence, round-trip persistence, state determination)

### Unit Testing Focus

Unit tests will focus on:
- Specific examples of validation state determination with known inputs
- Edge cases: missing persistence files, corrupted JSON, missing dependencies
- Error conditions: file permission errors, test execution failures
- Integration points: UI component rendering, test orchestration
- Mock external dependencies: file system, subprocess execution, datetime

### Property-Based Testing Configuration

Property tests will use the Hypothesis library for Python:
- Minimum 100 iterations per property test
- Each property test references its design document property
- Tag format: `# Feature: validation-system, Property {number}: {property_text}`

Example property test structure:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: validation-system, Property 3: Validation State Determination Correctness
@given(
    hash_match=st.booleans(),
    expiry_ok=st.booleans(),
    env_match=st.booleans(),
    tests_passed=st.booleans()
)
def test_validation_state_determination(hash_match, expiry_ok, env_match, tests_passed):
    """
    For any combination of criteria, validation state should be VALIDATED
    if and only if all four criteria pass.
    """
    all_pass = hash_match and expiry_ok and env_match and tests_passed
    
    status = determine_validation_status(
        hash_match=hash_match,
        expiry_ok=expiry_ok,
        env_match=env_match,
        tests_passed=tests_passed
    )
    
    assert status.is_validated == all_pass
```

### Test Organization

Tests will be organized by component:

```
tests/
├── test_validation_state_manager.py      # Unit + property tests for state management
├── test_validation_orchestrator.py       # Unit tests for workflow orchestration
├── test_validation_persistence.py        # Unit + property tests for persistence
├── test_validation_certificate.py        # Unit tests for certificate generation
├── test_validation_ui.py                 # Unit tests for UI components
├── test_validation_integration.py        # Integration tests for complete workflow
└── test_validation_properties.py         # Property-based tests for all properties
```

### Test Coverage Requirements

- Minimum 90% code coverage for validation system modules
- 100% coverage for validation state determination logic
- 100% coverage for hash calculation logic
- All 20 correctness properties must have corresponding property tests
- All error conditions must have unit tests

### IQ/OQ/PQ Test Markers

All tests will use pytest markers to indicate their validation phase:

```python
@pytest.mark.iq
@pytest.mark.urs("URS-VAL-01")
def test_dependency_versions_match():
    """IQ test: Verify all dependencies match locked versions."""
    pass

@pytest.mark.oq
@pytest.mark.urs("URS-FUNC_A-02")
def test_attribute_calculation_accuracy():
    """OQ test: Verify attribute calculations are correct."""
    pass

@pytest.mark.pq
@pytest.mark.urs("URS-UI-04")
def test_attribute_tab_workflow(browser):
    """PQ test: Verify user can complete attribute analysis workflow."""
    pass
```

### Continuous Integration

- All tests run on every commit
- Property tests run with 100 iterations in CI
- Test results are collected and stored as artifacts
- Failed tests block merges to main branch
- Coverage reports are generated and tracked over time

### Manual Testing

Manual testing will focus on:
- Visual validation of button colors and UI layout
- User experience during validation workflow
- PDF certificate readability and formatting
- Performance under various system loads
- Behavior with very large history logs

## Implementation Notes

### Existing Code Reuse

The validation system will leverage existing infrastructure:

1. **Hash Calculation**: Extend existing `validation.py` module
2. **Certificate Generation**: Extend existing `reports.py` module  
3. **Test Infrastructure**: Use existing pytest and Playwright setup
4. **Configuration**: Extend existing Pydantic settings in `config.py`
5. **Logging**: Use existing logging infrastructure

### New Dependencies

No new dependencies required. The validation system uses:
- `hashlib` (standard library) - for hash calculation
- `json` (standard library) - for persistence
- `datetime` (standard library) - for expiry tracking
- `pathlib` (standard library) - for file operations
- `pytest` (existing) - for test execution
- `playwright` (existing) - for UI tests
- `reportlab` (existing) - for PDF generation
- `pydantic` (existing) - for configuration
- `hypothesis` (add) - for property-based testing

### File Structure

```
src/sample_size_estimator/
├── validation/
│   ├── __init__.py
│   ├── state_manager.py          # ValidationStateManager
│   ├── orchestrator.py            # ValidationOrchestrator
│   ├── persistence.py             # ValidationPersistence
│   ├── certificate.py             # ValidationCertificateGenerator
│   ├── ui.py                      # ValidationUI
│   └── models.py                  # Data models
├── validation.py                  # Existing hash functions (keep for compatibility)
└── ...

.validation/                       # Validation persistence directory
├── validation_state.json          # Current validation state
└── validation_history.jsonl       # History log (JSON Lines format)

scripts/
├── validate.py                    # CLI script for manual validation
└── ...
```

### Migration Strategy

1. Create new `validation/` module with new components
2. Keep existing `validation.py` for backward compatibility
3. Update `main.py` to integrate validation UI components
4. Add validation button to Streamlit sidebar
5. Update existing `generate_validation_certificate.py` to use new orchestrator
6. Add validation status check on application startup

### Performance Considerations

- Hash calculation: Cache results, only recalculate when files change
- Test execution: Run in subprocess to avoid blocking UI
- History log: Use JSONL format for efficient append operations
- Certificate generation: Generate asynchronously to avoid UI blocking
- Persistence: Use atomic file writes to prevent corruption

### Security Considerations

- Validation state file: Store in user-writable directory, not system directory
- Certificate hash: Use SHA-256 for tamper detection
- File permissions: Ensure persistence files are readable only by application user
- Input validation: Validate all loaded JSON data against schemas
- Path traversal: Validate all file paths to prevent directory traversal attacks
