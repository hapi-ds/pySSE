#!/usr/bin/env python3
"""
Validation Certificate Generation Script

This script runs the test suite, collects results with URS markers,
calculates the validated hash of the calculation engine, and generates
a validation certificate PDF.

Requirements: REQ-22, REQ-24
"""

import sys
import platform
from datetime import datetime
from pathlib import Path
import subprocess
import json
import hashlib

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sample_size_estimator.reports import generate_validation_certificate
from sample_size_estimator.validation import calculate_file_hash


def get_system_info() -> dict[str, str]:
    """
    Collect system information for the validation certificate.
    
    Returns:
        Dictionary with OS, Python version, and key dependencies
    """
    # Get Python version
    python_version = platform.python_version()
    
    # Get OS information
    os_info = f"{platform.system()} {platform.release()}"
    
    # Get key dependency versions
    dependencies = {}
    try:
        import scipy
        dependencies["scipy"] = scipy.__version__
    except ImportError:
        dependencies["scipy"] = "Not installed"
    
    try:
        import numpy
        dependencies["numpy"] = numpy.__version__
    except ImportError:
        dependencies["numpy"] = "Not installed"
    
    try:
        import streamlit
        dependencies["streamlit"] = streamlit.__version__
    except ImportError:
        dependencies["streamlit"] = "Not installed"
    
    try:
        import pydantic
        dependencies["pydantic"] = pydantic.__version__
    except ImportError:
        dependencies["pydantic"] = "Not installed"
    
    try:
        import reportlab
        dependencies["reportlab"] = reportlab.Version
    except ImportError:
        dependencies["reportlab"] = "Not installed"
    
    return {
        "os": os_info,
        "python_version": python_version,
        "dependencies": dependencies
    }


def calculate_calculation_engine_hash() -> str:
    """
    Calculate SHA-256 hash of all calculation module files.
    
    This creates a combined hash of all calculation files to ensure
    the entire calculation engine is validated.
    
    Returns:
        Hexadecimal hash string of the calculation engine
    """
    calc_dir = Path(__file__).parent.parent / "src" / "sample_size_estimator" / "calculations"
    
    # Get all Python files in calculations directory (excluding __pycache__)
    calc_files = sorted([
        f for f in calc_dir.glob("*.py")
        if f.name != "__pycache__"
    ])
    
    # Create combined hash
    combined_hash = hashlib.sha256()
    
    for calc_file in calc_files:
        file_hash = calculate_file_hash(str(calc_file))
        combined_hash.update(file_hash.encode())
    
    return combined_hash.hexdigest()


def run_tests_and_collect_results() -> dict[str, list[dict[str, str]]]:
    """
    Run pytest test suite and collect results with URS markers.
    
    Returns:
        Dictionary with test results including URS IDs, test names, and status
    """
    print("Running test suite...")
    
    # Run pytest with verbose output
    result = subprocess.run(
        ["uv", "run", "pytest", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    # Parse test results from output
    urs_results = []
    test_passed = result.returncode == 0
    
    # Parse the output to extract test results
    # Combine stdout and stderr for complete output
    output = result.stdout + result.stderr
    lines = output.split("\n")
    
    # Track test statistics
    passed_count = 0
    failed_count = 0
    
    for line in lines:
        if "PASSED" in line or "FAILED" in line:
            # Extract test name and status
            parts = line.split("::")
            if len(parts) >= 2:
                test_file = parts[0].strip()
                # Get the test name (before PASSED/FAILED)
                test_part = parts[-1]
                if "PASSED" in test_part:
                    test_name = test_part.split("PASSED")[0].strip()
                    status = "PASS"
                    passed_count += 1
                else:
                    test_name = test_part.split("FAILED")[0].strip()
                    status = "FAIL"
                    failed_count += 1
                
                # Generate a URS ID based on test module
                # In a real implementation, tests would have @pytest.mark.urs() decorators
                urs_id = generate_urs_id_from_test(test_file, test_name)
                
                urs_results.append({
                    "urs_id": urs_id,
                    "test_name": test_name,
                    "status": status
                })
    
    # If no results parsed, add summary info
    if not urs_results:
        # Check if tests passed overall
        if test_passed:
            urs_results.append({
                "urs_id": "ALL-TESTS",
                "test_name": "Complete Test Suite",
                "status": "PASS"
            })
        else:
            urs_results.append({
                "urs_id": "ALL-TESTS",
                "test_name": "Complete Test Suite",
                "status": "FAIL"
            })
    
    print(f"  Passed: {passed_count}")
    print(f"  Failed: {failed_count}")
    
    return {
        "urs_results": urs_results,
        "all_passed": test_passed
    }


def generate_urs_id_from_test(test_file: str, test_name: str) -> str:
    """
    Generate a URS ID based on test file and name.
    
    This is a helper function to map tests to URS requirements.
    In production, tests should use @pytest.mark.urs() decorators.
    
    Args:
        test_file: Test file name
        test_name: Test function name
    
    Returns:
        URS requirement ID
    """
    # Map test files to URS categories
    if "attribute" in test_file:
        return "URS-FUNC_A"
    elif "variables" in test_file:
        return "URS-FUNC_V"
    elif "non_normal" in test_file:
        return "URS-FUNC_N"
    elif "reliability" in test_file:
        return "URS-FUNC_R"
    elif "validation" in test_file:
        return "URS-VAL"
    elif "reports" in test_file:
        return "URS-REP"
    elif "config" in test_file:
        return "URS-CFG"
    elif "logger" in test_file:
        return "URS-LOG"
    else:
        return "URS-GEN"


def main() -> int:
    """
    Main entry point for validation certificate generation.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 70)
    print("Sample Size Estimator - Validation Certificate Generation")
    print("=" * 70)
    print()
    
    # Collect system information
    print("Collecting system information...")
    system_info = get_system_info()
    print(f"  OS: {system_info['os']}")
    print(f"  Python: {system_info['python_version']}")
    print(f"  Dependencies: {len(system_info['dependencies'])} packages")
    print()
    
    # Run tests and collect results
    test_results = run_tests_and_collect_results()
    
    print(f"Test Results: {len(test_results['urs_results'])} tests collected")
    print(f"Overall Status: {'PASSED' if test_results['all_passed'] else 'FAILED'}")
    print()
    
    # Calculate validated hash
    print("Calculating calculation engine hash...")
    validated_hash = calculate_calculation_engine_hash()
    print(f"  Validated Hash: {validated_hash}")
    print()
    
    # Prepare certificate data
    certificate_data = {
        "test_date": datetime.now(),
        "tester": f"{platform.node()} - Automated Test System",
        "system_info": system_info,
        "urs_results": test_results["urs_results"],
        "validated_hash": validated_hash,
        "all_passed": test_results["all_passed"]
    }
    
    # Generate certificate
    output_dir = Path(__file__).parent.parent / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"validation_certificate_{timestamp}.pdf"
    
    print(f"Generating validation certificate...")
    print(f"  Output: {output_path}")
    
    try:
        generate_validation_certificate(certificate_data, str(output_path))
        print()
        print("=" * 70)
        print("SUCCESS: Validation certificate generated successfully!")
        print("=" * 70)
        print()
        print(f"Certificate saved to: {output_path}")
        print(f"Validated Hash: {validated_hash}")
        print()
        print("Next steps:")
        print("1. Review the validation certificate PDF")
        print("2. Update .env file with VALIDATED_HASH if all tests passed")
        print(f"   VALIDATED_HASH={validated_hash}")
        print()
        
        return 0
    except Exception as e:
        print()
        print("=" * 70)
        print(f"ERROR: Failed to generate validation certificate")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
