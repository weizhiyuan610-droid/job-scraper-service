"""
AI Prompt for job data extraction
"""

JOB_EXTRACTION_PROMPT = """You are a professional job information extraction assistant. Extract job details from the following web page content and output in strict JSON format.

WEB PAGE CONTENT:
{page_text}

Extract the following fields and return ONLY a JSON object (no other text):

{{
  "company": "Full company name",
  "title": "Complete job title",
  "location": "City, Country (include 'Remote' if applicable)",
  "type": "Select one: Full-time, Internship, Part-time, Contract",
  "industry": "Select from: 咨询, 投行, 科技互联网, 金融科技, 快消, 其他",
  "apply_link": "Complete application URL",
  "deadline": "Application deadline in YYYY-MM-DD format, or text like 'ASAP', 'Rolling' if not specified",
  "opened": "Posting date in YYYY-MM-DD format, or empty string if not found",
  "degree": "Select one: Bachelor, Master, PhD, MBA, Any, Preferred",
  "visa_sponsorship": "Select one: Yes, No, Case by case, Not mentioned",
  "target_year": "Target graduation year(s). Use comma-separated if multiple: e.g., '2025, 2026' or '2026' or 'Any'",
  "salary": "Salary range as shown on page (original text)",
  "description": "Complete job description (first 500 characters max)",
  "preferred_major": ["major1", "major2"] (array of preferred majors, empty array if not specified)
}}

EXTRACTION RULES:
1. Company name: Extract from logo, page title, breadcrumb, or meta tags
2. Job title: Extract from H1 tag or main heading
3. Location: Include city, state/province, and country. Mark "Remote" if applicable
4. Industry: Judge based on company type and job description
5. Deadline: Look for "Application deadline", "Apply by", etc. Use YYYY-MM-DD format or text
6. Visa sponsorship: Set to "Yes" if page mentions "visa", "sponsorship", "work authorization", "work permit"
7. Type: Default to "Full-time" if not specified
8. Degree: Default to "Any" if not mentioned
9. Apply link: Look for "Apply Now", "Apply here", "Application" buttons or links. Extract the complete URL. If not found, leave empty.
10. Salary: Extract exact text if shown, leave as empty string if not mentioned
11. If a field cannot be determined, use null or empty string/default value

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""

# Simplified version for faster processing
JOB_EXTRACTION_PROMPT_SIMPLE = """Extract job information from this page and return as JSON:

{page_text}

Required fields (JSON format):
{{
  "company": "string",
  "title": "string",
  "location": "string",
  "type": "Full-time/Internship/Part-time/Contract",
  "industry": "咨询/投行/科技互联网/金融科技/快消/其他",
  "apply_link": "URL",
  "deadline": "YYYY-MM-DD or ASAP/Rolling",
  "opened": "YYYY-MM-DD or empty",
  "degree": "Bachelor/Master/PhD/MBA/Any/Preferred",
  "visa_sponsorship": "Yes/No/Case by case/Not mentioned",
  "target_year": "2025, 2026, 2027, or Any (comma-separated if multiple)",
  "salary": "string or empty",
  "description": "string (max 500 chars)",
  "preferred_major": ["major1", "major2"]
}}

Return JSON only, no other text."""
