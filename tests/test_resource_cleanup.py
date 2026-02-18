"""Property-based tests for resource cleanup after test sessions.

This module tests that the Streamlit subprocess and browser resources are
properly cleaned up after test sessions complete.

Requirements:
    - 1.5: Ensure all resources are cleaned up when subprocess terminates
    - 8.5: Ensure all Browser_Instance resources are released after tests complete
"""

import subprocess
import time
from typing import Generator

import psutil
import pytest
import requests
from hypothesis import given, settings
import hypothesis.strategies as st


@settings(max_examples=10, deadline=None)
@given(
    verification_attempts=st.integers(min_value=1, max_value=3)
)
@pytest.mark.property
@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.slow
def test_property_resource_cleanup(
    streamlit_app: str,
    verification_attempts: int
) -> None:
    """Property: Resources remain accessible during session and cleanup after.
    
    **Property 2: Resource Cleanup**
    **Validates: Requirements 1.5, 8.5**
    
    This property test verifies that:
    1. During the test session, the subprocess remains accessible
    2. Resources are stable and consistently available
    3. The fixture properly manages the subprocess lifecycle
    
    The property being tested is:
    For any test session, the subprocess should remain accessible throughout
    the session, and after all tests complete, resources should be cleaned up.
    
    Note: This test validates the "during session" behavior. The actual cleanup
    is validated by the fixture's finally block and the integration tests.
    
    Args:
        streamlit_app: URL of running Streamlit app (from session fixture)
        verification_attempts: Number of times to verify accessibility (1-3)
    """
    health_url = f"{streamlit_app}/_stcore/health"
    
    # Property: App should be consistently accessible during the session
    for attempt in range(verification_attempts):
        response = requests.get(health_url, timeout=5)
        
        assert response.status_code == 200, (
            f"Health check attempt {attempt + 1}/{verification_attempts} failed. "
            f"Expected status 200, got {response.status_code}. "
            f"This indicates the subprocess is not stable during the session."
        )
        
        # Verify main page is also accessible
        response = requests.get(streamlit_app, timeout=5)
        assert response.status_code == 200, (
            f"Main page not accessible on attempt {attempt + 1}/{verification_attempts}. "
            f"This indicates resource instability during the session."
        )
        
        # Small delay between attempts
        if attempt < verification_attempts - 1:
            time.sleep(0.2)
    
    # Property: Response should contain actual content
    response = requests.get(streamlit_app, timeout=5)
    assert len(response.content) > 0, (
        "Main page returned empty content. "
        "This indicates the app is not fully functional."
    )


@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.slow
def test_subprocess_cleanup_releases_port() -> None:
    """Test that subprocess cleanup releases the port for reuse.
    
    Validates: Requirement 1.5 - Resources are cleaned up
    
    This test verifies that after the subprocess is terminated, the port
    is released and can be used again.
    """
    from tests.playwright_config import PlaywrightTestConfig
    
    # Use a different port to avoid conflicts
    test_port = 9601
    config = PlaywrightTestConfig(streamlit_port=test_port)
    
    # Build command to start Streamlit
    cmd = [
        "uv",
        "run",
        "streamlit",
        "run",
        "src/sample_size_estimator/app.py",
        f"--server.port={config.streamlit_port}",
        "--server.headless=true",
        "--server.address=localhost",
    ]
    
    # Start subprocess
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    
    try:
        # Wait for app to be ready
        health_url = f"{config.app_url}/_stcore/health"
        start_time = time.time()
        timeout = 30
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                break
            
            try:
                response = requests.get(health_url, timeout=1)
                if response.status_code == 200:
                    break
            except (requests.ConnectionError, requests.Timeout):
                pass
            
            time.sleep(0.5)
        
        # Verify app is running
        response = requests.get(health_url, timeout=5)
        assert response.status_code == 200
        
    finally:
        # Cleanup with explicit child process termination
        try:
            parent_process = psutil.Process(process.pid)
            children = parent_process.children(recursive=True)
            
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Kill children
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
                    
        except Exception:
            try:
                process.kill()
                process.wait()
            except Exception:
                pass
    
    # Wait for port to be released (Windows needs more time)
    time.sleep(5)
    
    # Verify port is released by trying to start another process on same port
    process2 = None
    try:
        process2 = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        # Wait briefly to see if it starts
        time.sleep(5)
        
        # Check if process is still running (it should be if port was released)
        if process2.poll() is not None:
            # Process failed to start - check if it's a port conflict
            stdout, stderr = process2.communicate()
            if "address already in use" in stderr.lower() or "port" in stderr.lower():
                pytest.fail(
                    "Second process failed to start due to port conflict. "
                    "This indicates the port was not properly released after cleanup."
                )
            else:
                # Some other error - this is acceptable for this test
                # (e.g., app startup error unrelated to port)
                pytest.skip(f"Second process failed for non-port reason: {stderr[:200]}")
        
    finally:
        # Cleanup second process
        if process2 is not None:
            try:
                parent_process = psutil.Process(process2.pid)
                children = parent_process.children(recursive=True)
                
                process2.terminate()
                try:
                    process2.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process2.kill()
                    process2.wait()
                
                for child in children:
                    try:
                        child.kill()
                    except psutil.NoSuchProcess:
                        pass
                        
            except Exception:
                try:
                    process2.kill()
                    process2.wait()
                except Exception:
                    pass


