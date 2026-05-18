"""
Event Horizon Lab - Job Scraper Service
Flask Web Application
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
from scraper.playwright_scraper import scrape_page_sync
from scraper import AIExtractor, SheetsWriter
from models import JobData
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


@app.route('/tutorial')
def tutorial():
    """Render tutorial page"""
    return render_template('tutorial.html')


@app.route('/api/scrape', methods=['POST'])
def scrape():
    """
    API endpoint to scrape a job posting

    Expects JSON body:
    {
        "url": "https://example.com/job-posting"
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
        if not data or 'url' not in data:
            return jsonify({
                "success": False,
                "error": "Missing URL in request body"
            }), 400

        url = data['url'].strip()

        if not url.startswith('http'):
            return jsonify({
                "success": False,
                "error": "Invalid URL format"
            }), 400

        logger.info(f"Scraping URL: {url}")

        # Step 1: Scrape web page
        logger.info("Step 1: Scraping web page...")
        scrape_result = scrape_page_sync(url, settings.headless_browser)

        if not scrape_result.get('success'):
            return jsonify({
                "success": False,
                "error": f"Failed to scrape page: {scrape_result.get('error', 'Unknown error')}"
            }), 400

        page_content = scrape_result['content']
        logger.info(f"Scraped content length: {len(page_content)} characters")

        # Step 2: Extract job data using AI
        logger.info("Step 2: Extracting job data with AI...")
        extractor = AIExtractor(api_key=settings.gemini_api_key, model=settings.ai_model)
        extract_result = extractor.extract_job_data(
            page_content,
            simple_mode=settings.ai_simple_mode
        )

        if not extract_result.get('success'):
            return jsonify({
                "success": False,
                "error": f"Failed to extract data: {extract_result.get('error', 'Unknown error')}"
            }), 400

        job_data = extract_result['data']

        # Validate with Pydantic
        try:
            job = JobData(**job_data)
            job_dict = job.model_dump()

            # Add metadata
            job_dict['source_url'] = url
            job_dict['scraped_at'] = scrape_result.get('metadata', {}).get('timestamp', '')

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
                "message": "Job data extracted successfully"
            })

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Data validation failed: {str(e)}"
            }), 400

    except Exception as e:
        logger.error(f"Unexpected error in scrape endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


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
        extractor = AIExtractor(api_key=settings.gemini_api_key, model=settings.ai_model)
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

    Expects JSON body with job data fields

    Returns:
    {
        "success": true/false,
        "row_number": 47,
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

        logger.info(f"Saving job: {job_data.get('company')} - {job_data.get('title')}")

        # Get Google credentials
        credentials = get_google_credentials()

        if not credentials:
            return jsonify({
                "success": False,
                "error": "Google credentials not configured"
            }), 500

        # Initialize writer
        writer = SheetsWriter(credentials_json=credentials)
        writer.open_spreadsheet(
            sheet_id=settings.google_sheet_id,
            sheet_name=settings.google_sheet_name
        )

        # Check for duplicates
        duplicate_row = writer.check_duplicate(
            job_data.get('company', ''),
            job_data.get('title', '')
        )

        if duplicate_row:
            logger.warning(f"Duplicate found at row {duplicate_row}")
            return jsonify({
                "success": False,
                "error": f"This job already exists in row {duplicate_row}",
                "duplicate_row": duplicate_row
            }), 409  # Conflict status code

        # Write to Google Sheets
        result = writer.write_job(job_data)

        if result.get('success'):
            logger.info(f"Saved to row {result['row_number']}")
            return jsonify({
                "success": True,
                "row_number": result['row_number'],
                "job_id": result['job_id'],
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
