"""Unit tests for Playwright configuration model.

Tests the PlaywrightTestConfig Pydantic model including default values,
validation, property methods, and environment variable overrides.

**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**
"""

import os
import pytest
from pydantic import ValidationError

from tests.playwright_config import PlaywrightTestConfig


def test_default_values() -> None:
    """Test that default configuration values are set correctly."""
    config = PlaywrightTestConfig()
    
    assert config.streamlit_port == 8501
    assert config.streamlit_host == "localhost"
    assert config.browser_type == "chromium"
    assert config.headless is True
    assert config.timeout == 30000
    assert config.screenshot_dir == "reports/screenshots"


def test_app_url_property() -> None:
    """Test that app_url property constructs correct URL."""
    config = PlaywrightTestConfig()
    assert config.app_url == "http://localhost:8501"
    
    config = PlaywrightTestConfig(streamlit_host="127.0.0.1", streamlit_port=8502)
    assert config.app_url == "http://127.0.0.1:8502"


def test_custom_values() -> None:
    """Test that custom configuration values are accepted."""
    config = PlaywrightTestConfig(
        streamlit_port=9000,
        streamlit_host="0.0.0.0",
        browser_type="firefox",
        headless=False,
        timeout=60000,
        screenshot_dir="custom/screenshots"
    )
    
    assert config.streamlit_port == 9000
    assert config.streamlit_host == "0.0.0.0"
    assert config.browser_type == "firefox"
    assert config.headless is False
    assert config.timeout == 60000
    assert config.screenshot_dir == "custom/screenshots"


def test_port_validation_minimum() -> None:
    """Test that port below 1024 raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        PlaywrightTestConfig(streamlit_port=1023)
    
    assert "Port must be between 1024 and 65535" in str(exc_info.value)


def test_port_validation_maximum() -> None:
    """Test that port above 65535 raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        PlaywrightTestConfig(streamlit_port=65536)
    
    assert "Port must be between 1024 and 65535" in str(exc_info.value)


def test_port_validation_valid_range() -> None:
    """Test that ports in valid range are accepted."""
    # Test minimum valid port
    config = PlaywrightTestConfig(streamlit_port=1024)
    assert config.streamlit_port == 1024
    
    # Test maximum valid port
    config = PlaywrightTestConfig(streamlit_port=65535)
    assert config.streamlit_port == 65535
    
    # Test common port
    config = PlaywrightTestConfig(streamlit_port=8080)
    assert config.streamlit_port == 8080



def test_environment_variable_override_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that PLAYWRIGHT_STREAMLIT_PORT environment variable overrides default."""
    monkeypatch.setenv("PLAYWRIGHT_STREAMLIT_PORT", "9000")
    config = PlaywrightTestConfig()
    assert config.streamlit_port == 9000


def test_environment_variable_override_host(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that PLAYWRIGHT_STREAMLIT_HOST environment variable overrides default."""
    monkeypatch.setenv("PLAYWRIGHT_STREAMLIT_HOST", "0.0.0.0")
    config = PlaywrightTestConfig()
    assert config.streamlit_host == "0.0.0.0"


def test_environment_variable_override_browser_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that PLAYWRIGHT_BROWSER_TYPE environment variable overrides default."""
    monkeypatch.setenv("PLAYWRIGHT_BROWSER_TYPE", "firefox")
    config = PlaywrightTestConfig()
    assert config.browser_type == "firefox"


def test_environment_variable_override_headless(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that PLAYWRIGHT_HEADLESS environment variable overrides default."""
    monkeypatch.setenv("PLAYWRIGHT_HEADLESS", "false")
    config = PlaywrightTestConfig()
    assert config.headless is False
    
    monkeypatch.setenv("PLAYWRIGHT_HEADLESS", "true")
    config = PlaywrightTestConfig()
    assert config.headless is True


def test_environment_variable_override_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that PLAYWRIGHT_TIMEOUT environment variable overrides default."""
    monkeypatch.setenv("PLAYWRIGHT_TIMEOUT", "60000")
    config = PlaywrightTestConfig()
    assert config.timeout == 60000


def test_environment_variable_override_screenshot_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that PLAYWRIGHT_SCREENSHOT_DIR environment variable overrides default."""
    monkeypatch.setenv("PLAYWRIGHT_SCREENSHOT_DIR", "custom/screenshots")
    config = PlaywrightTestConfig()
    assert config.screenshot_dir == "custom/screenshots"


