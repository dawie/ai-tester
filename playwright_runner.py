"""
playwright_runner.py
--------------------
Captures a target web page's HTML and screenshot using Playwright.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def capture_page(url: str, out_dir: str = "captures"):
    Path(out_dir).mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"[*] Visiting {url}")
        page.goto(url)
        page.wait_for_load_state("networkidle")

        html = page.content()
        screenshot_path = Path(out_dir) / "page.png"
        html_path = Path(out_dir) / "page.html"

        page.screenshot(path=str(screenshot_path), full_page=True)
        html_path.write_text(html, encoding="utf-8")

        browser.close()

        print(f"✅ Screenshot saved to {screenshot_path}")
        print(f"✅ HTML saved to {html_path}")

        return str(screenshot_path), html[:8000]  # limit HTML length for prompt safety
