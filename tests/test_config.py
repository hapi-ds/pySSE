"""Tests for configuration management."""

import pytest
from sample_size_estimator.config import AppSettings, get_settings


def test_app_settings_defaults():
    """Test that AppSettings has correct default values."""
    settings = AppSettings()
    
    assert settings.app_title == "Sample Size Estimator"
    assert settings.app_version == "0.1.0"
    assert settings.log_level == "INFO"
    assert settings.log_file == "logs/app.log"
    assert settings.log_format == "json"
    # validated_hash can be None or empty string depending on .env file
    assert settings.validated_hash in (None, "")
    assert settings.calculations_file == "src/sample_size_estimator/calculations/__init__.py"
    assert settings.report_output_dir == "reports"
    assert settings.report_author == "Sample Size Estimator System"
    assert settings.default_confidence == 95.0
    assert settings.default_reliability == 90.0


def test_get_settings_singleton():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


def test_app_settings_custom_values(monkeypatch):
    """Test that AppSettings can be customized via environment variables."""
    monkeypatch.setenv("APP_TITLE", "Custom Title")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DEFAULT_CONFIDENCE", "99.0")
    
    settings = AppSettings()
    
    assert settings.app_title == "Custom Title"
    assert settings.log_level == "DEBUG"
    assert settings.default_confidence == 99.0
