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
    claude_api_key: str = ""
    gemini_api_key: str = ""  # Fallback for Gemini

    # Google Sheets Configuration
    google_sheet_id: str = ""
    google_sheet_name: str = "职位数据"
    google_credentials_json: Optional[str] = None  # JSON string for Railway

    # Multi-User Sheets Configuration
    # User A's sheet
    user_a_sheet_id: str = ""
    user_a_sheet_name: str = "职位数据-小A"
    # User B's sheet
    user_b_sheet_id: str = ""
    user_b_sheet_name: str = "职位数据-小B"
    # User C's sheet
    user_c_sheet_id: str = ""
    user_c_sheet_name: str = "职位数据-小C"
    # User D's sheet (backup)
    user_d_sheet_id: str = ""
    user_d_sheet_name: str = "职位数据-备用"

    # Scraper Configuration
    headless_browser: bool = True
    page_timeout: int = 30000
    delay_between_requests: int = 2

    # AI Configuration
    ai_model: str = "gemini-2.5-flash"
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

    @property
    def user_sheets(self) -> dict:
        """Get user sheet configurations as a dictionary"""
        return {
            'a': {
                'id': self.user_a_sheet_id or self.google_sheet_id,
                'name': self.user_a_sheet_name,
                'display_name': '小A'
            },
            'b': {
                'id': self.user_b_sheet_id or self.google_sheet_id,
                'name': self.user_b_sheet_name,
                'display_name': '小B'
            },
            'c': {
                'id': self.user_c_sheet_id or self.google_sheet_id,
                'name': self.user_c_sheet_name,
                'display_name': '小C'
            },
            'd': {
                'id': self.user_d_sheet_id or self.google_sheet_id,
                'name': self.user_d_sheet_name,
                'display_name': '备用'
            }
        }


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
    logger.info(f"[DEBUG] Raw credentials_str length: {len(credentials_str)}")
    logger.info(f"[DEBUG] Raw credentials_str (first 300 chars): {repr(credentials_str[:300])}")
    logger.info(f"[DEBUG] Raw credentials_str (last 200 chars): {repr(credentials_str[-200:])}")

    # Try parsing as-is first
    try:
        creds = json.loads(credentials_str)
        logger.info("[DEBUG] Successfully parsed credentials directly (no fixes needed)")
        if 'private_key' in creds:
            logger.info(f"[DEBUG] private_key after direct parse (first 200 chars): {repr(creds['private_key'][:200])}")
            # Fix literal backslash-n to actual newlines
            while '\\n' in creds['private_key']:
                creds['private_key'] = creds['private_key'].replace('\\n', '\n')
            while '\\r' in creds['private_key']:
                creds['private_key'] = creds['private_key'].replace('\\r', '\r')
            while '\\t' in creds['private_key']:
                creds['private_key'] = creds['private_key'].replace('\\t', '\t')
            logger.info(f"[DEBUG] private_key after newline fix (first 200 chars): {repr(creds['private_key'][:200])}")
            logger.info(f"[DEBUG] private_key after newline fix (last 200 chars): {repr(creds['private_key'][-200:])}")
            logger.info(f"[DEBUG] private_key ends with END: {creds['private_key'].endswith('-----END PRIVATE KEY-----')}")
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
            # After JSON parsing, \\n in private_key is a literal backslash-n,
            # but it should be actual newlines for the key file
            if 'private_key' in creds:
                logger.info(f"[DEBUG] private_key before restore (first 200 chars): {repr(creds['private_key'][:200])}")
                # Use a loop to handle double-escaped newlines
                while '\\n' in creds['private_key']:
                    creds['private_key'] = creds['private_key'].replace('\\n', '\n')
                while '\\r' in creds['private_key']:
                    creds['private_key'] = creds['private_key'].replace('\\r', '\r')
                while '\\t' in creds['private_key']:
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

    # Check for at least one AI API key
    if not settings.claude_api_key and not settings.gemini_api_key:
        missing.append("CLAUDE_API_KEY or GEMINI_API_KEY")

    if not settings.google_sheet_id:
        missing.append("GOOGLE_SHEET_ID")

    return missing
