"""
generate_tests.py
-----------------
Uses captured page data to prompt Gemini for Playwright test-case suggestions.
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from playwright_runner import capture_page

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL = "gemini-2.5-computer-use-preview-10-2025"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent?key={API_KEY}"
)

def ask_gemini_for_tests(url: str):
    screenshot_path, short_html = capture_page(url)
    prompt_text = (
        f"Analyze this web page and propose Playwright (Python) test cases "
        f"to verify its basic functionality like navigation and forms.\n\n"
        f"Partial HTML content:\n{short_html[:5000]}"
    )

    # For now we won’t send binary data, just contextual text
    body = {
        "tools": [{"computer_use": {}}],
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt_text},
                ],
            }
        ],
    }

    print(f"[*] Asking Gemini for test suggestions on {url}")
    response = requests.post(ENDPOINT, json=body)
    print(f"[DEBUG] Status: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return None

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0].get("text", "")
        print("\n✅ Suggested Playwright test cases:\n")
        print(text)
        Path("tests").mkdir(exist_ok=True)
        with open("tests/ai_generated_tests.py", "w", encoding="utf-8") as f:
            f.write(text)
        print("\n💾 Saved to tests/ai_generated_tests.py")
    except Exception as e:
        print("⚠️ Could not parse model output:", e)
        print(response.text)

if __name__ == "__main__":
    target_url = "https://doe.sys-dev.net/kindilink/registrations/parents/new"  # ← replace with your web app
    ask_gemini_for_tests(target_url)
