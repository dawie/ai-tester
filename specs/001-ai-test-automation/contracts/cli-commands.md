# CLI Command Contracts

## Test Generation Command

### `ai-tester generate <url>`

**Purpose**: Generate test cases for a target web application

**Input**:
```bash
ai-tester generate https://example.com
  --output-dir tests/draft/
  --capture-dir captures/
  --headless true
  --timeout 30000
```

**Parameters**:
- `url` (required): Target web application URL
- `--output-dir` (optional): Directory for generated test files (default: tests/draft/)
- `--capture-dir` (optional): Directory for page captures (default: captures/)
- `--headless` (optional): Run browser in headless mode (default: true)
- `--timeout` (optional): Page load timeout in milliseconds (default: 30000)

**Output**:
```json
{
  "status": "success|error",
  "message": "Test generation completed|Error details",
  "generated_files": [
    "tests/draft/test_example_com_20251028_143022.py"
  ],
  "page_captures": [
    "captures/example_com_20251028_143022.html",
    "captures/example_com_20251028_143022.png"
  ],
  "test_count": 5,
  "duration_ms": 45000
}
```

**Exit Codes**:
- `0`: Success - tests generated successfully
- `1`: Target URL unreachable or HTTP error
- `2`: Gemini API error (rate limit, auth, service error)
- `3`: File system error (permissions, disk space)
- `4`: Invalid input parameters

**Error Handling** (per clarifications):
- Fail immediately on API errors with descriptive message
- Log error details and terminate gracefully on target app errors
- No retry attempts per fail-fast policy

---

## Test Execution Command

### `ai-tester execute`

**Purpose**: Execute approved test cases and generate reports

**Input**:
```bash
ai-tester execute
  --test-dir tests/approved/
  --report-dir reports/
  --artifacts-dir captures/
  --headless true
  --parallel false
```

**Parameters**:
- `--test-dir` (optional): Directory containing approved tests (default: tests/approved/)
- `--report-dir` (optional): Directory for test reports (default: reports/)
- `--artifacts-dir` (optional): Directory for failure artifacts (default: captures/)
- `--headless` (optional): Run browser in headless mode (default: true)
- `--parallel` (optional): Run tests in parallel (default: false)

**Output**:
```json
{
  "status": "success|failure|partial",
  "message": "All tests passed|X tests failed|Mixed results",
  "test_summary": {
    "total": 10,
    "passed": 8,
    "failed": 2,
    "skipped": 0,
    "duration_ms": 120000
  },
  "reports": [
    "reports/junit_20251028_143500.xml",
    "reports/html_20251028_143500.html"
  ],
  "failure_artifacts": [
    "captures/test_login_failure_20251028_143510.png",
    "captures/test_login_failure_20251028_143510.html"
  ]
}
```

**Exit Codes**:
- `0`: Success - all tests passed or acceptable failure rate
- `1`: Test execution failed (environment/setup issues)
- `2`: No approved tests found in specified directory
- `3`: File system error (permissions, disk space)

---

## File Movement Command

### `ai-tester approve <test-file>`

**Purpose**: Move test file from draft to approved directory

**Input**:
```bash
ai-tester approve tests/draft/test_example_com_20251028_143022.py
ai-tester approve tests/draft/test_*.py  # Wildcard support
```

**Parameters**:
- `test-file` (required): Path to test file(s) to approve

**Output**:
```json
{
  "status": "success|error",
  "message": "Test(s) approved|Error details",
  "moved_files": [
    {
      "from": "tests/draft/test_example_com_20251028_143022.py",
      "to": "tests/approved/test_example_com_20251028_143022.py"
    }
  ],
  "validation_errors": []
}
```

**Validation**:
- Test file must contain valid Python syntax
- Test functions must follow pytest conventions
- Required imports must be present (playwright, pytest)

---

## Status Command

### `ai-tester status`

**Purpose**: Show current state of test files and recent activity

**Input**:
```bash
ai-tester status
  --verbose false
  --days 7
```

**Output**:
```json
{
  "draft_tests": {
    "count": 3,
    "files": ["test_login.py", "test_checkout.py", "test_search.py"]
  },
  "approved_tests": {
    "count": 5,
    "files": ["test_homepage.py", "test_navigation.py", "..."]
  },
  "recent_activity": [
    {
      "action": "generate",
      "timestamp": "2025-10-28T14:30:22Z",
      "target": "https://example.com",
      "result": "success"
    },
    {
      "action": "execute", 
      "timestamp": "2025-10-28T14:25:10Z",
      "tests_run": 5,
      "result": "2 failed"
    }
  ],
  "environment": {
    "python_version": "3.11.5",
    "playwright_version": "1.48.0",
    "docker_image": "mcr.microsoft.com/playwright/python:v1.48.0-jammy",
    "gemini_api_configured": true
  }
}
```

---

## Environment Configuration

### Required Environment Variables

```bash
# .env file
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-computer-use-preview-10-2025
```

### Docker Integration

```bash
# Build container
docker build -t ai-tester .

# Generate tests
docker run -it --rm -v ${PWD}:/app ai-tester generate https://example.com

# Execute tests  
docker run -it --rm -v ${PWD}:/app ai-tester execute

# Status check
docker run -it --rm -v ${PWD}:/app ai-tester status
```

### Output Format Standards

**Console Output** (per constitution):
- Success operations: ✅ prefix
- Error operations: ❌ prefix
- Progress operations: [*] prefix
- Info operations: ℹ️ prefix

**File Naming Conventions**:
- Test files: `test_{sanitized_domain}_{timestamp}.py`
- Captures: `{sanitized_domain}_{timestamp}.{html|png}`
- Reports: `{junit|html}_{timestamp}.{xml|html}`

**JSON Response Format**:
- Always include `status` field (success|error|warning)
- Always include `message` field with human-readable description
- Include relevant file paths for debugging
- Include timing information for performance monitoring