def test_environment_variable_override_multiple(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that multiple environment variables can be overridden simultaneously."""
    monkeypatch.setenv("PLAYWRIGHT_STREAMLIT_PORT", "8080")
    monkeypatch.setenv("PLAYWRIGHT_BROWSER_TYPE", "webkit")
    monkeypatch.setenv("PLAYWRIGHT_HEADLESS", "false")
    
    config = PlaywrightTestConfig()
    assert config.streamlit_port == 8080
    assert config.browser_type == "webkit"
    assert config.headless is False


def test_environment_variable_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables are case-insensitive."""
    monkeypatch.setenv("playwright_streamlit_port", "7000")
    config = PlaywrightTestConfig()
    assert config.streamlit_port == 7000


def test_environment_variable_port_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that port validation applies to environment variable values."""
    monkeypatch.setenv("PLAYWRIGHT_STREAMLIT_PORT", "100")
    
    with pytest.raises(ValidationError) as exc_info:
        PlaywrightTestConfig()
    
    assert "Port must be between 1024 and 65535" in str(exc_info.value)


def test_app_url_with_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that app_url property works correctly with environment overrides."""
    monkeypatch.setenv("PLAYWRIGHT_STREAMLIT_HOST", "192.168.1.100")
    monkeypatch.setenv("PLAYWRIGHT_STREAMLIT_PORT", "3000")
    
    config = PlaywrightTestConfig()
    assert config.app_url == "http://192.168.1.100:3000"


# Property-Based Tests

from hypothesis import given, settings
import hypothesis.strategies as st


@settings(max_examples=100)
@given(
    port=st.integers(min_value=1024, max_value=65535),
    host=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and x.isprintable()),
    browser=st.sampled_from(["chromium", "firefox", "webkit"]),
    headless=st.booleans(),
    timeout=st.integers(min_value=1000, max_value=120000),
    screenshot_dir=st.text(min_size=1, max_size=100).filter(
        lambda x: x.strip() and x.isprintable() and "/" not in x[:1] and "\x00" not in x
    )
)
@pytest.mark.property
def test_property_configuration_from_environment(
    port: int,
    host: str,
    browser: str,
    headless: bool,
    timeout: int,
    screenshot_dir: str
) -> None:
    """Property: Configuration accepts all valid environment variable combinations.
    
    **Property 14: Configuration from Environment**
    **Validates: Requirements 11.5**
    
    This property test verifies that the PlaywrightTestConfig model correctly
    loads configuration from environment variables across a wide range of valid
    input combinations. It ensures that:
    - All valid port numbers (1024-65535) are accepted
    - Any non-empty host string is accepted
    - All supported browser types are accepted
    - Boolean headless values are correctly parsed
    - Timeout values in reasonable range are accepted
    - Screenshot directory paths are accepted
    """
    # Save original environment variables
    original_env = {}
    env_vars = [
        "PLAYWRIGHT_STREAMLIT_PORT",
        "PLAYWRIGHT_STREAMLIT_HOST",
        "PLAYWRIGHT_BROWSER_TYPE",
        "PLAYWRIGHT_HEADLESS",
        "PLAYWRIGHT_TIMEOUT",
        "PLAYWRIGHT_SCREENSHOT_DIR"
    ]
    
    for var in env_vars:
        original_env[var] = os.environ.get(var)
    
    try:
        # Set environment variables
        os.environ["PLAYWRIGHT_STREAMLIT_PORT"] = str(port)
        os.environ["PLAYWRIGHT_STREAMLIT_HOST"] = host
        os.environ["PLAYWRIGHT_BROWSER_TYPE"] = browser
        os.environ["PLAYWRIGHT_HEADLESS"] = str(headless).lower()
        os.environ["PLAYWRIGHT_TIMEOUT"] = str(timeout)
        os.environ["PLAYWRIGHT_SCREENSHOT_DIR"] = screenshot_dir
        
        # Create configuration from environment
        config = PlaywrightTestConfig()
        
        # Verify all values loaded correctly from environment
        assert config.streamlit_port == port, f"Port mismatch: expected {port}, got {config.streamlit_port}"
        assert config.streamlit_host == host, f"Host mismatch: expected {host}, got {config.streamlit_host}"
        assert config.browser_type == browser, f"Browser mismatch: expected {browser}, got {config.browser_type}"
        assert config.headless == headless, f"Headless mismatch: expected {headless}, got {config.headless}"
        assert config.timeout == timeout, f"Timeout mismatch: expected {timeout}, got {config.timeout}"
        assert config.screenshot_dir == screenshot_dir, f"Screenshot dir mismatch: expected {screenshot_dir}, got {config.screenshot_dir}"
        
        # Verify app_url property works correctly with environment values
        expected_url = f"http://{host}:{port}"
        assert config.app_url == expected_url, f"URL mismatch: expected {expected_url}, got {config.app_url}"
    
    finally:
        # Restore original environment variables
        for var in env_vars:
            if original_env[var] is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = original_env[var]
