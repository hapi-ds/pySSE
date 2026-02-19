"""Unit tests for ValidationPersistence.

This module contains unit tests for edge cases and error conditions
in the validation persistence system.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    ValidationEvent,
    ValidationState,
)
from src.sample_size_estimator.validation.persistence import ValidationPersistence


@pytest.fixture
def sample_validation_state():
    """Create a sample validation state for testing."""
    return ValidationState(
        validation_date=datetime(2024, 1, 15, 10, 30, 0),
        validation_hash="a" * 64,
        environment_fingerprint=EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={
                "scipy": "1.11.0",
                "numpy": "1.24.0",
                "pytest": "7.4.0"
            }
        ),
        iq_status="PASS",
        oq_status="PASS",
        pq_status="PASS",
        expiry_date=datetime(2025, 1, 15, 10, 30, 0),
        certificate_hash="b" * 64
    )


@pytest.fixture
def sample_validation_event():
    """Create a sample validation event for testing."""
    return ValidationEvent(
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
        event_type="VALIDATION_ATTEMPT",
        result="PASS",
        validation_hash="a" * 64,
        details={"test_count": 42, "duration": 120.5}
    )


class TestValidationPersistence:
    """Test suite for ValidationPersistence class."""

    def test_save_and_load_basic(self, sample_validation_state):
        """Test basic save and load functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save state
            persistence.save_validation_state(sample_validation_state)
            
            # Verify file exists
            assert persistence.state_file.exists()
            
            # Load state
            loaded_state = persistence.load_validation_state()
            
            # Verify loaded state matches
            assert loaded_state is not None
            assert loaded_state.validation_hash == sample_validation_state.validation_hash
            assert loaded_state.iq_status == sample_validation_state.iq_status

    def test_missing_persistence_directory(self, sample_validation_state):
        """Test that missing persistence directory is created automatically.
        
        Validates: Requirements 15.4
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use a non-existent subdirectory
            persistence_dir = Path(tmpdir) / "nested" / "validation"
            persistence = ValidationPersistence(persistence_dir)
            
            # Directory should not exist yet
            assert not persistence_dir.exists()
            
            # Save should create the directory
            persistence.save_validation_state(sample_validation_state)
            
            # Directory should now exist
            assert persistence_dir.exists()
            assert persistence.state_file.exists()

    def test_load_missing_state_file(self):
        """Test loading when state file doesn't exist.
        
        Validates: Requirements 15.4
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Try to load without saving first
            loaded_state = persistence.load_validation_state()
            
            # Should return None
            assert loaded_state is None

    def test_corrupted_json_file(self, sample_validation_state):
        """Test handling of corrupted JSON file.
        
        Validates: Requirements 15.5, 15.6
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save valid state first
            persistence.save_validation_state(sample_validation_state)
            
            # Corrupt the JSON file
            with open(persistence.state_file, "w", encoding="utf-8") as f:
                f.write("{invalid json content")
            
            # Try to load - should return None
            loaded_state = persistence.load_validation_state()
            assert loaded_state is None

    def test_missing_required_fields(self, sample_validation_state):
        """Test handling of state with missing required fields.
        
        Validates: Requirements 15.5, 15.6
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save valid state first
            persistence.save_validation_state(sample_validation_state)
            
            # Read and modify the state
            with open(persistence.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            # Remove a required field
            del state_data["validation_hash"]
            
            # Write back
            with open(persistence.state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f)
            
            # Try to load - should return None
            loaded_state = persistence.load_validation_state()
            assert loaded_state is None

    def test_invalid_field_types(self, sample_validation_state):
        """Test handling of invalid field types.
        
        Validates: Requirements 15.5, 15.6
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save valid state first
            persistence.save_validation_state(sample_validation_state)
            
            # Read and modify the state
            with open(persistence.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            # Change field to wrong type
            state_data["validation_hash"] = 12345  # Should be string
            
            # Write back
            with open(persistence.state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f)
            
            # Verify integrity check fails
            assert not persistence.verify_state_integrity(state_data)
            
            # Try to load - should return None
            loaded_state = persistence.load_validation_state()
            assert loaded_state is None

    def test_invalid_status_values(self, sample_validation_state):
        """Test handling of invalid status values.
        
        Validates: Requirements 15.5, 15.6
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save valid state first
            persistence.save_validation_state(sample_validation_state)
            
            # Read and modify the state
            with open(persistence.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            # Set invalid status
            state_data["iq_status"] = "INVALID_STATUS"
            
            # Verify integrity check fails
            assert not persistence.verify_state_integrity(state_data)

    def test_invalid_environment_fingerprint(self, sample_validation_state):
        """Test handling of invalid environment fingerprint structure.
        
        Validates: Requirements 15.5, 15.6
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save valid state first
            persistence.save_validation_state(sample_validation_state)
            
            # Read and modify the state
            with open(persistence.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            # Remove python_version from environment fingerprint
            del state_data["environment_fingerprint"]["python_version"]
            
            # Verify integrity check fails
            assert not persistence.verify_state_integrity(state_data)

    def test_append_to_history_basic(self, sample_validation_event):
        """Test basic history append functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Append event
            persistence.append_to_history(sample_validation_event)
            
            # Verify file exists
            assert persistence.history_file.exists()
            
            # Read and verify content
            with open(persistence.history_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            assert len(lines) == 1
            event_data = json.loads(lines[0])
            assert event_data["event_type"] == "VALIDATION_ATTEMPT"

    def test_append_multiple_events(self):
        """Test appending multiple events to history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Append multiple events
            for i in range(5):
                event = ValidationEvent(
                    timestamp=datetime(2024, 1, 1, 12, i, 0),
                    event_type="VALIDATION_ATTEMPT",
                    result="PASS",
                    validation_hash=f"hash_{i}",
                    details={"index": i}
                )
                persistence.append_to_history(event)
            
            # Retrieve history
            events = persistence.get_validation_history(limit=10)
            
            # Should have all 5 events
            assert len(events) == 5
            
            # Should be in reverse chronological order
            assert events[0].details["index"] == 4
            assert events[4].details["index"] == 0

    def test_get_history_with_limit(self):
        """Test retrieving history with limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Append 10 events
            for i in range(10):
                event = ValidationEvent(
                    timestamp=datetime(2024, 1, 1, 12, i, 0),
                    event_type="VALIDATION_ATTEMPT",
                    result="PASS",
                    validation_hash=f"hash_{i}",
                    details={"index": i}
                )
                persistence.append_to_history(event)
            
            # Retrieve with limit of 5
            events = persistence.get_validation_history(limit=5)
            
            # Should have only 5 events
            assert len(events) == 5
            
            # Should be the 5 most recent
            assert events[0].details["index"] == 9
            assert events[4].details["index"] == 5

    def test_get_history_empty_file(self):
        """Test retrieving history from non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Try to get history without creating file
            events = persistence.get_validation_history()
            
            # Should return empty list
            assert events == []

    def test_history_with_malformed_lines(self):
        """Test handling of malformed lines in history file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Create history file with some malformed lines
            persistence.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(persistence.history_file, "w", encoding="utf-8") as f:
                # Valid line
                f.write('{"timestamp": "2024-01-01T12:00:00", "event_type": "VALIDATION_ATTEMPT", "result": "PASS", "validation_hash": "hash1", "details": {}}\n')
                # Malformed line
                f.write('invalid json line\n')
                # Another valid line
                f.write('{"timestamp": "2024-01-01T13:00:00", "event_type": "VALIDATION_ATTEMPT", "result": "PASS", "validation_hash": "hash2", "details": {}}\n')
            
            # Retrieve history - should skip malformed line
            events = persistence.get_validation_history()
            
            # Should have 2 valid events
            assert len(events) == 2

    def test_trim_history_basic(self):
        """Test basic history trimming functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Append 20 events
            for i in range(20):
                event = ValidationEvent(
                    timestamp=datetime(2024, 1, 1, 12, i, 0),
                    event_type="VALIDATION_ATTEMPT",
                    result="PASS",
                    validation_hash=f"hash_{i}",
                    details={"index": i}
                )
                persistence.append_to_history(event)
            
            # Trim to 10 entries
            persistence.trim_history(max_entries=10)
            
            # Retrieve all events
            events = persistence.get_validation_history(limit=999)
            
            # Should have exactly 10 events
            assert len(events) == 10
            
            # Should be the 10 most recent
            assert events[0].details["index"] == 19
            assert events[9].details["index"] == 10

    def test_trim_history_no_op_when_under_limit(self):
        """Test that trimming does nothing when under limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Append 5 events
            for i in range(5):
                event = ValidationEvent(
                    timestamp=datetime(2024, 1, 1, 12, i, 0),
                    event_type="VALIDATION_ATTEMPT",
                    result="PASS",
                    validation_hash=f"hash_{i}",
                    details={"index": i}
                )
                persistence.append_to_history(event)
            
            # Trim to 10 entries (more than we have)
            persistence.trim_history(max_entries=10)
            
            # Retrieve all events
            events = persistence.get_validation_history(limit=999)
            
            # Should still have all 5 events
            assert len(events) == 5

    def test_trim_history_nonexistent_file(self):
        """Test that trimming handles non-existent file gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Try to trim without creating file - should not raise error
            persistence.trim_history(max_entries=10)
            
            # Should not create the file
            assert not persistence.history_file.exists()

    def test_atomic_write_on_save(self, sample_validation_state):
        """Test that save uses atomic write (temp file + rename)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Save state
            persistence.save_validation_state(sample_validation_state)
            
            # Verify final file exists
            assert persistence.state_file.exists()
            
            # Verify temp file doesn't exist
            temp_file = persistence.state_file.with_suffix(".tmp")
            assert not temp_file.exists()

    def test_verify_state_integrity_valid_state(self, sample_validation_state):
        """Test integrity verification with valid state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Convert state to dict
            state_dict = sample_validation_state.to_dict()
            
            # Verify integrity
            assert persistence.verify_state_integrity(state_dict)

    def test_event_json_line_round_trip(self, sample_validation_event):
        """Test ValidationEvent JSON line serialization round trip."""
        # Convert to JSON line
        json_line = sample_validation_event.to_json_line()
        
        # Parse back
        restored_event = ValidationEvent.from_json_line(json_line)
        
        # Verify fields match
        assert restored_event.event_type == sample_validation_event.event_type
        assert restored_event.result == sample_validation_event.result
        assert restored_event.validation_hash == sample_validation_event.validation_hash
        assert restored_event.details == sample_validation_event.details

    def test_history_with_empty_lines(self):
        """Test that empty lines in history file are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Create history file with empty lines
            persistence.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(persistence.history_file, "w", encoding="utf-8") as f:
                f.write('{"timestamp": "2024-01-01T12:00:00", "event_type": "VALIDATION_ATTEMPT", "result": "PASS", "validation_hash": "hash1", "details": {}}\n')
                f.write('\n')  # Empty line
                f.write('  \n')  # Whitespace line
                f.write('{"timestamp": "2024-01-01T13:00:00", "event_type": "VALIDATION_ATTEMPT", "result": "PASS", "validation_hash": "hash2", "details": {}}\n')
            
            # Retrieve history - should skip empty lines
            events = persistence.get_validation_history()
            
            # Should have 2 valid events
            assert len(events) == 2

    def test_state_with_none_certificate_hash(self):
        """Test handling of state with None certificate_hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Create state with None certificate_hash
            state = ValidationState(
                validation_date=datetime(2024, 1, 15, 10, 30, 0),
                validation_hash="a" * 64,
                environment_fingerprint=EnvironmentFingerprint(
                    python_version="3.11.5",
                    dependencies={"pytest": "7.4.0"}
                ),
                iq_status="PASS",
                oq_status="PASS",
                pq_status="PASS",
                expiry_date=datetime(2025, 1, 15, 10, 30, 0),
                certificate_hash=None  # Explicitly None
            )
            
            # Save and load
            persistence.save_validation_state(state)
            loaded_state = persistence.load_validation_state()
            
            # Verify None is preserved
            assert loaded_state is not None
            assert loaded_state.certificate_hash is None

    def test_event_with_none_validation_hash(self):
        """Test handling of event with None validation_hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = ValidationPersistence(Path(tmpdir))
            
            # Create event with None validation_hash
            event = ValidationEvent(
                timestamp=datetime(2024, 1, 15, 10, 30, 0),
                event_type="EXPIRY",
                result="FAIL",
                validation_hash=None,  # Explicitly None
                details={"reason": "Validation expired"}
            )
            
            # Append and retrieve
            persistence.append_to_history(event)
            events = persistence.get_validation_history()
            
            # Verify None is preserved
            assert len(events) == 1
            assert events[0].validation_hash is None

