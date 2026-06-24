"""
Pydantic schemas for job data validation
Enhanced with precise degree/visa parsing
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
import re


class JobExtraction(BaseModel):
    """Raw job data extracted by AI from web page"""
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    location: str = Field(..., description="Job location (city, country)")
    type: str = Field(..., description="Job type (Full-time/Internship/Part-time/Contract)")
    industry: str = Field(..., description="Industry sector")
    apply_link: str = Field(..., description="Application URL")
    deadline: str = Field(..., description="Application deadline (YYYY-MM-DD or text)")
    opened: Optional[str] = Field("", description="Posted date (YYYY-MM-DD)")

    # ============================================
    # ENHANCED: Precise degree parsing
    # ============================================
    degree_min: str = Field(default="any", description="Minimum REQUIRED degree: bachelor, master, phd, any")
    degree_preferred: str = Field(default="", description="Preferred degree (if different from min)")

    # Backward compatible: map old 'degree' field to degree_min
    degree: Optional[str] = Field(default="any", description="Legacy field - maps to degree_min")

    # ============================================
    # ENHANCED: Precise visa parsing
    # ============================================
    visa_sponsorship: bool = Field(default=False, description="Backward compatibility: true if sponsorship available")
    visa_mentioned: str = Field(default="not_mentioned", description="Visa status: explicit_yes, explicit_no, not_mentioned, case_by_case")
    visa_note: str = Field(default="", description="Brief note explaining visa situation")

    # ============================================
    # NEW: Enhanced visa source tracking
    # ============================================
    visa_source: str = Field(default="unknown", description="Visa info source: jd_explicit/company_history/unknown")
    visa_likelihood: str = Field(default="unknown", description="Visa likelihood: high/medium/low/unknown")

    target_year: str = Field(default="Any", description="Target graduation year")
    salary: Optional[str] = Field("", description="Salary range")
    description: str = Field(default="", description="Job description")

    # ============================================
    # RAW DESCRIPTION FOR VERIFICATION
    # ============================================
    raw_description: str = Field(default="", description="Full job description text for verification")

    preferred_major: Optional[List[str]] = Field(default_factory=list, description="Preferred majors")

    # New fields for smart recommendation
    skills_tags: Optional[List[str]] = Field(default_factory=list, description="Extracted skill tags for matching")
    department: Optional[str] = Field("", description="Department/Team")
    job_level: Optional[str] = Field("Not specified", description="Job level: Entry/Mid/Senior/Lead/Principal")
    work_mode: Optional[str] = Field("Not specified", description="Work mode: Remote/Hybrid/Onsite")
    target_audience: Optional[str] = Field("Not specified", description="Target audience: New Grad/Intern/Experienced")
    salary_range_normalized: Optional[str] = Field("", description="Normalized salary range for filtering")

    # ============================================
    # NEW: Requirements and Perks
    # ============================================
    requirements: str = Field(default="", description="Job requirements (experience, skills, qualifications) - max 500 chars")
    perks: Optional[List[str]] = Field(default_factory=list, description="Benefits and perks (insurance, vacation, bonus, etc.)")

    @field_validator('visa_mentioned')
    @classmethod
    def normalize_visa_mentioned(cls, v: str) -> str:
        """Normalize visa_mentioned values"""
        v_clean = v.lower().strip()

        valid_values = {
            'explicit_yes': 'explicit_yes',
            'yes': 'explicit_yes',
            'explicit_no': 'explicit_no',
            'no': 'explicit_no',
            'not_mentioned': 'not_mentioned',
            'not mentioned': 'not_mentioned',
            'case_by_case': 'case_by_case',
            'case by case': 'case_by_case',
        }

        for key, value in valid_values.items():
            if key in v_clean:
                return value

        # Try substring matching for flexibility
        if 'sponsor' in v_clean and 'not' not in v_clean and 'cannot' not in v_clean:
            return 'explicit_yes'
        elif 'cannot sponsor' in v_clean or 'must have' in v_clean:
            return 'explicit_no'
        elif 'case' in v_clean:
            return 'case_by_case'
        else:
            return 'not_mentioned'

    @field_validator('degree_min')
    @classmethod
    def normalize_degree_min(cls, v: str) -> str:
        """Normalize degree_min values"""
        v_lower = v.lower().strip()

        # Handle legacy 'degree' field values
        degree_mapping = {
            'phd': 'phd',
            'doctor': 'phd',
            'master': 'master',
            'mba': 'master',
            'bachelor': 'bachelor',
            'undergraduate': 'bachelor',
            'any': 'any',
            'prefer': 'any',  # "preferred" means any is acceptable minimum
            'preferred': 'any',
        }

        for key, value in degree_mapping.items():
            if key in v_lower:
                return value

        return 'any'

    @field_validator('degree_preferred')
    @classmethod
    def normalize_degree_preferred(cls, v: str) -> str:
        """Normalize degree_preferred values"""
        if not v or v.strip() == "":
            return ""

        v_lower = v.lower().strip()

        degree_mapping = {
            'phd': 'phd',
            'doctor': 'phd',
            'master': 'master',
            'mba': 'master',
            'bachelor': 'bachelor',
            'undergraduate': 'bachelor',
        }

        for key, value in degree_mapping.items():
            if key in v_lower:
                return value

        return v  # Return as-is if not recognized

    # Legacy field validator - maps old 'degree' to appropriate field
    @field_validator('degree', mode='before')
    @classmethod
    def map_legacy_degree(cls, v: str) -> str:
        """Map legacy degree field to degree_min"""
        # This validator runs before field assignment
        # We'll handle the mapping in the model logic
        return v or "any"

    @field_validator('industry')
    @classmethod
    def normalize_industry(cls, v: str) -> str:
        """Normalize industry values to English"""
        industry_mapping = {
            # Existing categories
            'consulting': 'Consulting',
            'investment banking': 'Investment Banking',
            'private equity': 'Private Equity',
            'venture capital': 'Venture Capital',
            'technology': 'Technology',
            'fintech': 'Fintech',
            'fashion': 'FMCG',
            'retail': 'FMCG',
            'consumer goods': 'FMCG',

            # New categories
            # Software / Tech roles
            'software development': 'SDE',
            'software engineer': 'SDE',
            'sde': 'SDE',
            'backend': 'SDE',
            'frontend': 'SDE',
            'full stack': 'SDE',
            'full-stack': 'SDE',
            'web development': 'SDE',
            'app development': 'SDE',

            # Data roles
            'data science': 'Data',
            'data scientist': 'Data',
            'data analyst': 'Data',
            'data engineering': 'Data',
            'analytics': 'Data',
            'machine learning': 'Data',
            'artificial intelligence': 'Data',
            'ai': 'Data',
            'ml': 'Data',

            # Engineering (non-software)
            'engineering': 'Engineering',
            'mechanical engineering': 'Engineering',
            'electrical engineering': 'Engineering',
            'civil engineering': 'Engineering',
            'chemical engineering': 'Engineering',
            'biomedical engineering': 'Engineering',
            'hardware engineering': 'Engineering',

            # Quant / Finance
            'quantitative': 'Quant',
            'quant': 'Quant',
            'quantitative finance': 'Quant',
            'quantitative research': 'Quant',
            'trading': 'Quant',
            'algorithmic trading': 'Quant',

            # Risk
            'risk management': 'Risk',
            'risk analyst': 'Risk',
            'compliance': 'Risk',
            'credit risk': 'Risk',
            'market risk': 'Risk',

            # Finance (general)
            'finance': 'Finance',
            'financial analyst': 'Finance',
            'corporate finance': 'Finance',
            'financial planning': 'Finance',

            # Marketing
            'marketing': 'Marketing',
            'digital marketing': 'Marketing',
            'brand': 'Marketing',
            'social media': 'Marketing',
            'content marketing': 'Marketing',
            'growth marketing': 'Marketing',

            # Design
            'design': 'Design',
            'ux designer': 'Design',
            'ui designer': 'Design',
            'ux/ui': 'Design',
            'product design': 'Design',
            'graphic design': 'Design',
            'visual design': 'Design',
            'user experience': 'Design',

            # Product Management
            'product management': 'Product Management',
            'product manager': 'Product Management',
            'pm': 'Product Management',
            'product owner': 'Product Management',
            'agile': 'Product Management',
            'scrum': 'Product Management',

            # Operations
            'operation': 'Operation',
            'operations': 'Operation',
            'supply chain': 'Operation',
            'logistics': 'Operation',
            'business operations': 'Operation',

            # Law / Legal
            'legal': 'Law',
            'law': 'Law',
            'paralegal': 'Law',
            'compliance': 'Law',
            'contract': 'Law',

            # Public Relations
            'public relation': 'Public Relations',
            'pr': 'Public Relations',
            'communication': 'Public Relations',
            'communications': 'Public Relations',
            'external affairs': 'Public Relations',
            'media relation': 'Public Relations',
        }
        v_lower = v.lower().strip()
        for key, value in industry_mapping.items():
            if key in v_lower:
                return value
        return 'Other'

    @field_validator('type')
    @classmethod
    def normalize_job_type(cls, v: str) -> str:
        """Normalize job type values"""
        v_lower = v.lower().strip()
        if 'full' in v_lower or 'permanent' in v_lower:
            return 'Full-time'
        elif 'intern' in v_lower:
            return 'Internship'
        elif 'part' in v_lower:
            return 'Part-time'
        elif 'contract' in v_lower:
            return 'Contract'
        else:
            return 'Full-time'  # Default

    @field_validator('job_level')
    @classmethod
    def normalize_job_level(cls, v: str) -> str:
        """Normalize job level values"""
        if not v or v.lower() == 'not specified':
            return 'Not specified'

        v_lower = v.lower().strip()
        if any(word in v_lower for word in ['entry', 'junior', 'associate', 'grad']):
            return 'Entry'
        elif any(word in v_lower for word in ['mid', 'intermediate']):
            return 'Mid'
        elif any(word in v_lower for word in ['senior', 'sr.', 'sr ']):
            return 'Senior'
        elif any(word in v_lower for word in ['lead', 'principal', 'staff']):
            return 'Lead'
        elif any(word in v_lower for word in ['manager', 'head', 'director', 'vp']):
            return 'Manager'
        else:
            return 'Not specified'

    @field_validator('work_mode')
    @classmethod
    def normalize_work_mode(cls, v: str) -> str:
        """Normalize work mode values"""
        if not v or v.lower() == 'not specified':
            return 'Not specified'

        v_lower = v.lower().strip()
        if 'remote' in v_lower:
            return 'Remote'
        elif 'hybrid' in v_lower:
            return 'Hybrid'
        elif 'onsite' in v_lower or 'on-site' in v_lower or 'office' in v_lower:
            return 'Onsite'
        else:
            return 'Not specified'

    @field_validator('target_audience')
    @classmethod
    def normalize_target_audience(cls, v: str) -> str:
        """Normalize target audience values"""
        if not v or v.lower() == 'not specified':
            return 'Not specified'

        v_lower = v.lower().strip()
        if any(word in v_lower for word in ['intern', 'student', 'placement']):
            return 'Intern'
        elif any(word in v_lower for word in ['new grad', 'recent grad', 'entry', 'graduate']):
            return 'New Grad'
        elif any(word in v_lower for word in ['experienced', 'professional', 'mid', 'senior']):
            return 'Experienced'
        else:
            return 'Not specified'


class CompanyInfo(BaseModel):
    """Company information (from database or AI inference)"""
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=False
    )

    domain: Optional[str] = Field("", description="Company domain/website")
    size_category: Optional[str] = Field("Mid", description="Company size: Startup/Small/Mid/Large/Enterprise")
    employee_count: Optional[str] = Field("", description="Employee count range")
    funding_stage: Optional[str] = Field("Private", description="Funding stage: Public/Private/Series A/B/C/etc")
    hq_location: Optional[str] = Field("", description="Headquarters location")
    year_founded: Optional[str] = Field("", description="Year company was founded")
    tier: Optional[str] = Field("Unknown", description="Company tier: Tier 1/2/3")
    company_website: Optional[str] = Field("", description="Company website URL")

    # Metadata about data source
    source: Optional[str] = Field("unknown", description="Data source: database/ai_inferred/ai_low_confidence/unknown")
    confidence: Optional[int] = Field(0, description="Confidence score 0-100")


class JobData(JobExtraction):
    """Complete job data ready for Google Sheets"""
    id: Optional[int] = Field(None, description="Job ID (auto-generated)")
    status: str = Field(default="Active", description="Job status")
    priority: str = Field(default="Medium", description="Job priority level")
    exclusive: bool = Field(default=False, description="Is this an exclusive opportunity?")

    # Company information (enriched from database/AI)
    company_info: Optional[CompanyInfo] = Field(default_factory=CompanyInfo, description="Enriched company information")

    # Pre-computed scores (calculated during scraping)
    priority_score: Optional[float] = Field(None, description="Priority score (0-100) for sorting")
    urgency_score: Optional[float] = Field(None, description="Urgency score (0-100) based on deadline")
    freshness_score: Optional[float] = Field(None, description="Freshness score (0-100) based on posted date")
    quality_score: Optional[float] = Field(None, description="Quality score (0-100) based on data completeness")
    matchability_score: Optional[float] = Field(None, description="Matchability score (0-100) for filtering")
    scores_calculated_at: Optional[str] = Field(None, description="Timestamp when scores were calculated")

    @field_validator('deadline')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate and normalize date format"""
        if not v or v.lower() in ['asap', 'immediately', 'rolling', 'ongoing', '']:
            return 'Rolling'
        # Try to parse common date formats
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}\s+\w+\s+\d{4}',  # D MMMM YYYY
        ]
        for pattern in date_patterns:
            if re.search(pattern, v):
                return v
        return v  # Return as-is if pattern doesn't match

    def to_google_sheets_row(self) -> list:
        """
        Convert to Google Sheets row format
        Enhanced with precise parsing fields
        """
        company_info = self.company_info or CompanyInfo()

        # Map legacy degree field to new structure
        degree_display = self.degree_min
        if self.degree_preferred:
            degree_display = f"{self.degree_min} (prefer {self.degree_preferred})"

        # Build visa display
        visa_display = "Yes" if self.visa_sponsorship else "No"
        if self.visa_mentioned == "not_mentioned":
            visa_display = "Not mentioned"
        elif self.visa_mentioned == "case_by_case":
            visa_display = "Case by case"

        # Format perks as comma-separated string
        perks_display = ', '.join(self.perks) if self.perks else ''

        return [
            '',                              # A列: ID (empty - not filled by this tool)
            self.company,                    # B列: Company
            self.title,                      # C列: Title
            self.industry,                   # D列: Industry
            self.location,                   # E列: Location
            self.salary,                     # F列: Salary (original)
            visa_display,                    # G列: VisaSponsorship (enhanced display)
            self.deadline,                   # H列: Deadline
            ', '.join(self.preferred_major) if self.preferred_major else '',  # I列: PreferredMajors
            self.target_year,                # J列: TargetYear
            degree_display,                  # K列: Degree (enhanced display)
            self.type,                       # L列: Type
            self.description,                # M列: Description (clean)
            self.apply_link,                 # N列: ApplicationUrl
            self.status,                     # O列: Status
            # Smart recommendation fields
            ', '.join(self.skills_tags) if self.skills_tags else '',  # P列: Skills
            self.department,                 # Q列: Department
            self.job_level,                  # R列: Job Level
            self.work_mode,                  # S列: Work Mode
            self.target_audience,            # T列: Target Audience
            self.salary_range_normalized,    # U列: Salary Range (normalized)
            # Company info fields (V-AC)
            company_info.size_category,      # V列: Company Size
            company_info.employee_count,     # W列: Employee Count
            company_info.funding_stage,      # X列: Funding Stage
            company_info.hq_location,        # Y列: Company HQ
            company_info.year_founded,       # Z列: Year Founded
            company_info.tier,               # AA列: Company Tier
            company_info.company_website,    # AB列: Company Website
            company_info.domain,             # AC列: Company Domain
            # ============================================
            # NEW: Enhanced parsing fields
            # ============================================
            self.degree_min,                 # AD列: Degree Min (new)
            self.degree_preferred,           # AE列: Degree Preferred (new)
            self.visa_mentioned,             # AF列: Visa Mentioned (new)
            self.visa_note,                  # AG列: Visa Note (new)
            self.raw_description[:1000] if self.raw_description else '',  # AH列: Raw Description (new, truncated for Sheets)
            # ============================================
            # Pre-computed scores (new columns)
            # ============================================
            str(self.priority_score) if self.priority_score is not None else '',  # AI列: Priority Score
            str(self.urgency_score) if self.urgency_score is not None else '',    # AJ列: Urgency Score
            str(self.freshness_score) if self.freshness_score is not None else '',  # AK列: Freshness Score
            str(self.quality_score) if self.quality_score is not None else '',    # AL列: Quality Score
            str(self.matchability_score) if self.matchability_score is not None else '',  # AM列: Matchability Score
            self.scores_calculated_at or '',  # AN列: Scores Calculated At
            # ============================================
            # NEW: Enhanced visa tracking + Requirements + Perks
            # ============================================
            self.requirements,               # AO列: Requirements (new)
            perks_display,                   # AP列: Perks (new)
            self.visa_source,                # AQ列: Visa Source (new)
            self.visa_likelihood,            # AR列: Visa Likelihood (new)
        ]
