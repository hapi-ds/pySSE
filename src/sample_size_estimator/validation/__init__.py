"""Validation system module for IQ/OQ/PQ validation workflow.

This module provides comprehensive validation functionality including:
- Validation state management and hash calculation
- IQ/OQ/PQ test orchestration
- Validation state persistence
- Validation certificate generation
- UI components for validation status display

The validation system ensures regulatory compliance by tracking code changes,
dependency versions, validation expiry, and test results.
"""

from .certificate import ValidationCertificateGenerator
from .models import (
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
from .orchestrator import ValidationOrchestrator
from .persistence import ValidationPersistence
from .state_manager import ValidationStateManager
from .ui import ValidationUI

__all__ = [
    "EnvironmentFingerprint",
    "IQCheck",
    "IQResult",
    "OQResult",
    "OQTest",
    "PQResult",
    "PQTest",
    "SystemInfo",
    "ValidationCertificateGenerator",
    "ValidationConfig",
    "ValidationEvent",
    "ValidationResult",
    "ValidationState",
    "ValidationStatus",
    "ValidationOrchestrator",
    "ValidationPersistence",
    "ValidationStateManager",
    "ValidationUI",
    "get_engine_validation_info",
]


def get_engine_validation_info(
    calculations_file: str,
    validated_hash: str | None
) -> dict[str, str | bool | None]:
    """Get validation information for calculation engine (compatibility function).

    This function provides backward compatibility with the old validation system.
    It checks the current validation state and returns information about whether
    the calculation engine is validated.

    Args:
        calculations_file: Path to calculations module (unused, kept for compatibility).
        validated_hash: Expected validated hash (unused, kept for compatibility).

    Returns:
        Dictionary with hash and validation state:
        - current_hash: Current validation hash
        - validated_hash: Validated hash from persistence
        - is_validated: Whether system is currently validated
        - status_message: Human-readable status message
    """
    try:
        # Use new validation system
        config = ValidationConfig()
        state_manager = ValidationStateManager(config)
        persistence = ValidationPersistence(config.persistence_dir)

        # Get current validation state
        persisted_state = persistence.load_validation_state()
        validation_status = state_manager.check_validation_status(persisted_state)

        # Calculate current hash
        try:
            current_hash = state_manager.calculate_validation_hash()
        except Exception:
            current_hash = "ERROR"

        # Get validated hash from persisted state
        validated_hash_from_state = persisted_state.validation_hash if persisted_state else None

        # Generate status message
        if validation_status.is_validated:
            status_message = "VALIDATED STATE: YES"
        elif not persisted_state:
            status_message = "VALIDATED STATE: NO - No validation state found"
        elif validation_status.failure_reasons:
            status_message = f"VALIDATED STATE: NO - {'; '.join(validation_status.failure_reasons[:2])}"
        else:
            status_message = "VALIDATED STATE: NO"

        return {
            "current_hash": current_hash,
            "validated_hash": validated_hash_from_state,
            "is_validated": validation_status.is_validated,
            "status_message": status_message
        }

    except Exception as e:
        return {
            "current_hash": "ERROR",
            "validated_hash": validated_hash,
            "is_validated": False,
            "status_message": f"VALIDATED STATE: ERROR - {str(e)}"
        }
