"""Property-based tests for ValidationPersistence.

This module contains property-based tests using Hypothesis to verify
universal correctness properties of the validation persistence system.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    ValidationEvent,
    ValidationState,
)
from src.sample_size_estimator.validation.persistence import ValidationPersistence


# Strategy for generating valid ValidationState objects
@st.composite
def validation_state_strategy(draw):
    """Generate a valid ValidationState for testing."""
    validation_date = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ))
    
    validation_hash = draw(st.text(
        min_size=64,
        max_size=64,
        alphabet=st.characters(whitelist_categories=("Nd", "Ll"))
    ))
    
    python_version = f"{draw(st.integers(3, 3))}.{draw(st.integers(8, 12))}.{draw(st.integers(0, 20))}"
    
    dep_count = draw(st.integers(min_value=1, max_value=7))
    dependencies = {
        f"package_{i}": f"{draw(st.integers(0, 5))}.{draw(st.integers(0, 20))}.{draw(st.integers(0, 50))}"
        for i in range(dep_count)
    }
    
    environment_fingerprint = EnvironmentFingerprint(
        python_version=python_version,
        dependencies=dependencies
    )
    
    iq_status = draw(st.sampled_from(["PASS", "FAIL"]))
    oq_status = draw(st.sampled_from(["PASS", "FAIL"]))
    pq_status = draw(st.sampled_from(["PASS", "FAIL"]))
    
    expiry_date = validation_date + timedelta(days=draw(st.integers(1, 730)))
    
    certificate_hash = draw(st.one_of(
        st.none(),
        st.text(min_size=64, max_size=64, alphabet=st.characters(whitelist_categories=("Nd", "Ll")))
    ))
    
    return ValidationState(
        validation_date=validation_date,
        validation_hash=validation_hash,
        environment_fingerprint=environment_fingerprint,
        iq_status=iq_status,
        oq_status=oq_status,
        pq_status=pq_status,
        expiry_date=expiry_date,
        certificate_hash=certificate_hash
    )


# Strategy for generating valid ValidationEvent objects
@st.composite
def validation_event_strategy(draw):
    """Generate a valid ValidationEvent for testing."""
    timestamp = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ))
    
    event_type = draw(st.sampled_from([
        "VALIDATION_ATTEMPT",
        "EXPIRY",
        "HASH_MISMATCH",
        "ENV_CHANGE"
    ]))
    
    result = draw(st.sampled_from(["PASS", "FAIL"]))
    
    validation_hash = draw(st.one_of(
        st.none(),
        st.text(min_size=64, max_size=64, alphabet=st.characters(whitelist_categories=("Nd", "Ll")))
    ))
    
    # Generate details dictionary
    details = draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))),
        values=st.one_of(
            st.text(max_size=50),
            st.integers(),
            st.booleans()
        ),
        max_size=5
    ))
    
    return ValidationEvent(
        timestamp=timestamp,
        event_type=event_type,
        result=result,
        validation_hash=validation_hash,
        details=details
    )


# Feature: validation-system, Property 11: Validation State Persistence Round Trip
@given(state=validation_state_strategy())
def test_validation_state_persistence_round_trip(state):
    """
    For any validation state, saving to JSON and then loading should
    produce an equivalent validation state with all fields preserved.
    
    **Validates: Requirements 15.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Save the state
        persistence.save_validation_state(state)
        
        # Load the state back
        loaded_state = persistence.load_validation_state()
        
        # Verify state was loaded
        assert loaded_state is not None
        
        # Verify all fields match
        assert loaded_state.validation_hash == state.validation_hash
        assert loaded_state.iq_status == state.iq_status
        assert loaded_state.oq_status == state.oq_status
        assert loaded_state.pq_status == state.pq_status
        assert loaded_state.certificate_hash == state.certificate_hash
        
        # Verify dates match (within 1 second tolerance for serialization)
        assert abs((loaded_state.validation_date - state.validation_date).total_seconds()) < 1
        assert abs((loaded_state.expiry_date - state.expiry_date).total_seconds()) < 1
        
        # Verify environment fingerprint matches
        assert loaded_state.environment_fingerprint.python_version == state.environment_fingerprint.python_version
        assert loaded_state.environment_fingerprint.dependencies == state.environment_fingerprint.dependencies


