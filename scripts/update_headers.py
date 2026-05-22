#!/usr/bin/env python3
"""
Update Google Sheet headers to include all new fields
Run this script to update the header row in your Google Sheet
"""
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gspread
from config import settings


def update_sheet_headers():
    """Update the headers in the Google Sheet"""

    # Define the new headers
    headers = [
        'ID',                    # A列
        'Company',               # B列
        'Title',                 # C列
        'Industry',              # D列
        'Location',              # E列
        'Salary',                # F列
        'VisaSponsorship',       # G列
        'Deadline',              # H列
        'PreferredMajors',       # I列
        'TargetYear',            # J列
        'Degree',                # K列
        'Type',                  # L列
        'Description',           # M列
        'ApplicationUrl',        # N列
        'Status',                # O列
        'Skills',                # P列
        'Department',            # Q列
        'JobLevel',              # R列
        'WorkMode',              # S列
        'TargetAudience',        # T列
        'SalaryRange',           # U列
        'CompanySize',           # V列
        'EmployeeCount',         # W列
        'FundingStage',          # X列
        'CompanyHQ',             # Y列
        'YearFounded',           # Z列
        'CompanyTier',           # AA列
        'CompanyWebsite',        # AB列
        'CompanyDomain',         # AC列
    ]

    print("=== Google Sheet Header Update ===")
    print(f"Sheet ID: {settings.google_sheet_id}")
    print(f"Sheet Name: {settings.google_sheet_name}")
    print(f"Total columns: {len(headers)}")
    print()

    if not settings.google_credentials_json:
        print("ERROR: GOOGLE_CREDENTIALS_JSON environment variable not set")
        return False

    try:
        # Use get_google_credentials which handles all the parsing
        from config import get_google_credentials
        credentials_dict = get_google_credentials()

        if not credentials_dict:
            print("ERROR: Failed to parse Google credentials")
            return False

        # Use gspread's service_account method which handles credentials better
        client = gspread.service_account_from_dict(credentials_dict)

        # Open spreadsheet
        sheet = client.open_by_key(settings.google_sheet_id)
        worksheet = sheet.worksheet(settings.google_sheet_name)

        # Get current headers
        current_headers = worksheet.row_values(1)
        print(f"Current headers ({len(current_headers)} columns):")
        print(current_headers)
        print()

        # Check if update is needed
        if len(current_headers) == len(headers):
            print("Headers already have the correct number of columns.")
            response = input("Do you want to update anyway? (y/n): ")
            if response.lower() != 'y':
                print("Update cancelled.")
                return True

        # Calculate the range (e.g., A1:AC1)
        end_col = chr(64 + len(headers)) if len(headers) <= 26 else f"A{chr(64 + len(headers) - 26)}"
        cell_range = f"A1:{end_col}1"

        # Update headers
        print(f"Updating headers to range {cell_range}...")
        worksheet.update(cell_range, [headers], value_input_option='USER_ENTERED')

        print()
        print("SUCCESS! Headers updated:")
        for i, header in enumerate(headers, 1):
            col_letter = chr(64 + i) if i <= 26 else f"A{chr(64 + i - 26)}"
            print(f"  {col_letter}列: {header}")

        print()
        print(f"Total: {len(headers)} columns")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = update_sheet_headers()
    sys.exit(0 if success else 1)
