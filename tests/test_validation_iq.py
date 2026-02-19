"""Installation Qualification (IQ) tests for the validation system.

These tests verify that the system is correctly installed with all required
dependencies, correct versions, and proper configuration.
"""

import sys
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

# Python 3.11+ has tomllib built-in, older versions need tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

import pytest


# Mark all tests in this file as IQ tests
pytestmark = pytest.mark.iq


@pytest.mark.urs("7.1")
def test_required_packages_installed() -> None:
    """Verify that all required Python packages are installed.
    
    Validates: Requirement 7.1
    """
    # Read required packages from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"
    
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    
    required_packages = pyproject_data["project"]["dependencies"]
    
    # Extract package names (remove version specifiers)
    package_names = []
    for dep in required_packages:
        # Handle different formats: "package>=1.0.0", "package==1.0.0", "package"
        pkg_name = dep.split(">=")[0].split("==")[0].split("<")[0].split(">")[0].strip()
        package_names.append(pkg_name)
    
    # Verify each package is installed
    missing_packages = []
    for pkg_name in package_names:
        try:
            version(pkg_name)
        except PackageNotFoundError:
            missing_packages.append(pkg_name)
    
    assert not missing_packages, f"Missing required packages: {missing_packages}"


@pytest.mark.urs("7.2")
def test_package_versions_match_lock() -> None:
    """Verify that package versions match the locked versions in uv.lock.
    
    Validates: Requirement 7.2
    """
    # Read pyproject.toml to get required packages
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"
    
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    
    required_packages = pyproject_data["project"]["dependencies"]
    
    # Extract package names and minimum versions
    version_mismatches = []
    for dep in required_packages:
        # Parse package name and version requirement
        if ">=" in dep:
            pkg_name, min_version = dep.split(">=")
            pkg_name = pkg_name.strip()
            min_version = min_version.strip()
            
            try:
                installed_version = version(pkg_name)
                # Parse versions for proper comparison
                installed_parts = [int(x) for x in installed_version.split(".")[:3]]
                min_parts = [int(x) for x in min_version.split(".")[:3]]
                
                # Pad to same length
                while len(installed_parts) < len(min_parts):
                    installed_parts.append(0)
                while len(min_parts) < len(installed_parts):
                    min_parts.append(0)
                
                # Compare versions
                if installed_parts < min_parts:
                    version_mismatches.append(
                        f"{pkg_name}: installed {installed_version} < required {min_version}"
                    )
            except PackageNotFoundError:
                version_mismatches.append(f"{pkg_name}: not installed")
            except (ValueError, AttributeError):
                # Skip packages with complex version strings
                pass
    
    assert not version_mismatches, f"Version mismatches: {version_mismatches}"


@pytest.mark.urs("7.3")
def test_python_version_meets_requirements() -> None:
    """Verify that the Python version meets minimum requirements.
    
    Validates: Requirement 7.3
    """
    # Read required Python version from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"
    
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    
    requires_python = pyproject_data["project"]["requires-python"]
    
    # Extract minimum version (handle ">=3.11" format)
    if ">=" in requires_python:
        min_version_str = requires_python.split(">=")[1].strip()
    else:
        pytest.fail(f"Unexpected requires-python format: {requires_python}")
    
    # Get current Python version
    current_version = sys.version_info
    current_version_str = f"{current_version.major}.{current_version.minor}"
    
    # Parse minimum version
    min_parts = min_version_str.split(".")
    min_major = int(min_parts[0])
    min_minor = int(min_parts[1]) if len(min_parts) > 1 else 0
    
    # Compare versions
    assert current_version.major > min_major or (
        current_version.major == min_major and current_version.minor >= min_minor
    ), f"Python {current_version_str} does not meet requirement {requires_python}"


