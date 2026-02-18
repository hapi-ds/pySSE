# Design Document: Playwright UI Testing

## Overview

This design document describes the implementation of end-to-end UI testing using Playwright browser automation for the Sample Size Estimator Streamlit application. The solution addresses the limitations of the current Streamlit AppTest framework by using true browser automation to interact with the running application.

The implementation will:
- Start the Streamlit application in a subprocess before tests
- Use Playwright to control a browser and interact with UI elements
- Verify calculations display correctly in the rendered HTML
- Maintain URS traceability for REQ-25 compliance
- Support both local development (visible browser) and CI/CD (headless mode)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Pytest Test Suite                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Test Session Fixtures (conftest.py)                   │ │
│  │  - streamlit_app (session scope)                       │ │
│  │  - browser (session scope)                             │ │
│  │  - page (function scope)                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Test Files                                            │ │
│  │  - test_ui_playwright_attribute.py                     │ │
│  │  - test_ui_playwright_variables.py                     │ │
│  │  - test_ui_playwright_non_normal.py                    │ │
│  │  - test_ui_playwright_reliability.py                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Playwright Browser                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Browser Instance (Chromium/Firefox/WebKit)            │ │
│  │  - Headless or Visible mode                            │ │
│  │  - Page navigation                                     │ │
│  │  - Element interaction (click, fill, select)           │ │
│  │  - Content verification (text, visibility)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Interacts with
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Streamlit App (Subprocess)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Sample Size Estimator Application                     │ │
│  │  - Running on localhost:8501                           │ │
│  │  - Started by subprocess_manager fixture               │ │
│  │  - Terminated after test session                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Test Session Start
    │
    ├─> Start Streamlit subprocess (streamlit_app fixture)
    │   └─> Wait for app to be ready (health check)
    │
    ├─> Launch Playwright browser (browser fixture)
    │   └─> Configure headless/visible mode
    │
    └─> For each test:
        ├─> Create new page (page fixture)
        ├─> Navigate to app URL
        ├─> Interact with UI elements
        ├─> Verify results in rendered HTML
        ├─> On failure: capture screenshot + logs
        └─> Close page
    
Test Session End
    │
    ├─> Close browser
    └─> Terminate Streamlit subprocess
```

## Components and Interfaces

### 1. Subprocess Manager (conftest.py fixture)

**Purpose:** Manage the Streamlit application lifecycle during testing.

**Interface:**
```python
@pytest.fixture(scope="session")
def streamlit_app() -> Generator[str, None, None]:
    """
    Start Streamlit app in subprocess, yield URL, then terminate.
    
    Returns:
        str: URL of running Streamlit app (e.g., "http://localhost:8501")
    
    Raises:
        TimeoutError: If app doesn't start within 30 seconds
    """
    pass
```

**Implementation Details:**
- Use `subprocess.Popen()` to start Streamlit
- Command: `["uv", "run", "streamlit", "run", "src/sample_size_estimator/app.py", "--server.port=8501", "--server.headless=true"]`
- Poll app health endpoint: `http://localhost:8501/_stcore/health`
- Wait up to 30 seconds for app to be ready
- Capture stdout/stderr for debugging
- Use `process.terminate()` then `process.wait(timeout=5)` for graceful shutdown
- Use `process.kill()` if terminate fails

### 2. Browser Manager (conftest.py fixture)

**Purpose:** Manage Playwright browser instance lifecycle.

**Interface:**
```python
@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """
    Launch Playwright browser for test session.
    
    Args:
        playwright: Playwright instance (provided by pytest-playwright)
    
    Returns:
        Browser: Playwright browser instance
    """
    pass
```

**Implementation Details:**
- Use `playwright.chromium.launch()` by default
- Read headless mode from environment variable `PLAYWRIGHT_HEADLESS` (default: True)
- Configure browser with appropriate timeouts
- Close browser after all tests complete

### 3. Page Manager (conftest.py fixture)

**Purpose:** Provide fresh browser page for each test.

**Interface:**
```python
@pytest.fixture(scope="function")
def page(browser: Browser, streamlit_app: str) -> Generator[Page, None, None]:
    """
    Create new browser page for each test.
    
    Args:
        browser: Playwright browser instance
        streamlit_app: URL of running Streamlit app
    
    Returns:
        Page: Playwright page instance navigated to app
    """
    pass
```

