"""
Visa Sponsorship Enhancement
Uses company visa history database to enhance visa information when JD is not explicit
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class VisaEnhancer:
    """
    Enhances visa sponsorship information using company history database

    Logic:
    1. If JD explicitly mentions visa → use JD information
    2. If JD doesn't mention visa AND company is in database → use historical data
    3. If JD doesn't mention visa AND company not in database → mark as unknown
    """

    def __init__(self, visa_history_db=None):
        """
        Initialize VisaEnhancer

        Args:
            visa_history_db: VisaHistoryDB instance (lazy loaded if not provided)
        """
        self._visa_db = visa_history_db

    @property
    def visa_db(self):
        """Lazy load visa history database"""
        if self._visa_db is None:
            try:
                from scraper.visa_history_manager import get_visa_history_db
                self._visa_db = get_visa_history_db()
                logger.debug("VisaEnhancer: Lazy loaded visa_history_db")
            except ImportError:
                logger.warning("VisaEnhancer: Could not import visa_history_manager")
                self._visa_db = False  # Mark as unavailable
        return self._visa_db if self._visa_db is not False else None

    def enhance_visa_info(self, job_data: Dict) -> Dict:
        """
        Enhance visa information using company history database

        Args:
            job_data: Job data dictionary from AI extraction

        Returns:
            Enhanced job data with updated visa_source and visa_likelihood
        """
        visa_mentioned = job_data.get('visa_mentioned', 'not_mentioned').lower()
        company_name = job_data.get('company', '')

        # Initialize new fields with defaults
        job_data['visa_source'] = 'unknown'
        job_data['visa_likelihood'] = 'unknown'

        # Case 1: JD explicitly mentions visa sponsorship
        if visa_mentioned in ['explicit_yes', 'explicit_no', 'case_by_case']:
            job_data['visa_source'] = 'jd_explicit'

            # Set likelihood based on JD mention
            if visa_mentioned == 'explicit_yes':
                job_data['visa_likelihood'] = 'high'
            elif visa_mentioned == 'explicit_no':
                job_data['visa_likelihood'] = 'low'
            elif visa_mentioned == 'case_by_case':
                job_data['visa_likelihood'] = 'medium'

            logger.debug(f"[VisaEnhancer] {company_name}: JD explicit → visa_source={job_data['visa_source']}, likelihood={job_data['visa_likelihood']}")

            # Update visa_note if not set
            if not job_data.get('visa_note'):
                job_data['visa_note'] = self._get_default_visa_note(visa_mentioned)

            return job_data

        # Case 2: JD doesn't mention visa, check company database
        if self.visa_db and company_name:
            company_info = self.visa_db.get_company(company_name)

            if company_info and company_info.visa_likelihood in ['high', 'medium']:
                # Company has visa sponsorship history
                job_data['visa_source'] = 'company_history'
                job_data['visa_likelihood'] = company_info.visa_likelihood

                # Update visa_sponsorship based on likelihood
                if company_info.visa_likelihood == 'high':
                    job_data['visa_sponsorship'] = True
                elif company_info.visa_likelihood == 'medium':
                    job_data['visa_sponsorship'] = True  # Assume positive for medium likelihood

                # Update visa_note with context
                generosity_text = company_info.visa_generosity or 'has sponsored visas'
                job_data['visa_note'] = f"JD未明确提及，但公司历史{generosity_text}（基于历史数据推测）"

                logger.debug(f"[VisaEnhancer] {company_name}: Company history found → visa_source=company_history, likelihood={job_data['visa_likelihood']}, generosity={company_info.visa_generosity}")

                return job_data
            else:
                logger.debug(f"[VisaEnhancer] {company_name}: Company not found in visa database or likelihood unknown")

        # Case 3: No visa information available
        job_data['visa_source'] = 'unknown'
        job_data['visa_likelihood'] = 'unknown'
        job_data['visa_sponsorship'] = False  # Default to False for safety

        if not job_data.get('visa_note'):
            job_data['visa_note'] = 'JD未提及，公司不在签证友好数据库'

        logger.debug(f"[VisaEnhancer] {company_name}: No visa info → visa_source=unknown, likelihood=unknown")

        return job_data

    def _get_default_visa_note(self, visa_mentioned: str) -> str:
        """Get default visa note based on visa_mentioned value"""
        notes = {
            'explicit_yes': 'JD明确说明提供签证担保',
            'explicit_no': 'JD明确说明不提供签证担保',
            'case_by_case': 'JD说明视情况而定提供签证担保',
            'not_mentioned': 'JD未提及签证担保'
        }
        return notes.get(visa_mentioned, '')

    def get_visa_display_info(self, job_data: Dict) -> Dict:
        """
        Get formatted display information for UI

        Args:
            job_data: Job data dictionary

        Returns:
            Dictionary with display-friendly visa information
        """
        visa_source = job_data.get('visa_source', 'unknown')
        visa_likelihood = job_data.get('visa_likelihood', 'unknown')

        # Display mapping
        source_labels = {
            'jd_explicit': 'JD明确说明',
            'company_history': '公司历史数据',
            'unknown': '未知'
        }

        likelihood_labels = {
            'high': '高可能性',
            'medium': '中等可能性',
            'low': '低可能性',
            'unknown': '未知'
        }

        # Get badge color for UI
        badge_colors = {
            'jd_explicit': 'green',
            'company_history': 'blue',
            'unknown': 'gray'
        }

        likelihood_colors = {
            'high': 'green',
            'medium': 'yellow',
            'low': 'red',
            'unknown': 'gray'
        }

        return {
            'visa_source_label': source_labels.get(visa_source, visa_source),
            'visa_likelihood_label': likelihood_labels.get(visa_likelihood, visa_likelihood),
            'source_badge_color': badge_colors.get(visa_source, 'gray'),
            'likelihood_badge_color': likelihood_colors.get(visa_likelihood, 'gray'),
            'show_note': visa_source == 'company_history'  # Show note prominently when using historical data
        }


def enhance_job_visa_info(job_data: Dict, visa_history_db=None) -> Dict:
    """
    Convenience function to enhance visa information

    Args:
        job_data: Job data dictionary
        visa_history_db: Optional VisaHistoryDB instance

    Returns:
        Enhanced job data
    """
    enhancer = VisaEnhancer(visa_history_db=visa_history_db)
    return enhancer.enhance_visa_info(job_data)


if __name__ == '__main__':
    # Test cases
    import logging
    logging.basicConfig(level=logging.DEBUG)

    print("=" * 70)
    print("Visa Enhancement Test")
    print("=" * 70)

    enhancer = VisaEnhancer()

    # Test Case 1: JD explicitly says yes
    test_job_1 = {
        'company': 'McKinsey & Company',
        'title': 'Consulting Graduate',
        'visa_mentioned': 'explicit_yes',
        'visa_sponsorship': True
    }
    print("\n[Test 1] JD Explicit Yes:")
    result = enhancer.enhance_visa_info(test_job_1.copy())
    print(f"  visa_source: {result['visa_source']}")
    print(f"  visa_likelihood: {result['visa_likelihood']}")
    print(f"  visa_note: {result['visa_note']}")

    # Test Case 2: JD doesn't mention, company in database
    test_job_2 = {
        'company': 'BCG',
        'title': 'Consulting Associate',
        'visa_mentioned': 'not_mentioned',
        'visa_sponsorship': False
    }
    print("\n[Test 2] JD Not Mentioned + BCG (in database):")
    result = enhancer.enhance_visa_info(test_job_2.copy())
    print(f"  visa_source: {result['visa_source']}")
    print(f"  visa_likelihood: {result['visa_likelihood']}")
    print(f"  visa_sponsorship: {result['visa_sponsorship']}")
    print(f"  visa_note: {result['visa_note']}")

    # Test Case 3: JD doesn't mention, company not in database
    test_job_3 = {
        'company': 'Unknown Startup Ltd',
        'title': 'Junior Developer',
        'visa_mentioned': 'not_mentioned',
        'visa_sponsorship': False
    }
    print("\n[Test 3] JD Not Mentioned + Unknown Company:")
    result = enhancer.enhance_visa_info(test_job_3.copy())
    print(f"  visa_source: {result['visa_source']}")
    print(f"  visa_likelihood: {result['visa_likelihood']}")
    print(f"  visa_sponsorship: {result['visa_sponsorship']}")
    print(f"  visa_note: {result['visa_note']}")
