"""
Event Horizon Lab - Job Scraper Service
Flask Web Application
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
from scraper import AIExtractor, SheetsWriter
from scraper.company_inference import get_company_inference
from scraper.visa_enhancer import VisaEnhancer
from models import JobData, CompanyInfo
from config import settings, validate_settings, get_google_credentials

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


def enrich_job_with_company_info(job_data: dict) -> dict:
    """
    Enrich job data with company information from database or AI inference

    Args:
        job_data: Job data dictionary with at least 'company' and 'industry' fields

    Returns:
        Updated job data with company_info field
    """
    try:
        company_name = job_data.get('company', '')
        industry = job_data.get('industry', '')

        if not company_name:
            # No company info available, use default
            job_data['company_info'] = CompanyInfo().model_dump()
            return job_data

        # Get company info from database or AI inference
        inference = get_company_inference()
        company_info_dict = inference.get_company_info(company_name, industry)

        # Create CompanyInfo object and add to job data as dict (Pydantic will validate)
        job_data['company_info'] = company_info_dict

        logger.info(f"Enriched {company_name} with company info: size={company_info_dict.get('size_category')}, tier={company_info_dict.get('tier')}")

    except Exception as e:
        logger.error(f"Error enriching company info: {e}", exc_info=True)
        # Use default company info on error
        job_data['company_info'] = CompanyInfo().model_dump()

    return job_data


def enrich_job_with_visa_info(job_data: dict) -> dict:
    """
    Enhance job data with visa information using company history database

    This function is called after AI extraction to fill in visa information
    when the JD doesn't explicitly mention visa sponsorship.

    Args:
        job_data: Job data dictionary

    Returns:
        Updated job data with visa_source and visa_likelihood fields
    """
    try:
        visa_enhancer = VisaEnhancer()
        enhanced_data = visa_enhancer.enhance_visa_info(job_data)

        company_name = job_data.get('company', '')
        logger.info(f"Enhanced visa info for {company_name}: source={enhanced_data.get('visa_source')}, likelihood={enhanced_data.get('visa_likelihood')}")

        return enhanced_data

    except Exception as e:
        logger.error(f"Error enhancing visa info: {e}", exc_info=True)
        # Set default values on error
        job_data['visa_source'] = 'error'
        job_data['visa_likelihood'] = 'unknown'
        return job_data


@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Get available users and their sheet configurations

    Returns:
    {
        "success": true,
        "users": [
            {"id": "a", "name": "小A", "sheet_name": "职位数据-小A"},
            {"id": "b", "name": "小B", "sheet_name": "职位数据-小B"},
            {"id": "c", "name": "小C", "sheet_name": "职位数据-小C"},
            {"id": "d", "name": "备用", "sheet_name": "职位数据-备用"}
        ]
    }
    """
    try:
        users = []
        for user_id, config in settings.user_sheets.items():
            users.append({
                'id': user_id,
                'name': config['display_name'],
                'sheet_name': config['name']
            })

        return jsonify({
            "success": True,
            "users": users
        })
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/tutorial')
def tutorial():
    """Render tutorial page"""
    return render_template('tutorial.html')


