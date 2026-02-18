"""Tests for Streamlit subprocess manager fixture.

This module tests the streamlit_app fixture that manages the Streamlit
application lifecycle during testing.

Since pytest fixtures cannot be called directly, these tests focus on
integration testing with the actual fixture to verify the subprocess
management behavior.

Requirements:
    - 1.1: Start Streamlit_App in subprocess when test suite begins
    - 1.2: Wait until application is ready to accept connections
    - 1.3: Terminate subprocess when test suite completes
    - 1.4: Raise timeout error if app doesn't start within 30 seconds
"""

import time

import pytest
import requests


@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.slow
@pytest.mark.integration
class TestSubprocessManagerIntegration:
    """Integration tests for subprocess manager with real subprocess.
    
    These tests use the actual streamlit_app fixture to verify real behavior.
    They are marked as slow since they start the actual Streamlit app.
    """

    def test_subprocess_starts_successfully(self, streamlit_app):
        """Test that Streamlit subprocess starts successfully.
        
        Validates: Requirement 1.1 - Start Streamlit_App in subprocess
        """
        # Verify we got a valid URL
        assert streamlit_app.startswith("http://")
        assert "localhost" in streamlit_app or "127.0.0.1" in streamlit_app
        assert ":8501" in streamlit_app  # Default port
        
        # Verify app is actually running by checking health endpoint
        health_url = f"{streamlit_app}/_stcore/health"
        response = requests.get(health_url, timeout=5)
        assert response.status_code == 200

    def test_health_check_waits_for_app_readiness(self, streamlit_app):
        """Test that health check endpoint responds correctly.
        
        Validates: Requirement 1.2 - Application is ready to accept connections
        """
        health_url = f"{streamlit_app}/_stcore/health"
        
        # Make multiple requests to verify stability
        for _ in range(3):
            response = requests.get(health_url, timeout=5)
            assert response.status_code == 200
            time.sleep(0.1)
        
        # Verify we can access the main page
        response = requests.get(streamlit_app, timeout=5)
        assert response.status_code == 200
        assert len(response.content) > 0

    def test_subprocess_serves_application(self, streamlit_app):
        """Test that subprocess serves the Streamlit application correctly.
        
        Validates: Requirement 1.1, 1.2 - App is running and accessible
        """
        # Access main page
        response = requests.get(streamlit_app, timeout=5)
        assert response.status_code == 200
        
        # Verify it's actually Streamlit content
        content = response.text.lower()
        assert "streamlit" in content or "sample size" in content

    def test_multiple_requests_to_running_app(self, streamlit_app):
        """Test that multiple requests can be made to the running app.
        
        Validates: Requirement 1.2 - Application accepts connections
        """
        # Make multiple requests to verify app stability
        for i in range(5):
            response = requests.get(streamlit_app, timeout=5)
            assert response.status_code == 200
            time.sleep(0.1)


@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
class TestSubprocessManagerConfiguration:
    """Tests for subprocess manager configuration."""

    def test_config_provides_correct_url(self, playwright_config):
        """Test that configuration provides correct app URL.
        
        Validates: Requirement 1.1 - Correct URL construction
        """
        assert playwright_config.app_url.startswith("http://")
        assert "localhost" in playwright_config.app_url
        assert str(playwright_config.streamlit_port) in playwright_config.app_url

    def test_config_default_port(self, playwright_config):
        """Test that configuration uses default port 8501.
        
        Validates: Requirement 1.1 - Default port configuration
        """
        assert playwright_config.streamlit_port == 8501

    def test_config_health_check_url(self, playwright_config):
        """Test that health check URL is correctly constructed.
        
        Validates: Requirement 1.2 - Health check URL format
        """
        health_url = f"{playwright_config.app_url}/_stcore/health"
        assert health_url.startswith("http://")
        assert "/_stcore/health" in health_url


@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
class TestSubprocessManagerDocumentation:
    """Tests to verify subprocess manager behavior is documented."""

    def test_fixture_has_docstring(self):
        """Test that streamlit_app fixture has proper documentation.
        
        Validates: Code quality - proper documentation
        """
        from tests.conftest import streamlit_app
        
        assert streamlit_app.__doc__ is not None
        assert len(streamlit_app.__doc__) > 0
        
        # Verify key concepts are documented
        doc = streamlit_app.__doc__.lower()
        assert "subprocess" in doc
        assert "health" in doc or "ready" in doc
        assert "terminate" in doc or "cleanup" in doc

    def test_fixture_scope_is_session(self):
        """Test that streamlit_app fixture uses session scope.
        
        Validates: Requirement 1.1, 1.3 - Start once per session, cleanup after
        """
        import inspect
        from tests.conftest import streamlit_app
        
        # Get the fixture definition
        # In pytest, we can check the fixture's scope through its metadata
        if hasattr(streamlit_app, "_pytestfixturefunction"):
            fixture_info = streamlit_app._pytestfixturefunction
            assert fixture_info.scope == "session"
        else:
            # Alternative: check the source code for @pytest.fixture(scope="session")
            source = inspect.getsource(streamlit_app)
            assert 'scope="session"' in source or "scope='session'" in source


