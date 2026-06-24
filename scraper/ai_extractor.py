"""
AI-based job data extraction using Claude API
"""
import os
import json
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Claude API endpoint
CLAUDE_API_BASE = "https://api.anthropic.com/v1/messages"


class AIExtractor:
    """Extract job data using Claude AI via REST API"""

    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize AI extractor

        Args:
            api_key: Claude API key (if None, reads from CLAUDE_API_KEY env var)
            model: Model name to use (claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022, etc.)
        """
        # Try to get API key from parameter, environment, or settings
        if api_key:
            self.api_key = api_key
        else:
            # Try environment variable first
            self.api_key = os.getenv("CLAUDE_API_KEY", "")
            if not self.api_key:
                # Fallback to settings
                try:
                    from config import settings
                    self.api_key = settings.claude_api_key
                except:
                    pass

        self.model_name = model
        self.api_url = CLAUDE_API_BASE

        if not self.api_key:
            logger.warning("No Claude API key found, extraction will fail")

    def extract_job_data(self, page_content: str, simple_mode: bool = False) -> Dict:
        """
        Extract job data from page content using AI

        Args:
            page_content: Text content from web page
            simple_mode: Use simplified prompt for faster processing

        Returns:
            Dictionary containing:
                - success: bool
                - data: dict (extracted job fields)
                - error: str (if failed)
        """
        if not self.api_key:
            return {
                "success": False,
                "data": {},
                "error": "Claude API key not configured"
            }

        try:
            from prompts import JOB_EXTRACTION_PROMPT, JOB_EXTRACTION_PROMPT_SIMPLE

            # Select prompt based on mode
            prompt_template = JOB_EXTRACTION_PROMPT_SIMPLE if simple_mode else JOB_EXTRACTION_PROMPT
            prompt = prompt_template.format(page_text=page_content[:20000])  # Claude supports more context

            logger.info(f"Sending request to Claude API (model: {self.model_name})")

            # Prepare request payload for Claude
            payload = {
                "model": self.model_name,
                "max_tokens": 8192,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            # Call Claude API via REST
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60  # 60 second timeout
            )

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"Claude API error {response.status_code}: {error_msg[:500]}")
                return {
                    "success": False,
                    "data": {},
                    "error": f"API error {response.status_code}: {error_msg[:200]}"
                }

            result = response.json()

            # Extract response text from Claude's response format
            if 'content' not in result or len(result['content']) == 0:
                return {
                    "success": False,
                    "data": {},
                    "error": "Empty response from Claude API"
                }

            # Claude returns content as a list of blocks
            response_text = result['content'][0].get('text', '')

            if not response_text:
                return {
                    "success": False,
                    "data": {},
                    "error": "Empty response text from Claude API"
                }

            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)

                # Handle case where API returns a list instead of dict
                if isinstance(extracted_data, list):
                    if len(extracted_data) > 0:
                        extracted_data = extracted_data[0]
                        logger.warning("API returned a list, using first item")
                    else:
                        raise ValueError("API returned empty list")

                logger.info(f"Successfully extracted job data: {extracted_data.get('title', 'Unknown')}")

                return {
                    "success": True,
                    "data": extracted_data,
                    "raw_response": response_text
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text[:500]}")

                # Try to extract JSON from response (handle markdown code blocks)
                import re
                # Remove markdown code blocks if present
                cleaned_text = response_text.strip()
                # Handle ```json at start and ``` at end
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:].lstrip()
                elif cleaned_text.startswith('```'):
                    cleaned_text = cleaned_text[3:].lstrip()
                # Remove closing ```
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3].rstrip()

                # Try parsing again
                try:
                    extracted_data = json.loads(cleaned_text)
                    if isinstance(extracted_data, list):
                        if len(extracted_data) > 0:
                            extracted_data = extracted_data[0]
                        else:
                            raise ValueError("Extracted empty list")
                    return {
                        "success": True,
                        "data": extracted_data,
                        "raw_response": response_text
                    }
                except:
                    return {
                        "success": False,
                        "data": {},
                        "error": f"Invalid JSON response: {str(e)}"
                    }

        except requests.exceptions.Timeout:
            logger.error("Claude API request timed out after 60 seconds")
            return {
                "success": False,
                "data": {},
                "error": "API request timed out (60s)"
            }
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }

    def extract_with_validation(self, page_content: str) -> Dict:
        """
        Extract job data with additional validation step

        Args:
            page_content: Text content from web page

        Returns:
            Result dictionary with validation info
        """
        result = self.extract_job_data(page_content)

        if not result["success"]:
            return result

        # Add validation metadata
        data = result["data"]

        # Check required fields
        required_fields = ["company", "title", "location", "type", "industry", "apply_link", "deadline", "visa_sponsorship"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        result["validation"] = {
            "has_all_required": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "confidence_score": self._calculate_confidence_score(data)
        }

        return result

    def _calculate_confidence_score(self, data: Dict) -> float:
        """
        Calculate confidence score based on extracted data quality

        Args:
            data: Extracted job data

        Returns:
            Confidence score (0-100)
        """
        score = 100

        # Deduct points for missing/low quality data
        if not data.get("company"):
            score -= 20
        if not data.get("title"):
            score -= 20
        if not data.get("location") or data.get("location") == "Unknown":
            score -= 10
        # Check if visa sponsorship is explicitly mentioned
        visa_mentioned = data.get("visa_mentioned", "not_mentioned")
        if visa_mentioned == "not_mentioned" or not data.get("visa_sponsorship", False):
            score -= 15
        if not data.get("description"):
            score -= 10
        if data.get("deadline") == "Rolling":
            score -= 5

        return max(0, min(100, score))


def extract_job_data_sync(api_key: str = None, page_content: str = "", simple_mode: bool = False) -> Dict:
    """
    Synchronous wrapper for extract_job_data

    Args:
        api_key: Claude API key
        page_content: Text content from web page
        simple_mode: Use simplified prompt

    Returns:
        Extraction result dictionary
    """
    extractor = AIExtractor(api_key=api_key)
    return extractor.extract_job_data(page_content, simple_mode=simple_mode)