**Implementation Details:**
- Create new page with `browser.new_page()`
- Navigate to streamlit_app URL
- Wait for page to load completely
- Yield page to test
- On test failure: capture screenshot to `reports/screenshots/`
- On test failure: capture console logs
- Close page after test

### 4. UI Interaction Helpers (conftest.py)

**Purpose:** Provide reusable functions for common Streamlit UI interactions.

**Interface:**
```python
def click_tab(page: Page, tab_name: str) -> None:
    """Click a Streamlit tab by name."""
    pass

def fill_number_input(page: Page, label: str, value: float) -> None:
    """Fill a Streamlit number input by label."""
    pass

def click_button(page: Page, button_text: str) -> None:
    """Click a Streamlit button by text."""
    pass

def get_text_content(page: Page, selector: str) -> str:
    """Get text content from element."""
    pass

def wait_for_element(page: Page, selector: str, timeout: int = 30000) -> None:
    """Wait for element to be visible."""
    pass
```

**Implementation Details:**
- Use Playwright's `page.locator()` with appropriate selectors
- Use `page.get_by_role()` for accessible element selection
- Use `page.get_by_text()` for text-based selection
- Handle Streamlit's dynamic element rendering
- Add appropriate waits for elements to be interactive

### 5. Test Files

**Structure:**
- `tests/test_ui_playwright_attribute.py` - Attribute tab tests
- `tests/test_ui_playwright_variables.py` - Variables tab tests
- `tests/test_ui_playwright_non_normal.py` - Non-Normal tab tests
- `tests/test_ui_playwright_reliability.py` - Reliability tab tests

**Common Pattern:**
```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
def test_attribute_zero_failure_calculation(page: Page):
    """Test zero-failure calculation in Attribute tab."""
    # Navigate to tab
    click_tab(page, "Attribute (Binomial)")
    
    # Fill inputs
    fill_number_input(page, "Confidence Level (%)", 95.0)
    fill_number_input(page, "Reliability (%)", 90.0)
    
    # Click calculate
    click_button(page, "Calculate Sample Size")
    
    # Verify results
    expect(page.locator("text=Sample Size")).to_be_visible()
    expect(page.locator("text=29")).to_be_visible()  # Expected n for c=0
```

## Data Models

### Configuration Model

```python
from pydantic import BaseModel, Field

class PlaywrightTestConfig(BaseModel):
    """Configuration for Playwright UI tests."""
    
    streamlit_port: int = Field(default=8501, description="Port for Streamlit app")
    streamlit_host: str = Field(default="localhost", description="Host for Streamlit app")
    browser_type: str = Field(default="chromium", description="Browser type (chromium/firefox/webkit)")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    timeout: int = Field(default=30000, description="Default timeout in milliseconds")
    screenshot_dir: str = Field(default="reports/screenshots", description="Directory for failure screenshots")
    
    @property
    def app_url(self) -> str:
        """Get full app URL."""
        return f"http://{self.streamlit_host}:{self.streamlit_port}"
```

### Test Result Model