# Property-Based Tests

from hypothesis import given, settings
import hypothesis.strategies as st


@settings(max_examples=100)
@given(
    health_check_attempts=st.integers(min_value=1, max_value=10)
)
@pytest.mark.property
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.slow
def test_property_subprocess_health_check(
    streamlit_app: str,
    health_check_attempts: int
) -> None:
    """Property: Subprocess manager ensures health endpoint responds before returning.

    **Property 1: Subprocess Health Check**
    **Validates: Requirements 1.2**

    This property test verifies that when the streamlit_app fixture returns,
    the Streamlit application is fully ready to accept connections. It tests
    this by making multiple health check requests to ensure the app is stable
    and consistently responsive.

    The property being tested is:
    For any test session, when the Streamlit subprocess starts, the subprocess
    manager should not return until the health endpoint responds successfully.

    Args:
        streamlit_app: URL of running Streamlit app (fixture ensures it's ready)
        health_check_attempts: Number of health check requests to make (1-10)
    """
    health_url = f"{streamlit_app}/_stcore/health"

    # Property: All health check requests should succeed
    # This verifies the fixture didn't return prematurely
    for attempt in range(health_check_attempts):
        response = requests.get(health_url, timeout=5)

        # Assert health endpoint is accessible and returns 200
        assert response.status_code == 200, (
            f"Health check attempt {attempt + 1}/{health_check_attempts} failed. "
            f"Expected status 200, got {response.status_code}. "
            f"This indicates the subprocess manager returned before the app was ready."
        )

        # Small delay between requests to test stability
        if attempt < health_check_attempts - 1:
            time.sleep(0.1)

    # Property: Main page should also be accessible
    # This verifies the app is not just responding to health checks but is fully functional
    response = requests.get(streamlit_app, timeout=5)
    assert response.status_code == 200, (
        f"Main page not accessible. Expected status 200, got {response.status_code}. "
        f"This indicates the app is responding to health checks but not serving content."
    )

    # Property: Response should contain actual content
    assert len(response.content) > 0, (
        "Main page returned empty content. "
        "This indicates the app is not fully initialized."
    )



# Property-Based Tests

from hypothesis import given, settings
import hypothesis.strategies as st


@settings(max_examples=100)
@given(
    health_check_attempts=st.integers(min_value=1, max_value=10)
)
@pytest.mark.property
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.slow
def test_property_subprocess_health_check(
    streamlit_app: str,
    health_check_attempts: int
) -> None:
    """Property: Subprocess manager ensures health endpoint responds before returning.
    
    **Property 1: Subprocess Health Check**
    **Validates: Requirements 1.2**
    
    This property test verifies that when the streamlit_app fixture returns,
    the Streamlit application is fully ready to accept connections. It tests
    this by making multiple health check requests to ensure the app is stable
    and consistently responsive.
    
    The property being tested is:
    For any test session, when the Streamlit subprocess starts, the subprocess
    manager should not return until the health endpoint responds successfully.
    
    Args:
        streamlit_app: URL of running Streamlit app (fixture ensures it's ready)
        health_check_attempts: Number of health check requests to make (1-10)
    """
    health_url = f"{streamlit_app}/_stcore/health"
    
    # Property: All health check requests should succeed
    # This verifies the fixture didn't return prematurely
    for attempt in range(health_check_attempts):
        response = requests.get(health_url, timeout=5)
        
        # Assert health endpoint is accessible and returns 200
        assert response.status_code == 200, (
            f"Health check attempt {attempt + 1}/{health_check_attempts} failed. "
            f"Expected status 200, got {response.status_code}. "
            f"This indicates the subprocess manager returned before the app was ready."
        )
        
        # Small delay between requests to test stability
        if attempt < health_check_attempts - 1:
            time.sleep(0.1)
    
    # Property: Main page should also be accessible
    # This verifies the app is not just responding to health checks but is fully functional
    response = requests.get(streamlit_app, timeout=5)
    assert response.status_code == 200, (
        f"Main page not accessible. Expected status 200, got {response.status_code}. "
        f"This indicates the app is responding to health checks but not serving content."
    )
    
    # Property: Response should contain actual content
    assert len(response.content) > 0, (
        "Main page returned empty content. "
        "This indicates the app is not fully initialized."
    )
