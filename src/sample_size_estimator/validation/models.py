"""Data models for the validation system.

This module defines all data classes used throughout the validation system,
including validation state, environment fingerprints, test results, and
configuration settings.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass
class EnvironmentFingerprint:
    """Snapshot of system environment including Python and dependency versions."""

    python_version: str
    dependencies: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the environment fingerprint.
        """
        return {
            "python_version": self.python_version,
            "dependencies": self.dependencies
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnvironmentFingerprint":
        """Create from dictionary.

        Args:
            data: Dictionary containing python_version and dependencies.

        Returns:
            EnvironmentFingerprint instance.
        """
        return cls(
            python_version=data["python_version"],
            dependencies=data["dependencies"]
        )


@dataclass
class ValidationState:
    """Complete validation state for persistence."""

    validation_date: datetime
    validation_hash: str
    environment_fingerprint: EnvironmentFingerprint
    iq_status: str
    oq_status: str
    pq_status: str
    expiry_date: datetime
    certificate_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the validation state.
        """
        return {
            "validation_date": self.validation_date.isoformat(),
            "validation_hash": self.validation_hash,
            "environment_fingerprint": self.environment_fingerprint.to_dict(),
            "iq_status": self.iq_status,
            "oq_status": self.oq_status,
            "pq_status": self.pq_status,
            "expiry_date": self.expiry_date.isoformat(),
            "certificate_hash": self.certificate_hash
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationState":
        """Create from dictionary.

        Args:
            data: Dictionary containing validation state fields.

        Returns:
            ValidationState instance.
        """
        return cls(
            validation_date=datetime.fromisoformat(data["validation_date"]),
            validation_hash=data["validation_hash"],
            environment_fingerprint=EnvironmentFingerprint.from_dict(
                data["environment_fingerprint"]
            ),
            iq_status=data["iq_status"],
            oq_status=data["oq_status"],
            pq_status=data["pq_status"],
            expiry_date=datetime.fromisoformat(data["expiry_date"]),
            certificate_hash=data.get("certificate_hash")
        )


@dataclass
class ValidationStatus:
    """Current validation status with detailed information."""

    is_validated: bool
    validation_date: datetime | None
    days_until_expiry: int | None
    hash_match: bool
    environment_match: bool
    tests_passed: bool
    failure_reasons: list[str] = field(default_factory=list)

    def get_button_color(self) -> str:
        """Get button color based on validation status.

        Returns:
            "green" if validated, "red" otherwise.
        """
        return "green" if self.is_validated else "red"

    def get_status_text(self) -> str:
        """Get status text for display.

        Returns:
            "VALIDATED" if validated, "NOT VALIDATED" otherwise.
        """
        return "VALIDATED" if self.is_validated else "NOT VALIDATED"


@dataclass
class IQCheck:
    """Individual IQ check result."""

    name: str
    description: str
    passed: bool
    expected_value: str | None = None
    actual_value: str | None = None
    failure_reason: str | None = None


@dataclass
class IQResult:
    """Installation Qualification test results."""

    passed: bool
    checks: list[IQCheck]
    timestamp: datetime

    def get_summary(self) -> dict[str, int]:
        """Get summary statistics.

        Returns:
            Dictionary with total, passed, and failed counts.
        """
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.passed)
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}


@dataclass
class OQTest:
    """Individual OQ test result."""

    test_name: str
    urs_id: str
    urs_requirement: str
    functional_area: str
    passed: bool
    failure_reason: str | None = None


@dataclass
class OQResult:
    """Operational Qualification test results."""

    passed: bool
    tests: list[OQTest]
    timestamp: datetime

    def get_summary(self) -> dict[str, int]:
        """Get summary statistics.

        Returns:
            Dictionary with total, passed, and failed counts.
        """
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t.passed)
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}

    def group_by_functional_area(self) -> dict[str, list[OQTest]]:
        """Group tests by functional area.

        Returns:
            Dictionary mapping functional area names to lists of tests.
        """
        groups: dict[str, list[OQTest]] = {}
        for test in self.tests:
            if test.functional_area not in groups:
                groups[test.functional_area] = []
            groups[test.functional_area].append(test)
        return groups


@dataclass
class PQTest:
    """Individual PQ test result."""

    test_name: str
    urs_id: str
    urs_requirement: str
    module: str
    workflow_description: str
    passed: bool
    failure_reason: str | None = None


@dataclass
class PQResult:
    """Performance Qualification test results."""

    passed: bool
    tests: list[PQTest]
    timestamp: datetime

    def get_summary(self) -> dict[str, int]:
        """Get summary statistics.

        Returns:
            Dictionary with total, passed, and failed counts.
        """
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t.passed)
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}

    def group_by_module(self) -> dict[str, list[PQTest]]:
        """Group tests by analysis module.

        Returns:
            Dictionary mapping module names to lists of tests.
        """
        groups: dict[str, list[PQTest]] = {}
        for test in self.tests:
            if test.module not in groups:
                groups[test.module] = []
            groups[test.module].append(test)
        return groups


@dataclass
class SystemInfo:
    """System information for validation certificate."""

    os_name: str
    os_version: str
    python_version: str
    dependencies: dict[str, str]


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
    certificate_path: Path | None = None
    certificate_hash: str | None = None


@dataclass
class ValidationEvent:
    """Validation history event."""

    timestamp: datetime
    event_type: str
    result: str
    validation_hash: str | None
    details: dict[str, Any] = field(default_factory=dict)

    def to_json_line(self) -> str:
        """Convert to JSON line for JSONL storage.

        Returns:
            JSON string representation of the event.
        """
        import json
        data = {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "result": self.result,
            "validation_hash": self.validation_hash,
            "details": self.details
        }
        return json.dumps(data)

    @classmethod
    def from_json_line(cls, line: str) -> "ValidationEvent":
        """Create from JSON line.

        Args:
            line: JSON string representation of the event.

        Returns:
            ValidationEvent instance.
        """
        import json
        data = json.loads(line)
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_type=data["event_type"],
            result=data["result"],
            validation_hash=data.get("validation_hash"),
            details=data.get("details", {})
        )


class ValidationConfig(BaseSettings):
    """Validation system configuration using Pydantic Settings.

    All settings can be overridden via environment variables with VALIDATION_ prefix
    or through .env file.
    """

    validation_expiry_days: int = 365
    tracked_dependencies: list[str] = field(
        default_factory=lambda: [
            "scipy",
            "numpy",
            "streamlit",
            "pydantic",
            "reportlab",
            "pytest",
            "playwright"
        ]
    )
    persistence_dir: Path = Path(".validation")
    certificate_output_dir: Path = Path("reports")
    reminder_thresholds: list[int] = field(default_factory=lambda: [30, 7])

    model_config = SettingsConfigDict(
        env_prefix="VALIDATION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