# Feature: validation-system, Property 12: Persisted State Completeness
@given(state=validation_state_strategy())
def test_persisted_state_completeness(state):
    """
    For any validation state saved to persistence, the JSON should include
    validation timestamp, hash, environment fingerprint, IQ/OQ/PQ status,
    and expiry date.
    
    **Validates: Requirements 15.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Save the state
        persistence.save_validation_state(state)
        
        # Read the raw JSON file
        with open(persistence.state_file, "r", encoding="utf-8") as f:
            state_data = json.load(f)
        
        # Verify all required fields are present
        required_fields = [
            "validation_date",
            "validation_hash",
            "environment_fingerprint",
            "iq_status",
            "oq_status",
            "pq_status",
            "expiry_date"
        ]
        
        for field in required_fields:
            assert field in state_data, f"Missing required field: {field}"
        
        # Verify environment fingerprint structure
        assert "python_version" in state_data["environment_fingerprint"]
        assert "dependencies" in state_data["environment_fingerprint"]
        
        # Verify status values are valid
        assert state_data["iq_status"] in ["PASS", "FAIL"]
        assert state_data["oq_status"] in ["PASS", "FAIL"]
        assert state_data["pq_status"] in ["PASS", "FAIL"]


# Feature: validation-system, Property 13: Corrupted Persistence Detection
@given(
    state=validation_state_strategy(),
    corruption_type=st.sampled_from([
        "missing_field",
        "invalid_type",
        "invalid_status",
        "malformed_json"
    ])
)
def test_corrupted_persistence_detection(state, corruption_type):
    """
    For any corrupted or invalid persistence file, the integrity validation
    should detect the corruption and return false.
    
    **Validates: Requirements 15.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Save a valid state first
        persistence.save_validation_state(state)
        
        # Read and corrupt the state
        with open(persistence.state_file, "r", encoding="utf-8") as f:
            state_data = json.load(f)
        
        # Apply corruption based on type
        if corruption_type == "missing_field":
            # Remove a required field
            del state_data["validation_hash"]
        elif corruption_type == "invalid_type":
            # Change a field to wrong type
            state_data["validation_hash"] = 123  # Should be string
        elif corruption_type == "invalid_status":
            # Set invalid status value
            state_data["iq_status"] = "INVALID"
        elif corruption_type == "malformed_json":
            # Write malformed JSON
            with open(persistence.state_file, "w", encoding="utf-8") as f:
                f.write("{invalid json content")
            
            # Try to load - should return None
            loaded_state = persistence.load_validation_state()
            assert loaded_state is None
            return
        
        # Write corrupted data back
        with open(persistence.state_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f)
        
        # Verify integrity check fails
        assert not persistence.verify_state_integrity(state_data)
        
        # Verify loading returns None
        loaded_state = persistence.load_validation_state()
        assert loaded_state is None


# Feature: validation-system, Property 14: History Event Completeness
@given(event=validation_event_strategy())
def test_history_event_completeness(event):
    """
    For any validation event appended to history, the event should include
    timestamp, event type, result, and all relevant details for that event type.
    
    **Validates: Requirements 20.2, 20.3, 20.4, 20.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Append the event
        persistence.append_to_history(event)
        
        # Read the history file
        with open(persistence.history_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        
        # Parse the JSON line
        event_data = json.loads(lines[0])
        
        # Verify all required fields are present
        assert "timestamp" in event_data
        assert "event_type" in event_data
        assert "result" in event_data
        assert "validation_hash" in event_data
        assert "details" in event_data
        
        # Verify values match
        assert event_data["event_type"] == event.event_type
        assert event_data["result"] == event.result
        assert event_data["validation_hash"] == event.validation_hash
        assert event_data["details"] == event.details


# Feature: validation-system, Property 15: History Retrieval Ordering
@given(
    event_count=st.integers(min_value=2, max_value=20),
    seed=st.integers(min_value=0, max_value=1000)
)
def test_history_retrieval_ordering(event_count, seed):
    """
    For any validation history log, retrieving history should return
    events in reverse chronological order (most recent first).
    
    **Validates: Requirements 20.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Create events with incrementing timestamps
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        events = []
        
        for i in range(event_count):
            event = ValidationEvent(
                timestamp=base_time + timedelta(minutes=i),
                event_type="VALIDATION_ATTEMPT",
                result="PASS",
                validation_hash=f"hash_{seed}_{i}",
                details={"index": i}
            )
            events.append(event)
            persistence.append_to_history(event)
        
        # Retrieve history
        retrieved_events = persistence.get_validation_history(limit=event_count)
        
        # Verify we got all events
        assert len(retrieved_events) == event_count
        
        # Verify they are in reverse chronological order (most recent first)
        for i in range(len(retrieved_events) - 1):
            assert retrieved_events[i].timestamp >= retrieved_events[i + 1].timestamp
        
        # Verify the first event is the most recent
        assert retrieved_events[0].details["index"] == event_count - 1
        
        # Verify the last event is the oldest
        assert retrieved_events[-1].details["index"] == 0


