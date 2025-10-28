"""
gemini_client.py
----------------
Simple script to verify access to Google's Gemini 2.5 Computer‑Use Preview model.
It sends a minimal request that declares the `computer_use` tool,
as required by this preview model.

Usage inside your container:
    docker run -it --rm -v ${PWD}:/app ai-tester python gemini_client.py
"""

import os
import requests
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# 1. Load environment variables
# ─────────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ─────────────────────────────────────────────────────────────
# 2. Model + endpoint configuration
# ─────────────────────────────────────────────────────────────
MODEL = "gemini-2.5-computer-use-preview-10-2025"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent?key={API_KEY}"
)

# ─────────────────────────────────────────────────────────────
# 3. Function to test the Computer‑Use API call
# ─────────────────────────────────────────────────────────────
def test_computer_use_request():
    if not API_KEY:
        raise EnvironmentError("GOOGLE_API_KEY not found. Check your .env file.")

    # Body required by the Computer‑Use Preview model
    body = {
        "tools": [{"computer_use": {}}],
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Hello Gemini 2.5 Computer‑Use Preview! "
                            "Please reply with a short greeting so I can confirm that the Computer‑Use tool works."
                        )
                    }
                ],
            }
        ],
    }

    print(f"[*] Sending request to {MODEL} …")
    try:
        response = requests.post(ENDPOINT, json=body)
    except Exception as e:
        print(f"❌ Network or request error: {e}")
        return

    print(f"[DEBUG] Status: {response.status_code}")
    try:
        print(response.json())
    except Exception:
        print(response.text)

    if response.status_code == 200:
        data = response.json()
        try:
            message = data["candidates"][0]["content"]["parts"][0].get("text", "")
            print("\n✅ Gemini API response:")
            print(message)
        except Exception as e:
            print("\n⚠️ Received 200 OK but couldn't parse message:")
            print(e)
    elif response.status_code == 400:
        print("\n⚠️ 400 Bad Request – usually means missing or malformed tool declarations.")
        print("   Double‑check that 'tools': [{'computer_use': {}}] is present in the payload.")
    elif response.status_code == 403:
        print("\n❌ 403 Forbidden – The API key or project lacks permission for this model.")
        print("   Ensure billing is enabled and preview access is approved.")
    elif response.status_code == 429:
        print("\n⚠️ 429 RESOURCE_EXHAUSTED – You’ve hit the model’s rate or quota limit.")
        print("   Wait a minute or verify quota in https://ai.dev/usage.")
    else:
        print(f"\n❌ Unexpected error {response.status_code}")


# ─────────────────────────────────────────────────────────────
# 4. Entry point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_computer_use_request()
