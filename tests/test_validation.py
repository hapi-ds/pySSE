"""
Property-based and unit tests for validation module.

Tests hash calculation, verification, and validation state logic.
"""

import tempfile
from pathlib import Path
import pytest
from hypothesis import given, strategies as st

from src.sample_size_estimator.validation_legacy import (
    calculate_file_hash,
    verify_validation_state,
    get_engine_validation_info
)


# Feature: sample-size-estimator, Property 26: Hash Calculation Determinism
@given(content=st.binary(min_size=0, max_size=10000))
def test_property_hash_determinism(content: bytes) -> None:
    """
    Property 26: Hash Calculation Determinism
    Validates: Requirements 21.1
    
    For any file content, calculating the SHA-256 hash multiple times
    should produce identical hash values.
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Calculate hash multiple times
        hash1 = calculate_file_hash(tmp_path)
        hash2 = calculate_file_hash(tmp_path)
        hash3 = calculate_file_hash(tmp_path)
        
        # All hashes should be identical
        assert hash1 == hash2 == hash3
        
        # Hash should be a valid hex string of correct length (64 chars for SHA-256)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)
    finally:
        Path(tmp_path).unlink()


# Feature: sample-size-estimator, Property 27: Hash Comparison Logic
@given(
    hash_value=st.text(
        alphabet='0123456789abcdef',
        min_size=64,
        max_size=64
    ),
    should_match=st.booleans()
)
def test_property_hash_comparison_logic(hash_value: str, should_match: bool) -> None:
    """
    Property 27: Hash Comparison Logic
    Validates: Requirements 21.3, 21.4, 21.5
    
    For any current hash H_current and validated hash H_validated,
    the validation state should be TRUE if and only if H_current == H_validated.
    """
    if should_match:
        # When hashes match
        validated_hash = hash_value
        is_validated, status_message = verify_validation_state(
            hash_value, validated_hash
        )
        
        assert is_validated is True
        assert "YES" in status_message
    else:
        # When hashes don't match (modify one character)
        validated_hash = hash_value[:-1] + ('0' if hash_value[-1] != '0' else '1')
        is_validated, status_message = verify_validation_state(
            hash_value, validated_hash
        )
        
        assert is_validated is False
        assert "NO" in status_message
        assert "UNVERIFIED CHANGE" in status_message


@given(hash_value=st.text(alphabet='0123456789abcdef', min_size=64, max_size=64))
def test_property_none_validated_hash(hash_value: str) -> None:
    """
    Property: None validated hash always returns False
    
    When validated_hash is None, validation state should always be False
    regardless of current hash value.
    """
    is_validated, status_message = verify_validation_state(hash_value, None)
    
    assert is_validated is False
    assert "No validated hash configured" in status_message


# Unit Tests

def test_calculate_file_hash_with_known_content() -> None:
    """Test hash calculation with known content."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write("test content")
        tmp_path = tmp_file.name
    
    try:
        hash_value = calculate_file_hash(tmp_path)
        
        # Verify it's a valid SHA-256 hash
        assert len(hash_value) == 64
        assert all(c in '0123456789abcdef' for c in hash_value)
    finally:
        Path(tmp_path).unlink()


def test_calculate_file_hash_empty_file() -> None:
    """Test hash calculation with empty file."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        hash_value = calculate_file_hash(tmp_path)
        
        # Empty file should have a specific SHA-256 hash
        expected_empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_value == expected_empty_hash
    finally:
        Path(tmp_path).unlink()


def test_calculate_file_hash_nonexistent_file() -> None:
    """Test hash calculation with nonexistent file."""
    with pytest.raises(FileNotFoundError):
        calculate_file_hash("/nonexistent/path/to/file.txt")


def test_verify_validation_state_match() -> None:
    """Test validation state when hashes match."""
    test_hash = "abc123" * 10 + "abcd"  # 64 chars
    is_validated, status_message = verify_validation_state(test_hash, test_hash)
    
    assert is_validated is True
    assert status_message == "VALIDATED STATE: YES"


def test_verify_validation_state_mismatch() -> None:
    """Test validation state when hashes don't match."""
    current_hash = "abc123" * 10 + "abcd"
    validated_hash = "def456" * 10 + "defg"
    
    is_validated, status_message = verify_validation_state(
        current_hash, validated_hash
    )
    
    assert is_validated is False
    assert "UNVERIFIED CHANGE" in status_message


def test_verify_validation_state_none() -> None:
    """Test validation state when validated hash is None."""
    current_hash = "abc123" * 10 + "abcd"
    is_validated, status_message = verify_validation_state(current_hash, None)
    
    assert is_validated is False
    assert "No validated hash configured" in status_message


def test_get_engine_validation_info_valid_file() -> None:
    """Test getting validation info for valid file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write("calculation engine code")
        tmp_path = tmp_file.name
    
    try:
        # Calculate expected hash
        expected_hash = calculate_file_hash(tmp_path)
        
        # Test with matching hash
        info = get_engine_validation_info(tmp_path, expected_hash)
        
        assert info["current_hash"] == expected_hash
        assert info["validated_hash"] == expected_hash
        assert info["is_validated"] is True
        assert "YES" in info["status_message"]
        
        # Test with non-matching hash
        wrong_hash = "0" * 64
        info = get_engine_validation_info(tmp_path, wrong_hash)
        
        assert info["current_hash"] == expected_hash
        assert info["validated_hash"] == wrong_hash
        assert info["is_validated"] is False
        assert "UNVERIFIED CHANGE" in info["status_message"]
    finally:
        Path(tmp_path).unlink()


def test_get_engine_validation_info_nonexistent_file() -> None:
    """Test getting validation info for nonexistent file."""
    info = get_engine_validation_info("/nonexistent/file.py", "abc123")
    
    assert info["current_hash"] == "ERROR"
    assert info["is_validated"] is False
    assert "ERROR" in info["status_message"]