@app.route('/api/extract-from-text', methods=['POST'])
def extract_from_text():
    """
    API endpoint to extract job data from pasted text

    Expects JSON body:
    {
        "text": "Job description text content",
        "url": "https://example.com (optional)"
    }

    Returns:
    {
        "success": true/false,
        "data": { extracted job fields },
        "error": "error message if failed"
    }
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing text in request body"
            }), 400

        text = data['text'].strip()
        url = data.get('url', '').strip()

        if len(text) < 50:
            return jsonify({
                "success": False,
                "error": "Text content too short. Please provide complete job description."
            }), 400

        logger.info(f"Extracting from text (length: {len(text)} characters)")
        if url:
            logger.info(f"Source URL: {url}")

        # Extract job data using AI (skip web scraping)
        logger.info("Extracting job data with AI...")

        # Select API key based on model
        if settings.ai_model.startswith('claude'):
            api_key = settings.claude_api_key
        else:
            api_key = settings.gemini_api_key

        extractor = AIExtractor(api_key=api_key, model=settings.ai_model)
        extract_result = extractor.extract_job_data(
            text,
            simple_mode=settings.ai_simple_mode
        )

        if not extract_result.get('success'):
            return jsonify({
                "success": False,
                "error": f"Failed to extract data: {extract_result.get('error', 'Unknown error')}"
            }), 400

        job_data = extract_result['data']

        # Enrich with company information
        job_data = enrich_job_with_company_info(job_data)

        # Enhance visa information
        job_data = enrich_job_with_visa_info(job_data)

        # Validate with Pydantic
        try:
            job = JobData(**job_data)
            job_dict = job.model_dump()

            # Add metadata
            if url:
                job_dict['source_url'] = url
            job_dict['scraped_at'] = ""  # No scraping timestamp for text input

            # Calculate confidence score
            if 'validation' in extract_result:
                job_dict['confidence_score'] = extract_result['validation']['confidence_score']
                job_dict['validation'] = extract_result['validation']
            else:
                job_dict['confidence_score'] = 85  # Default

            logger.info(f"Successfully extracted: {job.company} - {job.title}")

            return jsonify({
                "success": True,
                "data": job_dict,
                "message": "Job data extracted successfully from text"
            })

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Data validation failed: {str(e)}"
            }), 400

    except Exception as e:
        logger.error(f"Unexpected error in extract-from-text endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/save', methods=['POST'])
def save():
    """
    API endpoint to save job data to Google Sheets

    Expects JSON body with job data fields and optional user parameter:
    {
        "user": "a",  // Optional: which user's sheet to write to (default: "a")
        ...job data fields...
    }

    Returns:
    {
        "success": true/false,
        "row_number": 47,
        "saved_to": "小A的表格",
        "error": "error message if failed"
    }
    """
    try:
        job_data = request.get_json()

        if not job_data:
            return jsonify({
                "success": False,
                "error": "Missing job data in request body"
            }), 400

        # Get user parameter (default to "a" if not provided)
        user_id = job_data.pop('user', 'a')  # Remove from job_data before saving

        logger.info(f"Saving job for user '{user_id}': {job_data.get('company')} - {job_data.get('title')}")

        # Get user's sheet configuration
        user_sheets = settings.user_sheets
        user_config = user_sheets.get(user_id)

        if not user_config:
            return jsonify({
                "success": False,
                "error": f"Invalid user '{user_id}'. Valid users: {list(user_sheets.keys())}"
            }), 400

        sheet_id = user_config['id']
        sheet_name = user_config['name']

        if not sheet_id:
            return jsonify({
                "success": False,
                "error": f"No sheet ID configured for user '{user_config['display_name']}'. Please configure USER_{user_id.upper()}_SHEET_ID."
            }), 500

        logger.info(f"Writing to sheet: {sheet_name} (ID: {sheet_id})")

        # Get Google credentials
        credentials = get_google_credentials()

        if not credentials:
            return jsonify({
                "success": False,
                "error": "Google credentials not configured"
            }), 500

        # Initialize writer with user's sheet
        writer = SheetsWriter(credentials_json=credentials)
        writer.open_spreadsheet(
            sheet_id=sheet_id,
            sheet_name=sheet_name
        )

        # Check for duplicates in user's sheet
        duplicate_row = writer.check_duplicate(
            job_data.get('company', ''),
            job_data.get('title', '')
        )

        if duplicate_row:
            logger.warning(f"Duplicate found at row {duplicate_row} in {sheet_name}")
            return jsonify({
                "success": False,
                "error": f"This job already exists in row {duplicate_row}",
                "duplicate_row": duplicate_row,
                "sheet": sheet_name
            }), 409  # Conflict status code

        # Write to Google Sheets
        result = writer.write_job(job_data)

        if result.get('success'):
            logger.info(f"Saved to row {result['row_number']} in {sheet_name}")
            return jsonify({
                "success": True,
                "row_number": result['row_number'],
                "job_id": result['job_id'],
                "saved_to": f"{user_config['display_name']}的表格",
                "sheet_name": sheet_name,
                "message": "Job saved successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error')
            }), 500

    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to save: {str(e)}"
        }), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """
    Get statistics about the scraper

    Returns:
    {
        "total_jobs": 47,
        "success_rate": 95.7,
        "recent_scrapes": [...]
    }
    """
    try:
        credentials = get_google_credentials()

        if not credentials:
            return jsonify({
                "success": False,
                "error": "Google credentials not configured"
            }), 500

        writer = SheetsWriter(credentials_json=credentials)
        writer.open_spreadsheet(
            sheet_id=settings.google_sheet_id,
            sheet_name=settings.google_sheet_name
        )

        total_jobs = writer.get_job_count()

        return jsonify({
            "success": True,
            "stats": {
                "total_jobs": total_jobs,
                "success_rate": 95.0,  # Placeholder - could track actual rate
                "ai_model": settings.ai_model,
                "sheet_name": settings.google_sheet_name
            }
        })

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }), 200


@app.route('/api/update-headers', methods=['POST'])
def update_headers():
    """
    Update Google Sheet headers
    This endpoint updates the header row to include all new columns

    Returns:
    {
        "success": true/false,
        "message": "Headers updated successfully"
    }
    """
    try:
        # Define the new headers (enhanced with precise parsing fields)
        headers = [
            'ID', 'Company', 'Title', 'Industry', 'Location', 'Salary',
            'VisaSponsorship', 'Deadline', 'PreferredMajors', 'TargetYear',
            'Degree', 'Type', 'Description', 'ApplicationUrl', 'Status',
            'Skills', 'Department', 'JobLevel', 'WorkMode', 'TargetAudience',
            'SalaryRange', 'CompanySize', 'EmployeeCount', 'FundingStage',
            'CompanyHQ', 'YearFounded', 'CompanyTier', 'CompanyWebsite',
            'CompanyDomain',
            # NEW: Enhanced parsing fields for precise analysis
            'DegreeMin', 'DegreePreferred', 'VisaMentioned', 'VisaNote',
            'RawDescription',
            # Pre-computed scores
            'priority_score', 'urgency_score', 'freshness_score',
            'quality_score', 'matchability_score', 'scores_calculated_at',
            # NEW: Enhanced visa tracking + requirements + perks
            'Requirements', 'Perks', 'VisaSource', 'VisaLikelihood',
        ]

        credentials = get_google_credentials()
        if not credentials:
            return jsonify({
                "success": False,
                "error": "Google credentials not configured"
            }), 500

        writer = SheetsWriter(credentials_json=credentials)
        writer.open_spreadsheet(
            sheet_id=settings.google_sheet_id,
            sheet_name=settings.google_sheet_name
        )

        # Calculate the range (e.g., A1:AR1)
        # For 1-26: A-Z, for 27-52: AA-AZ, for 53-78: BA-BZ, etc.
        # We have 44 headers (A-AR), where AR = 44 (1-indexed)
        num_cols = len(headers)
        if num_cols <= 26:
            end_col = chr(64 + num_cols)  # A=65, so A=1, B=2, ..., Z=26
        else:
            # For columns beyond Z: AA, AB, ..., AZ, BA, ...
            first = chr(64 + (num_cols - 1) // 26)
            second = chr(64 + ((num_cols - 1) % 26) + 1)
            end_col = first + second
        cell_range = f"A1:{end_col}1"

        # Update headers
        writer.worksheet.update(cell_range, [headers], value_input_option='USER_ENTERED')

        logger.info(f"Updated Google Sheet headers to {len(headers)} columns")

        return jsonify({
            "success": True,
            "message": f"Headers updated to {len(headers)} columns",
            "headers": headers,
            "range": cell_range
        })

    except Exception as e:
        logger.error(f"Error updating headers: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/validate-links', methods=['GET', 'POST'])
def validate_links():
    """
    Validate job application links
    Checks if job links are valid and accessible

    Query params:
        offset: Starting index (default: 0, for batch checking)
        limit: Number of jobs to check (default: 50)

    Returns:
    {
        "success": true/false,
        "summary": {"total": 50, "valid": 45, "invalid": 5, "checked": 50, "remaining": 102},
        "results": [{link validation details}]
    }
    """
    try:
        # Get batch parameters
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 50))
        limit = min(limit, 100)  # Max 100 per batch

        credentials = get_google_credentials()
        if not credentials:
            return jsonify({
                "success": False,
                "error": "Google credentials not configured"
            }), 500

        writer = SheetsWriter(credentials_json=credentials)
        writer.open_spreadsheet(
            sheet_id=settings.google_sheet_id,
            sheet_name=settings.google_sheet_name
        )

        # Get all jobs from sheet
        all_jobs = writer.worksheet.get_all_records()
        total_jobs = len(all_jobs)

        logger.info(f"Validating links with offset={offset}, limit={limit}, total_jobs={total_jobs}")

        if not all_jobs or offset >= total_jobs:
            return jsonify({
                "success": True,
                "summary": {
                    "total": 0,
                    "valid": 0,
                    "invalid": 0,
                    "breakdown": {},
                    "checked": 0,
                    "remaining": 0,
                    "offset": offset,
                    "complete": True
                },
                "results": []
            })

        # Get jobs for this batch
        end_index = min(offset + limit, total_jobs)
        jobs_to_check = all_jobs[offset:end_index]

        from scraper.link_validator import validate_links_sync
        validation_result = validate_links_sync(jobs_to_check, timeout=8)

        # Add offset to each result for correct row number
        for result in validation_result['results']:
            result['row'] = result['row'] + offset  # Adjust row number based on offset

        logger.info(f"Link validation complete: {validation_result['valid']}/{validation_result['total']} valid")

        remaining_jobs = max(0, total_jobs - end_index)
        complete = remaining_jobs == 0

        return jsonify({
            "success": True,
            "summary": {
                "total": validation_result['total'],
                "valid": validation_result['valid'],
                "invalid": validation_result['invalid'],
                "breakdown": validation_result.get('breakdown', {}),
                "checked": end_index - offset,
                "remaining": remaining_jobs,
                "offset": offset,
                "next_offset": end_index if not complete else None,
                "complete": complete,
                "total_jobs": total_jobs,
                "progress": f"{end_index}/{total_jobs}"
            },
            "results": validation_result['results']
        })

    except Exception as e:
        logger.error(f"Error validating links: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found", "message": str(error)}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error", "message": str(error)}), 500


def main():
    """Run the Flask application"""
    # Log all environment variables for debugging (without values)
    logger.info("=== Environment Variables ===")
    logger.info(f"CLAUDE_API_KEY: {'✓ Set' if settings.claude_api_key else '✗ Missing'}")
    logger.info(f"GEMINI_API_KEY: {'✓ Set' if settings.gemini_api_key else '✗ Missing'}")
    logger.info(f"GOOGLE_SHEET_ID: {'✓ Set' if settings.google_sheet_id else '✗ Missing'}")
    logger.info(f"GOOGLE_CREDENTIALS_JSON: {'✓ Set' if settings.google_credentials_json else '✗ Missing'}")
    logger.info(f"PORT: {settings.port}")

    # Validate settings
    missing = validate_settings()
    if missing:
        logger.warning(f"Missing configuration: {', '.join(missing)}")
        logger.warning("Application will start but some features may not work")

    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Running on port: {settings.port}")

    app.run(
        host='0.0.0.0',
        port=settings.port,
        debug=settings.debug
    )


if __name__ == '__main__':
    main()
