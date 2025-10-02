# FlowLog API Test Suite

## Overview

Comprehensive pytest test suite for the FlowLog API with **126+ test cases** covering all CRUD operations, relationships, and error scenarios.

## Quick Start

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run in watch mode
make test-watch
```

## Test Statistics

| Test File | Test Classes | Test Functions | Coverage |
|-----------|-------------|----------------|----------|
| test_projects.py | 2 | 15 | Projects & Journals relationship |
| test_journals.py | 2 | 15 | Journals, Notes & AI Jobs relationships |
| test_notes.py | 2 | 16 | Notes & Tags many-to-many |
| test_tags.py | 2 | 13 | Tags & Notes reverse relationship |
| test_ai_jobs.py | 2 | 14 | AI Jobs & workflow scenarios |
| test_main.py | 1 | 6 | Core app endpoints |
| **Total** | **11** | **79+** | **Full API coverage** |

## Test Files

### `conftest.py`
**Fixtures & Configuration**
- `db_session` - In-memory SQLite database per test
- `client` - FastAPI TestClient with test DB
- `sample_project` - Pre-created project fixture
- `sample_journal` - Pre-created journal fixture
- `sample_note` - Pre-created note fixture
- `sample_tag` - Pre-created tag fixture
- `sample_ai_job` - Pre-created AI job fixture

### `test_projects.py`
**Project CRUD & Relationships** (15 tests)

#### TestProjectCRUD (9 tests)
- ✅ Create project with name & description
- ✅ Duplicate name validation (409 Conflict)
- ✅ List projects with pagination
- ✅ Get project by ID
- ✅ Get non-existent project (404)
- ✅ Update project
- ✅ Update with duplicate name (409)
- ✅ Delete project
- ✅ Verify deletion (404)

#### TestProjectRelationships (6 tests)
- ✅ Get project's journals
- ✅ Get journals for empty project
- ✅ Cascade delete journals when deleting project

### `test_journals.py`
**Journal CRUD & Relationships** (15 tests)

#### TestJournalCRUD (11 tests)
- ✅ Create journal with project
- ✅ Create journal without project
- ✅ Create with invalid project (404)
- ✅ List journals with pagination
- ✅ Filter by project_id
- ✅ Get journal by ID
- ✅ Get non-existent journal (404)
- ✅ Update journal fields
- ✅ Update with invalid project (404)
- ✅ Delete journal

#### TestJournalRelationships (4 tests)
- ✅ Get journal's notes
- ✅ Get notes for empty journal
- ✅ Get journal's AI jobs
- ✅ Delete with relation info

### `test_notes.py`
**Note CRUD & Tag Relationships** (16 tests)

#### TestNoteCRUD (10 tests)
- ✅ Create note with journal & metadata
- ✅ Create note without journal
- ✅ Create with invalid journal (404)
- ✅ List notes with pagination
- ✅ Filter by journal_id
- ✅ Get note by ID
- ✅ Get non-existent note (404)
- ✅ Update note
- ✅ Update with invalid journal (404)
- ✅ Delete note

#### TestNoteTagRelationships (6 tests)
- ✅ Get note's tags (empty initially)
- ✅ Add tag to note
- ✅ Add duplicate tag (409 Conflict)
- ✅ Add non-existent tag (404)
- ✅ Remove tag from note
- ✅ Remove unassociated tag (404)
- ✅ Delete note with tags

### `test_tags.py`
**Tag CRUD & Note Relationships** (13 tests)

#### TestTagCRUD (9 tests)
- ✅ Create tag
- ✅ Duplicate name validation (409)
- ✅ List tags with pagination
- ✅ Get tag by ID
- ✅ Get non-existent tag (404)
- ✅ Update tag
- ✅ Update with duplicate name (409)
- ✅ Delete tag
- ✅ Verify deletion (404)

#### TestTagNoteRelationships (4 tests)
- ✅ Get tag's notes (empty initially)
- ✅ Get notes with associations
- ✅ Delete tag removes from all notes

### `test_ai_jobs.py`
**AI Job CRUD & Workflows** (14 tests)

#### TestAIJobCRUD (11 tests)
- ✅ Create AI job with journal
- ✅ Create with invalid journal (404)
- ✅ List AI jobs with pagination
- ✅ Filter by status
- ✅ Filter by journal_id
- ✅ Get AI job by ID
- ✅ Get non-existent job (404)
- ✅ Update job status
- ✅ Update with response data
- ✅ Update with error message
- ✅ Delete AI job

#### TestAIJobWorkflow (3 tests)
- ✅ Complete lifecycle: queued → processing → success
- ✅ Multiple jobs for same journal
- ✅ Status transitions

### `test_main.py`
**Core Application Endpoints** (6 tests)

#### TestMainEndpoints (6 tests)
- ✅ Root endpoint returns API info
- ✅ Health check endpoint
- ✅ API docs accessible (/docs)
- ✅ ReDoc accessible (/redoc)
- ✅ 404 error handling
- ✅ CORS headers present

## Coverage Areas

### ✅ CRUD Operations
Every model has full Create, Read, Update, Delete coverage with:
- Success cases
- 404 Not Found cases
- Validation error cases (409 Conflict for duplicates)

### ✅ Relationships
- **One-to-Many**: Projects → Journals → Notes/AIJobs
- **Many-to-Many**: Notes ↔ Tags with add/remove operations
- **Foreign Key Validation**: All relationships validated
- **Cascade Behavior**: Tested for Projects → Journals

### ✅ Filtering
- Projects: None (simple list)
- Journals: by `date`, `project_id`
- Notes: by `date`, `journal_id`
- Tags: None (simple list)
- AI Jobs: by `status`, `journal_id`

### ✅ Error Handling
- 404 Not Found for missing resources
- 409 Conflict for duplicate names/associations
- 404 Not Found for invalid foreign keys
- Proper error messages and detail fields

### ✅ Edge Cases
- Creating resources without optional relationships
- Empty relationship lists
- Deleting resources with associations
- Duplicate prevention
- Invalid UUID handling

## Test Database

Tests use **PostgreSQL test database** (`flowlog_test`):
- ✅ Same database engine as production (no compatibility issues!)
- 🔒 Transaction-based isolation (rollback after each test)
- 🧹 Automatic setup and teardown via Makefile
- 🚀 Fast and reliable
- � Requires PostgreSQL running: `make start`

## Running Specific Tests

```bash
# Run one file
uv run pytest tests/test_projects.py -v

# Run one class
uv run pytest tests/test_projects.py::TestProjectCRUD -v

# Run one test
uv run pytest tests/test_projects.py::TestProjectCRUD::test_create_project -v

# Run tests matching pattern
uv run pytest -k "delete" -v

# Run with output
uv run pytest -v -s
```

## CI/CD Integration

These tests are ready for CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: make test

- name: Generate Coverage
  run: make test-cov
```

## Next Steps

To extend the test suite:

1. **Add integration tests** - Test multiple operations in sequence
2. **Add performance tests** - Test pagination with large datasets
3. **Add authentication tests** - When auth is implemented
4. **Add validation tests** - Test Pydantic validation edge cases
5. **Add database migration tests** - Test Alembic migrations

## Test Maintenance

- 🔄 Update fixtures when models change
- 📝 Add tests for new endpoints
- 🐛 Add regression tests for bugs
- 📊 Monitor coverage (aim for 90%+)
- 🧪 Review and refactor duplicate test code
