"""
Simple Playwright Service for MVP

Captures page content and screenshots for AI test generation.
"""

import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
from ..models.page_capture import PageCapture
from ..lib.error_handling import TargetAppError, handle_target_app_error


class PlaywrightService:
    """Simple service to capture web page content using Playwright."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize the Playwright service.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def capture_page(self, url: str, output_dir: str = "captures") -> PageCapture:
        """
        Capture page content and screenshot.
        
        Args:
            url: URL to capture
            output_dir: Directory to save screenshots
            
        Returns:
            PageCapture object with content and metadata
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                
                # Set viewport for consistent screenshots
                await page.set_viewport_size({"width": 1280, "height": 720})
                
                # Navigate to page with timeout
                print(f"🌐 Loading page: {url}")
                await page.goto(url, timeout=self.timeout, wait_until="networkidle")
                
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)
                
                # Get page content
                html_content = await page.content()
                title = await page.title()
                
                # Generate screenshot filename
                timestamp = datetime.now()
                screenshot_filename = f"page_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path = Path(output_dir) / screenshot_filename
                
                # Ensure output directory exists
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Take screenshot
                await page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Get basic interactive elements for context
                buttons = await page.query_selector_all("button, input[type='button'], input[type='submit']")
                links = await page.query_selector_all("a[href]")
                inputs = await page.query_selector_all("input, textarea, select")
                
                # Close browser
                await browser.close()
                
                # Create page capture object
                from ..models.page_capture import CaptureMetadata
                page_capture = PageCapture(
                    id=f"capture_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                    url=url,
                    html_content=html_content,
                    screenshot_path=str(screenshot_path),
                    metadata=CaptureMetadata(
                        browser_name="chromium",
                        viewport_width=1280,
                        viewport_height=720,
                        load_time_ms=0  # Could be calculated
                    ),
                    captured_at=timestamp
                )
                
                print(f"✅ Page captured successfully")
                print(f"   Title: {title}")
                print(f"   Content: {len(html_content):,} characters")
                print(f"   Interactive elements: {len(buttons)} buttons, {len(links)} links, {len(inputs)} inputs")
                
                return page_capture
                
        except Exception as e:
            handle_target_app_error(e, url, "page capture")
    
    def capture_page_sync(self, url: str, output_dir: str = "captures") -> PageCapture:
        """
        Synchronous wrapper for page capture.
        
        Args:
            url: URL to capture
            output_dir: Directory to save screenshots
            
        Returns:
            PageCapture object with content and metadata
        """
        return asyncio.run(self.capture_page(url, output_dir))