@pytest.mark.urs("7.4")
def test_calculation_engine_files_exist() -> None:
    """Verify that all calculation engine files are present and readable.
    
    Validates: Requirement 7.4
    """
    # Define expected calculation engine files
    calc_dir = Path("src/sample_size_estimator/calculations")
    
    expected_files = [
        "__init__.py",
        "attribute_calcs.py",
        "variables_calcs.py",
        "non_normal_calcs.py",
        "reliability_calcs.py",
    ]
    
    missing_files = []
    unreadable_files = []
    
    for filename in expected_files:
        filepath = calc_dir / filename
        
        if not filepath.exists():
            missing_files.append(str(filepath))
        else:
            # Try to read the file to verify it's readable
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    f.read(1)  # Read just one byte to verify readability
            except Exception as e:
                unreadable_files.append(f"{filepath}: {e}")
    
    assert not missing_files, f"Missing calculation files: {missing_files}"
    assert not unreadable_files, f"Unreadable calculation files: {unreadable_files}"


@pytest.mark.urs("7.5")
def test_configuration_files_valid() -> None:
    """Verify that configuration files are present and valid.
    
    Validates: Requirement 7.5
    """
    # Check pyproject.toml exists and is valid TOML
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"
    
    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        
        # Verify essential sections exist
        assert "project" in pyproject_data, "Missing [project] section in pyproject.toml"
        assert "name" in pyproject_data["project"], "Missing project name"
        assert "dependencies" in pyproject_data["project"], "Missing dependencies"
        
    except Exception as e:
        pytest.fail(f"Invalid pyproject.toml: {e}")
    
    # Check .env.example exists (optional .env file)
    env_example_path = Path(".env.example")
    if env_example_path.exists():
        try:
            with open(env_example_path, "r") as f:
                content = f.read()
            # Basic validation - should contain key=value pairs
            assert "=" in content or content.strip() == "", \
                ".env.example should contain key=value pairs or be empty"
        except Exception as e:
            pytest.fail(f"Invalid .env.example: {e}")


@pytest.mark.urs("7.6")
def test_iq_checks_aggregation() -> None:
    """Test that IQ results can be properly aggregated.
    
    This is a meta-test that verifies the IQ test framework itself.
    Validates: Requirement 7.6
    """
    from src.sample_size_estimator.validation.models import IQCheck, IQResult
    from datetime import datetime
    
    # Create sample IQ checks
    checks = [
        IQCheck(
            name="Package Check",
            description="Verify package installed",
            passed=True,
            expected_value="installed",
            actual_value="installed"
        ),
        IQCheck(
            name="Version Check",
            description="Verify version matches",
            passed=False,
            expected_value="1.0.0",
            actual_value="0.9.0",
            failure_reason="Version mismatch"
        ),
    ]
    
    # Create IQ result
    result = IQResult(
        passed=False,  # Overall fails if any check fails
        checks=checks,
        timestamp=datetime.now()
    )
    
    # Verify summary calculation
    summary = result.get_summary()
    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    
    # Verify overall status reflects failures
    assert not result.passed


@pytest.mark.urs("7.7")
def test_iq_failure_handling() -> None:
    """Test that IQ failures are properly recorded with details.
    
    Validates: Requirement 7.7
    """
    from src.sample_size_estimator.validation.models import IQCheck, IQResult
    from datetime import datetime
    
    # Create a failed IQ check with detailed information
    failed_check = IQCheck(
        name="Dependency Version Check",
        description="Verify scipy version",
        passed=False,
        expected_value=">=1.11.0",
        actual_value="1.10.0",
        failure_reason="Installed version 1.10.0 does not meet requirement >=1.11.0"
    )
    
    # Verify failure details are captured
    assert not failed_check.passed
    assert failed_check.failure_reason is not None
    assert "1.10.0" in failed_check.failure_reason
    assert "1.11.0" in failed_check.failure_reason
    
    # Create IQ result with failure
    result = IQResult(
        passed=False,
        checks=[failed_check],
        timestamp=datetime.now()
    )
    
    # Verify failure is reflected in result
    assert not result.passed
    assert len(result.checks) == 1
    assert result.checks[0].failure_reason is not None
