"""
Browser pool for reusing Playwright browser instances
Improves performance by avoiding browser creation overhead
"""
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import Optional, Dict
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class BrowserPool:
    """
    Pool of reusable browser instances
    Maintains multiple browser contexts for concurrent scraping
    """

    def __init__(self, max_browsers: int = 3, max_contexts_per_browser: int = 5):
        """
        Initialize browser pool

        Args:
            max_browsers: Maximum number of browser instances to maintain
            max_contexts_per_browser: Maximum contexts per browser
        """
        self.max_browsers = max_browsers
        self.max_contexts_per_browser = max_contexts_per_browser
        self.playwright = None
        self.browsers: list[Browser] = []
        self.available_contexts: asyncio.Queue = asyncio.Queue()
        self.total_contexts = 0
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self, headless: bool = True):
        """
        Initialize the browser pool

        Args:
            headless: Run browsers in headless mode
        """
        if self._initialized:
            return

        logger.info("Initializing browser pool...")
        self.playwright = await async_playwright().start()

        # Create initial browser with contexts
        await self._create_browser_with_contexts(headless, initial_contexts=2)
        self._initialized = True
        logger.info(f"Browser pool initialized with {self.available_contexts.qsize()} contexts")

    async def _create_browser_with_contexts(self, headless: bool, initial_contexts: int = 2):
        """Create a new browser instance with contexts"""
        if len(self.browsers) >= self.max_browsers:
            logger.warning("Max browsers reached, reusing existing browsers")
            return

        browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',  # Reduce memory usage
                '--disable-gpu',  # Not needed in headless
            ]
        )
        self.browsers.append(browser)
        logger.info(f"Created new browser (total: {len(self.browsers)})")

        # Create initial contexts
        for _ in range(min(initial_contexts, self.max_contexts_per_browser)):
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            await self.available_contexts.put(context)
            self.total_contexts += 1

    async def get_context(self) -> BrowserContext:
        """
        Get a browser context from the pool

        Returns:
            BrowserContext: An available context
        """
        if not self._initialized:
            await self.initialize()

        # Wait for an available context (with timeout)
        try:
            context = await asyncio.wait_for(
                self.available_contexts.get(),
                timeout=30
            )
            return context
        except asyncio.TimeoutError:
            # No context available, try to create more
            async with self._lock:
                if self.total_contexts < self.max_browsers * self.max_contexts_per_browser:
                    # Find a browser with available capacity
                    for browser in self.browsers:
                        contexts_count = sum(
                            1 for b in self.browsers
                            for c in browser.contexts
                        )
                        if contexts_count < self.max_contexts_per_browser:
                            context = await browser.new_context(
                                viewport={'width': 1920, 'height': 1080},
                                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            )
                            self.total_contexts += 1
                            return context

            # If still no context, wait for one to become available
            logger.warning("All contexts busy, waiting for available context...")
            return await self.available_contexts.get()

    async def return_context(self, context: BrowserContext):
        """
        Return a context to the pool

        Args:
            context: The context to return
        """
        # Clear cookies and storage to prevent state leakage
        try:
            await context.clear_cookies()
            await self.available_contexts.put(context)
        except Exception as e:
            logger.error(f"Error returning context to pool: {e}")
            # Context might be closed, create a replacement
            if self.browsers:
                try:
                    browser = self.browsers[0]
                    new_context = await browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    )
                    await self.available_contexts.put(new_context)
                except Exception as e2:
                    logger.error(f"Failed to create replacement context: {e2}")

    async def close_all(self):
        """Close all browsers and cleanup resources"""
        logger.info("Closing browser pool...")
        self._initialized = False

        # Close all queued contexts
        while not self.available_contexts.empty():
            try:
                context = self.available_contexts.get_nowait()
                await context.close()
            except asyncio.QueueEmpty:
                break

        # Close all browsers
        for browser in self.browsers:
            try:
                await browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

        self.browsers.clear()
        self.total_contexts = 0

        # Close playwright
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.error(f"Error stopping playwright: {e}")

        logger.info("Browser pool closed")

    @asynccontextmanager
    async def get_context_async(self):
        """
        Async context manager for getting and returning a context

        Usage:
            async with pool.get_context_async() as context:
                page = await context.new_page()
                # ... do work ...
        """
        context = await self.get_context()
        try:
            yield context
        finally:
            await self.return_context(context)


# Global browser pool instance
_global_pool: Optional[BrowserPool] = None


def get_browser_pool() -> BrowserPool:
    """Get the global browser pool instance"""
    global _global_pool
    if _global_pool is None:
        _global_pool = BrowserPool()
    return _global_pool


async def initialize_browser_pool(headless: bool = True):
    """Initialize the global browser pool"""
    pool = get_browser_pool()
    await pool.initialize(headless=headless)
    return pool


async def close_browser_pool():
    """Close the global browser pool"""
    global _global_pool
    if _global_pool:
        await _global_pool.close_all()
        _global_pool = None
