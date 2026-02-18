"""Pytest configuration and fixtures for Sample Size Estimator tests.

This module provides:
- Pytest markers for URS requirement traceability
- Common test data fixtures
- Hypothesis configuration for property-based testing
- Playwright fixtures for UI testing
"""

import os
import subprocess
import time
from typing import Generator

import pytest
import requests
from hypothesis import settings

from tests.playwright_config import PlaywrightTestConfig

# ============================================================================
# Pytest Markers for URS Requirement Traceability
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers for URS requirement traceability."""
    # URS markers for requirement traceability
    config.addinivalue_line(
        "markers",
        "urs(id): mark test as validating a specific URS requirement ID"
    )
    
    # Module markers for organizing tests
    config.addinivalue_line(
        "markers",
        "attribute: mark test as related to attribute calculations"
    )
    config.addinivalue_line(
        "markers",
        "variables: mark test as related to variables calculations"
    )
    config.addinivalue_line(
        "markers",
        "non_normal: mark test as related to non-normal calculations"
    )
    config.addinivalue_line(
        "markers",
        "reliability: mark test as related to reliability calculations"
    )
    config.addinivalue_line(
        "markers",
        "validation: mark test as related to validation and hash verification"
    )
    config.addinivalue_line(
        "markers",
        "reports: mark test as related to PDF report generation"
    )
    config.addinivalue_line(
        "markers",
        "config: mark test as related to configuration management"
    )
    config.addinivalue_line(
        "markers",
        "logging: mark test as related to logging functionality"
    )
    config.addinivalue_line(
        "markers",
        "ui: mark test as related to Streamlit UI"
    )
    
    # Test type markers
    config.addinivalue_line(
        "markers",
        "property: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers",
        "playwright: mark test as Playwright browser automation test"
    )
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end test requiring running application"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test execution results for fixtures.
    
    This hook stores test outcome information on the test item so that
    fixtures can access it during teardown to determine if the test failed.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ============================================================================
# Hypothesis Configuration for Property-Based Testing
# ============================================================================

# Configure hypothesis settings globally
# Requirement REQ-24: Minimum 100 iterations per property test
settings.register_profile(
    "default",
    max_examples=100,
    deadline=None,  # Disable deadline for complex calculations
    print_blob=True  # Print failing examples for debugging
)

settings.register_profile(
    "ci",
    max_examples=200,  # More thorough testing in CI
    deadline=None,
    print_blob=True
)

settings.register_profile(
    "dev",
    max_examples=50,  # Faster feedback during development
    deadline=None,
    print_blob=True
)

# Load the appropriate profile
settings.load_profile("default")


# ============================================================================
# Common Test Data Fixtures
# ============================================================================

@pytest.fixture
def valid_confidence_values():
    """Provide common valid confidence level values for testing."""
    return [50.0, 80.0, 90.0, 95.0, 99.0, 99.9]


@pytest.fixture
def valid_reliability_values():
    """Provide common valid reliability values for testing."""
    return [50.0, 80.0, 90.0, 95.0, 99.0, 99.9]


@pytest.fixture
def valid_allowable_failures():
    """Provide common valid allowable failure values for testing."""
    return [0, 1, 2, 3, 4, 5]


@pytest.fixture
def sample_attribute_input():
    """Provide a sample AttributeInput for testing."""
    from src.sample_size_estimator.models import AttributeInput
    return AttributeInput(
        confidence=95.0,
        reliability=90.0,
        allowable_failures=0
    )


@pytest.fixture
def sample_variables_input():
    """Provide a sample VariablesInput for testing."""
    from src.sample_size_estimator.models import VariablesInput
    return VariablesInput(
        confidence=95.0,
        reliability=90.0,
        sample_size=30,
        sample_mean=10.0,
        sample_std=1.0,
        lsl=7.0,
        usl=13.0,
        sided="two"
    )


@pytest.fixture
def sample_reliability_input():
    """Provide a sample ReliabilityInput for testing."""
    from src.sample_size_estimator.models import ReliabilityInput
    return ReliabilityInput(
        confidence=95.0,
        reliability=90.0,
        failures=0,
        activation_energy=0.7,
        use_temperature=298.15,
        test_temperature=358.15
    )


@pytest.fixture
def sample_normal_data():
    """Provide a sample normally distributed dataset for testing."""
    import numpy as np
    np.random.seed(42)
    return np.random.normal(loc=10.0, scale=2.0, size=50).tolist()


@pytest.fixture
def sample_non_normal_data():
    """Provide a sample non-normally distributed dataset for testing."""
    import numpy as np
    np.random.seed(42)
    # Exponential distribution is clearly non-normal
    return np.random.exponential(scale=2.0, size=50).tolist()


@pytest.fixture
def sample_data_with_outliers():
    """Provide a dataset with clear outliers for testing."""
    return [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 100.0, 200.0]


@pytest.fixture
def sample_positive_data():
    """Provide a sample dataset with all positive values for transformation testing."""
    import numpy as np
    np.random.seed(42)
    return np.random.uniform(low=0.1, high=100.0, size=30).tolist()


@pytest.fixture
def known_statistical_values():
    """Provide known statistical reference values for validation.
    
    These are well-established values from statistical tables and references
    used to verify calculation correctness.
    """
    return {
        "attribute": {
            # Success Run Theorem: C=95%, R=90% → n=29
            "success_run_95_90": {"confidence": 95.0, "reliability": 90.0, "expected_n": 29},
            # Success Run Theorem: C=90%, R=95% → n=45
            "success_run_90_95": {"confidence": 90.0, "reliability": 95.0, "expected_n": 45},
            # Binomial: C=95%, R=90%, c=1 → n=46
            "binomial_95_90_c1": {"confidence": 95.0, "reliability": 90.0, "c": 1, "expected_n": 46},
            # Binomial: C=95%, R=90%, c=2 → n=61
            "binomial_95_90_c2": {"confidence": 95.0, "reliability": 90.0, "c": 2, "expected_n": 61},
            # Binomial: C=95%, R=90%, c=3 → n=76
            "binomial_95_90_c3": {"confidence": 95.0, "reliability": 90.0, "c": 3, "expected_n": 76},
        },
        "variables": {
            # Process capability example: Mean=10, Std=1, LSL=7, USL=13 → Ppk=1.0
            "ppk_example_1": {
                "mean": 10.0,
                "std": 1.0,
                "lsl": 7.0,
                "usl": 13.0,
                "expected_ppk": 1.0
            },
            # Centered process: Mean=10, Std=0.5, LSL=8, USL=12 → Ppk≈1.33
            "ppk_example_2": {
                "mean": 10.0,
                "std": 0.5,
                "lsl": 8.0,
                "usl": 12.0,
                "expected_ppk": 1.333
            },
        },
        "reliability": {
            # Zero-failure demonstration: C=95%, r=0 → chi^2 value
            "zero_failure_95": {"confidence": 95.0, "failures": 0, "expected_chi2": 5.991},
            # Arrhenius example: Ea=0.7eV, T_use=298K, T_test=358K → AF≈10
            "arrhenius_example": {
                "activation_energy": 0.7,
                "use_temperature": 298.15,
                "test_temperature": 358.15,
                "expected_af_approx": 10.0
            },
        }
    }


@pytest.fixture
def temp_report_dir(tmp_path):
    """Provide a temporary directory for report generation testing."""
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    return report_dir


@pytest.fixture
def sample_calculation_report_data():
    """Provide sample data for calculation report generation."""
    from datetime import datetime
    return {
        "timestamp": datetime.now(),
        "module": "attribute",
        "inputs": {
            "confidence": 95.0,
            "reliability": 90.0,
            "allowable_failures": 0
        },
        "results": {
            "sample_size": 29,
            "method": "success_run"
        },
        "engine_hash": "abc123def456",
        "validated_state": True,
        "app_version": "1.0.0"
    }


@pytest.fixture
def sample_validation_certificate_data():
    """Provide sample data for validation certificate generation."""
    from datetime import datetime
    return {
        "test_date": datetime.now(),
        "tester": "Test System",
        "system_info": {
            "os": "Windows 10",
            "python_version": "3.11.0",
            "dependencies": {
                "scipy": "1.11.0",
                "numpy": "1.24.0",
                "streamlit": "1.28.0"
            }
        },
        "urs_results": [
            {"urs_id": "URS-FUNC_A-01", "status": "PASS", "test_name": "test_input_validation"},
            {"urs_id": "URS-FUNC_A-02", "status": "PASS", "test_name": "test_success_run_theorem"},
            {"urs_id": "URS-FUNC_A-03", "status": "PASS", "test_name": "test_binomial_calculation"},
        ],
        "validated_hash": "abc123def456789",
        "all_passed": True
    }


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing logging functionality."""
    import logging
    from io import StringIO
    
    # Create a logger with a string buffer
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # Add a string handler
    string_buffer = StringIO()
    handler = logging.StreamHandler(string_buffer)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    # Attach the buffer to the logger for easy access
    logger.string_buffer = string_buffer
    
    yield logger
    
    # Cleanup
    logger.removeHandler(handler)


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def assert_close():
    """Provide a utility function for comparing floating point values."""
    def _assert_close(actual, expected, rel_tol=1e-9, abs_tol=1e-9, msg=""):
        """Assert that two floating point values are close within tolerance."""
        import math
        if not math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol):
            raise AssertionError(
                f"{msg}\nExpected: {expected}\nActual: {actual}\n"
                f"Difference: {abs(actual - expected)}"
            )
    return _assert_close


