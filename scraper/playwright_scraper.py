"""
Playwright-based web scraper with parallel processing support
"""
import asyncio
from playwright.async_api import async_playwright, Browser
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Scrape web pages using Playwright with parallel processing"""

    def __init__(self, headless: bool = True, timeout: int = 60000):
        """
        Initialize scraper

        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds (default: 60000ms = 60s)
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self.browser

    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def scrape_page(self, url: str) -> dict:
        """
        Scrape a single job posting page

        Args:
            url: URL of the job posting

        Returns:
            Dictionary containing:
                - success: bool
                - content: str (page text content)
                - error: str (if failed)
                - metadata: dict (page info)
        """
        if not self.browser:
            await self.init_browser()

        page = await self.browser.new_page()

        try:
            # Set viewport and user agent
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            # Navigate to URL
            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

            # Wait for content to load
            await page.wait_for_timeout(2000)

            # Extract text content - remove navigation, footer, ads etc
            content = await page.evaluate("""() => {
                // Remove unwanted elements
                const selectorsToRemove = [
                    'nav', 'navigation', 'header', 'footer',
                    '.cookie-banner', '.popup', '.modal',
                    '.advertisement', '.sidebar', '.menu'
                ];

                selectorsToRemove.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => el.remove());
                });

                // Get main content
                const mainContent = document.querySelector('main') ||
                                   document.querySelector('[role="main"]') ||
                                   document.querySelector('.job-description') ||
                                   document.querySelector('.job-details') ||
                                   document.body;

                return mainContent ? mainContent.innerText : document.body.innerText;
            }""")

            # Extract metadata
            metadata = await page.evaluate("""() => {
                return {
                    title: document.title,
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                };
            }""")

            logger.info(f"Successfully scraped {url}, content length: {len(content)}")

            return {
                "success": True,
                "content": content,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "success": False,
                "content": "",
                "error": str(e),
                "metadata": {}
            }
        finally:
            await page.close()

    async def scrape_multiple_parallel(self, urls: List[str], max_concurrent: int = 3) -> List[dict]:
        """
        Scrape multiple URLs in parallel with concurrency limit

        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum number of concurrent scraping tasks

        Returns:
            List of scrape results
        """
        if not urls:
            return []

        if not self.browser:
            await self.init_browser()

        logger.info(f"Starting parallel scrape of {len(urls)} URLs (max concurrent: {max_concurrent})")

        async def scrape_with_semaphore(url, semaphore):
            """Scrape with semaphore to limit concurrency"""
            async with semaphore:
                result = await self.scrape_page(url)
                # Small delay between completions to be respectful
                await asyncio.sleep(0.5)
                return result

        # Create semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(max_concurrent)

        # Create all scraping tasks
        tasks = [scrape_with_semaphore(url, semaphore) for url in urls]

        # Execute all tasks in parallel and wait for completion
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results - convert exceptions to error dicts
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping {urls[i]}: {str(result)}")
                processed_results.append({
                    "success": False,
                    "content": "",
                    "error": str(result),
                    "metadata": {}
                })
            else:
                processed_results.append(result)

        successful = sum(1 for r in processed_results if r.get("success"))
        logger.info(f"Parallel scrape complete: {successful}/{len(urls)} successful")

        return processed_results


def scrape_page_sync(url: str, headless: bool = True) -> dict:
    """
    Synchronous wrapper for scrape_page

    Args:
        url: URL to scrape
        headless: Run in headless mode

    Returns:
        Scrape result dictionary
    """
    async def _scrape():
        scraper = PlaywrightScraper(headless=headless)
        try:
            result = await scraper.scrape_page(url)
            return result
        finally:
            await scraper.close_browser()

    return asyncio.run(_scrape())


def scrape_multiple_sync(urls: List[str], headless: bool = True, max_concurrent: int = 3) -> List[dict]:
    """
    Synchronous wrapper for scrape_multiple_parallel

    Args:
        urls: List of URLs to scrape
        headless: Run in headless mode
        max_concurrent: Maximum concurrent scraping tasks

    Returns:
        List of scrape results
    """
    async def _scrape():
        scraper = PlaywrightScraper(headless=headless)
        try:
            results = await scraper.scrape_multiple_parallel(urls, max_concurrent)
            return results
        finally:
            await scraper.close_browser()

    return asyncio.run(_scrape())