```python
from typing import Optional
from pydantic import BaseModel

class UITestResult(BaseModel):
    """Result of a UI test execution."""
    
    test_name: str
    passed: bool
    duration_seconds: float
    screenshot_path: Optional[str] = None
    console_logs: list[str] = []
    error_message: Optional[str] = None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Subprocess Health Check

*For any* test session, when the Streamlit subprocess starts, the subprocess manager should not return until the health endpoint responds successfully.

**Validates: Requirements 1.2**

### Property 2: Resource Cleanup

*For any* test session, after all tests complete, the subprocess should be terminated and all browser resources should be released.

**Validates: Requirements 1.5, 8.5**

### Property 3: Tab Navigation

*For any* tab in the application (Attribute, Variables, Non-Normal, Reliability), clicking the tab element should make that tab active and display its content.

**Validates: Requirements 3.1, 4.1, 5.1, 6.1**

### Property 4: Numeric Input Interaction

*For any* numeric input field with a valid value, filling the field should update the field's value to match the input.

**Validates: Requirements 3.2, 3.3, 4.2, 4.3, 6.2, 6.3**

### Property 5: Calculate Button Triggers Computation

*For any* tab with a calculate button, clicking the button should trigger the calculation and cause results to appear in the page.

**Validates: Requirements 3.4, 4.4, 6.4**

### Property 6: Results Display After Calculation

*For any* valid calculation inputs, after clicking calculate, result elements should be visible in the rendered page.

**Validates: Requirements 3.5, 4.5, 4.6, 4.7, 4.8, 5.4, 5.6, 5.7, 6.5, 6.6**

### Property 7: Data Input Interaction

*For any* text input field accepting comma-separated data, entering valid data should populate the field correctly.

**Validates: Requirements 5.2**

### Property 8: Dropdown Selection

*For any* dropdown menu, selecting an option should update the selected value.

**Validates: Requirements 5.8**

### Property 9: Error Messages for Invalid Inputs

*For any* invalid input that violates validation rules, an error message should display in the page.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

### Property 10: Test Isolation

*For any* test, the test should receive a fresh browser page that is independent of previous tests.

**Validates: Requirements 8.1**

### Property 11: Screenshot Capture on Failure

*For any* test that fails, a screenshot should be saved to the screenshots directory.

**Validates: Requirements 8.2**

### Property 12: Console Log Capture on Failure

*For any* test that fails, browser console logs should be captured and available for debugging.

**Validates: Requirements 8.3**

### Property 13: URS Marker Presence

*For all* Playwright UI test functions, the function should be decorated with both `@pytest.mark.urs("REQ-25")` and `@pytest.mark.urs("URS-VAL-03")` markers.

**Validates: Requirements 10.1, 10.2, 10.4**

### Property 14: Configuration from Environment

*For any* configuration parameter (port, browser type, headless mode, timeout), the value should be readable from environment variables.

**Validates: Requirements 11.5**

## Error Handling

### Subprocess Errors

**Startup Timeout:**
- If Streamlit doesn't start within 30 seconds, raise `TimeoutError` with message indicating health check failed
- Include subprocess stdout/stderr in error message for debugging
- Ensure subprocess is terminated even if startup fails

**Port Already in Use:**
- If port 8501 is already occupied, raise `OSError` with clear message
- Suggest using different port via environment variable
- Attempt to find available port automatically (optional enhancement)

**Subprocess Crash:**
- If Streamlit crashes during tests, detect via process polling
- Fail remaining tests with clear error message
- Capture crash logs for debugging

### Browser Errors

**Browser Launch Failure:**
- If Playwright fails to launch browser, raise `PlaywrightError` with details
- Check if browser binaries are installed (`playwright install`)
- Provide clear installation instructions in error message

**Element Not Found:**
- If UI element is not found within timeout, raise `TimeoutError`
- Include element selector in error message
- Capture screenshot showing current page state
- Log page HTML for debugging

**Navigation Timeout:**
- If page navigation exceeds timeout, raise `TimeoutError`
- Check if Streamlit app is still running
- Capture network logs if available

### Test Errors

**Assertion Failures:**
- Use Playwright's `expect()` API for clear assertion messages
- Include actual vs expected values in failure messages
- Automatically capture screenshot on assertion failure

**Unexpected Exceptions:**
- Catch and wrap unexpected exceptions with context
- Include test name, current URL, and page state
- Ensure cleanup still occurs (use try/finally)

## Testing Strategy

### Dual Testing Approach

This feature uses both unit tests and end-to-end tests:

**Unit Tests:**
- Test configuration loading (PlaywrightTestConfig)
- Test helper functions in isolation (click_tab, fill_number_input, etc.)
- Test error handling logic
- Mock Playwright API for fast execution

**End-to-End Tests:**
- Test complete user workflows through real browser
- Verify actual UI interactions work correctly
- Test against running Streamlit application
- Validate visual elements and rendered content

### Property-Based Testing

Property tests will use Hypothesis to generate test data:

**Configuration Properties:**
- Generate random valid port numbers (1024-65535)
- Generate random timeout values (1000-60000ms)
- Verify configuration loads correctly for all valid inputs

**Input Validation Properties:**
- Generate random valid confidence/reliability values (0.1-99.9)
- Generate random valid sample sizes (2-10000)
- Verify all valid inputs are accepted by UI

**Marker Verification Properties:**
- Collect all test functions from Playwright test files
- Verify each has required URS markers
- Verify marker format matches existing tests

### Test Organization

**Test Files:**
```
tests/
├── test_ui_playwright_attribute.py      # Attribute tab E2E tests
├── test_ui_playwright_variables.py      # Variables tab E2E tests
├── test_ui_playwright_non_normal.py     # Non-Normal tab E2E tests
├── test_ui_playwright_reliability.py    # Reliability tab E2E tests
├── test_playwright_config.py            # Configuration unit tests
├── test_playwright_helpers.py           # Helper function unit tests
└── test_playwright_fixtures.py          # Fixture behavior tests
```

**Test Markers:**
- `@pytest.mark.playwright` - All Playwright tests
- `@pytest.mark.e2e` - End-to-end tests requiring browser
- `@pytest.mark.urs("REQ-25")` - URS traceability
- `@pytest.mark.urs("URS-VAL-03")` - URS traceability
- `@pytest.mark.slow` - Tests that take >5 seconds

**Running Tests:**
```bash
# Run only Playwright tests
uv run pytest -m playwright -q

