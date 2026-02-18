# UI Tests for Sample Size Estimator

## Overview

This directory contains automated UI tests for the Sample Size Estimator application, fulfilling **Requirement 25: Performance Qualification UI Testing**.

## Test Approaches

### Playwright Browser Automation (Recommended)

The primary UI testing approach uses **Playwright** for true end-to-end browser automation. These tests start the Streamlit application in a subprocess and interact with it through a real browser.

**Playwright Test Files:**
- `test_ui_playwright_attribute.py` - Attribute (Binomial) tab E2E tests
- `test_ui_playwright_variables.py` - Variables (Normal) tab E2E tests
- `test_ui_playwright_non_normal.py` - Non-Normal Distribution tab E2E tests
- `test_ui_playwright_reliability.py` - Reliability tab E2E tests
- `test_playwright_urs_markers.py` - Property tests for URS traceability

### Streamlit AppTest (Deprecated/Alternative)

The following test files use the Streamlit AppTest framework but are currently non-functional due to import/scope limitations:
- `test_ui_attribute_tab.py` - AppTest approach (deprecated)
- `test_ui_variables_tab.py` - AppTest approach (deprecated)
- `test_ui_non_normal_tab.py` - AppTest approach (deprecated)
- `test_ui_reliability_tab.py` - AppTest approach (deprecated)

**Note:** These files are retained for reference but the Playwright approach is recommended for all UI testing.

## Installation

### Prerequisites

1. Install Python dependencies:
   ```bash
   uv sync
   ```

2. Install Playwright browser binaries:
   ```bash
   uv run playwright install chromium
   ```

3. On Linux, install system dependencies:
   ```bash
   uv run playwright install-deps
   ```

## Running Playwright Tests

### Environment Configuration

**IMPORTANT:** Playwright environment variables should be set as environment variables when running tests, NOT in the `.env` file. Adding them to `.env` will cause conflicts with the main application settings.

### Basic Test Execution

Run all Playwright tests in headless mode (recommended for CI/CD):
```bash
uv run pytest -m playwright -q
```

Run with visible browser for debugging:
```bash
# Windows PowerShell
$env:PLAYWRIGHT_HEADLESS="false"; uv run pytest -m playwright -v

# Windows CMD
set PLAYWRIGHT_HEADLESS=false && uv run pytest -m playwright -v

# Linux/Mac
PLAYWRIGHT_HEADLESS=false uv run pytest -m playwright -v
```

Run specific test file:
```bash
uv run pytest tests/test_ui_playwright_attribute.py -q
```

Run specific test:
```bash
uv run pytest tests/test_ui_playwright_attribute.py::test_attribute_tab_renders -v
```

### Available Environment Variables

Configure Playwright tests using these environment variables:

- `PLAYWRIGHT_HEADLESS`: Run browser in headless mode (default: `true`)
  - Set to `false` to see the browser window during tests
- `PLAYWRIGHT_STREAMLIT_PORT`: Port for Streamlit during tests (default: `8501`)
- `PLAYWRIGHT_STREAMLIT_HOST`: Host address (default: `localhost`)
- `PLAYWRIGHT_BROWSER_TYPE`: Browser to use (default: `chromium`)
  - Options: `chromium`, `firefox`, `webkit`
- `PLAYWRIGHT_TIMEOUT`: Timeout in milliseconds (default: `30000`)
- `PLAYWRIGHT_SCREENSHOT_DIR`: Directory for failure screenshots (default: `reports/screenshots`)

### Test Markers

Filter tests using pytest markers:

```bash
# Run only E2E tests
uv run pytest -m e2e -q

# Run only property-based tests
uv run pytest -m property -q

# Run tests for specific URS requirement
uv run pytest -m "urs('REQ-25')" -q
```

### Debugging Failed Tests

When tests fail, Playwright automatically captures:
1. **Screenshots**: Saved to `reports/screenshots/`
2. **Console logs**: Printed in test output

To debug interactively:
1. Run with visible browser: `$env:PLAYWRIGHT_HEADLESS="false"`
2. Add `page.pause()` in test code to open Playwright Inspector
3. Check screenshots in `reports/screenshots/` directory

### Common Issues and Solutions

**Issue: Tests timeout waiting for UI elements**
- Solution: Run with `PLAYWRIGHT_HEADLESS=false` to see what's happening
- Check if another Streamlit instance is running on port 8501
- Increase timeout: `$env:PLAYWRIGHT_TIMEOUT="60000"`

**Issue: ImportError when starting Streamlit**
- Solution: Reinstall package in editable mode: `uv pip install -e .`
- Ensure you're in the project root directory

**Issue: Port already in use**
- Solution: Kill existing Streamlit process or use different port
- Windows: `taskkill /F /PID <pid>`
- Linux/Mac: `kill <pid>`

**Issue: Browser not found**
- Solution: Install browser binaries: `uv run playwright install chromium`


### Basic Usage

Run all Playwright tests:
```bash
uv run pytest -m playwright -q
```

Run specific test file:
```bash
uv run pytest tests/test_ui_playwright_attribute.py -q
```

