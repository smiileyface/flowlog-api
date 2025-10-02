# Test Setup Guide

## Quick Start

### 1. Start PostgreSQL
```bash
make start p=dev
```

### 2. Run Tests
```bash
make test
```

That's it! The test database is automatically created and cleaned up.

## What Happens When You Run Tests

1. **Test database creation**: `flowlog_test` database is created
2. **Schema setup**: All tables are created once per test session
3. **Test execution**: Each test runs in an isolated transaction
4. **Rollback**: Transactions are rolled back after each test (clean state)
5. **Cleanup**: Test database is dropped after all tests complete

## Manual Test Database Management

### Create test database manually
```bash
make test-db-create
```

### Drop test database manually
```bash
make test-db-drop
```

### Useful for debugging
If you want to inspect the test database after tests fail:
```bash
# Create test DB
make test-db-create

# Run specific test
uv run pytest tests/test_projects.py::TestProjectCRUD::test_create_project -v

# Database remains available for inspection
psql postgresql://flowlog_user:flowlog_password@localhost:5432/flowlog_test

# Clean up when done
make test-db-drop
```

## Advantages of PostgreSQL Test Database

### ✅ Production Parity
- Same database engine as production
- JSONB, UUID, and all PostgreSQL features work exactly the same
- No SQLite compatibility issues

### ✅ Fast & Reliable
- Transaction rollback is faster than recreating tables
- Each test is truly isolated
- Parallel test execution possible (with pytest-xdist)

### ✅ Debugging Friendly
- Can connect to test database during debugging
- Can inspect data after test failures
- Same tools (psql, pgAdmin) work

## Test Isolation

Each test gets a clean database state through **transaction rollback**:

```python
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()  # ← Rolls back all changes
        connection.close()
```

This means:
- ✅ Fast (no table recreation)
- ✅ Isolated (each test starts with empty tables)
- ✅ Safe (can't corrupt test database permanently)

## Troubleshooting

### PostgreSQL not running
```bash
# Check if running
docker ps | grep postgres

# Start if not running
make start p=dev
```

### Test database already exists
```bash
# Drop and recreate
make test-db-drop
make test-db-create
```

### Connection refused
```bash
# Check PostgreSQL is accessible
psql postgresql://flowlog_user:flowlog_password@localhost:5432/postgres -c "SELECT 1"

# Check credentials in conftest.py match docker-compose.yaml
```

### Tests hanging
```bash
# Make sure no other process is using the test database
# Drop and recreate
make test-db-drop
```

## CI/CD Integration

For GitHub Actions or similar:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: flowlog_user
      POSTGRES_PASSWORD: flowlog_password
      POSTGRES_DB: postgres
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

steps:
  - name: Setup test database
    run: |
      PGPASSWORD=flowlog_password psql -h localhost -U flowlog_user -d postgres -c "CREATE DATABASE flowlog_test;"
  
  - name: Run tests
    run: uv run pytest tests/ -v
```

## Performance Tips

### Run tests in parallel (requires pytest-xdist)
```bash
# Install pytest-xdist
uv add --dev pytest-xdist

# Run with multiple workers
uv run pytest tests/ -n auto -v
```

### Run only failed tests
```bash
# First run
make test

# Rerun only failures
uv run pytest tests/ --lf -v
```

### Run tests matching a pattern
```bash
# Only project tests
uv run pytest tests/test_projects.py -v

# Only CRUD tests
uv run pytest -k "CRUD" -v

# Only relationship tests
uv run pytest -k "Relationship" -v
```
