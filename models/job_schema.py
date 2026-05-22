"""
Pydantic schemas for job data validation
"""
from pydantic import BaseModel, Field, field_validator
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


class JobData(JobExtraction):
    """Complete job data ready for Google Sheets"""
    id: Optional[int] = Field(None, description="Job ID (auto-generated)")
    status: str = Field(default="Active", description="Job status")
    priority: str = Field(default="Medium", description="Job priority level")
    exclusive: bool = Field(default=False, description="Is this an exclusive opportunity?")

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
        Maps to columns B-O (ID in column A is not filled by this tool)
        """
        return [
            '',                              # A列: ID (empty - not filled by this tool)
            self.company,                    # B列: Company
            self.title,                      # C列: Title
            self.industry,                   # D列: Industry
            self.location,                   # E列: Location
            self.salary,                     # F列: Salary
            self.visa_sponsorship,           # G列: VisaSponsorship
            self.deadline,                   # H列: Deadline
            ', '.join(self.preferred_major) if self.preferred_major else '',  # I列: PreferredMajors
            self.target_year,                # J列: TargetYear
            self.degree,                     # K列: Degree
            self.type,                       # L列: Type
            self.description,                # M列: Description
            self.apply_link,                 # N列: ApplicationUrl
            self.status,                     # O列: Status
        ]
