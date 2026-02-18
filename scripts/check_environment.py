#!/usr/bin/env python3
"""
Environment Check Script

This script verifies that all dependencies are correctly installed with
the expected versions and displays system information for Installation
Qualification (IQ).

Requirements: REQ-23
"""

import sys
import platform
from pathlib import Path
from typing import Dict, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(text)
    print("=" * 70)
    print()


def print_section(text: str) -> None:
    """Print a formatted section header."""
    print()
    print(f"{BLUE}{text}{RESET}")
    print("-" * 70)


def check_python_version() -> Tuple[bool, str]:
    """
    Check if Python version meets requirements.
    
    Returns:
        Tuple of (is_valid, version_string)
    """
    version = platform.python_version()
    major, minor, _ = version.split(".")
    
    # Requirement: Python >= 3.11
    is_valid = int(major) >= 3 and int(minor) >= 11
    
    return is_valid, version


def check_dependency(package_name: str, min_version: str = None) -> Tuple[bool, str, str]:
    """
    Check if a dependency is installed and optionally verify version.
    
    Args:
        package_name: Name of the package to check
        min_version: Minimum required version (optional)
    
    Returns:
        Tuple of (is_installed, installed_version, status_message)
    """
    try:
        if package_name == "streamlit":
            import streamlit
            installed_version = streamlit.__version__
        elif package_name == "pydantic":
            import pydantic
            installed_version = pydantic.__version__
        elif package_name == "pydantic-settings":
            import pydantic_settings
            installed_version = pydantic_settings.__version__
        elif package_name == "scipy":
            import scipy
            installed_version = scipy.__version__
        elif package_name == "numpy":
            import numpy
            installed_version = numpy.__version__
        elif package_name == "matplotlib":
            import matplotlib
            installed_version = matplotlib.__version__
        elif package_name == "reportlab":
            import reportlab
            installed_version = reportlab.Version
        elif package_name == "pytest":
            import pytest
            installed_version = pytest.__version__
        elif package_name == "hypothesis":
            import hypothesis
            installed_version = hypothesis.__version__
        elif package_name == "mypy":
            # Mypy doesn't have __version__, try subprocess
            import subprocess
            result = subprocess.run(
                ["mypy", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Parse version from output like "mypy 1.8.0 (compiled: yes)"
                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    installed_version = parts[1]
                else:
                    installed_version = "Unknown"
            else:
                return False, "Unknown", "Not found"
        elif package_name == "ruff":
            # Ruff doesn't have __version__, try subprocess
            import subprocess
            result = subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Parse version from output like "ruff 0.1.0"
                installed_version = result.stdout.strip().split()[-1]
            else:
                return False, "Unknown", "Not found"
        else:
            return False, "Unknown", "Package not recognized"
        
        # Check version if min_version specified
        if min_version:
            # Simple version comparison (works for most cases)
            installed_parts = installed_version.split(".")
            min_parts = min_version.split(".")
            
            # Compare major.minor versions
            for i in range(min(len(installed_parts), len(min_parts))):
                try:
                    inst_num = int(installed_parts[i].split("+")[0])  # Handle versions like "1.0.0+local"
                    min_num = int(min_parts[i])
                    
                    if inst_num > min_num:
                        break
                    elif inst_num < min_num:
                        return True, installed_version, f"Version too old (need >= {min_version})"
                except ValueError:
                    # Non-numeric version component, skip comparison
                    break
        
        return True, installed_version, "OK"
    
    except ImportError:
        return False, "Not installed", "Missing"
    except Exception as e:
        return False, "Unknown", f"Error: {str(e)}"


def get_system_info() -> Dict[str, str]:
    """
    Collect system information.
    
    Returns:
        Dictionary with system details
    """
    return {
        "OS": f"{platform.system()} {platform.release()}",
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor() or "Unknown",
        "Hostname": platform.node(),
        "Python Implementation": platform.python_implementation(),
        "Python Compiler": platform.python_compiler(),
    }


def main() -> int:
    """
    Main entry point for environment check.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_header("Sample Size Estimator - Environment Check")
    
    # System Information
    print_section("System Information")
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"  {key:.<25} {value}")
    
    # Python Version Check
    print_section("Python Version")
    python_valid, python_version = check_python_version()
    status_symbol = f"{GREEN}✓{RESET}" if python_valid else f"{RED}✗{RESET}"
    status_text = f"{GREEN}OK{RESET}" if python_valid else f"{RED}FAIL{RESET}"
    print(f"  {status_symbol} Python {python_version:.<20} [{status_text}]")
    
    if not python_valid:
        print(f"    {YELLOW}Warning: Python >= 3.11 is required{RESET}")
    
    # Core Dependencies
    print_section("Core Dependencies")
    
    core_deps = [
        ("streamlit", "1.30.0"),
        ("pydantic", "2.5.0"),
        ("pydantic-settings", "2.1.0"),
        ("scipy", "1.11.0"),
        ("numpy", "1.26.0"),
        ("matplotlib", "3.8.0"),
        ("reportlab", "4.0.0"),
    ]
    
    all_core_ok = True
    for package, min_version in core_deps:
        is_installed, version, status = check_dependency(package, min_version)
        
        if is_installed and status == "OK":
            status_symbol = f"{GREEN}✓{RESET}"
            status_display = f"{GREEN}{status}{RESET}"
        elif is_installed:
            status_symbol = f"{YELLOW}⚠{RESET}"
            status_display = f"{YELLOW}{status}{RESET}"
            all_core_ok = False
        else:
            status_symbol = f"{RED}✗{RESET}"
            status_display = f"{RED}{status}{RESET}"
            all_core_ok = False
        
        print(f"  {status_symbol} {package:.<20} {version:.<15} [{status_display}]")
    
    # Development Dependencies
    print_section("Development Dependencies")
    
    dev_deps = [
        ("pytest", "8.0.0"),
        ("hypothesis", "6.92.0"),
        ("mypy", "1.8.0"),
        ("ruff", "0.1.0"),
    ]
    
    all_dev_ok = True
    for package, min_version in dev_deps:
        is_installed, version, status = check_dependency(package, min_version)
        
        if is_installed and status == "OK":
            status_symbol = f"{GREEN}✓{RESET}"
            status_display = f"{GREEN}{status}{RESET}"
        elif is_installed:
            status_symbol = f"{YELLOW}⚠{RESET}"
            status_display = f"{YELLOW}{status}{RESET}"
            all_dev_ok = False
        else:
            status_symbol = f"{YELLOW}⚠{RESET}"
            status_display = f"{YELLOW}{status}{RESET}"
            all_dev_ok = False
        
        print(f"  {status_symbol} {package:.<20} {version:.<15} [{status_display}]")
    
    # Project Structure Check
    print_section("Project Structure")
    
    project_root = Path(__file__).parent.parent
    required_paths = [
        ("src/sample_size_estimator", "Source code directory"),
        ("tests", "Test directory"),
        ("scripts", "Scripts directory"),
        ("pyproject.toml", "Project configuration"),
        ("uv.lock", "Dependency lock file"),
        (".env.example", "Example environment file"),
    ]
    
    all_paths_ok = True
    for path_str, description in required_paths:
        path = project_root / path_str
        exists = path.exists()
        
        status_symbol = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
        status_text = f"{GREEN}Found{RESET}" if exists else f"{RED}Missing{RESET}"
        
        print(f"  {status_symbol} {path_str:.<30} [{status_text}]")
        
        if not exists:
            all_paths_ok = False
    
    # Summary
    print_section("Summary")
    
    overall_status = python_valid and all_core_ok and all_paths_ok
    
    if overall_status:
        print(f"  {GREEN}✓ Environment check PASSED{RESET}")
        print()
        print("  All required dependencies are installed and the project")
        print("  structure is correct. The application is ready to run.")
        print()
        print("  Next steps:")
        print("    1. Run tests: uv run pytest")
        print("    2. Start application: uv run streamlit run src/sample_size_estimator/app.py")
        print()
        return 0
    else:
        print(f"  {RED}✗ Environment check FAILED{RESET}")
        print()
        
        if not python_valid:
            print(f"  {RED}• Python version requirement not met{RESET}")
        
        if not all_core_ok:
            print(f"  {RED}• Some core dependencies are missing or outdated{RESET}")
            print("    Run: uv sync")
        
        if not all_dev_ok:
            print(f"  {YELLOW}• Some development dependencies are missing{RESET}")
            print("    Run: uv sync --group dev")
        
        if not all_paths_ok:
            print(f"  {RED}• Project structure is incomplete{RESET}")
        
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
