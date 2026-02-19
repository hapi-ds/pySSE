"""Unit tests for ValidationStateManager.

This module contains unit tests for edge cases and error conditions
in the validation state management system.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    ValidationConfig,
    ValidationState,
)
from src.sample_size_estimator.validation.state_manager import (
    ValidationStateManager,
)


class TestValidationStateManager:
    """Test suite for ValidationStateManager."""

    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = ValidationConfig(validation_expiry_days=180)
        manager = ValidationStateManager(config)
        
        assert manager.config == config
        assert manager.config.validation_expiry_days == 180

    def test_calculate_validation_hash_missing_directory(self):
        """Test hash calculation when calculations directory is missing."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        # Mock Path.exists to return False
        with patch.object(Path, 'exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Calculations directory not found"):
                manager.calculate_validation_hash()

    def test_calculate_validation_hash_no_python_files(self):
        """Test hash calculation when no Python files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            calc_dir = Path(tmpdir) / "src" / "sample_size_estimator" / "calculations"
            calc_dir.mkdir(parents=True)
            
            # Create only non-Python files
            (calc_dir / "readme.txt").write_text("Not a Python file")
            
            config = ValidationConfig()
            manager = ValidationStateManager(config)
            
            # Mock the calculations directory path
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'rglob') as mock_rglob:
                    mock_rglob.return_value = []
                    
                    with pytest.raises(ValueError, match="No Python files found"):
                        manager.calculate_validation_hash()

    def test_calculate_file_hash_missing_file(self):
        """Test file hash calculation with missing file."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        non_existent_file = Path("non_existent_file.py")
        
        with pytest.raises(FileNotFoundError):
            manager._calculate_file_hash(non_existent_file)

    def test_calculate_file_hash_permission_error(self):
        """Test file hash calculation with permission error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# Test file")
            
            config = ValidationConfig()
            manager = ValidationStateManager(config)
            
            # Mock open to raise PermissionError
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                with pytest.raises(PermissionError):
                    manager._calculate_file_hash(test_file)

    def test_get_environment_fingerprint_missing_dependency(self):
        """Test environment fingerprint with missing dependency."""
        config = ValidationConfig(tracked_dependencies=["nonexistent_package"])
        manager = ValidationStateManager(config)
        
        fingerprint = manager.get_environment_fingerprint()
        
        assert fingerprint.dependencies["nonexistent_package"] == "NOT_INSTALLED"

    def test_get_environment_fingerprint_version_detection_failure(self):
        """Test environment fingerprint when version detection fails."""
        config = ValidationConfig(tracked_dependencies=["test_package"])
        manager = ValidationStateManager(config)
        
        # Mock _get_package_version to raise a generic exception
        with patch.object(manager, '_get_package_version', side_effect=RuntimeError("Version error")):
            fingerprint = manager.get_environment_fingerprint()
            
            assert fingerprint.dependencies["test_package"] == "VERSION_UNKNOWN"

    def test_get_package_version_not_installed(self):
        """Test getting version of non-installed package."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        with pytest.raises(ImportError):
            manager._get_package_version("definitely_not_installed_package_xyz")

    def test_compare_environments_identical(self):
        """Test comparing identical environments."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        env1 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.24.0", "scipy": "1.10.0"}
        )
        
        env2 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.24.0", "scipy": "1.10.0"}
        )
        
        match, differences = manager.compare_environments(env1, env2)
        
        assert match is True
        assert len(differences) == 0

    def test_compare_environments_python_version_different(self):
        """Test comparing environments with different Python versions."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        env1 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.24.0"}
        )
        
        env2 = EnvironmentFingerprint(
            python_version="3.12.0",
            dependencies={"numpy": "1.24.0"}
        )
        
        match, differences = manager.compare_environments(env1, env2)
        
        assert match is False
        assert len(differences) == 1
        assert "Python version changed" in differences[0]
        assert "3.11.5" in differences[0]
        assert "3.12.0" in differences[0]

    def test_compare_environments_dependency_version_different(self):
        """Test comparing environments with different dependency versions."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        env1 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.24.0", "scipy": "1.10.0"}
        )
        
        env2 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.25.0", "scipy": "1.10.0"}
        )
        
        match, differences = manager.compare_environments(env1, env2)
        
        assert match is False
        assert len(differences) == 1
        assert "numpy" in differences[0]
        assert "1.24.0" in differences[0]
        assert "1.25.0" in differences[0]

    def test_compare_environments_missing_dependency(self):
        """Test comparing environments with missing dependency."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        env1 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.24.0", "scipy": "1.10.0"}
        )
        
        env2 = EnvironmentFingerprint(
            python_version="3.11.5",
            dependencies={"numpy": "1.24.0"}
        )
        
        match, differences = manager.compare_environments(env1, env2)
        
        assert match is False
        assert any("scipy" in diff for diff in differences)

    def test_is_validation_expired_not_expired(self):
        """Test validation expiry check when not expired."""
        config = ValidationConfig(validation_expiry_days=365)
        manager = ValidationStateManager(config)
        
        validation_date = datetime.now() - timedelta(days=100)
        
        is_expired, days_since = manager.is_validation_expired(validation_date)
        
        assert is_expired is False
        assert 99 <= days_since <= 101  # Allow 1 day tolerance

    def test_is_validation_expired_exactly_at_limit(self):
        """Test validation expiry check at exact limit."""
        config = ValidationConfig(validation_expiry_days=365)
        manager = ValidationStateManager(config)
        
        validation_date = datetime.now() - timedelta(days=365)
        
        is_expired, days_since = manager.is_validation_expired(validation_date)
        
        assert is_expired is True
        assert 364 <= days_since <= 366  # Allow 1 day tolerance

    def test_is_validation_expired_past_limit(self):
        """Test validation expiry check when past limit."""
        config = ValidationConfig(validation_expiry_days=365)
        manager = ValidationStateManager(config)
        
        validation_date = datetime.now() - timedelta(days=500)
        
        is_expired, days_since = manager.is_validation_expired(validation_date)
        
        assert is_expired is True
        assert 499 <= days_since <= 501  # Allow 1 day tolerance

    def test_check_validation_status_no_persisted_state(self):
        """Test validation status check with no persisted state."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        status = manager.check_validation_status(None)
        
        assert status.is_validated is False
        assert status.validation_date is None
        assert status.days_until_expiry is None
        assert status.hash_match is False
        assert status.environment_match is False
        assert status.tests_passed is False
        assert "No validation state found" in status.failure_reasons

    def test_check_validation_status_hash_calculation_error(self):
        """Test validation status check when hash calculation fails."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        # Create a valid persisted state
        persisted_state = ValidationState(
            validation_date=datetime.now(),
            validation_hash="test_hash",
            environment_fingerprint=manager.get_environment_fingerprint(),
            iq_status="PASS",
            oq_status="PASS",
            pq_status="PASS",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        
        # Mock calculate_validation_hash to raise an exception
        with patch.object(manager, 'calculate_validation_hash', side_effect=RuntimeError("Hash error")):
            status = manager.check_validation_status(persisted_state)
            
            assert status.is_validated is False
            assert status.hash_match is False
            assert any("Hash calculation failed" in reason for reason in status.failure_reasons)

    def test_check_validation_status_environment_check_error(self):
        """Test validation status check when environment check fails."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        persisted_state = ValidationState(
            validation_date=datetime.now(),
            validation_hash="test_hash",
            environment_fingerprint=EnvironmentFingerprint(
                python_version="3.11.5",
                dependencies={}
            ),
            iq_status="PASS",
            oq_status="PASS",
            pq_status="PASS",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        
        # Mock get_environment_fingerprint to raise an exception
        with patch.object(manager, 'get_environment_fingerprint', side_effect=RuntimeError("Env error")):
            # Also mock calculate_validation_hash to return matching hash
            with patch.object(manager, 'calculate_validation_hash', return_value="test_hash"):
                status = manager.check_validation_status(persisted_state)
                
                assert status.is_validated is False
                assert status.environment_match is False
                assert any("Environment check failed" in reason for reason in status.failure_reasons)

    def test_check_validation_status_iq_failed(self):
        """Test validation status check when IQ tests failed."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        current_env = manager.get_environment_fingerprint()
        
        persisted_state = ValidationState(
            validation_date=datetime.now(),
            validation_hash="test_hash",
            environment_fingerprint=current_env,
            iq_status="FAIL",
            oq_status="PASS",
            pq_status="PASS",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        
        with patch.object(manager, 'calculate_validation_hash', return_value="test_hash"):
            status = manager.check_validation_status(persisted_state)
            
            assert status.is_validated is False
            assert status.tests_passed is False
            assert any("IQ" in reason for reason in status.failure_reasons)

    def test_check_validation_status_all_criteria_pass(self):
        """Test validation status check when all criteria pass."""
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        current_env = manager.get_environment_fingerprint()
        
        persisted_state = ValidationState(
            validation_date=datetime.now(),
            validation_hash="test_hash",
            environment_fingerprint=current_env,
            iq_status="PASS",
            oq_status="PASS",
            pq_status="PASS",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        
        with patch.object(manager, 'calculate_validation_hash', return_value="test_hash"):
            status = manager.check_validation_status(persisted_state)
            
            assert status.is_validated is True
            assert status.hash_match is True
            assert status.environment_match is True
            assert status.tests_passed is True
            assert len(status.failure_reasons) == 0
            assert status.days_until_expiry is not None
            assert status.days_until_expiry > 0

    def test_check_validation_status_multiple_failures(self):
        """Test validation status check with multiple failures."""
        config = ValidationConfig(validation_expiry_days=100)
        manager = ValidationStateManager(config)
        
        # Create expired validation with different environment
        persisted_state = ValidationState(
            validation_date=datetime.now() - timedelta(days=200),
            validation_hash="old_hash",
            environment_fingerprint=EnvironmentFingerprint(
                python_version="3.10.0",
                dependencies={"numpy": "1.20.0"}
            ),
            iq_status="FAIL",
            oq_status="PASS",
            pq_status="FAIL",
            expiry_date=datetime.now() - timedelta(days=100)
        )
        
        with patch.object(manager, 'calculate_validation_hash', return_value="new_hash"):
            status = manager.check_validation_status(persisted_state)
            
            assert status.is_validated is False
            assert len(status.failure_reasons) >= 4  # Hash, expiry, env, tests
            assert any("hash mismatch" in reason.lower() for reason in status.failure_reasons)
            assert any("expired" in reason.lower() for reason in status.failure_reasons)
            assert any("environment changed" in reason.lower() for reason in status.failure_reasons)
            assert any("tests failed" in reason.lower() for reason in status.failure_reasons)
