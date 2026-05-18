"""
Google Sheets writer using gspread
"""
import os
import gspread
from typing import Dict, Optional
from oauth2client.service_account import ServiceAccountCredentials
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            import json
            from tempfile import NamedTemporaryFile

            logger.info(f"[DEBUG] SheetsWriter received credentials_json type: {type(credentials_json)}")

            # Handle escaped JSON in environment variables
            if isinstance(credentials_json, str):
                logger.info("[DEBUG] credentials_json is a string, parsing...")
                try:
                    # Try parsing as-is first
                    credentials_dict = json.loads(credentials_json)
                    logger.info("[DEBUG] Parsed credentials_json string directly")
                except json.JSONDecodeError:
                    # If it fails, try to fix common escaping issues
                    # Railway may escape quotes: {\"key\": \"value\"}
                    import re
                    cleaned = credentials_json.strip()

                    # Remove extra escaping
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
                        # Last resort: evaluate literal (safe for credentials only)
                        credentials_dict = eval(cleaned)
            else:
                logger.info("[DEBUG] credentials_json is already a dict")
                credentials_dict = credentials_json

            # DEBUG: Show private_key before any processing
            if 'private_key' in credentials_dict:
                literal_newline = '\\n'
                actual_newline = chr(10)
                logger.info(f"[DEBUG] SheetsWriter private_key BEFORE final check (first 200 chars): {repr(credentials_dict['private_key'][:200])}")
                logger.info(f"[DEBUG] private_key contains literal backslash-n? {literal_newline in credentials_dict['private_key']}")
                logger.info(f"[DEBUG] private_key contains actual newline? {actual_newline in credentials_dict['private_key']}")

            # CRITICAL: Ensure private_key has actual newlines, not literal \n
            # This handles both dict input and parsed JSON
            if 'private_key' in credentials_dict and isinstance(credentials_dict['private_key'], str):
                if '\\n' in credentials_dict['private_key']:
                    logger.info("[DEBUG] Found literal \\n in private_key, converting to actual newlines")
                    credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\n', '\n')
                    credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\r', '\r')
                    credentials_dict['private_key'] = credentials_dict['private_key'].replace('\\t', '\t')
                    logger.info(f"[DEBUG] After conversion, private_key (first 200 chars): {repr(credentials_dict['private_key'][:200])}")

            # DEBUG: Show private_key after all processing
            if 'private_key' in credentials_dict:
                actual_newline = chr(10)
                logger.info(f"[DEBUG] SheetsWriter private_key AFTER all processing (first 200 chars): {repr(credentials_dict['private_key'][:200])}")
                logger.info(f"[DEBUG] private_key contains actual newline NOW? {actual_newline in credentials_dict['private_key']}")

            # Create temp file for credentials
            with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(credentials_dict, f)
                temp_path = f.name

            # CRITICAL FIX: json.dump() escapes actual newlines to \n strings
            # We need to read the file back and fix the private_key field
            logger.info(f"[DEBUG] Temp file created at: {temp_path}")

            # Read the JSON file and parse it
            with open(temp_path, 'r') as f:
                file_content = f.read()

            # Parse the JSON to get a dict
            try:
                import json
                credentials_dict_from_file = json.loads(file_content)

                # Fix private_key if it has literal \n instead of actual newlines
                if 'private_key' in credentials_dict_from_file:
                    if '\\n' in credentials_dict_from_file['private_key']:
                        logger.info("[DEBUG] Found literal \\n in private_key from file, fixing...")
                        credentials_dict_from_file['private_key'] = credentials_dict_from_file['private_key'].replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')

                # Write the fixed JSON back to file
                with open(temp_path, 'w') as f:
                    json.dump(credentials_dict_from_file, f, ensure_ascii=False)

                logger.info("[DEBUG] Fixed newlines in private_key in temp file")

            except Exception as e:
                logger.error(f"[DEBUG] Error fixing private_key: {e}")
                # If fixing fails, try to continue with original file

            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(temp_path, scope)
                self.client = gspread.authorize(credentials)
            finally:
                os.unlink(temp_path)

        elif credentials_path and os.path.exists(credentials_path):
            # Use credentials file (local development)
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            self.client = gspread.authorize(credentials)
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

        # Find first empty row
        col_values = self.worksheet.col_values(1)  # Get all values in column A
        return len(col_values) + 1

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

            # Convert job data to row format
            from models.job_schema import JobData
            job = JobData(**job_data)
            row_data = job.to_google_sheets_row()

            # Write to sheet
            self.worksheet.append_row(row_data, value_input_option='USER_ENTERED')

            logger.info(f"Successfully wrote job to row {row_number}: {job.get('title', 'Unknown')}")

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
