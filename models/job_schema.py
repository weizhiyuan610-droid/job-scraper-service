"""
Pydantic schemas for job data validation
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
    degree: str = Field(..., description="Degree requirement")
    visa_sponsorship: str = Field(..., description="Visa sponsorship availability")
    target_year: str = Field(default="Any", description="Target graduation year")
    salary: Optional[str] = Field("", description="Salary range")
    description: str = Field(default="", description="Job description")
    preferred_major: Optional[List[str]] = Field(default_factory=list, description="Preferred majors")

    # New fields for smart recommendation
    skills_tags: Optional[List[str]] = Field(default_factory=list, description="Extracted skill tags for matching")
    department: Optional[str] = Field("", description="Department/Team")
    job_level: Optional[str] = Field("Not specified", description="Job level: Entry/Mid/Senior/Lead/Principal")
    work_mode: Optional[str] = Field("Not specified", description="Work mode: Remote/Hybrid/Onsite")
    target_audience: Optional[str] = Field("Not specified", description="Target audience: New Grad/Intern/Experienced")
    salary_range_normalized: Optional[str] = Field("", description="Normalized salary range for filtering")

    @field_validator('visa_sponsorship')
    @classmethod
    def normalize_visa_sponsorship(cls, v: str) -> str:
        """Normalize visa sponsorship values"""
        v_clean = v.lower().strip()

        # Exact matches first (handle user-selected values)
        if v_clean in ['yes', 'no', 'case by case', 'not mentioned']:
            return v_clean.capitalize() if v_clean != 'case by case' else 'Case by case'

        # Substring matches (handle AI-extracted variations)
        if any(word in v_clean for word in ['yes', 'available', 'provided', 'supported', 'sponsored']):
            return 'Yes'
        elif any(word in v_clean for word in ['no', 'unavailable']):
            return 'No'
        elif any(word in v_clean for word in ['case', 'consider']):
            return 'Case by case'
        else:
            return 'Not mentioned'

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

    @field_validator('degree')
    @classmethod
    def normalize_degree(cls, v: str) -> str:
        """Normalize degree values"""
        v_lower = v.lower().strip()
        if 'master' in v_lower or 'mba' in v_lower:
            return 'Master'
        elif 'phd' in v_lower or 'doctor' in v_lower:
            return 'PhD'
        elif 'bachelor' in v_lower or 'undergraduate' in v_lower:
            return 'Bachelor'
        elif 'any' in v_lower or 'prefer' in v_lower:
            return 'Any'
        else:
            return 'Preferred'

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
        Updated with smart recommendation fields and company info
        """
        company_info = self.company_info or CompanyInfo()

        return [
            '',                              # A列: ID (empty - not filled by this tool)
            self.company,                    # B列: Company
            self.title,                      # C列: Title
            self.industry,                   # D列: Industry
            self.location,                   # E列: Location
            self.salary,                     # F列: Salary (original)
            self.visa_sponsorship,           # G列: VisaSponsorship
            self.deadline,                   # H列: Deadline
            ', '.join(self.preferred_major) if self.preferred_major else '',  # I列: PreferredMajors
            self.target_year,                # J列: TargetYear
            self.degree,                     # K列: Degree
            self.type,                       # L列: Type
            self.description,                # M列: Description
            self.apply_link,                 # N列: ApplicationUrl
            self.status,                     # O列: Status
            # Smart recommendation fields
            ', '.join(self.skills_tags) if self.skills_tags else '',  # P列: Skills
            self.department,                 # Q列: Department
            self.job_level,                  # R列: Job Level
            self.work_mode,                  # S列: Work Mode
            self.target_audience,            # T列: Target Audience
            self.salary_range_normalized,    # U列: Salary Range (normalized)
            # Company info fields (new columns V-AC)
            company_info.size_category,      # V列: Company Size
            company_info.employee_count,     # W列: Employee Count
            company_info.funding_stage,      # X列: Funding Stage
            company_info.hq_location,        # Y列: Company HQ
            company_info.year_founded,       # Z列: Year Founded
            company_info.tier,               # AA列: Company Tier
            company_info.company_website,    # AB列: Company Website
        ]
