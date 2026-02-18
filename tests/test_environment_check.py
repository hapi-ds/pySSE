"""
Unit tests for environment check script.

Tests the environment verification functionality.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import check_environment


def test_check_python_version():
    """Test Python version checking."""
    is_valid, version = check_environment.check_python_version()
    
    # Should return a valid boolean and version string
    assert isinstance(is_valid, bool)
    assert isinstance(version, str)
    assert len(version.split(".")) >= 2  # At least major.minor


def test_check_dependency_installed():
    """Test checking for installed dependencies."""
    # Test with a known installed package
    is_installed, version, status = check_environment.check_dependency("pytest")
    
    assert is_installed is True
    assert version != "Not installed"
    assert status in ["OK", "Version too old (need >= 8.0.0)"]


def test_check_dependency_not_installed():
    """Test checking for non-existent package."""
    is_installed, version, status = check_environment.check_dependency("nonexistent_package_xyz")
    
    assert is_installed is False
    assert version in ["Not installed", "Unknown"]
    assert status in ["Missing", "Package not recognized"]


def test_get_system_info():
    """Test system information collection."""
    system_info = check_environment.get_system_info()
    
    # Should return a dictionary with expected keys
    assert isinstance(system_info, dict)
    assert "OS" in system_info
    assert "Python Implementation" in system_info
    assert "Hostname" in system_info
    
    # Values should not be empty
    assert len(system_info["OS"]) > 0
    assert len(system_info["Python Implementation"]) > 0


def test_check_core_dependencies():
    """Test that all core dependencies are installed."""
    core_deps = [
        "streamlit",
        "pydantic",
        "scipy",
        "numpy",
        "matplotlib",
        "reportlab",
    ]
    
    for package in core_deps:
        is_installed, version, status = check_environment.check_dependency(package)
        assert is_installed is True, f"{package} should be installed"
        assert version != "Not installed", f"{package} version should be detected"


def test_check_dev_dependencies():
    """Test that development dependencies are installed."""
    dev_deps = [
        "pytest",
        "hypothesis",
        "mypy",
        "ruff",
    ]
    
    for package in dev_deps:
        is_installed, version, status = check_environment.check_dependency(package)
        # Dev dependencies should be installed in test environment
        assert is_installed is True, f"{package} should be installed"
