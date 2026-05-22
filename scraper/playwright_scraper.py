"""
Playwright-based web scraper
"""
import asyncio
from playwright.async_api import async_playwright, Browser
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Scrape web pages using Playwright"""

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

    async def init_browser(self):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self.browser

    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None

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

            # Extract text content
            # Remove navigation, footer, ads etc
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

    async def scrape_multiple(self, urls: list) -> list:
        """
        Scrape multiple URLs

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scrape results
        """
        results = []
        for url in urls:
            result = await self.scrape_page(url)
            results.append(result)
            # Delay between requests to be respectful
            await asyncio.sleep(2)
        return results


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


def scrape_multiple_sync(urls: list, headless: bool = True) -> list:
    """
    Synchronous wrapper for scrape_multiple

    Args:
        urls: List of URLs to scrape
        headless: Run in headless mode

    Returns:
        List of scrape results
    """
    async def _scrape():
        scraper = PlaywrightScraper(headless=headless)
        try:
            results = await scraper.scrape_multiple(urls)
            return results
        finally:
            await scraper.close_browser()

    return asyncio.run(_scrape())