@pytest.fixture
def assert_array_close():
    """Provide a utility function for comparing arrays of floating point values."""
    def _assert_array_close(actual, expected, rel_tol=1e-9, abs_tol=1e-9, msg=""):
        """Assert that two arrays are element-wise close within tolerance."""
        import numpy as np
        actual_arr = np.array(actual)
        expected_arr = np.array(expected)
        
        if actual_arr.shape != expected_arr.shape:
            raise AssertionError(
                f"{msg}\nShape mismatch: {actual_arr.shape} != {expected_arr.shape}"
            )
        
        if not np.allclose(actual_arr, expected_arr, rtol=rel_tol, atol=abs_tol):
            max_diff = np.max(np.abs(actual_arr - expected_arr))
            raise AssertionError(
                f"{msg}\nArrays not close.\nMax difference: {max_diff}\n"
                f"Expected: {expected_arr}\nActual: {actual_arr}"
            )
    return _assert_array_close


# ============================================================================
# Playwright UI Testing Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def playwright_config() -> PlaywrightTestConfig:
    """Provide Playwright test configuration.
    
    Returns:
        PlaywrightTestConfig: Configuration loaded from environment variables
    """
    return PlaywrightTestConfig()


@pytest.fixture(scope="session")
def browser(playwright, playwright_config: PlaywrightTestConfig):
    """Launch Playwright browser for test session.
    
    This fixture manages the browser instance lifecycle for the test session:
    1. Launches browser based on configuration (Chromium by default)
    2. Configures headless mode from environment variable
    3. Sets default timeout for element interactions
    4. Closes browser after all tests complete
    
    Args:
        playwright: Playwright instance (provided by pytest-playwright)
        playwright_config: Configuration containing browser settings
    
    Yields:
        Browser: Playwright browser instance
    
    Requirements:
        - 2.1: Launch Browser_Instance using Playwright when tests execute
        - 2.2: Support headless mode for CI/CD environments
        - 2.3: Support visible mode for local debugging
        - 2.4: Close Browser_Instance when test completes
        - 2.5: Configure appropriate timeouts for element interactions
    """
    # Select browser type based on configuration
    browser_type = getattr(playwright, playwright_config.browser_type)
    
    # Launch browser with configured settings
    browser_instance = browser_type.launch(
        headless=playwright_config.headless,
    )
    
    print(f"\nLaunched {playwright_config.browser_type} browser "
          f"(headless={playwright_config.headless})")
    
    yield browser_instance
    
    # Cleanup: close browser
    browser_instance.close()
    print(f"\n{playwright_config.browser_type.capitalize()} browser closed")