# Run only E2E tests
uv run pytest -m e2e -q

# Run Playwright tests with visible browser (debugging)
PLAYWRIGHT_HEADLESS=false uv run pytest -m playwright -v

# Run specific tab tests
uv run pytest tests/test_ui_playwright_attribute.py -q

# Run all tests including Playwright
uv run pytest -q
```

### Test Configuration

**pytest.ini additions:**
```ini
[pytest]
markers =
    playwright: Playwright browser automation tests
    e2e: End-to-end tests requiring running application
    slow: Tests that take more than 5 seconds
```

**Environment Variables:**
```bash
# Playwright configuration
PLAYWRIGHT_HEADLESS=true          # Run in headless mode (default: true)
PLAYWRIGHT_BROWSER=chromium       # Browser type (default: chromium)
PLAYWRIGHT_TIMEOUT=30000          # Timeout in ms (default: 30000)
STREAMLIT_PORT=8501               # Streamlit app port (default: 8501)
STREAMLIT_HOST=localhost          # Streamlit app host (default: localhost)
```

### CI/CD Integration

**GitHub Actions Example:**
```yaml
- name: Install Playwright browsers
  run: uv run playwright install --with-deps chromium

- name: Run Playwright UI tests
  env:
    PLAYWRIGHT_HEADLESS: true
  run: uv run pytest -m playwright -q

- name: Upload screenshots on failure
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-screenshots
    path: reports/screenshots/
```

### Property Test Configuration

Each property test will run with minimum 100 iterations:

```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(port=st.integers(min_value=1024, max_value=65535))
@pytest.mark.property
def test_config_accepts_valid_ports(port: int):
    """Property: Configuration accepts all valid port numbers."""
    config = PlaywrightTestConfig(streamlit_port=port)
    assert config.streamlit_port == port
```

### Test Coverage Goals

- **Configuration module:** >95% coverage
- **Helper functions:** >90% coverage
- **Fixtures:** >85% coverage (some cleanup code hard to test)
- **E2E tests:** Focus on workflow coverage, not code coverage
- **Overall:** Maintain project's >85% coverage target

### Example Test Structure

**End-to-End Test Example:**
```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.e2e
def test_attribute_zero_failure_calculation(page: Page):
    """
    Test zero-failure calculation workflow in Attribute tab.
    
    Validates that entering C=95%, R=90% produces n=29 for c=0.
    """
    # Navigate to Attribute tab
    page.get_by_role("tab", name="Attribute (Binomial)").click()
    
    # Fill inputs
    page.get_by_label("Confidence Level (%)").fill("95")
    page.get_by_label("Reliability (%)").fill("90")
    
    # Click calculate
    page.get_by_role("button", name="Calculate Sample Size").click()
    
    # Verify results
    expect(page.get_by_text("Sample Size")).to_be_visible()
    expect(page.get_by_text("29")).to_be_visible()  # Expected n for c=0
```

**Property Test Example:**
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(
    confidence=st.floats(min_value=0.1, max_value=99.9),
    reliability=st.floats(min_value=0.1, max_value=99.9)
)
@pytest.mark.property
@pytest.mark.playwright
def test_valid_inputs_accepted(page: Page, confidence: float, reliability: float):
    """
    Property: All valid confidence and reliability values are accepted.
    
    Feature: playwright-ui-testing, Property 4: Numeric Input Interaction
    """
    page.get_by_role("tab", name="Attribute (Binomial)").click()
    
    # Fill inputs
    page.get_by_label("Confidence Level (%)").fill(str(confidence))
    page.get_by_label("Reliability (%)").fill(str(reliability))
    
    # Verify no error messages
    expect(page.get_by_text("error", re.IGNORECASE)).not_to_be_visible()
```

## Implementation Notes

### Playwright Installation

Playwright requires browser binaries to be installed:

