"""
Pydantic schemas for job data validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
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
        v_lower = v.lower().strip()
        if any(word in v_lower for word in ['yes', 'available', 'provided', 'supported', 'sponsored']):
            return 'Yes'
        elif any(word in v_lower for word in ['no', 'not', 'unavailable', 'not provided']):
            return 'No'
        elif any(word in v_lower for word in ['case', 'case by case', 'case-by-case', 'consider']):
            return 'Case by case'
        else:
            return 'Not mentioned'

    @field_validator('industry')
    @classmethod
    def normalize_industry(cls, v: str) -> str:
        """Normalize industry values to English"""
        industry_mapping = {
            'consulting': 'Consulting',
            'investment banking': 'Investment Banking',
            'private equity': 'Private Equity',
            'venture capital': 'Venture Capital',
            'technology': 'Technology',
            'fintech': 'Fintech',
            'fashion': 'FMCG',
            'retail': 'FMCG',
            'consumer goods': 'FMCG',
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
