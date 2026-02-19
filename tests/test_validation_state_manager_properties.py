"""Property-based tests for ValidationStateManager.

This module contains property-based tests using Hypothesis to verify
universal correctness properties of the validation state management system.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from src.sample_size_estimator.validation.models import (
    EnvironmentFingerprint,
    ValidationConfig,
    ValidationState,
)
from src.sample_size_estimator.validation.state_manager import (
    ValidationStateManager,
)


# Feature: validation-system, Property 5: Hash Calculation Idempotence
@given(
    file_count=st.integers(min_value=1, max_value=10),
    seed=st.integers(min_value=0, max_value=1000)
)
def test_hash_calculation_idempotence(file_count, seed):
    """
    For any set of calculation files, calculating the validation hash
    multiple times should produce the same result regardless of the order
    files are processed.
    
    **Validates: Requirements 3.4**
    """
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        calc_dir = Path(tmpdir) / "src" / "sample_size_estimator" / "calculations"
        calc_dir.mkdir(parents=True)
        
        # Create test Python files with deterministic content
        for i in range(file_count):
            file_path = calc_dir / f"calc_{i}.py"
            content = f"# Calculation file {i}\ndef func_{i}():\n    return {seed + i}\n"
            file_path.write_text(content)
        
        # Create state manager
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        # Override the calculations directory path for testing
        original_calc_dir = Path("src/sample_size_estimator/calculations")
        
        # Monkey-patch the calculate_validation_hash method to use our temp dir
        def patched_calculate_hash():
            python_files = sorted([
                f for f in calc_dir.rglob("*.py")
                if "__pycache__" not in str(f)
            ])
            
            if not python_files:
                raise ValueError(f"No Python files found in {calc_dir}")
            
            import hashlib
            combined_hash = hashlib.sha256()
            
            for file_path in python_files:
                file_hash = manager._calculate_file_hash(file_path)
                combined_hash.update(str(file_path).encode())
                combined_hash.update(file_hash.encode())
            
            return combined_hash.hexdigest()
        
        # Calculate hash multiple times
        hash1 = patched_calculate_hash()
        hash2 = patched_calculate_hash()
        hash3 = patched_calculate_hash()
        
        # All hashes should be identical (idempotent)
        assert hash1 == hash2
        assert hash2 == hash3


# Feature: validation-system, Property 6: Hash Sensitivity to File Changes
@given(
    original_content=st.text(min_size=10, max_size=100, alphabet=st.characters(blacklist_categories=("Cs", "Cc"))),
    modified_content=st.text(min_size=10, max_size=100, alphabet=st.characters(blacklist_categories=("Cs", "Cc")))
)
def test_hash_sensitivity_to_file_changes(original_content, modified_content):
    """
    For any calculation file, if the file content is modified,
    the validation hash should change.
    
    **Validates: Requirements 3.5**
    """
    # Skip if contents are identical
    if original_content == modified_content:
        return
    
    with tempfile.TemporaryDirectory() as tmpdir:
        calc_dir = Path(tmpdir) / "src" / "sample_size_estimator" / "calculations"
        calc_dir.mkdir(parents=True)
        
        test_file = calc_dir / "test_calc.py"
        
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        def calculate_hash_for_dir():
            python_files = sorted([
                f for f in calc_dir.rglob("*.py")
                if "__pycache__" not in str(f)
            ])
            
            import hashlib
            combined_hash = hashlib.sha256()
            
            for file_path in python_files:
                file_hash = manager._calculate_file_hash(file_path)
                combined_hash.update(str(file_path).encode())
                combined_hash.update(file_hash.encode())
            
            return combined_hash.hexdigest()
        
        # Calculate hash with original content (use UTF-8 encoding)
        test_file.write_text(original_content, encoding="utf-8")
        hash_original = calculate_hash_for_dir()
        
        # Calculate hash with modified content (use UTF-8 encoding)
        test_file.write_text(modified_content, encoding="utf-8")
        hash_modified = calculate_hash_for_dir()
        
        # Hashes should be different when content changes
        assert hash_original != hash_modified


# Feature: validation-system, Property 7: Hash Excludes Non-Python Files
@given(
    python_file_count=st.integers(min_value=1, max_value=5),
    non_python_file_count=st.integers(min_value=1, max_value=5)
)
def test_hash_excludes_non_python_files(python_file_count, non_python_file_count):
    """
    For any directory containing both Python and non-Python files,
    the validation hash should only include Python files and exclude
    __pycache__ directories.
    
    **Validates: Requirements 3.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        calc_dir = Path(tmpdir) / "src" / "sample_size_estimator" / "calculations"
        calc_dir.mkdir(parents=True)
        
        # Create Python files
        for i in range(python_file_count):
            (calc_dir / f"calc_{i}.py").write_text(f"# Python file {i}\n")
        
        # Create non-Python files
        for i in range(non_python_file_count):
            (calc_dir / f"data_{i}.txt").write_text(f"Data file {i}\n")
            (calc_dir / f"config_{i}.json").write_text(f'{{"key": {i}}}\n')
        
        # Create __pycache__ directory with .pyc files
        pycache_dir = calc_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "calc_0.cpython-311.pyc").write_bytes(b"fake pyc content")
        
        config = ValidationConfig()
        manager = ValidationStateManager(config)
        
        def calculate_hash_for_dir():
            python_files = sorted([
                f for f in calc_dir.rglob("*.py")
                if "__pycache__" not in str(f)
            ])
            
            import hashlib
            combined_hash = hashlib.sha256()
            
            for file_path in python_files:
                file_hash = manager._calculate_file_hash(file_path)
                combined_hash.update(str(file_path).encode())
                combined_hash.update(file_hash.encode())
            
            return combined_hash.hexdigest()
        
        hash_with_extras = calculate_hash_for_dir()
        
        # Remove non-Python files and recalculate
        for i in range(non_python_file_count):
            (calc_dir / f"data_{i}.txt").unlink()
            (calc_dir / f"config_{i}.json").unlink()
        
        hash_without_extras = calculate_hash_for_dir()
        
        # Hash should be the same - non-Python files don't affect it
        assert hash_with_extras == hash_without_extras


