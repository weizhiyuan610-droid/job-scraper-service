"""
AI-based company information inference
Uses Gemini AI to estimate company details for unknown companies
"""
import os
import logging
from typing import Optional, Dict
import google.generativeai as genai
from data.companies import get_company_info, SIZE_CATEGORIES, FUNDING_STAGES

logger = logging.getLogger(__name__)


class CompanyInfoInference:
    """AI-powered company information inference"""

    def __init__(self, api_key: str = None):
        """
        Initialize AI inference engine

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for company inference")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Cache for inferred companies
        self._inference_cache = {}

    def get_company_info(self, company_name: str, industry: str = "") -> Dict:
        """
        Get complete company info (from database or AI inference)

        Args:
            company_name: Company name
            industry: Job industry (helps with inference)

        Returns:
            Dictionary with company info
        """
        if not company_name:
            return self._get_default_info()

        # Check pre-built database first
        db_info = get_company_info(company_name)
        if db_info:
            logger.info(f"Found {company_name} in database")
            return db_info

        # Check cache
        if company_name in self._inference_cache:
            logger.info(f"Using cached inference for {company_name}")
            return self._inference_cache[company_name]

        # Use AI to infer
        logger.info(f"Inferring info for {company_name} (industry: {industry})")
        inferred_info = self._infer_with_ai(company_name, industry)

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
        prompt = self._build_inference_prompt(company_name, industry)

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Parse AI response
            import json
            try:
                # Try to extract JSON from response
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()

                inferred = json.loads(result)

                # Validate and normalize
                return self._normalize_inferred_info(company_name, inferred)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.debug(f"AI response was: {result}")
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
            "website": ""
        }


# Singleton instance
_inference_instance = None


def get_company_inference() -> CompanyInfoInference:
    """Get or create singleton inference instance"""
    global _inference_instance
    if _inference_instance is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        _inference_instance = CompanyInfoInference(api_key=api_key)
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
