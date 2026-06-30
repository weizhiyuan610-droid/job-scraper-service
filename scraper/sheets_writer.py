"""
Google Sheets writer using gspread
"""
import os
import tempfile
import json
import gspread
from typing import Dict, Optional
from oauth2client.service_account import ServiceAccountCredentials
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


def fix_pem_format(private_key: str) -> str:
    """
    Fix PEM private key format to ensure proper line wrapping

    PEM format requires:
    - Header: -----BEGIN PRIVATE KEY-----
    - Base64 content wrapped at 64 characters per line
    - Footer: -----END PRIVATE KEY-----

    Args:
        private_key: Private key string that may have incorrect formatting

    Returns:
        Properly formatted PEM key
    """
    if not private_key:
        return private_key

    normalized = private_key.strip()

    # Debug logging
    logger.info(f"[DEBUG] fix_pem_format input length: {len(normalized)}")
    logger.info(f"[DEBUG] fix_pem_format input (first 200 chars): {repr(normalized[:200])}")
    logger.info(f"[DEBUG] fix_pem_format input (last 200 chars): {repr(normalized[-200:])}")
    logger.info(f"[DEBUG] Has BEGIN header: {'-----BEGIN PRIVATE KEY-----' in normalized}")
    logger.info(f"[DEBUG] Has END header: {'-----END PRIVATE KEY-----' in normalized}")

    # Always re-wrap the key to ensure proper formatting
    # Extract the base64 content between headers, removing ALL whitespace
    if '-----BEGIN PRIVATE KEY-----' in normalized and '-----END PRIVATE KEY-----' in normalized:
        # Split and get content between headers
        parts = normalized.split('-----BEGIN PRIVATE KEY-----')
        if len(parts) > 1:
            remaining = parts[1]
            parts2 = remaining.split('-----END PRIVATE KEY-----')
            if len(parts2) > 1:
                base64_content = parts2[0].replace('\n', '').replace('\r', '').replace('\t', '').strip()

                logger.info(f"[DEBUG] Extracted base64 content length: {len(base64_content)}")

                # Re-wrap at exactly 64 characters per line
                wrapped_lines = []
                for i in range(0, len(base64_content), 64):
                    wrapped_lines.append(base64_content[i:i+64])

                wrapped_content = '\n'.join(wrapped_lines)
                result = f"-----BEGIN PRIVATE KEY-----\n{wrapped_content}\n-----END PRIVATE KEY-----\n"
                logger.info(f"[DEBUG] Re-wrapped PEM key, total length: {len(result)}")
                logger.info(f"[DEBUG] First 200 chars of result: {repr(result[:200])}")
                return result

    elif '-----BEGIN RSA PRIVATE KEY-----' in normalized:
        parts = normalized.split('-----BEGIN RSA PRIVATE KEY-----')
        if len(parts) > 1:
            remaining = parts[1]
            parts2 = remaining.split('-----END RSA PRIVATE KEY-----')
            if len(parts2) > 1:
                base64_content = parts2[0].replace('\n', '').replace('\r', '').replace('\t', '').strip()

                wrapped_lines = []
                for i in range(0, len(base64_content), 64):
                    wrapped_lines.append(base64_content[i:i+64])

                wrapped_content = '\n'.join(wrapped_lines)
                result = f"-----BEGIN RSA PRIVATE KEY-----\n{wrapped_content}\n-----END RSA PRIVATE KEY-----"
                logger.info(f"[DEBUG] Re-wrapped RSA PEM key, total length: {len(result)}")
                return result

    # If we can't parse it, return as-is
    logger.warning("[DEBUG] Could not fix PEM format, returning original")
    return private_key