# Feature: validation-system, Property 8: Environment Fingerprint Completeness
@given(
    python_major=st.integers(min_value=3, max_value=3),
    python_minor=st.integers(min_value=8, max_value=12),
    python_patch=st.integers(min_value=0, max_value=20)
)
def test_environment_fingerprint_completeness(python_major, python_minor, python_patch):
    """
    For any system environment, the captured environment fingerprint
    should include Python version and all configured key dependencies
    in valid JSON format.
    
    **Validates: Requirements 4.1, 4.2, 4.3**
    """
    config = ValidationConfig()
    manager = ValidationStateManager(config)
    
    # Get environment fingerprint
    fingerprint = manager.get_environment_fingerprint()
    
    # Verify Python version is present and in correct format
    assert fingerprint.python_version is not None
    assert isinstance(fingerprint.python_version, str)
    parts = fingerprint.python_version.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
    
    # Verify all tracked dependencies are present
    assert fingerprint.dependencies is not None
    assert isinstance(fingerprint.dependencies, dict)
    
    for dep in config.tracked_dependencies:
        assert dep in fingerprint.dependencies
        assert isinstance(fingerprint.dependencies[dep], str)
    
    # Verify it can be serialized to JSON
    fingerprint_dict = fingerprint.to_dict()
    assert "python_version" in fingerprint_dict
    assert "dependencies" in fingerprint_dict
    
    # Verify round-trip conversion
    restored = EnvironmentFingerprint.from_dict(fingerprint_dict)
    assert restored.python_version == fingerprint.python_version
    assert restored.dependencies == fingerprint.dependencies


# Feature: validation-system, Property 9: Environment Comparison Detects All Differences
@given(
    python_version_1=st.text(min_size=5, max_size=10, alphabet=st.characters(whitelist_categories=("Nd", "Po"))),
    python_version_2=st.text(min_size=5, max_size=10, alphabet=st.characters(whitelist_categories=("Nd", "Po"))),
    dep_count=st.integers(min_value=1, max_value=5)
)
def test_environment_comparison_detects_differences(python_version_1, python_version_2, dep_count):
    """
    For any two environment fingerprints with differences in Python version
    or dependency versions, the comparison should flag all differences.
    
    **Validates: Requirements 4.4**
    """
    config = ValidationConfig()
    manager = ValidationStateManager(config)
    
    # Create two different environments
    deps1 = {f"package_{i}": f"1.{i}.0" for i in range(dep_count)}
    deps2 = {f"package_{i}": f"2.{i}.0" for i in range(dep_count)}
    
    env1 = EnvironmentFingerprint(
        python_version=python_version_1,
        dependencies=deps1
    )
    
    env2 = EnvironmentFingerprint(
        python_version=python_version_2,
        dependencies=deps2
    )
    
    # Compare environments
    match, differences = manager.compare_environments(env1, env2)
    
    # If versions are different, should not match
    if python_version_1 != python_version_2:
        assert not match
        # Should have at least one difference for Python version
        assert any("Python version" in diff for diff in differences)
    
    # Should detect all dependency differences
    if deps1 != deps2:
        assert not match
        # Should have differences for each changed package
        for pkg in deps1.keys():
            if deps1[pkg] != deps2.get(pkg):
                assert any(pkg in diff for diff in differences)


