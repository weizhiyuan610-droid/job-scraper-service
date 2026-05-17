"""
AI-based job data extraction using Gemini API
"""
import json
import os
from typing import Optional, Dict
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class AIExtractor:
    """Extract job data using Gemini AI"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize AI extractor

        Args:
            api_key: Gemini API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model_name = model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

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
        try:
            from .prompts import JOB_EXTRACTION_PROMPT, JOB_EXTRACTION_PROMPT_SIMPLE

            # Select prompt based on mode
            prompt_template = JOB_EXTRACTION_PROMPT_SIMPLE if simple_mode else JOB_EXTRACTION_PROMPT
            prompt = prompt_template.format(page_text=page_content[:15000])  # Limit content length

            logger.info(f"Sending request to Gemini API (model: {self.model_name})")

            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent output
                    max_output_tokens=2000,
                    response_mime_type="application/json"
                )
            )

            if not response or not response.text:
                return {
                    "success": False,
                    "data": {},
                    "error": "Empty response from Gemini API"
                }

            # Parse JSON response
            try:
                extracted_data = json.loads(response.text)
                logger.info(f"Successfully extracted job data: {extracted_data.get('title', 'Unknown')}")

                return {
                    "success": True,
                    "data": extracted_data,
                    "raw_response": response.text
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response.text[:500]}")

                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        extracted_data = json.loads(json_match.group())
                        return {
                            "success": True,
                            "data": extracted_data,
                            "raw_response": response.text
                        }
                    except:
                        pass

                return {
                    "success": False,
                    "data": {},
                    "error": f"Invalid JSON response: {str(e)}"
                }

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
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
        if data.get("visa_sponsorship") == "Not mentioned":
            score -= 15
        if not data.get("description"):
            score -= 10
        if data.get("deadline") == "Rolling":
            score -= 5

        return max(0, min(100, score))


def extract_job_data_sync(api_key: str, page_content: str, simple_mode: bool = False) -> Dict:
    """
    Synchronous wrapper for extract_job_data

    Args:
        api_key: Gemini API key
        page_content: Text content from web page
        simple_mode: Use simplified prompt

    Returns:
        Extraction result dictionary
    """
    extractor = AIExtractor(api_key=api_key)
    return extractor.extract_job_data(page_content, simple_mode=simple_mode)
