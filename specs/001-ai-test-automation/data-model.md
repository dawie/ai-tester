# Data Model: AI-Driven Playwright Test Automation

**Feature**: 001-ai-test-automation  
**Date**: 2025-10-28  
**Status**: Complete

## Core Entities

### Test Case
**Purpose**: Represents a generated or human-edited Playwright test function

**Attributes**:
- `name: str` - Unique test function name following pytest conventions
- `description: str` - Human-readable test purpose
- `target_url: str` - Web application URL this test targets
- `source_page_capture_id: str` - Reference to the page capture used for generation
- `test_code: str` - Python Playwright test implementation
- `status: TestStatus` - DRAFT | APPROVED | DEPRECATED
- `selectors: List[SelectorInfo]` - Element selectors used in test
- `created_at: datetime` - Initial generation timestamp
- `last_modified: datetime` - Last human edit timestamp
- `generated_by: str` - AI model version used for generation

**Validation Rules**:
- Test name must be valid Python function identifier
- Test code must be syntactically valid Python
- Target URL must be valid HTTP/HTTPS URL
- Only APPROVED tests can be executed

**State Transitions**:
```
DRAFT → APPROVED (human review complete)
APPROVED → DEPRECATED (test no longer relevant)
DRAFT → DEPRECATED (test deemed invalid)
```

### Page Capture
**Purpose**: Snapshot of web page state used for AI analysis context

**Attributes**:
- `id: str` - Unique identifier (timestamp-based)
- `url: str` - Target web application URL
- `html_content: str` - Captured DOM HTML (truncated if needed)
- `screenshot_path: str` - Path to full-page screenshot file
- `metadata: CaptureMetadata` - Browser, viewport, timing information
- `captured_at: datetime` - Capture timestamp
- `content_hash: str` - SHA256 hash for deduplication
- `error_info: Optional[ErrorInfo]` - Capture failure details if applicable

**Validation Rules**:
- URL must be reachable and return valid HTTP response
- HTML content limited to prevent token overflow in AI prompts
- Screenshot must be valid PNG/JPEG format
- Error info required if capture failed

**Relationships**:
- One PageCapture can generate multiple TestCases
- TestCase references source PageCapture via source_page_capture_id

### Test Report
**Purpose**: Results from executing a set of test cases

**Attributes**:
- `id: str` - Unique report identifier
- `execution_start: datetime` - Test run start time
- `execution_end: datetime` - Test run completion time
- `test_results: List[TestResult]` - Individual test outcomes
- `total_tests: int` - Number of tests executed
- `passed_count: int` - Number of successful tests
- `failed_count: int` - Number of failed tests
- `skipped_count: int` - Number of skipped tests
- `junit_xml_path: str` - Path to JUnit XML report file
- `html_report_path: Optional[str]` - Path to HTML report if generated

**Validation Rules**:
- Execution end must be after execution start
- Count fields must sum to total_tests
- All referenced file paths must exist

### Test Run
**Purpose**: Single execution session encompassing all tests and artifacts

**Attributes**:
- `id: str` - Unique session identifier
- `trigger_type: str` - MANUAL | CI_CD | SCHEDULED
- `environment: Dict[str, str]` - Environment variables and configuration
- `docker_image: str` - Container image used for execution
- `test_directory: str` - Source directory (tests/approved/)
- `artifacts_directory: str` - Output directory for captures/reports
- `exit_code: int` - Overall execution result (0 = success)
- `console_output: str` - Complete stdout/stderr capture

**Validation Rules**:
- Exit code 0 indicates successful execution (all tests passed or acceptable failures)
- Artifacts directory must contain expected output files
- Console output must include success/failure indicators per constitution

## Supporting Data Structures

### SelectorInfo
```python
@dataclass
class SelectorInfo:
    element_type: str  # button, input, link, etc.
    selector_text: str  # actual CSS/text selector
    selector_type: str  # css, text, role, data-testid
    stability_score: float  # 0.0-1.0, higher = more stable
    fallback_selectors: List[str]  # alternative selectors
```

### CaptureMetadata
```python
@dataclass
class CaptureMetadata:
    browser_name: str  # chromium, firefox, webkit
    viewport_width: int
    viewport_height: int
    user_agent: str
    load_time_ms: int
    network_idle_time_ms: int
```

### TestResult
```python
@dataclass
class TestResult:
    test_name: str
    status: str  # PASSED, FAILED, SKIPPED
    duration_ms: int
    error_message: Optional[str]
    failure_screenshot_path: Optional[str]
    failure_html_path: Optional[str]
    console_logs: List[str]
```

### ErrorInfo
```python
@dataclass
class ErrorInfo:
    error_type: str  # NETWORK_ERROR, TIMEOUT, HTTP_ERROR
    error_code: Optional[int]  # HTTP status code if applicable
    error_message: str
    occurred_at: datetime
    retry_attempted: bool = False  # Always False per fail-fast policy
```

## Storage Strategy

**File System Organization**:
- Test cases stored as Python files in tests/draft/ and tests/approved/
- Page captures stored as HTML + PNG files in captures/
- Test reports stored as XML/HTML files in reports/
- Metadata stored as JSON files alongside artifacts

**Persistence**:
- No database required - file system provides sufficient persistence
- JSON serialization for metadata objects
- Standard pytest/JUnit XML for test reporting
- Git version control for test code history

## Data Flow

1. **Capture Phase**: URL → PageCapture (HTML + screenshot + metadata)
2. **Generation Phase**: PageCapture → AI API → TestCase (DRAFT status)
3. **Review Phase**: Human edits TestCase → moves to tests/approved/
4. **Execution Phase**: Approved TestCases → TestRun → TestReport
5. **Reporting Phase**: TestReport → JUnit XML + HTML + failure artifacts

## Constraints

- HTML content truncated to prevent AI token limits
- Screenshot files limited to reasonable resolution for storage
- Test reports retained for configurable period
- Page captures deduplicated by content hash
- All timestamps in UTC for consistency