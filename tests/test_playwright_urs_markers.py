"""Property-based test for URS marker presence on Playwright tests.

This module verifies that all Playwright UI test functions are properly
decorated with the required URS traceability markers.

Requirements:
    - 10.1: All UI tests marked with @pytest.mark.urs("REQ-25")
    - 10.2: All UI tests marked with @pytest.mark.urs("URS-VAL-03")
    - 10.4: Maintain same traceability format as existing tests
"""

import ast
import pytest
from pathlib import Path
from typing import List, Tuple


def get_playwright_test_files() -> List[Path]:
    """Get all Playwright test files in the tests directory.
    
    Returns:
        List of Path objects for Playwright test files
    """
    tests_dir = Path(__file__).parent
    return list(tests_dir.glob("test_ui_playwright_*.py"))


def extract_test_functions_and_markers(file_path: Path) -> List[Tuple[str, List[str]]]:
    """Extract test function names and their URS markers from a Python file.
    
    Args:
        file_path: Path to the Python test file
    
    Returns:
        List of tuples (function_name, list_of_urs_markers)
    """
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    
    test_functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            # Extract URS markers from decorators
            urs_markers = []
            for decorator in node.decorator_list:
                # Handle @pytest.mark.urs("REQ-25") format
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if (isinstance(decorator.func.value, ast.Attribute) and
                            isinstance(decorator.func.value.value, ast.Name) and
                            decorator.func.value.value.id == 'pytest' and
                            decorator.func.value.attr == 'mark' and
                            decorator.func.attr == 'urs'):
                            # Extract the URS ID from the first argument
                            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                urs_markers.append(decorator.args[0].value)
            
            test_functions.append((node.name, urs_markers))
    
    return test_functions


# Feature: playwright-ui-testing, Property 13: URS Marker Presence
@pytest.mark.property
@pytest.mark.playwright
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
def test_property_urs_marker_presence():
    """
    Property 13: URS Marker Presence
    **Validates: Requirements 10.1, 10.2, 10.4**
    
    For all Playwright UI test functions, the function should be decorated
    with both @pytest.mark.urs("REQ-25") and @pytest.mark.urs("URS-VAL-03") markers.
    """
    # Get all Playwright test files
    playwright_test_files = get_playwright_test_files()
    
    # Verify we found some test files
    assert len(playwright_test_files) > 0, "No Playwright test files found"
    
    # Track all test functions and their markers
    all_tests = []
    missing_markers = []
    
    for test_file in playwright_test_files:
        test_functions = extract_test_functions_and_markers(test_file)
        
        for func_name, urs_markers in test_functions:
            all_tests.append((test_file.name, func_name))
            
            # Check for required markers
            has_req_25 = "REQ-25" in urs_markers
            has_urs_val_03 = "URS-VAL-03" in urs_markers
            
            if not has_req_25 or not has_urs_val_03:
                missing_info = {
                    'file': test_file.name,
                    'function': func_name,
                    'has_REQ-25': has_req_25,
                    'has_URS-VAL-03': has_urs_val_03,
                    'found_markers': urs_markers
                }
                missing_markers.append(missing_info)
    
    # Report findings
    print(f"\nAnalyzed {len(all_tests)} test functions across {len(playwright_test_files)} files")
    
    if missing_markers:
        print(f"\nFound {len(missing_markers)} test functions with missing URS markers:")
        for info in missing_markers:
            print(f"\n  File: {info['file']}")
            print(f"  Function: {info['function']}")
            print(f"  Has REQ-25: {info['has_REQ-25']}")
            print(f"  Has URS-VAL-03: {info['has_URS-VAL-03']}")
            print(f"  Found markers: {info['found_markers']}")
    
    # Assert that all test functions have both required markers
    assert len(missing_markers) == 0, (
        f"{len(missing_markers)} test function(s) missing required URS markers. "
        f"All Playwright test functions must have both @pytest.mark.urs('REQ-25') "
        f"and @pytest.mark.urs('URS-VAL-03') markers."
    )


@pytest.mark.property
@pytest.mark.playwright
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
def test_property_urs_marker_format():
    """
    Verify that URS markers use the correct format.
    
    This test ensures that URS markers follow the expected pattern:
    - @pytest.mark.urs("REQ-25")
    - @pytest.mark.urs("URS-VAL-03")
    
    **Validates: Requirements 10.4**
    """
    playwright_test_files = get_playwright_test_files()
    
    # Expected URS IDs for Playwright tests
    expected_urs_ids = {"REQ-25", "URS-VAL-03"}
    
    invalid_markers = []
    
    for test_file in playwright_test_files:
        test_functions = extract_test_functions_and_markers(test_file)
        
        for func_name, urs_markers in test_functions:
            # Check that all URS markers are in the expected set
            for marker in urs_markers:
                if marker not in expected_urs_ids:
                    invalid_markers.append({
                        'file': test_file.name,
                        'function': func_name,
                        'invalid_marker': marker
                    })
    
    if invalid_markers:
        print(f"\nFound {len(invalid_markers)} unexpected URS markers:")
        for info in invalid_markers:
            print(f"\n  File: {info['file']}")
            print(f"  Function: {info['function']}")
            print(f"  Unexpected marker: {info['invalid_marker']}")
    
    # Assert that all URS markers are valid
    assert len(invalid_markers) == 0, (
        f"{len(invalid_markers)} test function(s) have unexpected URS markers. "
        f"Playwright tests should only use REQ-25 and URS-VAL-03."
    )


@pytest.mark.property
@pytest.mark.playwright
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
def test_property_playwright_marker_presence():
    """
    Verify that all Playwright test functions have the @pytest.mark.playwright marker.
    
    This ensures tests can be filtered using pytest -m playwright.
    
    **Validates: Requirements 10.5, 12.1**
    """
    playwright_test_files = get_playwright_test_files()
    
    missing_playwright_marker = []
    
    for test_file in playwright_test_files:
        # Parse the file to check for playwright markers
        with open(test_file, 'r') as f:
            tree = ast.parse(f.read(), filename=str(test_file))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Check for @pytest.mark.playwright decorator
                has_playwright_marker = False
                
                for decorator in node.decorator_list:
                    # Handle @pytest.mark.playwright format
                    if isinstance(decorator, ast.Attribute):
                        if (isinstance(decorator.value, ast.Attribute) and
                            isinstance(decorator.value.value, ast.Name) and
                            decorator.value.value.id == 'pytest' and
                            decorator.value.attr == 'mark' and
                            decorator.attr == 'playwright'):
                            has_playwright_marker = True
                            break
                
                if not has_playwright_marker:
                    missing_playwright_marker.append({
                        'file': test_file.name,
                        'function': node.name
                    })
    
    if missing_playwright_marker:
        print(f"\nFound {len(missing_playwright_marker)} test functions without @pytest.mark.playwright:")
        for info in missing_playwright_marker:
            print(f"  {info['file']}::{info['function']}")
    
    # Assert that all test functions have the playwright marker
    assert len(missing_playwright_marker) == 0, (
        f"{len(missing_playwright_marker)} test function(s) missing @pytest.mark.playwright marker. "
        f"All Playwright test functions must be marked for filtering."
    )