@pytest.fixture(scope="function")
def page(browser, streamlit_app: str, playwright_config: PlaywrightTestConfig, request):
    """Create new browser page for each test.
    
    This fixture provides a fresh browser page for each test:
    1. Creates new page from browser instance
    2. Navigates to Streamlit app URL
    3. Waits for page to load completely
    4. Yields page to test
    5. On test failure: captures screenshot and console logs
    6. Closes page after test completes
    
    Args:
        browser: Playwright browser instance (session scope)
        streamlit_app: URL of running Streamlit app (session scope)
        playwright_config: Configuration containing screenshot directory
        request: Pytest request object for accessing test information
    
    Yields:
        Page: Playwright page instance navigated to app
    
    Requirements:
        - 8.1: Reset browser state for each test (test isolation)
        - 8.2: Capture screenshot for debugging on test failure
        - 8.3: Capture browser console logs on test failure
    """
    # Create new page
    page_instance = browser.new_page()
    
    # Set default timeout from configuration
    page_instance.set_default_timeout(playwright_config.timeout)
    
    # Collect console logs for debugging
    console_logs = []
    
    def log_console_message(msg):
        """Capture console messages."""
        console_logs.append(f"[{msg.type}] {msg.text}")
    
    page_instance.on("console", log_console_message)
    
    # Navigate to Streamlit app
    page_instance.goto(streamlit_app)
    
    # Wait for page to load completely
    # Wait for Streamlit's main container to be visible
    page_instance.wait_for_selector("[data-testid='stAppViewContainer']", timeout=30000)
    
    # Wait for Streamlit React app to fully hydrate
    # This is critical - Streamlit takes time to render the actual content
    try:
        page_instance.wait_for_selector("text=Sample Size Estimator", timeout=30000)
    except Exception:
        # If title doesn't appear, at least wait for some content
        page_instance.wait_for_timeout(5000)
    
    # CRITICAL: Wait for tabs to be rendered
    # Streamlit tabs take additional time to render after the main content
    # This is especially important for property tests that immediately try to click tabs
    try:
        # Wait for at least one tab button to be present
        page_instance.wait_for_selector("button[role='tab']", timeout=30000)
        # Give Streamlit a moment to finish rendering all tabs
        page_instance.wait_for_timeout(2000)
    except Exception:
        # If tabs don't appear, wait a bit longer and continue
        # The test will fail with a better error message
        page_instance.wait_for_timeout(3000)
    
    yield page_instance
    
    # Cleanup: capture artifacts on failure, then close page
    try:
        # Check if test failed
        if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
            # Capture screenshot
            screenshot_dir = playwright_config.screenshot_dir
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Generate screenshot filename from test name
            test_name = request.node.name
            screenshot_path = os.path.join(screenshot_dir, f"{test_name}.png")
            page_instance.screenshot(path=screenshot_path)
            print(f"\nScreenshot saved: {screenshot_path}")
            
            # Print console logs
            if console_logs:
                print("\nBrowser console logs:")
                for log in console_logs:
                    print(f"  {log}")
    except Exception as e:
        print(f"\nError capturing test failure artifacts: {e}")
    finally:
        # Always close the page
        page_instance.close()


