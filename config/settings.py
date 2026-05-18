"""
Application settings and configuration
"""
import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional
import json

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    gemini_api_key: str = ""

    # Google Sheets Configuration
    google_sheet_id: str = ""
    google_sheet_name: str = "职位数据"
    google_credentials_json: Optional[str] = None  # JSON string for Railway

    # Scraper Configuration
    headless_browser: bool = True
    page_timeout: int = 30000
    delay_between_requests: int = 2

    # AI Configuration
    ai_model: str = "gemini-3.1-flash-lite-preview"
    ai_temperature: float = 0.1
    ai_simple_mode: bool = True  # Use simplified prompt for faster processing

    # Application Configuration
    app_name: str = "Event Horizon Lab - Job Scraper"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Railway Configuration
    port: int = int(os.getenv("PORT", 5000))
    is_railway: bool = "RAILWAY_ENVIRONMENT" in os.getenv("RAILWAY_ENVIRONMENT", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()


def get_google_credentials() -> dict:
    """
    Get Google credentials as dict

    Returns:
        Credentials dictionary or None
    """
    if not settings.google_credentials_json:
        logger.warning("GOOGLE_CREDENTIALS_JSON environment variable is not set")
        return None

    credentials_str = settings.google_credentials_json

    # DEBUG: Show first 300 chars of raw environment variable
    logger.info(f"[DEBUG] Raw credentials_str (first 300 chars): {repr(credentials_str[:300])}")

    # Try parsing as-is first
    try:
        creds = json.loads(credentials_str)
        logger.info("[DEBUG] Successfully parsed credentials directly (no fixes needed)")
        if 'private_key' in creds:
            logger.info(f"[DEBUG] private_key after direct parse (first 200 chars): {repr(creds['private_key'][:200])}")
        return creds
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse credentials JSON directly: {e}")

        # Try fixing common escaping issues
        import re
        cleaned = credentials_str.strip()

        # Fix 1: Remove extra escaping: {\"key\": \"value\"} → {"key": "value"}
        cleaned = re.sub(r'\\"', '"', cleaned)

        # Fix 2: Replace actual newlines with \n in JSON strings
        # This handles the case where private_key contains real newlines instead of \n
        logger.info(f"[DEBUG] Before newline replacement, cleaned (first 300 chars): {repr(cleaned[:300])}")
        cleaned = cleaned.replace('\n', '\\n')
        cleaned = cleaned.replace('\r', '\\r')
        cleaned = cleaned.replace('\t', '\\t')
        logger.info(f"[DEBUG] After newline replacement, cleaned (first 300 chars): {repr(cleaned[:300])}")

        try:
            creds = json.loads(cleaned)
            logger.info("[DEBUG] Successfully parsed credentials after fixing escape characters and newlines")

            # IMPORTANT: Restore actual newlines in private_key
            # After JSON parsing, \n in private_key is a literal backslash-n,
            # but it should be actual newlines for the key file
            if 'private_key' in creds:
                logger.info(f"[DEBUG] private_key before restore (first 200 chars): {repr(creds['private_key'][:200])}")
                creds['private_key'] = creds['private_key'].replace('\\n', '\n')
                creds['private_key'] = creds['private_key'].replace('\\r', '\r')
                creds['private_key'] = creds['private_key'].replace('\\t', '\t')
                logger.info("[DEBUG] Restored actual newlines in private_key")
                logger.info(f"[DEBUG] private_key after restore (first 200 chars): {repr(creds['private_key'][:200])}")

            return creds
        except json.JSONDecodeError as e2:
            logger.error(f"Failed to parse credentials JSON after cleaning: {e2}")
            logger.error(f"Credentials string (first 200 chars): {credentials_str[:200]}")
            return None


def validate_settings() -> list[str]:
    """
    Validate required settings

    Returns:
        List of missing required settings
    """
    missing = []

    if not settings.gemini_api_key:
        missing.append("GEMINI_API_KEY")

    if not settings.google_sheet_id:
        missing.append("GOOGLE_SHEET_ID")

    return missing
