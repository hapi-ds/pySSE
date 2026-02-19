"""
Hash verification module for validation state tracking.

This module provides functions to calculate SHA-256 hashes of files
and verify the validation state of the calculation engine.
"""

import hashlib
from pathlib import Path


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.

    Args:
        file_path: Path to file to hash

    Returns:
        Hexadecimal hash string

    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If the file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha256_hash = hashlib.sha256()

    with open(path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def verify_validation_state(
    current_hash: str,
    validated_hash: str | None
) -> tuple[bool, str]:
    """
    Compare current hash against validated hash.

    Args:
        current_hash: Current file hash
        validated_hash: Expected validated hash (or None if not set)

    Returns:
        Tuple of (is_validated, status_message)
    """
    if validated_hash is None:
        return (False, "VALIDATED STATE: NO - No validated hash configured")

    if current_hash == validated_hash:
        return (True, "VALIDATED STATE: YES")
    else:
        return (False, "VALIDATED STATE: NO - UNVERIFIED CHANGE")


def get_engine_validation_info(
    calculations_file: str,
    validated_hash: str | None
) -> dict[str, str | bool | None]:
    """
    Get complete validation information for calculation engine.

    Args:
        calculations_file: Path to calculations module
        validated_hash: Expected validated hash

    Returns:
        Dictionary with hash and validation state
    """
    try:
        current_hash = calculate_file_hash(calculations_file)
        is_validated, status_message = verify_validation_state(
            current_hash, validated_hash
        )

        return {
            "current_hash": current_hash,
            "validated_hash": validated_hash,
            "is_validated": is_validated,
            "status_message": status_message
        }
    except (OSError, FileNotFoundError) as e:
        return {
            "current_hash": "ERROR",
            "validated_hash": validated_hash,
            "is_validated": False,
            "status_message": f"VALIDATED STATE: ERROR - {str(e)}"
        }
