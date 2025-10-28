# Quickstart Guide: AI-Driven Playwright Test Automation

## Prerequisites

1. **Docker Desktop** installed and running
2. **Google Gemini API Key** with Computer Use access
3. **Git** (optional, for version control)

## Setup

### 1. Clone and Configure

```bash
git clone <repository-url>
cd ai-tester
```

### 2. Environment Configuration

Create `.env` file in the project root:

```bash
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-computer-use-preview-10-2025
```

### 3. Build Docker Container

```bash
docker build -t ai-tester .
```

**Expected output:**
```
✅ Docker image built successfully
```

## Basic Workflow

### Step 1: Generate Test Cases

Point the system at a web application to generate tests:

```bash
docker run -it --rm -v ${PWD}:/app ai-tester generate https://example.com
```

**What happens:**
1. 🌐 Browser opens and navigates to target URL
2. 📸 System captures page HTML and screenshot  
3. 🤖 Gemini AI analyzes content and generates test cases
4. 💾 Tests saved to `tests/draft/test_example_com_YYYYMMDD_HHMMSS.py`

**Expected output:**
```
[*] Visiting https://example.com
✅ Screenshot saved to captures/example_com_20251028_143022.png
✅ HTML saved to captures/example_com_20251028_143022.html
[*] Asking Gemini for test suggestions...
✅ Generated 5 test cases in tests/draft/test_example_com_20251028_143022.py
```

### Step 2: Review and Approve Tests

1. **Open the generated test file** in your editor:
   ```bash
   code tests/draft/test_example_com_20251028_143022.py
   ```

2. **Review the generated tests:**
   - Check selectors are appropriate
   - Verify test logic matches your expectations
   - Add additional assertions if needed
   - Remove irrelevant tests

3. **Approve the tests** by moving to approved directory:
   ```bash
   docker run -it --rm -v ${PWD}:/app ai-tester approve tests/draft/test_example_com_20251028_143022.py
   ```

**Expected output:**
```
✅ Test approved: tests/approved/test_example_com_20251028_143022.py
```

### Step 3: Execute Tests

Run all approved tests:

```bash
docker run -it --rm -v ${PWD}:/app ai-tester execute
```

**What happens:**
1. 🔍 System scans `tests/approved/` directory
2. 🚀 Runs all tests in Docker container with Playwright
3. 📊 Generates JUnit XML and HTML reports
4. 📸 Captures failure artifacts for any failed tests

**Expected output:**
```
[*] Found 5 approved tests
[*] Running tests in Docker container...
✅ test_homepage_loads: PASSED (1.2s)
✅ test_navigation_menu: PASSED (0.8s)
❌ test_contact_form: FAILED (2.1s)
✅ test_search_functionality: PASSED (1.5s)
✅ test_footer_links: PASSED (0.6s)

Test Results: 4 passed, 1 failed, 0 skipped (6.2s total)
✅ JUnit report: reports/junit_20251028_143500.xml
✅ HTML report: reports/html_20251028_143500.html
❌ Failure artifacts: captures/test_contact_form_failure_20251028_143510.png
```

## File Structure After Running

```
ai-tester/
├── tests/
│   ├── draft/                    # AI-generated tests awaiting review
│   │   └── (new generated tests)
│   └── approved/                 # Human-reviewed tests ready for execution
│       └── test_example_com_20251028_143022.py
├── captures/                     # Page captures and failure artifacts
│   ├── example_com_20251028_143022.html
│   ├── example_com_20251028_143022.png
│   └── test_contact_form_failure_20251028_143510.png
├── reports/                      # Test execution reports
│   ├── junit_20251028_143500.xml
│   └── html_20251028_143500.html
├── .env                         # Environment configuration
└── Dockerfile                   # Container definition
```

## Common Commands

### Check System Status
```bash
docker run -it --rm -v ${PWD}:/app ai-tester status
```

### Generate Tests with Custom Options
```bash
# Longer timeout for slow sites
docker run -it --rm -v ${PWD}:/app ai-tester generate https://slow-site.com --timeout 60000

# Custom output directory
docker run -it --rm -v ${PWD}:/app ai-tester generate https://example.com --output-dir tests/experimental/
```

### Execute Tests in Headed Mode (for debugging)
```bash
docker run -it --rm -v ${PWD}:/app \
  --ipc=host --env DISPLAY ai-tester \
  execute --headless false
```

### Approve Multiple Tests at Once
```bash
docker run -it --rm -v ${PWD}:/app ai-tester approve tests/draft/test_*.py
```

## Troubleshooting

### ❌ "API key not configured"
- Verify `.env` file exists with valid `GOOGLE_API_KEY`
- Check API key has access to Gemini Computer Use preview

### ❌ "Target application unreachable"
- Verify URL is accessible from your network
- Check for typos in URL
- Ensure target site doesn't block automated access

### ❌ "No approved tests found"
- Run `docker run -it --rm -v ${PWD}:/app ai-tester status` to check test locations
- Ensure tests have been moved from `tests/draft/` to `tests/approved/`

### ❌ "Docker permission denied"
- On Linux: Add user to docker group or use `sudo`
- On Windows: Ensure Docker Desktop is running

### ❌ "Generated tests fail to execute"
- Review test selectors - website may have changed
- Check for dynamic content that requires stable selectors
- Manually edit tests in `tests/approved/` directory

## Next Steps

1. **Set up CI/CD**: Add test execution to your build pipeline
2. **Customize selectors**: Edit generated tests to use data-testid attributes
3. **Add authentication**: Extend tests to handle login flows (future enhancement)
4. **Schedule regular runs**: Set up automated test generation for regression testing

## Configuration Options

### Environment Variables (.env)
```bash
GOOGLE_API_KEY=required_api_key
GEMINI_MODEL=gemini-2.5-computer-use-preview-10-2025  # Optional, defaults to this
DEBUG=false                                            # Optional, enables verbose logging
TIMEOUT_MS=30000                                      # Optional, default page timeout
```

### Docker Run Options
```bash
# Standard usage
docker run -it --rm -v ${PWD}:/app ai-tester <command>

# With custom environment file
docker run -it --rm -v ${PWD}:/app --env-file custom.env ai-tester <command>

# For headed mode (Linux with X11)
docker run -it --rm -v ${PWD}:/app --ipc=host --env DISPLAY ai-tester <command>
```