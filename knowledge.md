# 🧠 Project Knowledge – _AI Tester Environment_

**Date:** 2025‑10‑24  
**Platform:** Windows + Docker Desktop  

---

## 1️⃣ Overview

Goal: build a containerized Python + Playwright system that connects to Google’s **Gemini 2.5 Computer Use Preview API** for:
1. Inspecting web applications automatically,  
2. Using Gemini to propose Playwright test cases,  
3. Running, reporting, and iterating on those test cases.

---

## 2️⃣ Environment Setup Summary (what we built)

| Step | Component | Description |
|:--|:--|:--|
| **1** | **Docker Desktop** | Base runtime (Windows → Linux containers). |
| **2** | **Project Folder** | `C:\Code\AI Tester` holds all source files. |
| **3** | **Dockerfile** | Based on `mcr.microsoft.com/playwright/python:v1.48.0-jammy`; installs Playwright + pytest + requests + dotenv. |
| **4** | **requirements.txt** | `playwright`, `pytest`, `pytest‑html`, `requests`, `python‑dotenv`. |
| **5** | **.env** | Stores `GOOGLE_API_KEY=` (+ optional `GEMINI_MODEL=`). |
| **6** | **gemini_client.py** | Verified connectivity to Gemini API; now configured for `gemini‑2.5‑computer‑use‑preview‑10‑2025` with correct `tools: [{"computer_use": {}}]` payload. |
| **7** | **playwright_runner.py** | Captures a web app’s screenshot and partial HTML for Gemini context. |
| **8** | **generate_tests.py** | Sends captured content to Gemini; saves suggested test script in `tests/ai_generated_tests.py`. |
| **9** | **pytest / Playwright** | Executes generated tests (headless by default). |
| **10** | **Validated API Response** | Gemini returned a `functionCall: {"name": "open_web_browser"}` → confirmed correct model invocation. |

---

## 3️⃣ Key Commands Recap

| Purpose | Command |
|:--|:--|
| Build Docker image | `docker build -t ai-tester .` |
| Test Gemini Connection | `docker run -it --rm ai-tester python gemini_client.py` |
| Generate tests | `docker run -it --rm -v ${PWD}:/app ai-tester python generate_tests.py` |
| Execute tests (headless) | `docker run -it --rm -v ${PWD}:/app ai-tester pytest tests/ai_generated_tests.py` |

---

## 4️⃣ What We Have Validated

- ✅ Docker environment builds correctly.  
- ✅ Playwright runs in container.  
- ✅ Gemini 2.5 Computer Use API reachable with billing enabled.  
- ✅ Proper JSON schema using `"tools": [{"computer_use": {}}]`.  
- ✅ Model emits function‑calls (proof of active preview session).  
- ✅ Test‑generation pipeline works end‑to‑end.

---

## 5️⃣ Known Considerations / Fixes

| Issue | Description / Solution |
|:--|:--|
| 429 `RESOURCE_EXHAUSTED` | Key has 0 free‑tier quota → needs active billing (+ preview quota). |
| 404 `Model not found` | Wrong endpoint / key lacks access → list models via `GET /v1beta/models?key=` and use name shown. |
| 400 `Invalid JSON payload` | Use `{ "tools": [{ "computer_use": {} }] }`, not `{ "name": "computer" }`. |
| Playwright flags | `--headed` only works in Node CLI; Python tests use `pytest` and `headless=False` inside script. |
| PowerShell syntax | Use one‑line commands or PowerShell back‑ticks (`). |

---

## 6️⃣ To‑Do / Next Steps

| Area | Task |
|:--|:--|
| **1. Implement tool loop** | JSON response contains `functionCall` (e.g., `open_web_browser`). Write a Python Playwright executor that performs these actions and sends updated context back to Gemini. |
| **2. Richer context** | Expand `generate_tests.py` to send Base64‑encoded screenshots and trimmed DOM for better page understanding. |
| **3. Review UI** | Add a minimal web / CLI interface for human test editing before execution. |
| **4. Reporting** | Integrate `pytest‑html` or Allure for HTML reports. |
| **5. CI/CD automation** | Add GitHub Actions / GitLab CI pipeline to (1) build → (2) generate tests → (3) execute → (4) archive reports. |
| **6. Prompt engineering** | Iterate on prompting for cleaner, runnable Playwright code. |
| **7. Security** | Manage keys via environment secrets in CI/CD. |
| **8. Computer‑Use Exploration** | Once the executor loop is ready, let the model autonomously explore pages → generate deeper tests. |

---

## 7️⃣ Example Project Layout

- 2025‑10‑27 – Implemented and verified tool_runner.py
  - Gemini 2.5 Computer‑Use model responds with function calls.
  - Playwright executes each call; results captured under /captures.
  - Workflow validated inside Docker on Windows.
  - Next tasks: extend function map; enable automatic test‑file export.
