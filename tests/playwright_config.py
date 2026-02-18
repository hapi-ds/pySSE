"""Configuration model for Playwright UI tests.

This module provides the PlaywrightTestConfig Pydantic model for managing
test configuration including Streamlit app settings, browser configuration,
and test execution parameters.
"""

import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PlaywrightTestConfig(BaseSettings):
    """Configuration for Playwright UI tests.
    
    This model manages all configuration parameters for Playwright-based
    end-to-end UI testing, including Streamlit application settings,
    browser configuration, and test execution parameters.
    
    Attributes:
        streamlit_port: Port number for Streamlit application (1024-65535)
        streamlit_host: Host address for Streamlit application
        browser_type: Browser to use (chromium/firefox/webkit)
        headless: Whether to run browser in headless mode
        timeout: Default timeout for element interactions in milliseconds
        screenshot_dir: Directory path for failure screenshots
    """
    
    streamlit_port: int = Field(
        default=8501,
        description="Port for Streamlit app"
    )
    streamlit_host: str = Field(
        default="localhost",
        description="Host for Streamlit app"
    )
    browser_type: str = Field(
        default="chromium",
        description="Browser type (chromium/firefox/webkit)"
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    timeout: int = Field(
        default=30000,
        description="Default timeout in milliseconds"
    )
    screenshot_dir: str = Field(
        default="reports/screenshots",
        description="Directory for failure screenshots"
    )
    
    @property
    def app_url(self) -> str:
        """Get full app URL.
        
        Returns:
            str: Complete URL for accessing the Streamlit application
        """
        return f"http://{self.streamlit_host}:{self.streamlit_port}"
    
    @field_validator("streamlit_port")
    @classmethod
    def validate_port_range(cls, v: int) -> int:
        """Validate port is in valid range (1024-65535).
        
        Args:
            v: Port number to validate
            
        Returns:
            int: Validated port number
            
        Raises:
            ValueError: If port is outside valid range
        """
        if not 1024 <= v <= 65535:
            raise ValueError(
                f"Port must be between 1024 and 65535, got {v}"
            )
        return v
    
    model_config = SettingsConfigDict(
        env_prefix="PLAYWRIGHT_",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env file
        env_file=os.path.join(os.getcwd(), ".env"),  # Load from current working directory .env file
        env_file_encoding="utf-8"
    )