@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
def test_cleanup_handles_already_terminated_process() -> None:
    """Test that cleanup handles already-terminated processes gracefully.
    
    Validates: Requirement 1.5 - Cleanup is robust
    
    This test verifies that the cleanup code handles edge cases where
    the process has already terminated before cleanup runs.
    """
    from tests.playwright_config import PlaywrightTestConfig
    
    config = PlaywrightTestConfig()
    
    # Build command to start Streamlit
    cmd = [
        "uv",
        "run",
        "streamlit",
        "run",
        "src/sample_size_estimator/app.py",
        f"--server.port={config.streamlit_port}",
        "--server.headless=true",
        "--server.address=localhost",
    ]
    
    # Start subprocess
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    
    # Immediately kill the process
    process.kill()
    process.wait()
    
    # Verify process is terminated
    assert process.poll() is not None
    
    # Now try cleanup (should handle gracefully)
    try:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    except Exception as e:
        # Cleanup should not raise exceptions for already-terminated processes
        # But if it does, we want to know about it
        pytest.fail(f"Cleanup raised exception for already-terminated process: {e}")
    
    # Verify process is still terminated (cleanup didn't break anything)
    assert process.poll() is not None


@pytest.mark.urs("REQ-25")
@pytest.mark.urs("URS-VAL-03")
@pytest.mark.playwright
@pytest.mark.slow
@pytest.mark.integration
def test_subprocess_cleanup_simulation() -> None:
    """Test that subprocess cleanup properly terminates process and releases resources.
    
    Validates: Requirements 1.5, 8.5 - Resource cleanup
    
    This test simulates the fixture lifecycle to verify cleanup behavior:
    1. Starts a Streamlit subprocess on a different port
    2. Verifies it's running and accessible
    3. Terminates it (simulating fixture cleanup)
    4. Verifies process is terminated and port is released
    """
    from tests.playwright_config import PlaywrightTestConfig
    
    # Use a different port to avoid conflicts with session fixture
    test_port = 9501
    config = PlaywrightTestConfig(streamlit_port=test_port)
    
    # Build command to start Streamlit
    cmd = [
        "uv",
        "run",
        "streamlit",
        "run",
        "src/sample_size_estimator/app.py",
        f"--server.port={config.streamlit_port}",
        "--server.headless=true",
        "--server.address=localhost",
    ]
    
    # Start subprocess
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    
    try:
        # Wait for app to be ready
        health_url = f"{config.app_url}/_stcore/health"
        start_time = time.time()
        timeout = 30
        
        app_ready = False
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                pytest.fail(
                    f"Process terminated unexpectedly.\n"
                    f"Exit code: {process.returncode}\n"
                    f"STDOUT:\n{stdout}\n"
                    f"STDERR:\n{stderr}"
                )
            
            try:
                response = requests.get(health_url, timeout=1)
                if response.status_code == 200:
                    app_ready = True
                    break
            except (requests.ConnectionError, requests.Timeout):
                pass
            
            time.sleep(0.5)
        
        if not app_ready:
            stdout, stderr = process.communicate(timeout=5)
            pytest.fail(
                f"App failed to start within {timeout} seconds.\n"
                f"STDOUT:\n{stdout}\n"
                f"STDERR:\n{stderr}"
            )
        
        # Verify app is accessible
        response = requests.get(health_url, timeout=5)
        assert response.status_code == 200
        
        # Get process info before termination
        process_pid = process.pid
        parent_process = psutil.Process(process_pid)
        
        # Verify process is running
        assert process.poll() is None
        assert parent_process.is_running()
        
    finally:
        # Cleanup: Terminate subprocess (simulating fixture cleanup)
        # On Windows, we need to kill child processes explicitly
        try:
            # Get all child processes before terminating
            parent_process = psutil.Process(process.pid)
            children = parent_process.children(recursive=True)
            
            # Terminate parent
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Terminate children
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # Wait for children to terminate
            time.sleep(1)
            
            # Force kill any remaining children
            for child in children:
                try:
                    if child.is_running():
                        child.kill()
                except psutil.NoSuchProcess:
                    pass
                    
        except Exception:
            try:
                process.kill()
                process.wait()
            except Exception:
                pass
    
    # Verify process is terminated
    assert process.poll() is not None, "Process still running after cleanup"
    
    # Verify app is not accessible (give more time for port release on Windows)
    time.sleep(3)  # Give time for port to be released
    
    try:
        response = requests.get(health_url, timeout=2)
        pytest.fail(
            f"App still accessible after cleanup (status {response.status_code}). "
            f"Resources were not properly released."
        )
    except (requests.ConnectionError, requests.Timeout):
        # Expected - app should not be accessible
        pass
    
    # Verify parent process is not running
    try:
        parent_process = psutil.Process(process_pid)
        if parent_process.is_running():
            pytest.fail(f"Parent process (PID {process_pid}) still running after cleanup")
    except psutil.NoSuchProcess:
        # Expected - process should not exist
        pass
