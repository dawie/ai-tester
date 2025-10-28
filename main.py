from playwright.sync_api import sync_playwright

def capture_screenshot(url="https://example.com", path="screenshot.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=path, full_page=True)
        browser.close()
        print(f"✅ Screenshot saved to {path}")

if __name__ == "__main__":
    capture_screenshot()
