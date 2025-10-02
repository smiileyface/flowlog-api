UV_RUN=uv run
p=dev

# Docker commands
start:
	@docker compose --profile "$(p)" up --build -d

stop:
	@docker compose --profile "$(p)" down

# Database migrations
genmigrations:
	$(UV_RUN) alembic revision --autogenerate -m "$(m)"

migrate:
	$(UV_RUN) alembic upgrade head

db-reset:
	@echo "🗑️  Resetting database..."
	@docker compose --profile "$(p)" down
	@docker volume rm flowlog_postgres_data || true
	@echo "✅ Database volume removed"
	@docker compose --profile "$(p)" up -d postgres
	@echo "⏳ Waiting for PostgreSQL to be ready..."
	@sleep 5
	@$(UV_RUN) alembic upgrade head
	@echo "✅ Database reset and migrations applied!"

db-drop:
	@echo "🗑️  Dropping and recreating database..."
	@docker exec flowlog_postgres psql -U flowlog_user -d postgres -c "DROP DATABASE IF EXISTS flowlog;"
	@docker exec flowlog_postgres psql -U flowlog_user -d postgres -c "CREATE DATABASE flowlog;"
	@echo "✅ Database dropped and recreated!"
	@$(UV_RUN) alembic upgrade head
	@echo "✅ Migrations applied!"

# Test database setup
test-db-create:
	@echo "🔧 Creating test database..."
	@docker exec flowlog_postgres psql -U flowlog_user -d postgres -c "DROP DATABASE IF EXISTS flowlog_test;" 2>/dev/null || true
	@docker exec flowlog_postgres psql -U flowlog_user -d postgres -c "CREATE DATABASE flowlog_test;"
	@echo "✅ Test database created!"

test-db-drop:
	@echo "🗑️  Dropping test database..."
	@docker exec flowlog_postgres psql -U flowlog_user -d postgres -c "DROP DATABASE IF EXISTS flowlog_test;" 2>/dev/null || true
	@echo "✅ Test database dropped!"

# Code quality
lint:
	@echo "Running Ruff linter..."
	$(UV_RUN) ruff check .

lint-fix:
	@echo "Running Ruff linter with auto-fix..."
	$(UV_RUN) ruff check --fix .

format:
	@echo "Running Ruff formatter..."
	$(UV_RUN) ruff format .

format-check:
	@echo "Checking code formatting..."
	$(UV_RUN) ruff format --check .

typecheck:
	@echo "Running Pyright type checker..."
	$(UV_RUN) pyright

# Testing
test:
	@echo "🧪 Running tests with pytest..."
	@$(MAKE) test-db-create
	@$(UV_RUN) pytest tests/ -v
	@$(MAKE) test-db-drop

test-cov:
	@echo "🧪 Running tests with coverage..."
	@$(MAKE) test-db-create
	@$(UV_RUN) pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
	@$(MAKE) test-db-drop

test-watch:
	@echo "🧪 Running tests in watch mode..."
	@$(MAKE) test-db-create
	@echo "⚠️  Note: Test database will remain active. Run 'make test-db-drop' when done."
	@$(UV_RUN) pytest-watch tests/ -- -v

# Combined checks
check: format-check lint typecheck
	@echo "✅ All checks passed!"

# Fix and format everything
fix: lint-fix format
	@echo "✅ Code fixed and formatted!"

# Show help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Docker:"
	@echo "  make start [p=dev|prod]  - Start Docker containers"
	@echo "  make stop [p=dev|prod]   - Stop Docker containers"
	@echo ""
	@echo "Database:"
	@echo "  make genmigrations m='message' - Generate migration"
	@echo "  make migrate             - Run migrations"
	@echo "  make db-reset            - Reset database (remove volume and recreate)"
	@echo "  make db-drop             - Drop and recreate database (keep volume)"
	@echo ""
	@echo "Testing:"
	@echo "  make test                - Run tests (auto-creates/drops test DB)"
	@echo "  make test-cov            - Run tests with coverage report"
	@echo "  make test-watch          - Run tests in watch mode"
	@echo "  make test-db-create      - Create test database"
	@echo "  make test-db-drop        - Drop test database"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                - Run linter"
	@echo "  make lint-fix            - Run linter with auto-fix"
	@echo "  make format              - Format code"
	@echo "  make format-check        - Check code formatting"
	@echo "  make typecheck           - Run type checker"
	@echo "  make check               - Run all checks (format, lint, type)"
	@echo "  make fix                 - Fix and format all code"
