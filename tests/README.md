# Tests

This directory contains the test suite for the FlowLog application using pytest.

## Test Structure

```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── test_main.py          # Tests for main app endpoints
├── test_projects.py      # Tests for project CRUD and relationships
├── test_journals.py      # Tests for journal CRUD and relationships
├── test_notes.py         # Tests for note CRUD and tag relationships
├── test_tags.py          # Tests for tag CRUD and note relationships
└── test_ai_jobs.py       # Tests for AI job CRUD and workflows
```

## Running Tests

### Run all tests
```bash
make test
```

### Run tests with coverage report
```bash
make test-cov
```

### Run tests in watch mode (auto-rerun on file changes)
```bash
make test-watch
```

### Run specific test file
```bash
uv run pytest tests/test_projects.py -v
```

### Run specific test class
```bash
uv run pytest tests/test_projects.py::TestProjectCRUD -v
```

### Run specific test function
```bash
uv run pytest tests/test_projects.py::TestProjectCRUD::test_create_project -v
```

## Test Coverage

The test suite covers:

### Projects API
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Name uniqueness validation
- ✅ Conflict detection
- ✅ Getting project's journals
- ✅ Cascade delete behavior

### Journals API
- ✅ CRUD operations
- ✅ Project relationship validation
- ✅ Filtering by project_id and date
- ✅ Getting journal's notes and AI jobs
- ✅ Relationship cascade behavior

### Notes API
- ✅ CRUD operations
- ✅ Journal relationship validation
- ✅ Filtering by journal_id and date
- ✅ Tag associations (many-to-many)
- ✅ Adding/removing tags
- ✅ Duplicate tag prevention

### Tags API
- ✅ CRUD operations
- ✅ Name uniqueness validation
- ✅ Getting tag's notes
- ✅ Note relationship management

### AI Jobs API
- ✅ CRUD operations
- ✅ Journal relationship validation (required)
- ✅ Status transitions (queued → processing → success/error)
- ✅ Filtering by status and journal_id
- ✅ Response data handling
- ✅ Error handling

### Main Endpoints
- ✅ Root endpoint
- ✅ Health check
- ✅ API documentation access
- ✅ 404 error handling
- ✅ CORS configuration

## Test Database

Tests use a **PostgreSQL test database** (`flowlog_test`) that:
- Uses the same database engine as production (no compatibility issues!)
- Is automatically created before tests and dropped after
- Uses transactions that rollback after each test for isolation
- Independent from the development database (`flowlog`)
- Requires PostgreSQL to be running (via `make start`)

## Fixtures

Available fixtures in `conftest.py`:

- `db_session` - Fresh database session for each test
- `client` - FastAPI TestClient with test database
- `sample_project` - Pre-created test project
- `sample_journal` - Pre-created test journal (linked to sample_project)
- `sample_note` - Pre-created test note (linked to sample_journal)
- `sample_tag` - Pre-created test tag
- `sample_ai_job` - Pre-created test AI job (linked to sample_journal)

## Writing New Tests

### Example test structure:

```python
def test_my_feature(client, sample_project):
    """Test description."""
    # Arrange - setup test data
    data = {"name": "Test"}
    
    # Act - perform the action
    response = client.post("/api/v1/endpoint/", json=data)
    
    # Assert - verify results
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Test"
```

### Using fixtures:

```python
def test_with_existing_data(client, sample_journal, sample_note):
    """Test can use multiple fixtures."""
    # sample_journal and sample_note are already created
    response = client.get(f"/api/v1/journals/{sample_journal['id']}/notes")
    assert response.status_code == 200
```

## Test Organization

Tests are organized by resource and grouped into classes:

- `TestResourceCRUD` - Basic CRUD operation tests
- `TestResourceRelationships` - Relationship and association tests
- `TestResourceWorkflow` - Complex workflow scenarios

This structure makes it easy to:
- Find tests for specific functionality
- Run related tests together
- Understand test coverage at a glance