```bash
# Install Playwright Python package
uv add --dev playwright pytest-playwright

# Install browser binaries
uv run playwright install chromium

# Install system dependencies (Linux)
uv run playwright install-deps
```

### Streamlit Widget Selectors

Streamlit generates dynamic IDs, so use stable selectors:

**Recommended Selectors:**
- `page.get_by_role("tab", name="Tab Name")` - For tabs
- `page.get_by_label("Label Text")` - For inputs with labels
- `page.get_by_role("button", name="Button Text")` - For buttons
- `page.get_by_text("Text Content")` - For text verification
- `page.locator("[data-testid='stNumberInput']")` - For Streamlit-specific elements

**Avoid:**
- CSS class selectors (Streamlit classes change between versions)
- XPath with absolute paths (brittle)
- Element IDs (Streamlit generates random IDs)

### Debugging Tips

**Run with visible browser:**
```bash
PLAYWRIGHT_HEADLESS=false uv run pytest -m playwright -v -s
```

**Slow down execution:**
```python
browser = playwright.chromium.launch(headless=False, slow_mo=1000)  # 1 second delay
```

**Interactive debugging:**
```python
page.pause()  # Opens Playwright Inspector
```

**Capture trace:**
```python
context.tracing.start(screenshots=True, snapshots=True)
# ... test code ...
context.tracing.stop(path="trace.zip")
# View with: playwright show-trace trace.zip
```

### Performance Considerations

**Optimize Test Speed:**
- Reuse browser instance across tests (session scope)
- Use headless mode (faster than visible)
- Run tests in parallel with pytest-xdist (future enhancement)
- Cache Streamlit app startup (session scope fixture)

**Expected Execution Times:**
- Streamlit startup: ~5-10 seconds
- Single E2E test: ~2-5 seconds
- Full Playwright suite: ~2-3 minutes
- All tests (including Playwright): ~5-7 minutes

### Maintenance Considerations

**When Streamlit UI Changes:**
- Update selectors in helper functions (centralized in conftest.py)
- Run tests to identify broken selectors
- Use Playwright Inspector to find new selectors

**When Adding New Tabs:**
- Create new test file: `test_ui_playwright_<tab_name>.py`
- Follow existing test patterns
- Add URS markers for traceability

**When Updating Playwright:**
- Run `uv run playwright install` to update browser binaries
- Check for breaking changes in Playwright API
- Update selectors if Playwright's locator API changes

## Dependencies

### New Dependencies

**Playwright:**
- Package: `playwright>=1.40.0`
- Purpose: Browser automation for E2E testing
- Justification: Industry-standard tool for browser automation, better than Selenium for modern web apps
- Maintenance: Actively maintained by Microsoft, frequent updates

**pytest-playwright:**
- Package: `pytest-playwright>=0.4.0`
- Purpose: Pytest plugin for Playwright integration
- Justification: Provides fixtures and configuration for Playwright in pytest
- Maintenance: Official Playwright plugin, well-maintained

### Dependency Justification

**Why Playwright over Selenium:**
- Better handling of modern web frameworks (React, Vue, Streamlit)
- Auto-waiting for elements (reduces flaky tests)
- Built-in screenshot and video recording
- Faster execution
- Better debugging tools (Playwright Inspector)
- Native async support

**Why pytest-playwright:**
- Seamless integration with existing pytest suite
- Provides browser and page fixtures
- Handles browser lifecycle automatically
- Supports parallel execution
- Compatible with pytest markers and configuration

### Installation

Add to `pyproject.toml`:
```toml
[dependency-groups]
dev = [
    # ... existing dependencies ...
    "playwright>=1.40.0",
    "pytest-playwright>=0.4.0",
]
```

Install:
```bash
uv sync
uv run playwright install chromium
```

## Security Considerations

**Subprocess Security:**
- Streamlit runs on localhost only (not exposed to network)
- Use random available port if default port conflicts
- Terminate subprocess even if tests fail (cleanup in finally block)

**Browser Security:**
- Run browser in isolated context (no shared cookies/storage)
- Clear browser data between test sessions
- Don't store sensitive data in test fixtures

**Screenshot Security:**
- Screenshots may contain sensitive test data
- Store in `reports/screenshots/` (gitignored)
- Clean up old screenshots periodically
- Don't commit screenshots to version control

**CI/CD Security:**
- Use headless mode in CI (no display server needed)
- Don't expose Streamlit port to external network
- Use ephemeral test environments
- Clean up resources after test runs
