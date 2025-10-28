# Implementation Plan: AI-Driven Playwright Test Automation

**Branch**: `001-ai-test-automation` | **Date**: 2025-10-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-test-automation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Automated test generation system that uses Docker containers with Playwright to analyze web applications, leverages Google Gemini Computer Use API to generate comprehensive test cases, enables human review workflow, and executes approved tests with detailed reporting. Core value: eliminates manual test writing effort while discovering edge cases humans might miss.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Playwright, pytest, pytest-playwright, google-genai, python-dotenv, requests  
**Storage**: File system (tests, captures, reports directories)  
**Testing**: pytest with pytest-playwright for test execution  
**Target Platform**: Docker containers (Linux-based) with official Playwright images
**Project Type**: Single project (CLI automation tool)  
**Performance Goals**: Generate test cases for 5-page web application in under 3 minutes (excluding API latency)  
**Constraints**: Fail-fast on API errors, no retry mechanisms, stable selectors prioritized over dynamic content  
**Scale/Scope**: Single machine execution, functional UI testing only (no performance/security/accessibility testing)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Containerization First ✅ PASS
- **✅ Python dependencies in requirements.txt**: Playwright, pytest, google-genai specified
- **✅ Official Playwright Docker images**: Base image mcr.microsoft.com/playwright/python:v1.48.0-jammy
- **✅ Environment secrets via .env**: Google API key loaded from environment variables
- **✅ Reproducible builds**: Dockerfile ensures consistent environment

### II. AI-Driven Test Generation ✅ PASS  
- **✅ Page captures include HTML + screenshots**: FR-003 mandates both capture types
- **✅ Sufficient AI context**: HTML + screenshot sent to Gemini Computer Use API
- **✅ Tests saved to tests/ directory**: FR-005 specifies tests/draft/ for generated content
- **✅ Human review workflow**: User Story 2 enables review and approval before execution

### III. Observability & Debugging ✅ PASS
- **✅ Captures saved to captures/**: FR-009 mandates failure artifacts in captures/ directory  
- **✅ JUnit XML reports**: FR-008 requires reports/ directory for CI/CD integration
- **✅ Clear console output**: FR-011 mandates success (✅) and failure (❌) indicators
- **✅ API interaction logging**: FR-013 requires descriptive error messages for API failures

**POST-DESIGN VALIDATION**: ✅ **ALL PRINCIPLES SATISFIED**
- CLI commands implement all constitutional requirements
- Data model supports required artifacts and observability
- Directory structure aligns with containerization and workflow principles
- Error handling follows fail-fast approach per constitution

**GATE RESULT**: ✅ **APPROVED FOR IMPLEMENTATION**

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-test-automation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── test_case.py        # Test case entity with metadata
│   ├── page_capture.py     # Page capture entity (HTML + screenshot)
│   └── test_report.py      # Test execution results entity
├── services/
│   ├── playwright_service.py   # Web page capture and browser automation
│   ├── gemini_service.py       # AI test generation via Computer Use API
│   └── test_runner.py          # Test execution and reporting
├── cli/
│   ├── generate.py            # Test generation command
│   ├── execute.py             # Test execution command
│   └── main.py               # CLI entry point
└── lib/
    ├── selectors.py          # Stable selector generation utilities
    ├── error_handling.py     # Fail-fast error management
    └── file_utils.py         # Directory structure management

tests/
├── draft/                    # AI-generated tests awaiting review
├── approved/                 # Human-reviewed tests ready for execution  
├── contract/                 # API contract tests (if needed)
├── integration/              # End-to-end workflow tests
└── unit/                     # Component unit tests

captures/                     # Page captures and failure artifacts
reports/                      # JUnit XML and HTML reports
.env                         # Environment configuration (API keys)
requirements.txt             # Python dependencies
Dockerfile                   # Container definition
```

**Structure Decision**: Single project structure selected. This is a CLI automation tool that doesn't require web frontend or mobile components. The directory structure aligns with constitution requirements: clear separation of draft vs approved tests, dedicated captures and reports directories, and containerized execution environment.
