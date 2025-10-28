"""
tool_runner.py
---------------
Interactive loop that executes Gemini 2.5 Computer‑Use Preview
functionCalls using Playwright and sends back observations.
Saves a screenshot + HTML for every step.
"""

import os
import json
import base64
import pathlib
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# ─────────────────────────────────────────────────────────────
# 1. Environment setup
# ─────────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = "gemini-2.5-computer-use-preview-10-2025"

ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent?key={API_KEY}"
)

# ─────────────────────────────────────────────────────────────
# 2. Helpers for Gemini requests
# ─────────────────────────────────────────────────────────────
def call_gemini(tools, prev_contents):
    """Send a generateContent request to Gemini."""
    body = {"tools": tools, "contents": prev_contents}
    resp = requests.post(ENDPOINT, json=body)
    resp.raise_for_status()
    return resp.json()

def make_user_part(text=None, img_b64=None):
    """Create a 'part' payload with optional image."""
    parts = []
    if text:
        parts.append({"text": text})
    if img_b64:
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": img_b64,
            }
        })
    return {"role": "user", "parts": parts}

# ─────────────────────────────────────────────────────────────
# 3. Playwright wrapper for Gemini actions
# ─────────────────────────────────────────────────────────────
class BrowserTool:
    def __init__(self):
        self.play = None
        self.browser = None
        self.page = None
        self.step_dir = pathlib.Path("captures")
        self.step_dir.mkdir(exist_ok=True)
        self.step_count = 0

    def start(self):
        self.play = sync_playwright().start()
        self.browser = self.play.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        print("🌐 Browser started (headless Chromium).")

    # --- Gemini‑invokable actions ---
    def open_web_browser(self, args):
        if self.page:
            return {"status": "browser already opened"}

    def goto_url(self, args):
        url = args.get("url")
        if not url:
            return {"error": "missing url"}
        print(f"➡️ Navigating to {url}")
        self.page.goto(url, timeout=30000)
        return {"status": f"navigated to {url}"}

    def click_element(self, args):
        selector = args.get("selector")
        print(f"🖱️ Clicking {selector}")
        self.page.click(selector)
        return {"status": f"clicked {selector}"}

    def type_text(self, args):
        selector = args.get("selector")
        text = args.get("text", "")
        print(f"⌨️ Typing '{text}' into {selector}")
        self.page.fill(selector, text)
        return {"status": f"filled {selector} with {text}"}

    # --- helpers ---
    def get_screenshot_and_dom(self):
        self.step_count += 1
        img_bytes = self.page.screenshot()
        html = self.page.content()
        b64 = base64.b64encode(img_bytes).decode("utf-8")

        # save locally for debugging
        n = self.step_count
        (self.step_dir / f"step_{n}.png").write_bytes(img_bytes)
        (self.step_dir / f"step_{n}.html").write_text(html, encoding="utf-8")
        print(f"📸 Saved captures/step_{n}.png and step_{n}.html")
        return b64, html

    def close(self):
        if self.browser:
            self.browser.close()
        if self.play:
            self.play.stop()
        print("🛑 Browser closed.")

# ─────────────────────────────────────────────────────────────
# 4. Main interactive loop
# ─────────────────────────────────────────────────────────────
def run_interactive_session(start_prompt="Open a browser window and describe it."):
    tools = [{"computer_use": {}}]
    contents = [make_user_part(text=start_prompt + " (Browser is ready to use.)")]

    browser_tool = BrowserTool()
    browser_tool.start()

    for step in range(10):  # safety limit
        print(f"\n🔁 Step {step+1}")
        result = call_gemini(tools, contents)
        parts = result["candidates"][0]["content"]["parts"]

        finished = False
        for p in parts:
            if "functionCall" in p:
                fn = p["functionCall"]["name"]
                args = p["functionCall"].get("args", {})
                print(f"🧠 Gemini calls: {fn} {json.dumps(args)}")

                if hasattr(browser_tool, fn):
                    obs = getattr(browser_tool, fn)(args)
                    b64, html = browser_tool.get_screenshot_and_dom()
                    feedback = (
                        f"Executed {fn}. Observation: {obs}. "
                        "Here is the updated page HTML."
                    )
                    contents.append(make_user_part(text=feedback, img_b64=b64))
                else:
                    print(f"⚠️ Unknown function: {fn}")
                    finished = True
                    break

            elif "text" in p:  # model returned final text
                print("\n✅ Model text output:")
                print(p["text"])
                finished = True
                break

        if finished:
            break

    browser_tool.close()
    print("🏁 Session finished.")

# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_interactive_session()