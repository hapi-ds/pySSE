"""Validation state persistence and history management.

This module handles saving and loading validation state to/from JSON files,
maintaining validation history logs, and verifying state integrity.
"""

import json
import logging
from pathlib import Path
from typing import Any

from .models import ValidationEvent, ValidationState

logger = logging.getLogger(__name__)


class ValidationPersistence:
    """Handles persistence of validation state and history.
    
    Stores validation state in JSON format for human readability and
    history events in JSONL (JSON Lines) format for efficient appending.
    """

    def __init__(self, persistence_dir: Path):
        """Initialize with persistence directory.

        Args:
            persistence_dir: Directory for validation state files.
        """
        self.persistence_dir = Path(persistence_dir)
        self.state_file = self.persistence_dir / "validation_state.json"
        self.history_file = self.persistence_dir / "validation_history.jsonl"

    def save_validation_state(self, state: ValidationState) -> None:
        """Save validation state to JSON file.

        Creates the persistence directory if it doesn't exist.
        Uses atomic write to prevent corruption.

        Args:
            state: Validation state to save.

        Validates: Requirements 15.1, 15.2, 15.3
        """
        try:
            # Create directory if it doesn't exist
            self.persistence_dir.mkdir(parents=True, exist_ok=True)

            # Convert state to dictionary
            state_dict = state.to_dict()

            # Write to temporary file first (atomic write)
            temp_file = self.state_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)

            # Rename to actual file (atomic on most systems)
            temp_file.replace(self.state_file)

            logger.info(f"Validation state saved to {self.state_file}")

        except OSError as e:
            logger.error(f"Failed to save validation state: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving validation state: {e}")
            raise

    def load_validation_state(self) -> ValidationState | None:
        """Load validation state from JSON file.

        Returns:
            ValidationState if file exists and is valid, None otherwise.

        Validates: Requirements 15.3, 15.4, 15.5, 15.6
        """
        try:
            # Check if file exists
            if not self.state_file.exists():
                logger.info("No validation state file found")
                return None

            # Read and parse JSON
            with open(self.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)

            # Verify integrity
            if not self.verify_state_integrity(state_data):
                logger.error("Validation state file is corrupted or invalid")
                return None

            # Convert to ValidationState object
            state = ValidationState.from_dict(state_data)
            logger.info(f"Validation state loaded from {self.state_file}")
            return state

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation state JSON: {e}")
            return None
        except OSError as e:
            logger.error(f"Failed to read validation state file: {e}")
            return None
        except KeyError as e:
            logger.error(f"Missing required field in validation state: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading validation state: {e}")
            return None

    def verify_state_integrity(self, state_data: dict[str, Any]) -> bool:
        """Verify integrity of loaded state data.

        Checks that all required fields are present and have valid types.

        Args:
            state_data: Raw state data from JSON file.

        Returns:
            True if state is valid, False if corrupted.

        Validates: Requirements 15.5, 15.6
        """
        required_fields = {
            "validation_date": str,
            "validation_hash": str,
            "environment_fingerprint": dict,
            "iq_status": str,
            "oq_status": str,
            "pq_status": str,
            "expiry_date": str,
        }

        try:
            # Check all required fields are present
            for field, expected_type in required_fields.items():
                if field not in state_data:
                    logger.error(f"Missing required field: {field}")
                    return False

                # Check type
                if not isinstance(state_data[field], expected_type):
                    logger.error(
                        f"Invalid type for field {field}: "
                        f"expected {expected_type}, got {type(state_data[field])}"
                    )
                    return False

            # Verify environment fingerprint structure
            env_fp = state_data["environment_fingerprint"]
            if "python_version" not in env_fp or "dependencies" not in env_fp:
                logger.error("Invalid environment fingerprint structure")
                return False

            if not isinstance(env_fp["python_version"], str):
                logger.error("Invalid python_version type in environment fingerprint")
                return False

            if not isinstance(env_fp["dependencies"], dict):
                logger.error("Invalid dependencies type in environment fingerprint")
                return False

            # Verify status values
            valid_statuses = {"PASS", "FAIL"}
            for status_field in ["iq_status", "oq_status", "pq_status"]:
                if state_data[status_field] not in valid_statuses:
                    logger.error(
                        f"Invalid status value for {status_field}: "
                        f"{state_data[status_field]}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error verifying state integrity: {e}")
            return False

    def append_to_history(self, event: ValidationEvent) -> None:
        """Append validation event to history log.

        Creates the persistence directory and history file if they don't exist.
        Uses JSONL format for efficient appending.

        Args:
            event: Validation event to log.

        Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5
        """
        try:
            # Create directory if it doesn't exist
            self.persistence_dir.mkdir(parents=True, exist_ok=True)

            # Append event as JSON line
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(event.to_json_line() + "\n")

            logger.debug(f"Validation event appended to history: {event.event_type}")

        except OSError as e:
            logger.error(f"Failed to append to validation history: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error appending to history: {e}")
            raise

    def get_validation_history(self, limit: int = 100) -> list[ValidationEvent]:
        """Retrieve validation history.

        Returns events in reverse chronological order (most recent first).
        Limits the number of returned events to prevent memory issues.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List of validation events (most recent first).

        Validates: Requirements 20.6, 20.7
        """
        try:
            # Check if history file exists
            if not self.history_file.exists():
                logger.info("No validation history file found")
                return []

            # Read all lines
            events: list[ValidationEvent] = []
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            event = ValidationEvent.from_json_line(line)
                            events.append(event)
                        except Exception as e:
                            logger.warning(f"Failed to parse history line: {e}")
                            continue

            # Return most recent events first, limited to specified count
            events.reverse()
            return events[:limit]

        except OSError as e:
            logger.error(f"Failed to read validation history: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error reading validation history: {e}")
            return []

    def trim_history(self, max_entries: int = 100) -> None:
        """Trim history log to keep only the most recent entries.

        This method implements history log size limiting by keeping only
        the most recent entries and removing older ones.

        Args:
            max_entries: Maximum number of entries to keep.

        Validates: Requirements 20.7
        """
        try:
            # Check if history file exists
            if not self.history_file.exists():
                return

            # Read all events
            events = self.get_validation_history(limit=999999)  # Get all events

            # If we're under the limit, nothing to do
            if len(events) <= max_entries:
                return

            # Keep only the most recent entries
            events_to_keep = events[:max_entries]

            # Write back to file (events are already in reverse chronological order)
            with open(self.history_file, "w", encoding="utf-8") as f:
                for event in reversed(events_to_keep):  # Write in chronological order
                    f.write(event.to_json_line() + "\n")

            logger.info(
                f"Trimmed validation history from {len(events)} to {len(events_to_keep)} entries"
            )

        except Exception as e:
            logger.error(f"Failed to trim validation history: {e}")
            # Don't raise - trimming is not critical

