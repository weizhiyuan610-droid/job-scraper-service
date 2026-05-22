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
  "skills_tags": ["skill1", "skill2", "skill3"] (array of technical/functional skills extracted from requirements. Extract 5-10 key skills. Include: programming languages, tools, frameworks, soft skills. Empty array if not found),
  "department": "Department or team name (e.g., 'Engineering', 'Data Science', 'Product', 'Marketing', 'Sales', 'Finance'). Leave empty if not specified",
  "job_level": "Select one based on title and requirements: Entry, Mid, Senior, Lead, Manager, Not specified",
  "work_mode": "Select one based on location info: Remote, Hybrid, Onsite, Not specified",
  "target_audience": "Select one based on requirements: Intern, New Grad, Experienced, Not specified",
  "salary_range_normalized": "Normalized salary range in format 'minK-maxK' (e.g., '80K-120K'). Leave empty if salary not mentioned or cannot be parsed",
  "status": "Active (assume Active unless page explicitly says closed/expired/filled)"
}}

EXTRACTION RULES:
1. Company name: Extract from logo, page title, breadcrumb, or meta tags
2. Job title: Extract from H1 tag or main heading
3. Location: Include city, state/province, and country. Mark "Remote" if applicable
4. Industry: Judge based on company type and job description. Choose the most appropriate category:

   INDUSTRY CLASSIFICATION GUIDE:

   - Consulting: Management consulting, strategy consulting (McKinsey, BCG, Bain, Deloitte Consulting)
   - Investment Banking: IB, M&A, capital markets, investment banking division (Goldman Sachs IB, JPMorgan IB)
   - Private Equity: PE, investment firms, buyout funds (Blackstone, KKR, Carlyle)
   - Venture Capital: VC, startup investing, seed funding (Sequoia, Andreessen Horowitz)
   - Technology: General tech companies, tech roles not specifically SDE/Data (Apple, Microsoft, general tech)
   - Fintech: Financial technology, payment systems, crypto (Stripe, Square, Coinbase)
   - FMCG: Consumer goods, retail, fashion, CPG (P&G, Unilever, Nike, L'Oréal)

   - SDE: Software Development Engineer, software engineer, backend, frontend, full-stack, web development, mobile development
     Keywords: software engineer, SDE, backend, frontend, full-stack, full stack, web developer, mobile developer, iOS, Android, DevOps

   - Data: Data science, data analyst, data engineering, analytics, machine learning, AI
     Keywords: data scientist, data analyst, data engineer, analytics, machine learning, artificial intelligence, AI engineer, ML engineer

   - Engineering: Mechanical, electrical, civil, chemical, biomedical, hardware engineering (non-software)
     Keywords: mechanical engineer, electrical engineer, civil engineer, chemical engineer, hardware engineer, manufacturing engineer

   - Quant: Quantitative finance, quantitative research, trading, algorithmic trading
     Keywords: quantitative analyst, quant, quantitative researcher, trading, algorithmic trading, derivatives pricing

   - Risk: Risk management, risk analyst, compliance, credit risk, market risk
     Keywords: risk manager, risk analyst, compliance, credit risk, market risk, operational risk, risk management

   - Finance: Financial analyst, corporate finance, financial planning (not investment banking)
     Keywords: financial analyst, finance manager, corporate finance, FP&A, financial planning, treasury

   - Marketing: Digital marketing, brand, social media, content marketing, growth marketing
     Keywords: marketing manager, digital marketing, brand manager, social media manager, growth marketing, content marketing

   - Design: UX/UI, product design, graphic design, visual design
     Keywords: UX designer, UI designer, product designer, graphic designer, visual designer, interaction designer

   - Product Management: Product manager, PM, product owner, agile/scrum
     Keywords: product manager, PM, product owner, technical product manager, agile, scrum, product strategy

   - Operation: Operations, supply chain, logistics, business operations
     Keywords: operations manager, supply chain, logistics, business operations, manufacturing operations

   - Law: Legal, paralegal, compliance, contracts
     Keywords: lawyer, attorney, legal counsel, paralegal, legal analyst, contract manager

   - Public Relations: PR, communications, external affairs, media relations
     Keywords: PR manager, public relations, communications manager, external affairs, media relations, corporate communications

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

12. Skills Tags (IMPORTANT for recommendation system): Extract 5-10 key skills from requirements:
   Programming Languages: Python, Java, JavaScript, C++, Go, Rust, Swift, Kotlin, TypeScript
   Web/Frontend: React, Vue, Angular, HTML, CSS, Next.js, Tailwind
   Backend: Node.js, Django, Flask, FastAPI, Spring Boot, Express
   Data/AI: SQL, PostgreSQL, MongoDB, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy
   Cloud: AWS, GCP, Azure, Docker, Kubernetes, Terraform
   Tools: Git, Jenkins, CI/CD, Agile, Scrum, Jira
   Soft Skills: Communication, Leadership, Problem-solving, Teamwork, Analytical

13. Department: Look for team/department mentions (Engineering, Data Science, Product, Marketing, Sales, Finance, Operations, Design, Legal, HR)

14. Job Level Classification:
   - Entry: "Entry level", "Junior", "Associate", "New Grad", "0-2 years"
   - Mid: "Mid-level", "3-5 years", "Intermediate"
   - Senior: "Senior", "6+ years", "Sr."
   - Lead: "Lead", "Principal", "Staff", "Tech Lead"
   - Manager: "Manager", "Director", "VP", "Head of"
   - Not specified: If no level mentioned

15. Work Mode Classification:
   - Remote: explicitly mentions "Remote", "Work from home", "WFO"
   - Hybrid: mentions "Hybrid", "Flexible", "2-3 days in office"
   - Onsite: mentions "On-site", "Office based", specific location only
   - Not specified: If no work mode mentioned

16. Target Audience Classification:
   - Intern: mentions "Internship", "Intern", "Student", "Placement"
   - New Grad: mentions "New Grad", "Recent Graduate", "Entry level", "0-2 years"
   - Experienced: mentions "3+ years", "Experienced", "Professional"

17. Salary Normalization: Convert salary to format "minK-maxK":
   - "$80,000 - $120,000" → "80K-120K"
   - "£50k-£70k" → "50K-70K"
   - "Competitive" → ""
   - Leave empty if cannot parse

18. Status: Set to "Active" by default. Only set to "Inactive" if page explicitly says "closed", "expired", "filled", "no longer accepting applications"
19. If a field cannot be determined, use null or empty string/default value
20. Description: Clean up the text by removing company name prefixes and redundant phrases like "is looking for", "is hiring", "we are seeking". Focus on actual job responsibilities and requirements.

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
  "skills_tags": ["Python", "SQL", "AWS"] (extract 5-10 key skills),
  "department": "department name",
  "job_level": "Entry/Mid/Senior/Lead/Manager/Not specified",
  "work_mode": "Remote/Hybrid/Onsite/Not specified",
  "target_audience": "Intern/New Grad/Experienced/Not specified",
  "salary_range_normalized": "80K-120K" or empty,
  "status": "Active" (default Active, only Inactive if closed/expired/filled)
}}

INDUSTRY GUIDE:
- SDE: software engineer, backend, frontend, full-stack, web/mobile dev
- Data: data scientist, data analyst, ML, AI, analytics
- Engineering: mechanical, electrical, civil, chemical, hardware
- Quant: quantitative finance, trading, algorithms
- Risk: risk management, compliance, credit/market risk
- Finance: financial analyst, corporate finance, FP&A
- Marketing: digital marketing, brand, social media, growth
- Design: UX/UI, product design, graphic design
- Product Management: product manager, PM, product owner
- Operation: operations, supply chain, logistics
- Law: legal, paralegal, contracts
- Public Relations: PR, communications, media relations

SKILL EXAMPLES:
- Languages: Python, Java, JavaScript, C++, Go, TypeScript, SQL
- Frameworks: React, Vue, Django, Flask, Spring, TensorFlow
- Cloud: AWS, GCP, Azure, Docker, Kubernetes
- Tools: Git, CI/CD, Agile, Scrum

Return JSON only, no other text."""