Run specific test:
```bash
uv run pytest tests/test_ui_playwright_attribute.py::test_attribute_zero_failure_calculation -v
```

### Filtering Tests

Run only E2E tests:
```bash
uv run pytest -m e2e -q
```

Run only property tests:
```bash
uv run pytest -m property -q
```

Run tests for specific URS requirement:
```bash
uv run pytest -m "urs" -q
```

### Debugging

Run with visible browser (not headless):
```bash
PLAYWRIGHT_HEADLESS=false uv run pytest -m playwright -v -s
```

On Windows PowerShell:
```powershell
$env:PLAYWRIGHT_HEADLESS="false"; uv run pytest -m playwright -v -s
```

Run with Playwright Inspector (interactive debugging):
```bash
PWDEBUG=1 uv run pytest tests/test_ui_playwright_attribute.py::test_attribute_tab_renders
```

### Configuration

Playwright tests can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PLAYWRIGHT_HEADLESS` | `true` | Run browser in headless mode |
| `PLAYWRIGHT_BROWSER` | `chromium` | Browser type (chromium/firefox/webkit) |
| `PLAYWRIGHT_TIMEOUT` | `30000` | Timeout in milliseconds |
| `STREAMLIT_PORT` | `8501` | Port for Streamlit application |
| `STREAMLIT_HOST` | `localhost` | Host for Streamlit application |

Example:
```bash
PLAYWRIGHT_HEADLESS=false PLAYWRIGHT_TIMEOUT=60000 uv run pytest -m playwright -v
```

## Test Architecture

### Fixtures (conftest.py)

**Session-scoped fixtures:**
- `streamlit_app` - Starts Streamlit in subprocess, yields URL, terminates after session
- `browser` - Launches Playwright browser, closes after session

**Function-scoped fixtures:**
- `page` - Creates fresh browser page for each test, captures screenshots on failure

### Helper Functions

Reusable UI interaction helpers in `conftest.py`:
- `click_tab(page, tab_name)` - Click a Streamlit tab
- `fill_number_input(page, label, value)` - Fill numeric input field
- `click_button(page, button_text)` - Click button by text
- `get_text_content(page, selector)` - Get element text
- `wait_for_element(page, selector, timeout)` - Wait for element visibility

### Test Types

**End-to-End Tests (`@pytest.mark.e2e`):**
- Test complete user workflows through browser
- Verify calculations display correctly
- Test error handling and validation
- Validate UI interactions

**Property Tests (`@pytest.mark.property`):**
- Verify universal properties hold across inputs
- Test tab navigation consistency
- Validate input field behavior
- Ensure URS marker presence

## Troubleshooting

### Browser Not Found

If you see "Executable doesn't exist" errors:
```bash
uv run playwright install chromium
```

### Port Already in Use

If port 8501 is occupied:
```bash
STREAMLIT_PORT=8502 uv run pytest -m playwright -q
```

### Tests Timeout

Increase timeout for slow systems:
```bash
PLAYWRIGHT_TIMEOUT=60000 uv run pytest -m playwright -q
```

### Screenshot Artifacts

Failed test screenshots are saved to:
```
reports/screenshots/test_name.png
```

Review these to debug test failures.

### Streamlit App Won't Start

Check if the app runs manually:
```bash
uv run streamlit run src/sample_size_estimator/app.py
```

If it works manually but not in tests, check subprocess logs in test output.

## Known Issues

### Streamlit AppTest Limitations

1. **Import Scope**: `AppTest.from_function()` creates an isolated execution context where imported functions are not available
2. **Module Structure**: The app uses relative imports which don't work well with AppTest's isolated execution model

These issues led to the adoption of Playwright for UI testing.

## Compliance with REQ-25

**Requirement 25** states:
> THE System SHALL include automated UI tests using Streamlit AppTest or similar framework

**Status**: ✅ FULL COMPLIANCE
- Automated UI tests implemented using Playwright browser automation
- Tests cover all tabs and user workflows
- Tests are properly marked with URS traceability (`@pytest.mark.urs("REQ-25")`, `@pytest.mark.urs("URS-VAL-03")`)
- Tests run automatically in CI/CD pipelines
- Property tests verify correctness properties across all test functions

## Test Coverage

Each tab has comprehensive test coverage:
- ✅ Tab rendering and navigation
- ✅ Valid input workflows with calculations
- ✅ Invalid input error handling
- ✅ Edge cases and boundary conditions
- ✅ Results display verification
- ✅ Property-based testing for universal behaviors

## CI/CD Integration

Playwright tests run in CI/CD pipelines with:
- Headless browser mode (no display server required)
- Automatic screenshot capture on failure
- Test result reporting compatible with CI systems
- Parallel execution support (future enhancement)

Example GitHub Actions workflow:
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

## Future Improvements

1. ~~Add browser-based integration tests~~ ✅ Completed with Playwright
2. Add visual regression testing
3. Add performance testing for large datasets
4. Implement parallel test execution with pytest-xdist
5. Add cross-browser testing (Firefox, WebKit)

## References

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- Requirement 25: Performance Qualification UI Testing
- URS-VAL-03: UI Validation Requirements
- Design Document: `.kiro/specs/playwright-ui-testing/design.md`
