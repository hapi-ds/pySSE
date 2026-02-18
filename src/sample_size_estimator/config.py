"""Configuration management using Pydantic Settings.

This module provides centralized configuration for the Sample Size Estimator
application, loading settings from environment variables with sensible defaults.
"""


from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Environment variable names should be uppercase (e.g., APP_TITLE, LOG_LEVEL).
    """

    # Application settings
    app_title: str = "Sample Size Estimator"
    app_version: str = "0.1.0"

    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_format: str = "json"

    # Validation settings
    validated_hash: str | None = None
    calculations_file: str = "src/sample_size_estimator/calculations/__init__.py"

    # Report settings
    report_output_dir: str = "reports"
    report_author: str = "Sample Size Estimator System"

    # Statistical defaults
    default_confidence: float = 95.0
    default_reliability: float = 90.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Singleton instance
_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    """Get application settings singleton.

    Returns:
        AppSettings: The application settings instance.

    Note:
        Settings are loaded once and cached for the lifetime of the application.
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings
