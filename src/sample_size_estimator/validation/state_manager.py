"""Validation state management module.

This module provides the ValidationStateManager class for managing validation
state determination, hash calculation, environment fingerprinting, and validation
status checking.
"""

import hashlib
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .models import (
    EnvironmentFingerprint,
    ValidationConfig,
    ValidationState,
    ValidationStatus,
)


class ValidationStateManager:
    """Manages validation state determination based on multiple criteria.
    
    This class handles:
    - Calculating validation hashes of calculation engine files
    - Capturing environment fingerprints (Python and dependency versions)
    - Comparing environments to detect changes
    - Checking validation expiry
    - Determining overall validation status
    
    Validates: Requirements 2.1-2.7, 3.1-3.5, 4.1-4.5, 5.1-5.4
    """

    def __init__(self, config: ValidationConfig):
        """Initialize with validation configuration.
        
        Args:
            config: Configuration including expiry days, tracked dependencies
        """
        self.config = config

    def calculate_validation_hash(self) -> str:
        """Calculate combined SHA-256 hash of all calculation engine files.
        
        This method:
        1. Finds all Python files in the calculations directory
        2. Excludes __pycache__ directories and non-Python files
        3. Sorts files alphabetically for consistent ordering
        4. Calculates SHA-256 hash for each file
        5. Combines individual hashes into a single validation hash
        
        Returns:
            Hexadecimal hash string representing all calculation files
        
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
        """
        # Find the calculations directory
        calculations_dir = Path("src/sample_size_estimator/calculations")
        
        if not calculations_dir.exists():
            raise FileNotFoundError(
                f"Calculations directory not found: {calculations_dir}"
            )
        
        # Collect all Python files, excluding __pycache__
        python_files = sorted([
            f for f in calculations_dir.rglob("*.py")
            if "__pycache__" not in str(f)
        ])
        
        if not python_files:
            raise ValueError(
                f"No Python files found in {calculations_dir}"
            )
        
        # Calculate hash for each file and combine
        combined_hash = hashlib.sha256()
        
        for file_path in python_files:
            file_hash = self._calculate_file_hash(file_path)
            # Include filename in hash to detect renames
            combined_hash.update(str(file_path).encode())
            combined_hash.update(file_hash.encode())
        
        return combined_hash.hexdigest()

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a single file.
        
        Args:
            file_path: Path to file to hash
        
        Returns:
            Hexadecimal hash string
        
        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks for efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()

    def get_environment_fingerprint(self) -> EnvironmentFingerprint:
        """Capture current Python version and dependency versions.
        
        This method:
        1. Captures the Python version (major.minor.patch format)
        2. Captures versions of all tracked dependencies
        3. Handles missing dependencies gracefully (marks as "NOT_INSTALLED")
        4. Handles version detection failures (marks as "VERSION_UNKNOWN")
        
        Returns:
            EnvironmentFingerprint object with version information
        
        Validates: Requirements 4.1, 4.2, 4.3
        """
        # Get Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Get dependency versions
        dependencies: dict[str, str] = {}
        
        for package_name in self.config.tracked_dependencies:
            try:
                version = self._get_package_version(package_name)
                dependencies[package_name] = version
            except ImportError:
                dependencies[package_name] = "NOT_INSTALLED"
            except Exception:
                dependencies[package_name] = "VERSION_UNKNOWN"
        
        return EnvironmentFingerprint(
            python_version=python_version,
            dependencies=dependencies
        )

    def _get_package_version(self, package_name: str) -> str:
        """Get version of an installed package.
        
        Args:
            package_name: Name of the package
        
        Returns:
            Version string
        
        Raises:
            ImportError: If package is not installed
        """
        import importlib.metadata
        return importlib.metadata.version(package_name)

    def compare_environments(
        self,
        env1: EnvironmentFingerprint,
        env2: EnvironmentFingerprint
    ) -> tuple[bool, list[str]]:
        """Compare two environment fingerprints.
        
        This method detects differences in:
        - Python version
        - Any tracked dependency version
        
        Args:
            env1: First environment fingerprint
            env2: Second environment fingerprint
        
        Returns:
            Tuple of (environments_match, list_of_differences)
            - environments_match: True if identical, False if any differences
            - list_of_differences: List of human-readable difference descriptions
        
        Validates: Requirements 4.4, 4.5
        """
        differences: list[str] = []
        
        # Compare Python versions
        if env1.python_version != env2.python_version:
            differences.append(
                f"Python version changed: {env1.python_version} -> {env2.python_version}"
            )
        
        # Compare dependency versions
        all_packages = set(env1.dependencies.keys()) | set(env2.dependencies.keys())
        
        for package in sorted(all_packages):
            version1 = env1.dependencies.get(package, "NOT_INSTALLED")
            version2 = env2.dependencies.get(package, "NOT_INSTALLED")
            
            if version1 != version2:
                differences.append(
                    f"{package} version changed: {version1} -> {version2}"
                )
        
        environments_match = len(differences) == 0
        
        return environments_match, differences

    def is_validation_expired(
        self,
        validation_date: datetime
    ) -> tuple[bool, int]:
        """Check if validation has expired.
        
        Args:
            validation_date: Date of last successful validation
        
        Returns:
            Tuple of (is_expired, days_since_validation)
            - is_expired: True if validation age exceeds expiry threshold
            - days_since_validation: Number of days since validation
        
        Validates: Requirements 5.1, 5.2, 5.3, 5.4
        """
        now = datetime.now()
        days_since_validation = (now - validation_date).days
        is_expired = days_since_validation >= self.config.validation_expiry_days
        
        return is_expired, days_since_validation

    def check_validation_status(
        self,
        persisted_state: ValidationState | None
    ) -> ValidationStatus:
        """Determine current validation status based on all criteria.
        
        This method checks:
        1. Hash match: Does current hash match validated hash?
        2. Expiry: Has validation expired?
        3. Environment match: Has environment changed?
        4. Tests passed: Did all IQ/OQ/PQ tests pass?
        
        Validation is VALIDATED if and only if all four criteria pass.
        
        Args:
            persisted_state: Previously saved validation state (or None)
        
        Returns:
            ValidationStatus with overall status and failure details
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
        """
        # If no persisted state, not validated
        if persisted_state is None:
            return ValidationStatus(
                is_validated=False,
                validation_date=None,
                days_until_expiry=None,
                hash_match=False,
                environment_match=False,
                tests_passed=False,
                failure_reasons=["No validation state found"]
            )
        
        failure_reasons: list[str] = []
        
        # Check 1: Hash match
        try:
            current_hash = self.calculate_validation_hash()
            hash_match = current_hash == persisted_state.validation_hash
            if not hash_match:
                failure_reasons.append(
                    f"Validation hash mismatch: current={current_hash[:16]}..., "
                    f"validated={persisted_state.validation_hash[:16]}..."
                )
        except Exception as e:
            hash_match = False
            failure_reasons.append(f"Hash calculation failed: {str(e)}")
        
        # Check 2: Expiry
        is_expired, days_since = self.is_validation_expired(
            persisted_state.validation_date
        )
        if is_expired:
            failure_reasons.append(
                f"Validation expired: {days_since} days since validation "
                f"(limit: {self.config.validation_expiry_days} days)"
            )
        
        # Check 3: Environment match
        try:
            current_env = self.get_environment_fingerprint()
            env_match, env_differences = self.compare_environments(
                persisted_state.environment_fingerprint,
                current_env
            )
            if not env_match:
                failure_reasons.append(
                    f"Environment changed: {'; '.join(env_differences)}"
                )
        except Exception as e:
            env_match = False
            failure_reasons.append(f"Environment check failed: {str(e)}")
        
        # Check 4: Tests passed
        tests_passed = (
            persisted_state.iq_status == "PASS" and
            persisted_state.oq_status == "PASS" and
            persisted_state.pq_status == "PASS"
        )
        if not tests_passed:
            failed_phases = []
            if persisted_state.iq_status != "PASS":
                failed_phases.append("IQ")
            if persisted_state.oq_status != "PASS":
                failed_phases.append("OQ")
            if persisted_state.pq_status != "PASS":
                failed_phases.append("PQ")
            failure_reasons.append(
                f"Tests failed: {', '.join(failed_phases)} phase(s) did not pass"
            )
        
        # Overall validation status
        is_validated = (
            hash_match and
            not is_expired and
            env_match and
            tests_passed
        )
        
        # Calculate days until expiry
        days_until_expiry = None
        if not is_expired:
            days_until_expiry = self.config.validation_expiry_days - days_since
        
        return ValidationStatus(
            is_validated=is_validated,
            validation_date=persisted_state.validation_date,
            days_until_expiry=days_until_expiry,
            hash_match=hash_match,
            environment_match=env_match,
            tests_passed=tests_passed,
            failure_reasons=failure_reasons
        )
