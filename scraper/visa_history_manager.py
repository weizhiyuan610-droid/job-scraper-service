"""
Company Visa History Manager

Manages historical visa sponsorship data for companies.
This data is used to improve visa sponsorship predictions in job scoring.
"""
import os
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class CompanyVisaHistory:
    """
    Represents historical visa sponsorship data for a company
    """

    def __init__(
        self,
        company_name: str,
        visa_likelihood: str = 'unknown',
        visa_generosity: str = '',
        company_tier: str = 'Unknown',
        industry: str = '',
        core_visa_departments: List[str] = None,
        company_name_variants: List[str] = None,
        historical_notes: str = '',
        visa_reliability: str = 'proven',
        fulltime_available: bool = True,
        internship_available: bool = True,
    ):
        self.company_name = company_name
        self.visa_likelihood = visa_likelihood  # 'high', 'medium', 'low', 'unknown'
        self.visa_generosity = visa_generosity  # e.g., "极其大方", "case by case"
        self.company_tier = company_tier  # 'Tier 1', 'Tier 2', 'Tier 3', 'Unknown'
        self.industry = industry
        self.core_visa_departments = core_visa_departments or []
        self.company_name_variants = company_name_variants or []
        self.historical_notes = historical_notes
        self.visa_reliability = visa_reliability  # 'proven', 'reported', 'speculated'
        self.fulltime_available = fulltime_available
        self.internship_available = internship_available

    def to_dict(self) -> Dict:
        """Convert to dictionary for database insertion"""
        return {
            'company_name': self.company_name,
            'company_name_variants': self.company_name_variants,
            'industry': self.industry,
            'company_tier': self.company_tier,
            'visa_likelihood': self.visa_likelihood,
            'visa_generosity': self.visa_generosity,
            'visa_reliability': self.visa_reliability,
            'core_visa_departments': self.core_visa_departments,
            'fulltime_positions_available': self.fulltime_available,
            'internship_positions_available': self.internship_available,
            'historical_notes': self.historical_notes,
            'data_source': 'manual',
            'last_verified_date': datetime.now().date().isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CompanyVisaHistory':
        """Create from dictionary (e.g., from database or JSON)"""
        return cls(
            company_name=data.get('company_name', ''),
            visa_likelihood=data.get('visa_likelihood', 'unknown'),
            visa_generosity=data.get('visa_generosity', ''),
            company_tier=data.get('company_tier', 'Unknown'),
            industry=data.get('industry', ''),
            core_visa_departments=data.get('core_visa_departments', []),
            company_name_variants=data.get('company_name_variants', []),
            historical_notes=data.get('historical_notes', ''),
            visa_reliability=data.get('visa_reliability', 'proven'),
            fulltime_available=data.get('fulltime_positions_available', True),
            internship_available=data.get('internship_positions_available', True),
        )


class VisaHistoryDatabase:
    """
    In-memory database of company visa history.
    Can be loaded from JSON file or Supabase.
    """

    def __init__(self):
        self.companies: Dict[str, CompanyVisaHistory] = {}
        self._load_initial_data()

    def _load_initial_data(self):
        """Load initial hardcoded data based on Notion research"""
        # This data comes from the user's Notion pages
        initial_companies = [
            # MBB Consulting
            {
                'company_name': 'McKinsey & Company',
                'company_name_variants': ['McKinsey'],
                'industry': 'Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Implementation', 'Digital'],
                'historical_notes': 'Tier 1 consulting firm, known for excellent visa sponsorship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Boston Consulting Group',
                'company_name_variants': ['BCG'],
                'industry': 'Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Digital', 'Technology'],
                'historical_notes': 'Consistently sponsors visas for international candidates.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Bain & Company',
                'company_name_variants': ['Bain'],
                'industry': 'Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Technology'],
                'historical_notes': 'Strong visa sponsorship record for full-time and internship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Big 4
            {
                'company_name': 'PwC',
                'company_name_variants': ['PricewaterhouseCoopers', 'PwC UK'],
                'industry': 'Accounting/Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '很大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Technology', 'Audit', 'Tax'],
                'historical_notes': 'PwC historically very generous with visa sponsorship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Deloitte',
                'company_name_variants': ['Deloitte UK'],
                'industry': 'Accounting/Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '很大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Technology', 'Audit', 'Financial Advisory'],
                'historical_notes': 'Strong visa sponsorship across consulting and technology.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'KPMG',
                'company_name_variants': ['KPMG UK'],
                'industry': 'Accounting/Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '很大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Technology', 'Audit', 'Advisory'],
                'historical_notes': 'Historically generous with visa sponsorship (KPMG).',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'EY',
                'company_name_variants': ['Ernst & Young', 'EY UK'],
                'industry': 'Accounting/Consulting',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '很大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Technology', 'Audit', 'Strategy'],
                'historical_notes': 'Consistent visa sponsorship for consulting and technology.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Strategy Consulting (Tier 2)
            {
                'company_name': 'Oliver Wyman',
                'company_name_variants': ['OW'],
                'industry': 'Consulting',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting', 'Digital'],
                'historical_notes': 'Specialized consulting with good visa sponsorship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'LEK',
                'company_name_variants': ['L.E.K. Consulting'],
                'industry': 'Consulting',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting'],
                'historical_notes': 'Strong visa sponsorship for consulting roles.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Roland Berger',
                'company_name_variants': ['RB'],
                'industry': 'Consulting',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Consulting'],
                'historical_notes': 'European consulting firm with solid visa support.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Investment Banks (Tier 1)
            {
                'company_name': 'Goldman Sachs',
                'company_name_variants': ['GS'],
                'industry': 'Investment Banking',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Investment Banking', 'Securities', 'Technology'],
                'historical_notes': 'Top-tier investment bank with excellent visa history.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'JPMorgan Chase',
                'company_name_variants': ['JPM', 'J.P. Morgan'],
                'industry': 'Investment Banking',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Investment Banking', 'Technology', 'Asset Management'],
                'historical_notes': 'Consistently sponsors visas for banking and technology.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Morgan Stanley',
                'company_name_variants': ['MS'],
                'industry': 'Investment Banking',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Investment Banking', 'Technology', 'Wealth Management'],
                'historical_notes': 'Strong visa sponsorship across all divisions.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Bank of America',
                'company_name_variants': ['BoA', 'BAML'],
                'industry': 'Investment Banking',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Investment Banking', 'Technology', 'Global Markets'],
                'historical_notes': 'Reliable visa sponsorship for international hires.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Citigroup',
                'company_name_variants': ['Citi'],
                'industry': 'Investment Banking',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Investment Banking', 'Technology'],
                'historical_notes': 'Strong visa support for qualified candidates.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Tech Companies (Tier 1)
            {
                'company_name': 'Google',
                'company_name_variants': ['Alphabet'],
                'industry': 'Technology',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Software Engineering', 'Product', 'Data Science', 'Cloud'],
                'historical_notes': 'Most generous company for visa sponsorship globally.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Amazon',
                'company_name_variants': ['AWS'],
                'industry': 'Technology',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Software Engineering', 'AWS', 'Consumer', 'Devices'],
                'historical_notes': 'Consistently sponsors visas for SDE and related roles.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Microsoft',
                'company_name_variants': [],
                'industry': 'Technology',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Software Engineering', 'Cloud', 'AI'],
                'historical_notes': 'Excellent visa sponsorship record for technical roles.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Meta',
                'company_name_variants': ['Facebook'],
                'industry': 'Technology',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '极其大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Software Engineering', 'Product', 'AI'],
                'historical_notes': 'Strong visa sponsorship for engineering and product.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Fintech Companies
            {
                'company_name': 'Revolut',
                'company_name_variants': [],
                'industry': 'Fintech',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Engineering', 'Product', 'Operations'],
                'historical_notes': 'Leading fintech with good visa sponsorship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Monzo',
                'company_name_variants': [],
                'industry': 'Fintech',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Engineering', 'Product'],
                'historical_notes': 'Digital bank with solid visa support.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Wise',
                'company_name_variants': ['TransferWise'],
                'industry': 'Fintech',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Engineering', 'Product'],
                'historical_notes': 'International money transfer, visa-friendly.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            {
                'company_name': 'Stripe',
                'company_name_variants': [],
                'industry': 'Fintech',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Engineering', 'Product'],
                'historical_notes': 'Payments infrastructure, hires international talent.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Other Tier 2 Companies
            {
                'company_name': 'Palantir',
                'company_name_variants': [],
                'industry': 'Technology',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Software Engineering', 'Data Science'],
                'historical_notes': 'Data analytics with good visa sponsorship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Asset Management
            {
                'company_name': 'Blackstone',
                'company_name_variants': [],
                'industry': 'Investment Management',
                'company_tier': 'Tier 1',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Private Equity', 'Real Estate', 'Technology'],
                'historical_notes': 'Alternative investment manager with visa sponsorship.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # Trading Firms
            {
                'company_name': 'Jane Street',
                'company_name_variants': [],
                'industry': 'Trading',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'high',
                'visa_generosity': '大方',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Trading', 'Technology'],
                'historical_notes': 'Proprietary trading, hires international talent.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
            # UK-Specific
            {
                'company_name': 'BBC',
                'company_name_variants': ['British Broadcasting Corporation'],
                'industry': 'Media',
                'company_tier': 'Tier 2',
                'visa_likelihood': 'medium',
                'visa_generosity': 'case by case',
                'visa_reliability': 'proven',
                'core_visa_departments': ['Technology', 'Journalism'],
                'historical_notes': 'UK public broadcaster, varies by role.',
                'fulltime_positions_available': True,
                'internship_positions_available': True,
            },
        ]

        for data in initial_companies:
            company = CompanyVisaHistory.from_dict(data)
            self.add_company(company)

        logger.info(f"Loaded {len(self.companies)} companies with visa history data")

    def add_company(self, company: CompanyVisaHistory):
        """Add or update a company in the database"""
        self.companies[company.company_name.lower()] = company

    def get_company(self, company_name: str) -> Optional[CompanyVisaHistory]:
        """
        Get company visa history by name.
        Supports partial matching and variants.
        """
        # Try exact match first
        company = self.companies.get(company_name.lower())
        if company:
            return company

        # Try matching by variants
        for c in self.companies.values():
            if company_name.lower() in [v.lower() for v in c.company_name_variants]:
                return c
            # Also try matching if company name is a variant
            if c.company_name.lower() in company_name.lower() or company_name.lower() in c.company_name.lower():
                return c

        return None

    def get_visa_likelihood(self, company_name: str) -> str:
        """
        Get visa likelihood for a company.
        Returns: 'high', 'medium', 'low', 'unknown'
        """
        company = self.get_company(company_name)
        return company.visa_likelihood if company else 'unknown'

    def get_visa_score(self, company_name: str, jd_explicit_visa: bool = False) -> float:
        """
        Get visa score (0-20) for job scoring.
        If JD explicitly mentions visa, return max score.
        Otherwise, use historical data.
        """
        if jd_explicit_visa:
            return 20.0

        likelihood = self.get_visa_likelihood(company_name)

        # Map likelihood to score
        scores = {
            'high': 18.0,
            'medium': 12.0,
            'low': 5.0,
            'unknown': 10.0,
        }
        return scores.get(likelihood, 10.0)

    def get_company_tier(self, company_name: str) -> str:
        """Get company tier for job scoring"""
        company = self.get_company(company_name)
        return company.company_tier if company else 'Unknown'

    def list_companies_by_industry(self, industry: str) -> List[CompanyVisaHistory]:
        """List all companies in a specific industry"""
        return [c for c in self.companies.values() if c.industry == industry]

    def list_companies_by_tier(self, tier: str) -> List[CompanyVisaHistory]:
        """List all companies in a specific tier"""
        return [c for c in self.companies.values() if c.company_tier == tier]

    def export_to_json(self, filepath: str):
        """Export database to JSON file"""
        data = [c.to_dict() for c in self.companies.values()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported {len(data)} companies to {filepath}")

    @classmethod
    def import_from_json(cls, filepath: str) -> 'VisaHistoryDatabase':
        """Import database from JSON file"""
        db = cls()
        db.companies = {}  # Clear initial data

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for company_data in data:
            company = CompanyVisaHistory.from_dict(company_data)
            db.add_company(company)

        logger.info(f"Imported {len(db.companies)} companies from {filepath}")
        return db


# Singleton instance for use across the application
_visa_db: Optional[VisaHistoryDatabase] = None


def get_visa_history_db() -> VisaHistoryDatabase:
    """Get the singleton visa history database instance"""
    global _visa_db
    if _visa_db is None:
        _visa_db = VisaHistoryDatabase()
    return _visa_db


def reset_visa_history_db():
    """Reset the singleton instance (useful for testing)"""
    global _visa_db
    _visa_db = None


if __name__ == '__main__':
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)

    db = get_visa_history_db()

    # Test lookups
    test_companies = [
        'McKinsey & Company',
        'McKinsey',
        'BCG',
        'Boston Consulting Group',
        'KPMG',
        'Google',
        'Unknown Company',
    ]

    print("\n=== Visa History Lookup Tests ===")
    for company in test_companies:
        visa_info = db.get_company(company)
        if visa_info:
            print(f"\n{company}:")
            print(f"  Likelihood: {visa_info.visa_likelihood}")
            print(f"  Generosity: {visa_info.visa_generosity}")
            print(f"  Tier: {visa_info.company_tier}")
            print(f"  Score: {db.get_visa_score(company)}")
        else:
            print(f"\n{company}: Not found (score: {db.get_visa_score(company)})")

    # Export to JSON
    db.export_to_json('company_visa_history.json')
    print("\nExported to company_visa_history.json")
