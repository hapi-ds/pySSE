"""Unit tests for validation system data models.

Tests the data classes and their serialization/deserialization methods.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    IQCheck,
    IQResult,
    OQResult,
    OQTest,
    PQResult,
    PQTest,
    SystemInfo,
    ValidationConfig,
    ValidationEvent,
    ValidationResult,
    ValidationState,
    ValidationStatus,
)


def test_environment_fingerprint_to_dict():
    """Test EnvironmentFingerprint serialization to dictionary."""
    env = EnvironmentFingerprint(
        python_version="3.11.5",
        dependencies={"numpy": "1.24.0", "scipy": "1.11.0"}
    )
    
    result = env.to_dict()
    
    assert result["python_version"] == "3.11.5"
    assert result["dependencies"]["numpy"] == "1.24.0"
    assert result["dependencies"]["scipy"] == "1.11.0"


def test_environment_fingerprint_from_dict():
    """Test EnvironmentFingerprint deserialization from dictionary."""
    data = {
        "python_version": "3.11.5",
        "dependencies": {"numpy": "1.24.0", "scipy": "1.11.0"}
    }
    
    env = EnvironmentFingerprint.from_dict(data)
    
    assert env.python_version == "3.11.5"
    assert env.dependencies["numpy"] == "1.24.0"
    assert env.dependencies["scipy"] == "1.11.0"


def test_environment_fingerprint_round_trip():
    """Test EnvironmentFingerprint round-trip serialization."""
    original = EnvironmentFingerprint(
        python_version="3.11.5",
        dependencies={"numpy": "1.24.0", "scipy": "1.11.0"}
    )
    
    data = original.to_dict()
    restored = EnvironmentFingerprint.from_dict(data)
    
    assert restored.python_version == original.python_version
    assert restored.dependencies == original.dependencies


def test_validation_state_to_dict():
    """Test ValidationState serialization to dictionary."""
    env = EnvironmentFingerprint(
        python_version="3.11.5",
        dependencies={"numpy": "1.24.0"}
    )
    validation_date = datetime(2024, 1, 15, 10, 30, 0)
    expiry_date = datetime(2025, 1, 15, 10, 30, 0)
    
    state = ValidationState(
        validation_date=validation_date,
        validation_hash="abc123",
        environment_fingerprint=env,
        iq_status="PASS",
        oq_status="PASS",
        pq_status="PASS",
        expiry_date=expiry_date,
        certificate_hash="def456"
    )
    
    result = state.to_dict()
    
    assert result["validation_date"] == validation_date.isoformat()
    assert result["validation_hash"] == "abc123"
    assert result["iq_status"] == "PASS"
    assert result["oq_status"] == "PASS"
    assert result["pq_status"] == "PASS"
    assert result["expiry_date"] == expiry_date.isoformat()
    assert result["certificate_hash"] == "def456"


def test_validation_state_from_dict():
    """Test ValidationState deserialization from dictionary."""
    data = {
        "validation_date": "2024-01-15T10:30:00",
        "validation_hash": "abc123",
        "environment_fingerprint": {
            "python_version": "3.11.5",
            "dependencies": {"numpy": "1.24.0"}
        },
        "iq_status": "PASS",
        "oq_status": "PASS",
        "pq_status": "PASS",
        "expiry_date": "2025-01-15T10:30:00",
        "certificate_hash": "def456"
    }
    
    state = ValidationState.from_dict(data)
    
    assert state.validation_date == datetime(2024, 1, 15, 10, 30, 0)
    assert state.validation_hash == "abc123"
    assert state.environment_fingerprint.python_version == "3.11.5"
    assert state.iq_status == "PASS"
    assert state.oq_status == "PASS"
    assert state.pq_status == "PASS"
    assert state.expiry_date == datetime(2025, 1, 15, 10, 30, 0)
    assert state.certificate_hash == "def456"


def test_validation_state_round_trip():
    """Test ValidationState round-trip serialization."""
    env = EnvironmentFingerprint(
        python_version="3.11.5",
        dependencies={"numpy": "1.24.0"}
    )
    validation_date = datetime(2024, 1, 15, 10, 30, 0)
    expiry_date = datetime(2025, 1, 15, 10, 30, 0)
    
    original = ValidationState(
        validation_date=validation_date,
        validation_hash="abc123",
        environment_fingerprint=env,
        iq_status="PASS",
        oq_status="PASS",
        pq_status="PASS",
        expiry_date=expiry_date,
        certificate_hash="def456"
    )
    
    data = original.to_dict()
    restored = ValidationState.from_dict(data)
    
    assert restored.validation_date == original.validation_date
    assert restored.validation_hash == original.validation_hash
    assert restored.iq_status == original.iq_status
    assert restored.oq_status == original.oq_status
    assert restored.pq_status == original.pq_status
    assert restored.expiry_date == original.expiry_date
    assert restored.certificate_hash == original.certificate_hash


def test_validation_status_button_color():
    """Test ValidationStatus button color logic."""
    validated = ValidationStatus(
        is_validated=True,
        validation_date=datetime.now(),
        days_until_expiry=100,
        hash_match=True,
        environment_match=True,
        tests_passed=True
    )
    
    not_validated = ValidationStatus(
        is_validated=False,
        validation_date=None,
        days_until_expiry=None,
        hash_match=False,
        environment_match=True,
        tests_passed=True,
        failure_reasons=["Hash mismatch"]
    )
    
    assert validated.get_button_color() == "green"
    assert not_validated.get_button_color() == "red"


def test_validation_status_text():
    """Test ValidationStatus status text logic."""
    validated = ValidationStatus(
        is_validated=True,
        validation_date=datetime.now(),
        days_until_expiry=100,
        hash_match=True,
        environment_match=True,
        tests_passed=True
    )
    
    not_validated = ValidationStatus(
        is_validated=False,
        validation_date=None,
        days_until_expiry=None,
        hash_match=False,
        environment_match=True,
        tests_passed=True,
        failure_reasons=["Hash mismatch"]
    )
    
    assert validated.get_status_text() == "VALIDATED"
    assert not_validated.get_status_text() == "NOT VALIDATED"


def test_iq_result_summary():
    """Test IQResult summary statistics."""
    checks = [
        IQCheck("Check 1", "Description 1", True),
        IQCheck("Check 2", "Description 2", True),
        IQCheck("Check 3", "Description 3", False, failure_reason="Failed")
    ]
    
    result = IQResult(
        passed=False,
        checks=checks,
        timestamp=datetime.now()
    )
    
    summary = result.get_summary()
    
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1


def test_oq_result_summary():
    """Test OQResult summary statistics."""
    tests = [
        OQTest("Test 1", "URS-01", "Requirement 1", "Attribute", True),
        OQTest("Test 2", "URS-02", "Requirement 2", "Variables", True),
        OQTest("Test 3", "URS-03", "Requirement 3", "Attribute", False, "Failed")
    ]
    
    result = OQResult(
        passed=False,
        tests=tests,
        timestamp=datetime.now()
    )
    
    summary = result.get_summary()
    
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1


def test_oq_result_group_by_functional_area():
    """Test OQResult grouping by functional area."""
    tests = [
        OQTest("Test 1", "URS-01", "Requirement 1", "Attribute", True),
        OQTest("Test 2", "URS-02", "Requirement 2", "Variables", True),
        OQTest("Test 3", "URS-03", "Requirement 3", "Attribute", True)
    ]
    
    result = OQResult(
        passed=True,
        tests=tests,
        timestamp=datetime.now()
    )
    
    groups = result.group_by_functional_area()
    
    assert len(groups) == 2
    assert len(groups["Attribute"]) == 2
    assert len(groups["Variables"]) == 1


def test_pq_result_summary():
    """Test PQResult summary statistics."""
    tests = [
        PQTest("Test 1", "URS-01", "Requirement 1", "Attribute", "Workflow 1", True),
        PQTest("Test 2", "URS-02", "Requirement 2", "Variables", "Workflow 2", True),
        PQTest("Test 3", "URS-03", "Requirement 3", "Attribute", "Workflow 3", False, "Failed")
    ]
    
    result = PQResult(
        passed=False,
        tests=tests,
        timestamp=datetime.now()
    )
    
    summary = result.get_summary()
    
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1


def test_pq_result_group_by_module():
    """Test PQResult grouping by module."""
    tests = [
        PQTest("Test 1", "URS-01", "Requirement 1", "Attribute", "Workflow 1", True),
        PQTest("Test 2", "URS-02", "Requirement 2", "Variables", "Workflow 2", True),
        PQTest("Test 3", "URS-03", "Requirement 3", "Attribute", "Workflow 3", True)
    ]
    
    result = PQResult(
        passed=True,
        tests=tests,
        timestamp=datetime.now()
    )
    
    groups = result.group_by_module()
    
    assert len(groups) == 2
    assert len(groups["Attribute"]) == 2
    assert len(groups["Variables"]) == 1


def test_validation_event_to_json_line():
    """Test ValidationEvent serialization to JSON line."""
    event = ValidationEvent(
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
        event_type="VALIDATION_ATTEMPT",
        result="PASS",
        validation_hash="abc123",
        details={"duration": 120}
    )
    
    json_line = event.to_json_line()
    
    assert "2024-01-15T10:30:00" in json_line
    assert "VALIDATION_ATTEMPT" in json_line
    assert "PASS" in json_line
    assert "abc123" in json_line
    assert "120" in json_line


def test_validation_event_from_json_line():
    """Test ValidationEvent deserialization from JSON line."""
    json_line = '{"timestamp": "2024-01-15T10:30:00", "event_type": "VALIDATION_ATTEMPT", "result": "PASS", "validation_hash": "abc123", "details": {"duration": 120}}'
    
    event = ValidationEvent.from_json_line(json_line)
    
    assert event.timestamp == datetime(2024, 1, 15, 10, 30, 0)
    assert event.event_type == "VALIDATION_ATTEMPT"
    assert event.result == "PASS"
    assert event.validation_hash == "abc123"
    assert event.details["duration"] == 120


def test_validation_event_round_trip():
    """Test ValidationEvent round-trip serialization."""
    original = ValidationEvent(
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
        event_type="VALIDATION_ATTEMPT",
        result="PASS",
        validation_hash="abc123",
        details={"duration": 120}
    )
    
    json_line = original.to_json_line()
    restored = ValidationEvent.from_json_line(json_line)
    
    assert restored.timestamp == original.timestamp
    assert restored.event_type == original.event_type
    assert restored.result == original.result
    assert restored.validation_hash == original.validation_hash
    assert restored.details == original.details


def test_validation_config_defaults():
    """Test ValidationConfig default values."""
    config = ValidationConfig()
    
    assert config.validation_expiry_days == 365
    assert "scipy" in config.tracked_dependencies
    assert "numpy" in config.tracked_dependencies
    assert "streamlit" in config.tracked_dependencies
    assert config.persistence_dir == Path(".validation")
    assert config.certificate_output_dir == Path("reports")
    assert config.reminder_thresholds == [30, 7]