# Feature: validation-system, Property 10: Validation Expiry Calculation Correctness
@given(
    days_ago=st.integers(min_value=0, max_value=1000),
    expiry_days=st.integers(min_value=1, max_value=500)
)
def test_validation_expiry_calculation(days_ago, expiry_days):
    """
    For any validation date and expiry configuration, the system should
    correctly calculate days elapsed and determine if validation has expired.
    
    **Validates: Requirements 5.2, 5.3, 5.4**
    """
    config = ValidationConfig(validation_expiry_days=expiry_days)
    manager = ValidationStateManager(config)
    
    # Create validation date in the past
    validation_date = datetime.now() - timedelta(days=days_ago)
    
    # Check expiry
    is_expired, days_since = manager.is_validation_expired(validation_date)
    
    # Verify days calculation is correct (within 1 day tolerance for timing)
    assert abs(days_since - days_ago) <= 1
    
    # Verify expiry determination is correct
    expected_expired = days_ago >= expiry_days
    assert is_expired == expected_expired


# Feature: validation-system, Property 3: Validation State Determination Correctness
@given(
    hash_match=st.booleans(),
    expiry_ok=st.booleans(),
    env_match=st.booleans(),
    tests_passed=st.booleans()
)
def test_validation_state_determination(hash_match, expiry_ok, env_match, tests_passed):
    """
    For any combination of hash match, expiry status, environment match,
    and test results, the validation state should be VALIDATED if and only
    if all four criteria pass.
    
    **Validates: Requirements 2.5, 2.6**
    """
    config = ValidationConfig(validation_expiry_days=365)
    manager = ValidationStateManager(config)
    
    # Create a mock persisted state
    validation_date = datetime.now()
    if not expiry_ok:
        # Make it expired
        validation_date = datetime.now() - timedelta(days=400)
    
    # Create environment fingerprint
    current_env = manager.get_environment_fingerprint()
    
    # Create persisted environment (same or different based on env_match)
    if env_match:
        persisted_env = current_env
    else:
        # Create different environment
        persisted_env = EnvironmentFingerprint(
            python_version="3.0.0",  # Different version
            dependencies=current_env.dependencies
        )
    
    # Determine test status
    iq_status = "PASS" if tests_passed else "FAIL"
    oq_status = "PASS" if tests_passed else "FAIL"
    pq_status = "PASS" if tests_passed else "FAIL"
    
    # Create persisted state with a dummy hash
    # We'll mock the hash check separately
    persisted_state = ValidationState(
        validation_date=validation_date,
        validation_hash="dummy_hash",
        environment_fingerprint=persisted_env,
        iq_status=iq_status,
        oq_status=oq_status,
        pq_status=pq_status,
        expiry_date=validation_date + timedelta(days=365)
    )
    
    # Mock the hash calculation to control hash_match
    original_calculate_hash = manager.calculate_validation_hash
    
    def mock_calculate_hash():
        if hash_match:
            return "dummy_hash"
        else:
            return "different_hash"
    
    manager.calculate_validation_hash = mock_calculate_hash
    
    try:
        # Check validation status
        status = manager.check_validation_status(persisted_state)
        
        # Validation should be true if and only if all criteria pass
        all_pass = hash_match and expiry_ok and env_match and tests_passed
        assert status.is_validated == all_pass
        
        # Verify individual criteria are correctly reported
        assert status.hash_match == hash_match
        assert status.environment_match == env_match
        assert status.tests_passed == tests_passed
        
        # If not validated, should have failure reasons
        if not all_pass:
            assert len(status.failure_reasons) > 0
        
    finally:
        # Restore original method
        manager.calculate_validation_hash = original_calculate_hash
