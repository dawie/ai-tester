<!--
Sync Impact Report:
- Version: INITIAL → 1.0.0
- New constitution created for AI Tester project
- Principles: 3 core principles established (Containerization, AI-Driven Testing, Observability)
- Templates status:
  ✅ plan-template.md - reviewed, compatible
  ✅ spec-template.md - reviewed, compatible
  ✅ tasks-template.md - reviewed, compatible
- No follow-up TODOs
-->

# AI Tester Constitution

## Core Principles

### I. Containerization First

All functionality MUST run in Docker containers to ensure environment consistency.

**Rules**:
- Python dependencies declared in `requirements.txt`
- Playwright browser automation MUST use official Playwright Docker images
- Environment secrets (API keys) MUST be loaded via `.env` files, never hardcoded
- Container builds MUST be reproducible and versioned

**Rationale**: Windows + Linux compatibility, isolation from host system variations, CI/CD portability.

### II. AI-Driven Test Generation

Test cases MUST be generated or enhanced using AI models (Gemini API) analyzing captured page state.

**Rules**:
- Page captures MUST include both HTML content and screenshots
- AI prompts MUST provide sufficient context (DOM structure, visual state)
- Generated tests MUST be saved to `tests/` directory before execution
- Human review of generated tests is RECOMMENDED but not blocking

**Rationale**: Accelerates test coverage, discovers edge cases humans might miss, adapts to UI changes.

### III. Observability & Debugging

All operations MUST produce traceable outputs to enable debugging.

**Rules**:
- Captures (HTML, screenshots) MUST be saved to `captures/` directory
- Test reports MUST be generated (JUnit XML minimum)
- Console output MUST indicate success (✅) or failure (❌) clearly
- API interactions MUST log request/response status codes

**Rationale**: Enables rapid troubleshooting of test failures, validates AI model behavior, supports audit trails.

## Technology Stack

**Language**: Python 3.11+  
**UI Automation**: Playwright (Python sync API)  
**AI Model**: Google Gemini 2.5 Computer-Use Preview  
**Testing**: pytest with pytest-playwright  
**Containerization**: Docker with official Playwright base images  
**Environment**: python-dotenv for configuration

## Development Workflow

**Test Execution Flow**:
1. Capture page state (HTML + screenshot) → `captures/`
2. Send context to Gemini API for test generation
3. Save generated tests → `tests/ai_generated_tests.py`
4. Execute tests via pytest
5. Generate reports → `reports/`

**Quality Gates**:
- Docker build MUST succeed before running tests
- API key MUST be configured before AI operations
- Playwright browsers MUST be installed in container

## Governance

This constitution defines the non-negotiable architecture for the AI Tester project. 

**Amendment Process**: Changes require documentation of rationale and impact on existing scripts.

**Compliance**: All new features MUST align with containerization, AI-driven testing, and observability principles.

**Version**: 1.0.0 | **Ratified**: 2025-10-28 | **Last Amended**: 2025-10-28
