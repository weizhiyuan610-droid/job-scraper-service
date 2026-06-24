"""
Prompts for AI-based job data extraction
"""

# Simple prompt for faster extraction
JOB_EXTRACTION_PROMPT_SIMPLE = """You are a job data extraction expert. Extract structured information from the following job posting text.

Return ONLY a JSON object (no markdown, no explanation):

{{
  "company": "Company name",
  "title": "Job title",
  "location": "Location (e.g., 'London, UK' or 'Remote')",
  "type": "Full-time, Part-time, Contract, or Internship",
  "industry": "Industry (e.g., SDE, Quant, PM, MLE, Data, Other)",
  "apply_link": "Application URL or 'Unknown'",
  "deadline": "Application deadline or 'Rolling'",
  "opened": "Job posting date (YYYY-MM-DD) or leave empty",
  "degree_min": "Minimum degree: bachelors, masters, phd, any",
  "degree_preferred": "Preferred degree field or leave empty",
  "visa_sponsorship": true or false,
  "visa_mentioned": "explicit_yes, explicit_no, or not_mentioned",
  "visa_note": "Brief note about visa sponsorship or leave empty",
  "target_year": "Target graduation year or 'Any'",
  "salary": "Salary information or leave empty",
  "description": "Brief 1-2 sentence summary of the role",
  "requirements": "Job requirements (experience, skills, education) - brief text",
  "perks": ["benefit1", "benefit2"] (array of benefits like health insurance, vacation, bonus, etc. Empty array if not mentioned)
}}

Job Posting:
{page_text}

CRITICAL: Return ONLY the raw JSON object. DO NOT wrap in ```json``` code blocks. DO NOT add any explanation. Just the JSON object starting with {{ and ending with }}."""

# Detailed prompt for comprehensive extraction
JOB_EXTRACTION_PROMPT = """You are an expert job data extraction system specializing in quant finance, software engineering, and tech industry positions. Your task is to extract structured information from job postings with high accuracy.

EXTRACTION RULES:
1. Return ONLY valid JSON - no markdown, no explanation, no code blocks
2. Use "Unknown" for missing/uncertain values (except for boolean fields)
3. visa_sponsorship must be true/false (default to false if not mentioned)
4. For UK roles: Look for "visa sponsorship", "right to work", "skilled worker visa"
5. For US roles: Look for "H1B", "OPT", "CPT", "work authorization", "sponsorship"
6. For EU roles: Look for "work permit", "visa sponsorship", "EU citizenship"
7. Extract the most specific location available (e.g., "London, UK" not just "UK")
8. For type, choose: Full-time, Part-time, Contract, Internship, or Unknown

JSON FORMAT:
{{
  "company": "Company name (e.g., 'Jane Street', 'Google')",
  "title": "Job title (e.g., 'Quantitative Researcher', 'Software Engineer')",
  "location": "City, Country or 'Remote' or 'Unknown'",
  "type": "Full-time, Part-time, Contract, Internship, or Unknown",
  "industry": "SDE, Quant, PM, MLE, Data, DS, Other, or Unknown",
  "apply_link": "Application URL (full https://...)",
  "deadline": "Application deadline (YYYY-MM-DD) or 'Rolling' or 'Unknown'",
  "opened": "Posting date (YYYY-MM-DD) or empty string",
  "degree_min": "bachelors, masters, phd, or any",
  "degree_preferred": "Preferred field (e.g., 'CS', 'Math', 'Physics') or empty",
  "visa_sponsorship": true or false,
  "visa_mentioned": "explicit_yes, explicit_no, or not_mentioned",
  "visa_note": "Brief explanation of visa policy",
  "target_year": "Graduation year (e.g., '2025') or 'Any'",
  "salary": "Salary info if available (e.g., '£100k-£150k') or empty",
  "description": "2-3 sentence summary of the role and key requirements"
}}

Job Posting to Extract:
{page_text}

CRITICAL: Return ONLY the raw JSON object. DO NOT wrap in ```json``` code blocks. DO NOT add any explanation. Just the JSON object starting with {{ and ending with }}."""