# Feature: validation-system, Property 16: History Log Size Limiting
@given(
    total_events=st.integers(min_value=10, max_value=50),
    max_entries=st.integers(min_value=5, max_value=20)
)
def test_history_log_size_limiting(total_events, max_entries):
    """
    For any validation history log exceeding the configured limit,
    the oldest entries should be removed while preserving the most
    recent entries.
    
    **Validates: Requirements 20.7**
    """
    # Skip if max_entries >= total_events (nothing to trim)
    if max_entries >= total_events:
        return
    
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Create many events
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        for i in range(total_events):
            event = ValidationEvent(
                timestamp=base_time + timedelta(minutes=i),
                event_type="VALIDATION_ATTEMPT",
                result="PASS",
                validation_hash=f"hash_{i}",
                details={"index": i}
            )
            persistence.append_to_history(event)
        
        # Trim history
        persistence.trim_history(max_entries=max_entries)
        
        # Retrieve all events
        retrieved_events = persistence.get_validation_history(limit=999999)
        
        # Verify we have exactly max_entries
        assert len(retrieved_events) == max_entries
        
        # Verify we kept the most recent entries
        # The most recent event should have index = total_events - 1
        assert retrieved_events[0].details["index"] == total_events - 1
        
        # The oldest kept event should have index = total_events - max_entries
        assert retrieved_events[-1].details["index"] == total_events - max_entries


# Additional edge case tests for persistence

@given(state=validation_state_strategy())
def test_persistence_creates_directory(state):
    """Verify that persistence creates the directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a non-existent subdirectory
        persistence_dir = Path(tmpdir) / "subdir" / "validation"
        persistence = ValidationPersistence(persistence_dir)
        
        # Directory should not exist yet
        assert not persistence_dir.exists()
        
        # Save state should create the directory
        persistence.save_validation_state(state)
        
        # Directory should now exist
        assert persistence_dir.exists()
        assert persistence.state_file.exists()


@given(event=validation_event_strategy())
def test_history_appends_without_overwriting(event):
    """Verify that appending to history doesn't overwrite existing events."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Append first event
        event1 = ValidationEvent(
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            event_type="VALIDATION_ATTEMPT",
            result="PASS",
            validation_hash="hash1",
            details={"id": 1}
        )
        persistence.append_to_history(event1)
        
        # Append second event
        event2 = ValidationEvent(
            timestamp=datetime(2024, 1, 1, 13, 0, 0),
            event_type="VALIDATION_ATTEMPT",
            result="PASS",
            validation_hash="hash2",
            details={"id": 2}
        )
        persistence.append_to_history(event2)
        
        # Retrieve history
        events = persistence.get_validation_history(limit=10)
        
        # Should have both events
        assert len(events) == 2
        assert events[0].details["id"] == 2  # Most recent first
        assert events[1].details["id"] == 1


def test_load_nonexistent_state_returns_none():
    """Verify that loading from a non-existent file returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Try to load without saving first
        loaded_state = persistence.load_validation_state()
        
        assert loaded_state is None


def test_get_history_from_nonexistent_file_returns_empty():
    """Verify that getting history from non-existent file returns empty list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence_dir = Path(tmpdir)
        persistence = ValidationPersistence(persistence_dir)
        
        # Try to get history without creating file first
        events = persistence.get_validation_history()
        
        assert events == []

