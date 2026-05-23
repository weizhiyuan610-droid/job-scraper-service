"""
Link Validator - Check if job application links are valid
Uses async HTTP requests for efficient checking
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class LinkValidator:
    """Validate job application links"""

    def __init__(self, timeout: int = 10, max_concurrent: int = 5):
        """
        Initialize link validator

        Args:
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent requests
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_concurrent = max_concurrent

    def is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format"""
        if not url or not isinstance(url, str):
            return False

        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return False

        try:
            result = urlparse(url)
            return result.scheme in ('http', 'https') and result.netloc
        except Exception:
            return False

    async def check_single_link(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """
        Check a single link

        Args:
            session: aiohttp session
            url: URL to check

        Returns:
            Dictionary with check results
        """
        if not self.is_valid_url(url):
            return {
                'url': url,
                'valid': False,
                'status': 'INVALID_URL',
                'status_code': None,
                'error': 'Invalid URL format'
            }

        try:
            # Try HEAD request first (faster, doesn't download content)
            async with session.head(url, timeout=self.timeout, allow_redirects=True) as response:
                status_code = response.status

                # Consider 2xx and 3xx as valid
                if 200 <= status_code < 400:
                    return {
                        'url': url,
                        'valid': True,
                        'status': 'OK',
                        'status_code': status_code,
                        'final_url': str(response.url),
                        'error': None
                    }
                elif status_code == 404:
                    return {
                        'url': url,
                        'valid': False,
                        'status': 'NOT_FOUND',
                        'status_code': status_code,
                        'error': 'Page not found (404)'
                    }
                elif status_code >= 400:
                    return {
                        'url': url,
                        'valid': False,
                        'status': 'ERROR',
                        'status_code': status_code,
                        'error': f'HTTP {status_code}'
                    }

        except asyncio.TimeoutError:
            return {
                'url': url,
                'valid': False,
                'status': 'TIMEOUT',
                'status_code': None,
                'error': 'Request timeout'
            }
        except aiohttp.ClientError as e:
            # Some sites don't support HEAD, try GET
            try:
                async with session.get(url, timeout=self.timeout, allow_redirects=True) as response:
                    status_code = response.status
                    if 200 <= status_code < 400:
                        return {
                            'url': url,
                            'valid': True,
                            'status': 'OK',
                            'status_code': status_code,
                            'final_url': str(response.url),
                            'error': None
                        }
                    return {
                        'url': url,
                        'valid': False,
                        'status': 'ERROR',
                        'status_code': status_code,
                        'error': f'HTTP {status_code}'
                    }
            except Exception as e2:
                return {
                    'url': url,
                    'valid': False,
                    'status': 'FAILED',
                    'status_code': None,
                    'error': str(e)[:100]
                }
        except Exception as e:
            return {
                'url': url,
                'valid': False,
                'status': 'FAILED',
                'status_code': None,
                'error': str(e)[:100]
            }

    async def check_links_batch(self, urls: List[str]) -> List[Dict]:
        """
        Check multiple links concurrently

        Args:
            urls: List of URLs to check

        Returns:
            List of check results
        """
        # Filter out invalid URLs
        valid_urls = [(i, url) for i, url in enumerate(urls) if self.is_valid_url(url)]

        if not valid_urls:
            return [{'url': url, 'valid': False, 'status': 'INVALID_URL', 'error': 'Invalid URL'} for url in urls]

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_with_semaphore(session, index, url):
            async with semaphore:
                result = await self.check_single_link(session, url)
                result['index'] = index
                return result

        # Create HTTP session
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [check_with_semaphore(session, i, url) for i, url in valid_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        final_results = []
        for r in results:
            if isinstance(r, Exception):
                final_results.append({
                    'url': 'unknown',
                    'valid': False,
                    'status': 'ERROR',
                    'error': str(r)
                })
            else:
                final_results.append(r)

        return final_results

    def check_links_sync(self, urls: List[str]) -> List[Dict]:
        """
        Synchronous wrapper for async link checking

        Args:
            urls: List of URLs to check

        Returns:
            List of check results
        """
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(self.check_links_batch(urls))
            finally:
                loop.close()
            return results
        except Exception as e:
            logger.error(f"Error checking links: {e}")
            return [{
                'url': url,
                'valid': False,
                'status': 'ERROR',
                'error': f'Validation error: {str(e)}'
            } for url in urls]

    def validate_jobs_from_sheet(self, jobs: List[Dict]) -> Dict:
        """
        Validate links from job data

        Args:
            jobs: List of job dictionaries with 'apply_link' field

        Returns:
            Dictionary with validation summary and results
        """
        # Extract URLs with job info
        url_jobs = []
        for i, job in enumerate(jobs):
            url = job.get('apply_link', '') or job.get('ApplicationUrl', '')
            if url:
                url_jobs.append({
                    'index': i,
                    'url': url,
                    'company': job.get('company', '') or job.get('Company', ''),
                    'title': job.get('title', '') or job.get('Title', ''),
                })

        if not url_jobs:
            return {
                'total': 0,
                'valid': 0,
                'invalid': 0,
                'results': []
            }

        urls = [uj['url'] for uj in url_jobs]

        # Check all links
        check_results = self.check_links_sync(urls)

        # Combine results with job info
        combined_results = []
        for check_result, url_job in zip(check_results, url_jobs):
            combined_results.append({
                **check_result,
                'company': url_job['company'],
                'title': url_job['title'],
                'row': url_job['index'] + 2  # +2 because row 1 is header
            })

        # Calculate summary
        valid_count = sum(1 for r in combined_results if r['valid'])
        invalid_count = len(combined_results) - valid_count

        # Categorize issues
        not_found = sum(1 for r in combined_results if r['status'] == 'NOT_FOUND')
        timeout = sum(1 for r in combined_results if r['status'] == 'TIMEOUT')
        failed = sum(1 for r in combined_results if r['status'] == 'FAILED')
        invalid_url = sum(1 for r in combined_results if r['status'] == 'INVALID_URL')

        return {
            'total': len(combined_results),
            'valid': valid_count,
            'invalid': invalid_count,
            'breakdown': {
                'not_found': not_found,
                'timeout': timeout,
                'failed': failed,
                'invalid_url': invalid_url
            },
            'results': combined_results
        }


def validate_links_sync(jobs: List[Dict], timeout: int = 10) -> Dict:
    """
    Convenience function to validate job links

    Args:
        jobs: List of job dictionaries
        timeout: Request timeout in seconds

    Returns:
        Validation summary and results
    """
    validator = LinkValidator(timeout=timeout)
    return validator.validate_jobs_from_sheet(jobs)