@pytest.fixture(scope="session")
def streamlit_app(playwright_config: PlaywrightTestConfig) -> Generator[str, None, None]:
    """Start Streamlit app in subprocess, yield URL, then terminate.
    
    This fixture manages the Streamlit application lifecycle for the test session:
    1. Starts Streamlit in a subprocess with appropriate arguments
    2. Polls the health endpoint until the app is ready (30 second timeout)
    3. Yields the app URL to tests
    4. Terminates the subprocess after all tests complete
    
    Args:
        playwright_config: Configuration containing port and host settings
    
    Yields:
        str: URL of running Streamlit app (e.g., "http://localhost:8501")
    
    Raises:
        TimeoutError: If app doesn't start within 30 seconds
        RuntimeError: If subprocess fails to start or crashes
    
    Requirements:
        - 1.1: Start Streamlit_App in subprocess when test suite begins
        - 1.2: Wait until application is ready to accept connections
        - 1.3: Terminate subprocess when test suite completes
        - 1.4: Raise timeout error if app doesn't start within 30 seconds
        - 1.5: Ensure all resources are cleaned up when subprocess terminates
    """
    # Start subprocess
    process = None
    try:
        # Ensure we run from project root where main.py is located
        project_root = os.getcwd()
        main_py_path = os.path.join(project_root, "main.py")
        
        # Build command with absolute path
        cmd = [
            "uv",
            "run",
            "streamlit",
            "run",
            main_py_path,
            f"--server.port={playwright_config.streamlit_port}",
            "--server.headless=true",
            "--server.address=localhost",
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            cwd=project_root,  # Explicitly set working directory
        )
        
        # Wait for app to be ready (health check polling)
        health_url = f"{playwright_config.app_url}/_stcore/health"
        start_time = time.time()
        timeout = 30  # seconds
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if process.poll() is not None:
                # Process terminated unexpectedly
                stdout, stderr = process.communicate()
                raise RuntimeError(
                    f"Streamlit process terminated unexpectedly.\n"
                    f"Exit code: {process.returncode}\n"
                    f"STDOUT:\n{stdout}\n"
                    f"STDERR:\n{stderr}"
                )
            
            # Try to connect to health endpoint
            try:
                response = requests.get(health_url, timeout=1)
                if response.status_code == 200:
                    # App is ready!
                    print(f"\nStreamlit app started successfully at {playwright_config.app_url}")
                    break
            except (requests.ConnectionError, requests.Timeout):
                # App not ready yet, continue waiting
                pass
            
            time.sleep(0.5)  # Wait before next check
        else:
            # Timeout reached
            # Get any output that was produced
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            
            raise TimeoutError(
                f"Streamlit app failed to start within {timeout} seconds.\n"
                f"Health check URL: {health_url}\n"
                f"STDOUT:\n{stdout}\n"
                f"STDERR:\n{stderr}"
            )
        
        # Yield app URL to tests
        yield playwright_config.app_url
        
    finally:
        # Cleanup: terminate subprocess
        if process is not None:
            try:
                # Try graceful termination first
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print("\nStreamlit app terminated gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination fails
                    process.kill()
                    process.wait()
                    print("\nStreamlit app force killed")
            except Exception as e:
                print(f"\nError during Streamlit cleanup: {e}")
                # Try force kill as last resort
                try:
                    process.kill()
                    process.wait()
                except Exception:
                    pass


# ============================================================================
# Playwright UI Interaction Helper Functions
# ============================================================================

def click_tab(page, tab_name: str) -> None:
    """Click a Streamlit tab by name.
    
    Uses Playwright's get_by_role() for accessible element selection.
    Waits for the tab to be visible and clickable before clicking.
    
    Args:
        page: Playwright Page instance
        tab_name: Name of the tab to click (e.g., "Attribute (Binomial)")
    
    Requirements:
        - 3.1: Click tab element to navigate to tab
        - 4.1: Click tab element to navigate to Variables tab
        - 5.1: Click tab element to navigate to Non-Normal tab
        - 6.1: Click tab element to navigate to Reliability tab
    """
    page.get_by_role("tab", name=tab_name).click()


def fill_number_input(page, label: str, value: float) -> None:
    """Fill a Streamlit number input by label.
    
    Uses Playwright's get_by_label() for accessible element selection.
    Clears the input first, then fills with the new value.
    
    Args:
        page: Playwright Page instance
        label: Label text of the number input (e.g., "Confidence Level (%)")
        value: Numeric value to enter
    
    Requirements:
        - 3.2: Input numeric value into confidence field
        - 3.3: Input numeric value into reliability field
        - 4.2: Input sample parameters
        - 4.3: Input specification limits
        - 6.2: Input test parameters
        - 6.3: Input Arrhenius parameters
    """
    input_element = page.get_by_label(label)
    input_element.clear()
    input_element.fill(str(value))


def click_button(page, button_text: str) -> None:
    """Click a Streamlit button by text.
    
    Uses Playwright's get_by_role() for accessible element selection.
    Waits for the button to be visible and clickable before clicking.
    
    Args:
        page: Playwright Page instance
        button_text: Text displayed on the button (e.g., "Calculate Sample Size")
    
    Requirements:
        - 3.4: Click calculate button to trigger calculation
        - 4.4: Click calculate button to trigger tolerance limit calculation
        - 5.3: Click detect outliers button
        - 5.5: Click test normality button
        - 5.9: Click apply transformation button
        - 6.4: Click calculate button to trigger test duration calculation
    """
    page.get_by_role("button", name=button_text).click()


def get_text_content(page, selector: str) -> str:
    """Get text content from element.
    
    Waits for the element to be visible before retrieving text content.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector or text selector for the element
    
    Returns:
        str: Text content of the element
    
    Requirements:
        - 3.5: Verify results table is visible
        - 3.6: Verify sample size matches expected value
        - 4.5: Verify tolerance factor displays
        - 4.6: Verify upper and lower tolerance limits display
        - 4.7: Verify Ppk value displays
        - 4.8: Verify PASS/FAIL status displays
        - 5.4: Verify outlier count displays
        - 5.6: Verify Shapiro-Wilk p-value displays
        - 5.7: Verify Anderson-Darling results display
        - 6.5: Verify test duration displays
        - 6.6: Verify acceleration factor displays
    """
    element = page.locator(selector)
    element.wait_for(state="visible")
    return element.text_content()


def wait_for_element(page, selector: str, timeout: int = 30000) -> None:
    """Wait for element to be visible.
    
    Waits for the specified element to appear and be visible in the page.
    
    Args:
        page: Playwright Page instance
        selector: CSS selector or text selector for the element
        timeout: Maximum time to wait in milliseconds (default: 30000)
    
    Raises:
        TimeoutError: If element doesn't become visible within timeout
    
    Requirements:
        - 3.5: Verify results table is visible
        - 4.5: Verify tolerance factor displays
        - 5.4: Verify outlier count displays
        - 5.6: Verify Shapiro-Wilk p-value displays
        - 6.5: Verify test duration displays
    """
    page.locator(selector).wait_for(state="visible", timeout=timeout)
