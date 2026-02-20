"""Preservation property tests for validated-hash-default-fix.

This test file contains property-based tests to verify that the bugfix
does NOT break existing behavior in production contexts, other tests,
and the singleton pattern.

These tests should PASS on UNFIXED code (capturing baseline behavior)
and continue to PASS after the fix is applied (confirming no regressions).

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**
"""

import pytest
from hypothesis import given, strategies as st
from sample_size_estimator.config import AppSettings, get_settings


def test_preservation_production_env_loading():
    """Preservation: Production AppSettings() continues to load from .env.
    
    This test verifies that AppSettings() without _env_file=None parameter
    continues to load configuration from the .env file in production contexts.
    
    **EXPECTED ON UNFIXED CODE**: PASSES (baseline behavior)
    **EXPECTED AFTER FIX**: PASSES (behavior preserved)
    
    **Validates: Requirement 3.1**
    """
    # Production instantiation - should load from .env
    settings = AppSettings()
    
    # Verify that validated_hash is loaded from .env file
    expected_hash = "a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e"
    assert settings.validated_hash == expected_hash, (
        f"Preservation violation: Production AppSettings() should load "
        f"validated_hash from .env file ({expected_hash!r}), "
        f"but got {settings.validated_hash!r}"
    )
    
    # Verify other settings are also loaded correctly
    assert settings.app_title == "Sample Size Estimator"
    assert settings.log_level == "INFO"


def test_preservation_singleton_pattern():
    """Preservation: get_settings() singleton continues to work correctly.
    
    This test verifies that the get_settings() singleton function continues
    to return the same instance with values loaded from environment variables
    and .env file.
    
    **EXPECTED ON UNFIXED CODE**: PASSES (baseline behavior)
    **EXPECTED AFTER FIX**: PASSES (behavior preserved)
    
    **Validates: Requirement 3.2**
    """
    # Get singleton instance
    settings1 = get_settings()
    settings2 = get_settings()
    
    # Verify singleton pattern works
    assert settings1 is settings2, (
        "Preservation violation: get_settings() should return the same instance"
    )
    
    # Verify settings are loaded from .env
    expected_hash = "a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e"
    assert settings1.validated_hash == expected_hash, (
        f"Preservation violation: Singleton should load validated_hash from .env, "
        f"but got {settings1.validated_hash!r}"
    )


def test_preservation_custom_values_with_monkeypatch(monkeypatch):
    """Preservation: test_app_settings_custom_values continues to work.
    
    This test verifies that tests using monkeypatch.setenv() to override
    settings continue to work correctly after the fix.
    
    **EXPECTED ON UNFIXED CODE**: PASSES (baseline behavior)
    **EXPECTED AFTER FIX**: PASSES (behavior preserved)
    
    **Validates: Requirement 3.3**
    """
    # Set custom environment variables
    monkeypatch.setenv("APP_TITLE", "Custom Title")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DEFAULT_CONFIDENCE", "99.0")
    
    # Create new settings instance
    settings = AppSettings()
    
    # Verify custom values are loaded
    assert settings.app_title == "Custom Title", (
        "Preservation violation: monkeypatch.setenv should override app_title"
    )
    assert settings.log_level == "DEBUG", (
        "Preservation violation: monkeypatch.setenv should override log_level"
    )
    assert settings.default_confidence == 99.0, (
        "Preservation violation: monkeypatch.setenv should override default_confidence"
    )


@given(
    app_title=st.text(
        min_size=1, 
        max_size=50,
        alphabet=st.characters(blacklist_characters='\x00\n\r')
    ),
    log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]),
    confidence=st.floats(min_value=0.01, max_value=99.99)
)
def test_preservation_property_env_override(app_title, log_level, confidence):
    """Property 2: Preservation - Environment Loading in Production.
    
    For any context that is NOT the test_app_settings_defaults test
    (production code, other tests, singleton pattern), AppSettings SHALL
    continue to load configuration from the .env file exactly as before,
    preserving all existing environment-based configuration behavior.
    
    This property-based test generates random environment configurations
    and verifies that AppSettings() loads them correctly.
    
    **EXPECTED ON UNFIXED CODE**: PASSES (baseline behavior)
    **EXPECTED AFTER FIX**: PASSES (behavior preserved)
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    """
    import os
    
    # Set random environment variables using os.environ
    old_values = {}
    try:
        # Save old values
        for key in ["APP_TITLE", "LOG_LEVEL", "DEFAULT_CONFIDENCE"]:
            old_values[key] = os.environ.get(key)
        
        # Set new values
        os.environ["APP_TITLE"] = app_title
        os.environ["LOG_LEVEL"] = log_level
        os.environ["DEFAULT_CONFIDENCE"] = str(confidence)
        
        # Create settings instance
        settings = AppSettings()
        
        # Property: Environment variables should be loaded correctly
        assert settings.app_title == app_title, (
            f"Property violation: AppSettings() should load app_title={app_title!r} "
            f"from environment, but got {settings.app_title!r}"
        )
        assert settings.log_level == log_level, (
            f"Property violation: AppSettings() should load log_level={log_level!r} "
            f"from environment, but got {settings.log_level!r}"
        )
        assert settings.default_confidence == confidence, (
            f"Property violation: AppSettings() should load default_confidence={confidence} "
            f"from environment, but got {settings.default_confidence}"
        )
    finally:
        # Restore old values
        for key, value in old_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_preservation_other_tests_unaffected():
    """Preservation: Other tests that rely on environment configuration work.
    
    This test verifies that other tests in the test suite that rely on
    environment configuration continue to function correctly after the fix.
    
    **EXPECTED ON UNFIXED CODE**: PASSES (baseline behavior)
    **EXPECTED AFTER FIX**: PASSES (behavior preserved)
    
    **Validates: Requirement 3.4**
    """
    # Simulate other tests that expect .env to be loaded
    settings = AppSettings()
    
    # Verify that .env values are available
    assert settings.validated_hash is not None, (
        "Preservation violation: Other tests expect validated_hash to be loaded from .env"
    )
    assert settings.calculations_file == "src/sample_size_estimator/calculations/__init__.py"
    assert settings.report_output_dir == "reports"


@given(st.just("production_context"))
def test_preservation_property_production_loading(context):
    """Property: Production contexts continue to load from .env file.
    
    For all production contexts (not test_app_settings_defaults),
    AppSettings() should continue to load from .env file.
    
    **EXPECTED ON UNFIXED CODE**: PASSES (baseline behavior)
    **EXPECTED AFTER FIX**: PASSES (behavior preserved)
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    """
    # Production context - should load from .env
    settings = AppSettings()
    
    # Property: validated_hash should be loaded from .env in production
    expected_hash = "a4826d4db0e60972182dada4617a3c12cbff54167676b7a1a5d7e55c43482e1e"
    assert settings.validated_hash == expected_hash, (
        f"Property violation: In {context}, AppSettings() should load "
        f"validated_hash from .env ({expected_hash!r}), "
        f"but got {settings.validated_hash!r}"
    )
