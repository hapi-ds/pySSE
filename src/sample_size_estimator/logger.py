"""
Logging infrastructure for audit trail and debugging.

This module provides structured logging capabilities with JSON formatting
for regulatory compliance and audit trail requirements.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'calculation_data'):
            log_data['calculation_data'] = record.calculation_data

        if hasattr(record, 'validation_data'):
            log_data['validation_data'] = record.validation_data

        return json.dumps(log_data)


def setup_logger(
    name: str,
    log_file: str,
    log_level: str = "INFO",
    log_format: str = "json"
) -> logging.Logger:
    """
    Set up application logger.

    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: "json" or "text"

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File handler
    file_handler = logging.FileHandler(log_file)

    if log_format == "json":
        file_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Console handler for errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    logger.addHandler(console_handler)

    return logger


def log_calculation(
    logger: logging.Logger,
    module: str,
    inputs: dict[str, Any],
    results: dict[str, Any]
) -> None:
    """
    Log a calculation execution.

    Args:
        logger: Logger instance
        module: Calculation module name
        inputs: Input parameters
        results: Calculation results
    """
    logger.info(
        f"Calculation executed: {module}",
        extra={
            'calculation_data': {
                'module': module,
                'inputs': inputs,
                'results': results
            }
        }
    )


def log_validation_check(
    logger: logging.Logger,
    current_hash: str,
    validated_hash: str | None,
    is_validated: bool
) -> None:
    """
    Log a validation state check.

    Args:
        logger: Logger instance
        current_hash: Current file hash
        validated_hash: Expected validated hash
        is_validated: Whether validation passed
    """
    logger.info(
        f"Validation check: {'PASSED' if is_validated else 'FAILED'}",
        extra={
            'validation_data': {
                'current_hash': current_hash,
                'validated_hash': validated_hash,
                'is_validated': is_validated
            }
        }
    )