class SheetsWriter:
    """Write job data to Google Sheets"""

    def __init__(self, credentials_path: str = None, credentials_json: dict = None):
        """
        Initialize Sheets writer

        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account credentials as dict (for Railway env var)
        """
        self.client = None
        self.sheet = None
        self.worksheet = None

        if credentials_json:
            # Use credentials from environment variable (Railway)
            # Use the newer gspread API that uses google-auth instead of oauth2client
            logger.info(f"[DEBUG] SheetsWriter received credentials_json type: {type(credentials_json)}")

            # Handle escaped JSON in environment variables
            if isinstance(credentials_json, str):
                logger.info("[DEBUG] credentials_json is a string, parsing...")
                try:
                    credentials_dict = json.loads(credentials_json)
                    logger.info("[DEBUG] Parsed credentials_json string directly")
                except json.JSONDecodeError:
                    # If it fails, try to fix common escaping issues
                    cleaned = credentials_json.strip()
                    cleaned = re.sub(r'\"', '"', cleaned)

                    # Replace actual newlines with \n in JSON strings
                    cleaned = cleaned.replace('\n', '\\n')
                    cleaned = cleaned.replace('\r', '\\r')
                    cleaned = cleaned.replace('\t', '\\t')

                    try:
                        credentials_dict = json.loads(cleaned)
                        # Restore actual newlines in private_key
                        if 'private_key' in credentials_dict:
                            credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\n', '\n')
                            credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\r', '\r')
                            credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\t', '\t')
                    except:
                        credentials_dict = eval(cleaned)
            else:
                logger.info("[DEBUG] credentials_json is already a dict")
                credentials_dict = credentials_json

            # CRITICAL: Ensure private_key has actual newlines, not literal \n
            if 'private_key' in credentials_dict and isinstance(credentials_dict['private_key'], str):
                if '\\n' in credentials_dict['private_key']:
                    logger.info("[DEBUG] Found literal \\n in private_key, converting to actual newlines")
                    credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\n', '\n')
                    credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\r', '\r')
                    credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\t', '\t')

            # Fix PEM format - ensure proper 64-character line wrapping
            if 'private_key' in credentials_dict and credentials_dict['private_key']:
                logger.info("[DEBUG] Fixing PEM key format")
                credentials_dict['private_key'] = fix_pem_format(credentials_dict['private_key'])

            # Use temporary file approach to avoid pyasn1 string parsing issues
            # This is more reliable than passing dict directly
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            logger.info("[DEBUG] Using temporary file approach for credentials")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(credentials_dict, f)
                temp_path = f.name
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(temp_path, scope)
                self.client = gspread.authorize(credentials)
                logger.info("[DEBUG] Credentials created successfully using temp file")
            finally:
                try:
                    os.unlink(temp_path)
                except:
                    pass

        elif credentials_path and os.path.exists(credentials_path):
            # Use credentials file (local development)
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            logger.info(f"[DEBUG] Using credentials file: {credentials_path}")
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            self.client = gspread.authorize(credentials)
            logger.info("[DEBUG] Credentials created from file")
        else:
            raise ValueError("Either credentials_path or credentials_json must be provided")

        logger.info("Google Sheets client initialized")

    def open_spreadsheet(self, sheet_id: str, sheet_name: str = "职位数据"):
        """
        Open Google spreadsheet by ID

        Args:
            sheet_id: Spreadsheet ID from URL
            sheet_name: Name of the worksheet tab
        """
        try:
            self.sheet = self.client.open_by_key(sheet_id)
            self.worksheet = self.sheet.worksheet(sheet_name)
            logger.info(f"Opened spreadsheet: {sheet_id}, worksheet: {sheet_name}")
        except gspread.SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {sheet_id}")
            raise
        except gspread.WorksheetNotFound:
            logger.error(f"Worksheet not found: {sheet_name}")
            # Create worksheet if it doesn't exist
            self.sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
            self.worksheet = self.sheet.worksheet(sheet_name)
            logger.info(f"Created new worksheet: {sheet_name}")

    def get_next_row_number(self) -> int:
        """
        Get the next available row number

        Returns:
            Row number (1-indexed)
        """
        if not self.worksheet:
            raise ValueError("Worksheet not opened. Call open_spreadsheet first.")

        # Get all records to find the first truly empty row
        try:
            # Get all data as records
            records = self.worksheet.get_all_records()
            # Find first row index that's completely empty or doesn't exist
            # Add 2 because: 1 for header row, 1 for 0-index to 1-index conversion
            return len(records) + 2
        except Exception as e:
            # Fallback: check column values
            logger.warning(f"Error using get_all_records, using fallback: {e}")
            # Get all rows and find first empty one
            all_rows = self.worksheet.get_all_values()
            # Find first row with no data in any column
            for idx, row in enumerate(all_rows, start=1):
                if not any(cell.strip() for cell in row):
                    return idx
            # If all rows have data, append to end
            return len(all_rows) + 1

    def write_job(self, job_data: Dict) -> Dict:
        """
        Write a single job to Google Sheets

        Args:
            job_data: Dictionary containing job fields

        Returns:
            Dictionary with success status and row number
        """
        try:
            if not self.worksheet:
                raise ValueError("Worksheet not opened. Call open_spreadsheet first.")

            # Get next row number
            row_number = self.get_next_row_number()

            # Generate ID
            job_data['id'] = row_number

            # Add timestamp if opened is empty
            if not job_data.get('opened') or job_data['opened'] == '':
                job_data['opened'] = datetime.now().strftime('%Y-%m-%d')

            # Convert job data to row format with pre-computed scores
            from models.job_schema import JobData
            from scraper.job_scorer import enhance_job_with_scores

            # Ensure company_info is a dict, not a string
            if 'company_info' in job_data and isinstance(job_data['company_info'], str):
                try:
                    job_data['company_info'] = json.loads(job_data['company_info'])
                    logger.info(f"Parsed company_info from JSON string")
                except json.JSONDecodeError:
                    logger.warning(f"company_info is invalid JSON string, using default")
                    job_data['company_info'] = {}

            # Enhance job data with pre-computed scores
            job_with_scores = enhance_job_with_scores(job_data)
            job = JobData(**job_with_scores)
            row_data = job.to_google_sheets_row()

            # Write to sheet using update to specify exact range (B-AR columns)
            # row_data[0] is empty for column A, row_data[1:] is columns B-AR (43 columns)
            # Range format: "B6:AR6" for row 6
            cell_range = f"B{row_number}:AR{row_number}"

            # row_data has 44 elements (index 0-43), index 0 is empty for column A
            # We need columns B-AR which are indices 1-43 (43 columns total)
            row_to_write = row_data[1:44]  # Skip column A, take columns B-AR (43 columns)
            # Pad with empty strings if needed
            while len(row_to_write) < 43:
                row_to_write.append('')

            self.worksheet.update(cell_range, [row_to_write], value_input_option='USER_ENTERED')

            logger.info(f"Successfully wrote job to row {row_number}: {job.title}")

            return {
                "success": True,
                "row_number": row_number,
                "job_id": row_number
            }

        except Exception as e:
            logger.error(f"Error writing to Google Sheets: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def check_duplicate(self, company: str, title: str) -> Optional[int]:
        """
        Check if a job already exists in the sheet

        Args:
            company: Company name
            title: Job title

        Returns:
            Row number if duplicate found, None otherwise
        """
        try:
            if not self.worksheet:
                return None

            # Get all records
            records = self.worksheet.get_all_records()

            for idx, record in enumerate(records, start=2):  # Start from row 2 (row 1 is header)
                if (record.get('company', '').lower() == company.lower() and
                    record.get('title', '').lower() == title.lower()):
                    return idx

            return None

        except Exception as e:
            logger.error(f"Error checking duplicates: {str(e)}")
            return None

    def get_job_count(self) -> int:
        """
        Get total number of jobs in the sheet

        Returns:
            Number of job rows (excluding header)
        """
        if not self.worksheet:
            return 0

        return len(self.worksheet.col_values(1)) - 1  # Subtract header row


def write_to_sheets_sync(sheet_id: str, sheet_name: str, job_data: Dict, credentials: dict) -> Dict:
    """
    Synchronous wrapper for write_job

    Args:
        sheet_id: Google Sheets ID
        sheet_name: Worksheet name
        job_data: Job data dictionary
        credentials: Service account credentials dict

    Returns:
        Result dictionary
    """
    writer = SheetsWriter(credentials_json=credentials)
    writer.open_spreadsheet(sheet_id, sheet_name)
    return writer.write_job(job_data)
