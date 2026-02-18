"""
Property-based and unit tests for logging module.

Tests logging configuration, JSON formatting, and helper functions.
"""

import tempfile
import json
import logging
from pathlib import Path
import pytest
from hypothesis import given, strategies as st

from src.sample_size_estimator.logger import (
    JSONFormatter,
    setup_logger,
    log_calculation,
    log_validation_check
)


# Feature: sample-size-estimator, Property 29: Calculation Logging Completeness
@given(
    module=st.text(min_size=1, max_size=50),
    inputs=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.floats(allow_nan=False), st.integers(), st.text())
    ),
    results=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.floats(allow_nan=False), st.integers(), st.text())
    )
)
def test_property_calculation_logging_completeness(
    module: str,
    inputs: dict,
    results: dict
) -> None:
    """
    Property 29: Calculation Logging Completeness
    Validates: Requirements 26.1
    
    For any calculation execution, the log entry should contain timestamp,
    module name, all input parameters, and all calculated results.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp_file:
        log_path = tmp_file.name
    
    try:
        logger = setup_logger(
            "test_calc_logger",
            log_path,
            log_level="INFO",
            log_format="json"
        )
        
        # Log calculation
        log_calculation(logger, module, inputs, results)
        
        # Read log file
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse JSON log entry
        log_entry = json.loads(log_content.strip())
        
        # Verify all required fields are present
        assert 'timestamp' in log_entry
        assert 'level' in log_entry
        assert 'message' in log_entry
        assert 'calculation_data' in log_entry
        
        # Verify calculation data completeness
        calc_data = log_entry['calculation_data']
        assert calc_data['module'] == module
        assert calc_data['inputs'] == inputs
        assert calc_data['results'] == results
        
        # Clean up logger handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    finally:
        Path(log_path).unlink(missing_ok=True)


# Feature: sample-size-estimator, Property 30: Validation Logging Completeness
@given(
    current_hash=st.text(alphabet='0123456789abcdef', min_size=64, max_size=64),
    validated_hash=st.one_of(
        st.none(),
        st.text(alphabet='0123456789abcdef', min_size=64, max_size=64)
    ),
    is_validated=st.booleans()
)
def test_property_validation_logging_completeness(
    current_hash: str,
    validated_hash: str | None,
    is_validated: bool
) -> None:
    """
    Property 30: Validation Logging Completeness
    Validates: Requirements 26.2
    
    For any validation check, the log entry should contain timestamp,
    current hash, validated hash, and validation outcome.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp_file:
        log_path = tmp_file.name
    
    try:
        logger = setup_logger(
            "test_val_logger",
            log_path,
            log_level="INFO",
            log_format="json"
        )
        
        # Log validation check
        log_validation_check(logger, current_hash, validated_hash, is_validated)
        
        # Read log file
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse JSON log entry
        log_entry = json.loads(log_content.strip())
        
        # Verify all required fields are present
        assert 'timestamp' in log_entry
        assert 'level' in log_entry
        assert 'message' in log_entry
        assert 'validation_data' in log_entry
        
        # Verify validation data completeness
        val_data = log_entry['validation_data']
        assert val_data['current_hash'] == current_hash
        assert val_data['validated_hash'] == validated_hash
        assert val_data['is_validated'] == is_validated
        
        # Clean up logger handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    finally:
        Path(log_path).unlink(missing_ok=True)


# Unit Tests

def test_json_formatter_basic() -> None:
    """Test basic JSON formatting."""
    formatter = JSONFormatter()
    
    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Format the record
    formatted = formatter.format(record)
    
    # Parse JSON
    log_data = json.loads(formatted)
    
    # Verify structure
    assert log_data['level'] == 'INFO'
    assert log_data['message'] == 'Test message'
    assert 'timestamp' in log_data
    assert log_data['line'] == 10


def test_json_formatter_with_calculation_data() -> None:
    """Test JSON formatting with calculation data."""
    formatter = JSONFormatter()
    
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=20,
        msg="Calculation executed",
        args=(),
        exc_info=None
    )
    
    # Add calculation data
    record.calculation_data = {
        'module': 'attribute',
        'inputs': {'confidence': 95.0},
        'results': {'sample_size': 29}
    }
    
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    
    assert 'calculation_data' in log_data
    assert log_data['calculation_data']['module'] == 'attribute'


def test_setup_logger_creates_file() -> None:
    """Test that setup_logger creates log file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        log_path = Path(tmp_dir) / "logs" / "test.log"
        
        logger = setup_logger(
            "test_logger",
            str(log_path),
            log_level="INFO",
            log_format="json"
        )
        
        # Log a message
        logger.info("Test message")
        
        # Verify file was created
        assert log_path.exists()
        
        # Clean up handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def test_setup_logger_text_format() -> None:
    """Test logger with text format."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp_file:
        log_path = tmp_file.name
    
    try:
        logger = setup_logger(
            "test_text_logger",
            log_path,
            log_level="DEBUG",
            log_format="text"
        )
        
        logger.info("Test message")
        
        # Read log file
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Verify it's not JSON (should be plain text)
        assert "Test message" in log_content
        assert "INFO" in log_content
        
        # Clean up handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    finally:
        Path(log_path).unlink(missing_ok=True)


def test_setup_logger_prevents_duplicate_handlers() -> None:
    """Test that setup_logger doesn't add duplicate handlers."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp_file:
        log_path = tmp_file.name
    
    try:
        # Create logger twice with same name
        logger1 = setup_logger("duplicate_test", log_path)
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger("duplicate_test", log_path)
        
        # Should return same logger without adding handlers
        assert logger1 is logger2
        assert len(logger2.handlers) == initial_handler_count
        
        # Clean up handlers
        for handler in logger1.handlers[:]:
            handler.close()
            logger1.removeHandler(handler)
    finally:
        Path(log_path).unlink(missing_ok=True)


def test_log_calculation_writes_to_file() -> None:
    """Test that log_calculation writes to log file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp_file:
        log_path = tmp_file.name
    
    try:
        logger = setup_logger("calc_test", log_path, log_format="json")
        
        inputs = {"confidence": 95.0, "reliability": 90.0}
        results = {"sample_size": 29}
        
        log_calculation(logger, "attribute", inputs, results)
        
        # Read and verify
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        log_entry = json.loads(log_content.strip())
        assert log_entry['calculation_data']['module'] == 'attribute'
        
        # Clean up handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    finally:
        Path(log_path).unlink(missing_ok=True)


def test_log_validation_check_writes_to_file() -> None:
    """Test that log_validation_check writes to log file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp_file:
        log_path = tmp_file.name
    
    try:
        logger = setup_logger("val_test", log_path, log_format="json")
        
        current_hash = "abc123" * 10 + "abcd"
        validated_hash = "abc123" * 10 + "abcd"
        
        log_validation_check(logger, current_hash, validated_hash, True)
        
        # Read and verify
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        log_entry = json.loads(log_content.strip())
        assert log_entry['validation_data']['is_validated'] is True
        
        # Clean up handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    finally:
        Path(log_path).unlink(missing_ok=True)
