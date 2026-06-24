"""
AI-based company information inference
Uses Claude AI to estimate company details for unknown companies
"""
import os
import logging
from typing import Optional, Dict
import requests
from data.companies import get_company_info

logger = logging.getLogger(__name__)

# Claude API endpoint
CLAUDE_API_BASE = "https://api.anthropic.com/v1/messages"


class CompanyInfoInference:
    """AI-powered company information inference"""

    def __init__(self, api_key: str = None, model: str = "claude-3-5-haiku-20241022"):
        """
        Initialize AI inference engine

        Args:
            api_key: Claude API key (defaults to CLAUDE_API_KEY env var)
            model: Model to use for inference (Haiku is faster and cheaper for this task)
        """
        # Try to get API key from parameter, environment, or settings
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("CLAUDE_API_KEY", "")
            if not self.api_key:
                try:
                    from config import settings
                    self.api_key = settings.claude_api_key
                except:
                    pass

        if not self.api_key:
            logger.warning("No Claude API key found, company inference will use defaults only")

        self.model_name = model
        self.api_url = CLAUDE_API_BASE

        # Cache for inferred companies
        self._inference_cache = {}

    def get_company_info(self, company_name: str, industry: str = "") -> Dict:
        """
        Get complete company info (from database or AI inference)

        Args:
            company_name: Company name
            industry: Job industry (helps with inference)

        Returns:
            Dictionary with company info including source and confidence
        """
        if not company_name:
            info = self._get_default_info()
            info["source"] = "unknown"
            info["confidence"] = 0
            return info

        # Check pre-built database first
        db_info = get_company_info(company_name)
        if db_info:
            logger.info(f"Found {company_name} in database")
            db_info["source"] = "database"
            db_info["confidence"] = 100
            return db_info

        # Check cache
        if company_name in self._inference_cache:
            logger.info(f"Using cached inference for {company_name}")
            return self._inference_cache[company_name]

        # Use AI to infer
        logger.info(f"Inferring info for {company_name} (industry: {industry})")
        inferred_info = self._infer_with_ai(company_name, industry)

        # Add source metadata
        confidence = self._calculate_confidence(inferred_info, company_name)
        inferred_info["source"] = "ai_low_confidence" if confidence < 70 else "ai_inferred"
        inferred_info["confidence"] = confidence

        # Cache the result
        self._inference_cache[company_name] = inferred_info

        return inferred_info

    def _infer_with_ai(self, company_name: str, industry: str) -> Dict:
        """
        Use AI to infer company information

        Args:
            company_name: Company name
            industry: Job industry context

        Returns:
            Inferred company info dict
        """
        if not self.api_key:
            logger.warning("No API key for company inference, using defaults")
            return self._get_default_info(company_name)

        prompt = self._build_inference_prompt(company_name, industry)

        try:
            payload = {
                "model": self.model_name,
                "max_tokens": 1024,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30  # 30 second timeout
            )

            if response.status_code != 200:
                logger.error(f"Company inference API error {response.status_code}")
                return self._get_default_info(company_name)

            result = response.json()

            # Extract response text from Claude's response format
            if 'content' not in result or len(result['content']) == 0:
                logger.error("Empty response from company inference API")
                return self._get_default_info(company_name)

            result_text = result['content'][0].get('text', '')

            if not result_text:
                logger.error("Empty response text from company inference API")
                return self._get_default_info(company_name)

            # Parse AI response
            import json
            try:
                # Try to extract JSON from response
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                inferred = json.loads(result_text)

                # Validate and normalize
                return self._normalize_inferred_info(company_name, inferred)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.debug(f"AI response was: {result_text[:300]}")
                return self._get_default_info(company_name)

        except requests.exceptions.Timeout:
            logger.error(f"Company inference timed out for {company_name}")
            return self._get_default_info(company_name)
        except Exception as e:
            logger.error(f"AI inference failed for {company_name}: {e}")
            return self._get_default_info(company_name)

    def _build_inference_prompt(self, company_name: str, industry: str) -> str:
        """Build prompt for AI inference"""
        return f"""You are a company information expert. Based on the company name "{company_name}" and industry "{industry}", estimate the company's information.

Respond ONLY with a JSON object (no other text):

{{
  "domain": "best guess of company domain (e.g., companyname.com)",
  "size_category": "Select one: Startup, Small, Mid, Large, Enterprise",
  "employee_count": "estimated range (e.g., '51-200', '1000+')",
  "funding_stage": "Select one: Pre-seed, Seed, Series A, Series B, Series C, Series D+, Public, Private",
  "industry": "{industry or 'Other'}",
  "hq_location": "best guess (e.g., 'San Francisco, CA' or 'Unknown')",
  "year_founded": "estimate or 'Unknown'",
  "tier": "Select one: Tier 1 (industry leader), Tier 2 (established), Tier 3 (emerging), Unknown",
  "website": "best guess (e.g., 'https://www.companyname.com' or 'Unknown')"
}}

INFERENCE GUIDELINES:
1. Size Category:
   - Startup: Famous startups, unicorns (<10 years old, rapid growth)
   - Small: 51-200 employees (small startups, local companies)
   - Mid: 201-1000 employees (growing startups, mid-size companies)
   - Large: 1001-10000 employees (established companies)
   - Enterprise: 10000+ employees (big corporations, Fortune 500)

2. Funding Stage:
   - If the company is publicly traded → Public
   - If well-known private company (Stripe, SpaceX, etc.) → Private
   - If startup with funding news → estimate stage (Series A/B/C)
   - If unknown → Private

3. Tier:
   - Tier 1: Industry leaders (FAANG, MBB, big banks, top startups)
   - Tier 2: Established companies (regional banks, mid-tier tech)
   - Tier 3: Emerging/smaller companies
   - Unknown: If you cannot determine

4. Use "Unknown" for any field you cannot reasonably estimate

Return JSON only, no explanation."""

    def _normalize_inferred_info(self, company_name: str, inferred: Dict) -> Dict:
        """Normalize and validate inferred information"""
        default_info = self._get_default_info(company_name)

        # Merge with defaults, keeping inferred values if valid
        result = default_info.copy()
        for key, value in inferred.items():
            if value and value != "Unknown" and value != "":
                result[key] = value

        # Validate size_category
        valid_sizes = ["Startup", "Small", "Mid", "Large", "Enterprise"]
        if result.get("size_category") not in valid_sizes:
            result["size_category"] = "Mid"

        # Validate funding_stage
        valid_stages = ["Pre-seed", "Seed", "Series A", "Series B", "Series C", "Series D+", "Public", "Private"]
        if result.get("funding_stage") not in valid_stages:
            result["funding_stage"] = "Private"

        # Validate tier
        valid_tiers = ["Tier 1", "Tier 2", "Tier 3", "Unknown"]
        if result.get("tier") not in valid_tiers:
            result["tier"] = "Unknown"

        return result

    def _calculate_confidence(self, company_info: Dict, company_name: str) -> int:
        """
        Calculate confidence score for inferred company information

        Args:
            company_info: Inferred company information
            company_name: Original company name

        Returns:
            Confidence score 0-100
        """
        score = 50  # Base score

        # Add points for specific fields being filled
        if company_info.get("domain"):
            score += 15
        if company_info.get("employee_count"):
            score += 10
        if company_info.get("year_founded") and company_info["year_founded"] != "Unknown":
            score += 10
        if company_info.get("hq_location") and company_info["hq_location"] != "Unknown":
            score += 10

        # Deduct points for generic/unknown values
        if company_info.get("tier") == "Unknown":
            score -= 10
        if company_info.get("size_category") == "Mid":
            score -= 5  # Mid is the default

        # Check if company name looks specific (contains Inc, LLC, Ltd, etc.)
        specific_suffixes = ["Inc", "LLC", "Ltd", "Corp", "Group", "Solutions", "Technologies"]
        if any(suffix in company_name for suffix in specific_suffixes):
            score += 10

        # Cap at 100, minimum 10
        return max(10, min(100, score))

    def _get_default_info(self, company_name: str = "Unknown") -> Dict:
        """Get default company info for unknown companies"""
        return {
            "domain": "",
            "size_category": "Mid",
            "employee_count": "",
            "funding_stage": "Private",
            "industry": "Other",
            "hq_location": "Unknown",
            "year_founded": "",
            "tier": "Unknown",
            "company_website": "",
            "source": "unknown",
            "confidence": 0
        }


# Singleton instance
_inference_instance = None


def get_company_inference() -> CompanyInfoInference:
    """Get or create singleton inference instance"""
    global _inference_instance
    if _inference_instance is None:
        _inference_instance = CompanyInfoInference()
    return _inference_instance


def enrich_company_info(company_name: str, industry: str = "") -> Dict:
    """
    Convenience function to get company info

    Args:
        company_name: Company name
        industry: Job industry

    Returns:
        Company information dictionary
    """
    inference = get_company_inference()
    return inference.get_company_info(company_name, industry)
