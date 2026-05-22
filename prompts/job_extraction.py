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
  "industry": "Select from: Consulting, Investment Banking, Private Equity, Venture Capital, Technology, Fintech, FMCG, SDE, Data, Engineering, Quant, Risk, Finance, Marketing, Design, Product Management, Operation, Law, Public Relations, Other",
  "apply_link": "Complete application URL",
  "deadline": "Application deadline in YYYY-MM-DD format, or text like 'ASAP', 'Rolling' if not specified",
  "opened": "Posting date in YYYY-MM-DD format, or empty string if not found",
  "degree": "Select one: Bachelor, Master, PhD, MBA, Any, Preferred",
  "visa_sponsorship": "Select one: Yes, No, Case by case, Not mentioned",
  "target_year": "Target graduation year(s). Use comma-separated if multiple: e.g., '2025, 2026' or '2026' or 'Any'",
  "salary": "Salary range as shown on page (original text)",
  "description": "Clean job description without company name prefix. Remove patterns like 'Company X is looking for/hiring/seeking'. Extract core responsibilities and requirements (first 500 characters max)",
  "preferred_major": ["major1", "major2"] (array of preferred majors. Classify into: STEM, CS, Media, Art, Business, Finance, Law, Other. Add '-related' suffix if JD mentions 'related disciplines' or similar. Empty array if not specified),
  "status": "Active (assume Active unless page explicitly says closed/expired/filled)"
}}

EXTRACTION RULES:
1. Company name: Extract from logo, page title, breadcrumb, or meta tags
2. Job title: Extract from H1 tag or main heading
3. Location: Include city, state/province, and country. Mark "Remote" if applicable
4. Industry: Judge based on company type and job description. Choose the most appropriate category:
   - Consulting: Management consulting, strategy consulting
   - Investment Banking: IB, M&A, capital markets
   - Private Equity: PE, investment firms
   - Venture Capital: VC, startup investing
   - Technology: General tech companies, tech roles
   - Fintech: Financial technology
   - FMCG: Consumer goods, retail, fashion
   - SDE: Software Development Engineer, software engineer, backend, frontend, full-stack, web development
   - Data: Data science, data analyst, data engineering, analytics, machine learning, AI
   - Engineering: Mechanical, electrical, civil, chemical, biomedical, hardware engineering
   - Quant: Quantitative finance, quantitative research, trading, algorithmic trading
   - Risk: Risk management, risk analyst, compliance
   - Finance: Financial analyst, corporate finance, financial planning (not investment banking)
   - Marketing: Digital marketing, brand, social media, content marketing, growth marketing
   - Design: UX/UI, product design, graphic design, visual design
   - Product Management: Product manager, PM, product owner, agile/scrum
   - Operation: Operations, supply chain, logistics, business operations
   - Law: Legal, paralegal, compliance, contracts
   - Public Relations: PR, communications, external affairs, media relations
   - Other: Any other industry not listed above
5. Deadline: Look for "Application deadline", "Apply by", etc. Use YYYY-MM-DD format or text
6. Visa sponsorship: Set to "Yes" if page mentions "visa", "sponsorship", "work authorization", "work permit"
7. Type: Default to "Full-time" if not specified
8. Degree: Default to "Any" if not mentioned
9. Apply link: Look for "Apply Now", "Apply here", "Application" buttons or links. Extract the complete URL. If not found, leave empty.
10. Salary: Extract exact text if shown, leave as empty string if not mentioned
11. Preferred major classification:
   - STEM: Water, Environment, Electronics, Civil, Mechanical, Chemical, Materials, Physics, Chemistry, Biology, Math, Statistics
   - CS: Computer Science, Software Engineering, Information Technology, Data Science, AI, Machine Learning, Coding
   - Media: Journalism, Communication, Media Studies, Marketing, PR, Advertising, Broadcasting
   - Art: Design, Fine Arts, Music, Film, Photography, Creative Arts, Fashion
   - Business: Business, Management, Marketing, HR, Economics, Accounting
   - Finance: Finance, Investment, Banking, Economics, Accounting
   - Law: Law, Legal Studies
   - Other: Any other field not listed above
   - Add '-related' suffix if job mentions "related disciplines", "related fields", "or similar"
12. Status: Set to "Active" by default. Only set to "Inactive" if page explicitly says "closed", "expired", "filled", "no longer accepting applications"
13. If a field cannot be determined, use null or empty string/default value
14. Description: Clean up the text by removing company name prefixes and redundant phrases like "is looking for", "is hiring", "we are seeking". Focus on actual job responsibilities and requirements.

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
  "industry": "Consulting/Investment Banking/Private Equity/Venture Capital/Technology/Fintech/FMCG/SDE/Data/Engineering/Quant/Risk/Finance/Marketing/Design/Product Management/Operation/Law/Public Relations/Other",
  "apply_link": "URL",
  "deadline": "YYYY-MM-DD or ASAP/Rolling",
  "opened": "YYYY-MM-DD or empty",
  "degree": "Bachelor/Master/PhD/MBA/Any/Preferred",
  "visa_sponsorship": "Yes/No/Case by case/Not mentioned",
  "target_year": "2025, 2026, 2027, or Any (comma-separated if multiple)",
  "salary": "string or empty",
  "description": "Clean description without company prefix or 'looking for' phrases (max 500 chars)",
  "preferred_major": ["STEM", "CS", "Media", "Art", "Business", "Finance", "Law", "Other"] (classify majors, add '-related' if mentions related disciplines),
  "status": "Active" (default Active, only Inactive if closed/expired/filled)
}}

Return JSON only, no other text."""
