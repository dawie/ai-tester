# Tasks: AI-Driven Playwright Test Automation

**Input**: Design documents from `/specs/001-ai-test-automation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project per plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with requirements.txt dependencies (Playwright, pytest, google-genai, python-dotenv, requests)
- [ ] T003 [P] Configure Dockerfile with official Playwright base image mcr.microsoft.com/playwright/python:v1.48.0-jammy
- [ ] T004 [P] Create .env.example template with required environment variables (GOOGLE_API_KEY, GEMINI_MODEL)
- [ ] T005 [P] Setup directory structure: src/, tests/draft/, tests/approved/, captures/, reports/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create base models in src/models/test_case.py with TestCase entity (name, description, target_url, test_code, status)
- [ ] T007 [P] Create PageCapture model in src/models/page_capture.py (id, url, html_content, screenshot_path, metadata)
- [ ] T008 [P] Create TestReport model in src/models/test_report.py (execution times, test results, counts)
- [ ] T009 [P] Create TestRun model in src/models/test_run.py (session tracking, environment, artifacts)
- [ ] T010 Create error handling utilities in src/lib/error_handling.py with fail-fast approach
- [ ] T011 [P] Create file utilities in src/lib/file_utils.py for directory management (draft/approved separation)
- [ ] T012 [P] Create selector utilities in src/lib/selectors.py for stable selector generation
- [ ] T013 Create CLI main entry point in src/cli/main.py with command routing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Test Discovery (Priority: P1) 🎯 MVP

**Goal**: Generate test cases from web applications using Gemini Computer Use API

**Independent Test**: Provide target URL, verify test case files generated with valid Playwright syntax in tests/draft/

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create PlaywrightService in src/services/playwright_service.py for page capture (HTML + screenshot)
- [ ] T015 [P] [US1] Create GeminiService in src/services/gemini_service.py for AI test generation via Computer Use API
- [ ] T016 [US1] Implement generate command in src/cli/generate.py with URL input and page capture logic
- [ ] T017 [US1] Integrate Gemini API calls with page context (HTML + screenshot) for test generation
- [ ] T018 [US1] Implement test file generation and saving to tests/draft/ directory with timestamp naming
- [ ] T019 [US1] Add error handling for API failures (fail immediately with descriptive messages per clarifications)
- [ ] T020 [US1] Add error handling for target application errors (log details and fail gracefully per clarifications)
- [ ] T021 [US1] Implement stable selector generation prioritizing text content, ARIA roles, data-testid attributes

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Human Review & Approval (Priority: P2)

**Goal**: Enable human review workflow with draft/approved directory structure

**Independent Test**: Generate sample tests, manually edit them, verify system distinguishes draft vs approved status

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement approve command in src/cli/approve.py for moving tests from draft to approved directory
- [ ] T023 [P] [US2] Add test file validation in src/lib/file_utils.py (syntax check, pytest conventions, required imports)
- [ ] T024 [US2] Implement status command in src/cli/status.py showing draft/approved test counts and recent activity
- [ ] T025 [US2] Add wildcard support for approving multiple test files at once
- [ ] T026 [US2] Implement file preservation logic to never overwrite approved tests during regeneration
- [ ] T027 [US2] Add clear naming conventions and directory structure support for organizing test suites

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Test Execution & Reporting (Priority: P3)

**Goal**: Execute approved tests and generate comprehensive reports with failure artifacts

**Independent Test**: Provide pre-written tests, execute in Docker, validate report generation and failure artifacts

### Implementation for User Story 3

- [ ] T028 [P] [US3] Create TestRunner service in src/services/test_runner.py for pytest execution in Docker environment
- [ ] T029 [P] [US3] Implement execute command in src/cli/execute.py for running tests from tests/approved/ directory
- [ ] T030 [US3] Add JUnit XML report generation in reports/ directory for CI/CD integration
- [ ] T031 [US3] Implement failure artifact capture (screenshots, HTML snapshots, console logs) in captures/ directory
- [ ] T032 [US3] Add HTML report generation for human-readable test results
- [ ] T033 [US3] Implement test execution with both headless and headed browser mode support
- [ ] T034 [US3] Add test run session tracking with timestamps and unique identifiers
- [ ] T035 [US3] Implement comprehensive console output with success (✅) and failure (❌) indicators per constitution

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T036 [P] Add comprehensive logging throughout all services for observability per constitution
- [ ] T037 [P] Implement environment configuration validation (API key presence, Docker setup)
- [ ] T038 [P] Add command-line help and usage documentation
- [ ] T039 [P] Implement Docker integration with volume mounting for all commands
- [ ] T040 Code cleanup and refactoring across all modules
- [ ] T041 [P] Add performance monitoring for 3-minute test generation goal
- [ ] T042 Run quickstart.md validation to ensure documentation accuracy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1/US2 but independently testable

### Within Each User Story

- Models and utilities before services
- Services before CLI commands
- Core implementation before integration and error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within the foundational phase marked [P] can run in parallel
- Services within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all services for User Story 1 together:
Task: "Create PlaywrightService in src/services/playwright_service.py"
Task: "Create GeminiService in src/services/gemini_service.py"

# Then implement integration tasks sequentially:
Task: "Implement generate command in src/cli/generate.py"
Task: "Integrate Gemini API calls with page context"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- File paths are exact and follow the single project structure from plan.md
- All tasks follow the strict checklist format with Task ID, optional [P] marker, optional [Story] label, and file paths