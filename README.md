# Flowlog API

A modern FastAPI-based journaling and note-taking application with PostgreSQL database and AI integration capabilities.

## Features

- 📝 **Journaling**: Create and manage journal entries
- 📓 **Notes**: Organize notes with tags and projects
- 🏷️ **Tags**: Flexible tagging system for organizing content
- 📂 **Projects**: Group related notes and journal entries
- 🤖 **AI Jobs**: Integration for AI-powered features
- 🔍 **RESTful API**: Clean, versioned API endpoints
- 🐘 **PostgreSQL**: Robust database with Alembic migrations
- 🐳 **Docker**: Containerized development and production environments
- ✅ **Testing**: Comprehensive test suite with pytest
- 🎨 **Code Quality**: Linting with Ruff and type checking with Pyright

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Package Manager**: uv
- **Python**: 3.12+
- **Container**: Docker & Docker Compose

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- PostgreSQL 15 (via Docker)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd flowlog-api
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Set up environment variables

Create a `.env` file in the root directory:

```env
# App settings
APP_NAME=Flowlog
DEBUG=True
VERSION=0.1.0
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://flowlog_user:flowlog_password@localhost:5432/flowlog

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520
ALGORITHM=HS256

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 4. Start the database

```bash
make start p=dev
```

This will start PostgreSQL in a Docker container.

### 5. Run database migrations

```bash
make migrate
```

### 6. Access the application

- **Development**: The app runs inside Docker at http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## Development

### Docker Profiles

The project supports two Docker profiles:

- **dev**: Development environment with hot-reload (port 8001)
- **prod**: Production environment (port 8002)

### Common Commands

```bash
# Start development environment
make start p=dev

# Stop containers
make stop p=dev

# View all available commands
make help
```

### Database Management

```bash
# Create a new migration
make genmigrations m="description of changes"

# Apply migrations
make migrate

# Reset database (removes volume)
make db-reset

# Drop and recreate database (keeps volume)
make db-drop
```

### Code Quality

```bash
# Run linter
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format

# Check formatting
make format-check

# Type checking
make typecheck

# Run all checks
make check

# Fix and format everything
make fix
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests in watch mode
make test-watch
```

Tests automatically create and drop a test database (`flowlog_test`).

## Project Structure

```
flowlog-api/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── app/
│   ├── api/
│   │   └── v1/          # API v1 endpoints
│   │       ├── ai_jobs.py
│   │       ├── journals.py
│   │       ├── notes.py
│   │       ├── projects.py
│   │       └── tags.py
│   ├── core/            # Core configuration
│   │   └── settings.py
│   ├── db/              # Database configuration
│   │   └── session.py
│   ├── models/          # SQLAlchemy models
│   │   ├── ai.py
│   │   ├── journal.py
│   │   ├── note.py
│   │   ├── project.py
│   │   └── tag.py
│   ├── schemas/         # Pydantic schemas
│   │   ├── ai.py
│   │   ├── journal.py
│   │   ├── note.py
│   │   ├── project.py
│   │   ├── tag.py
│   │   └── response.py
│   └── main.py          # FastAPI application
├── tests/               # Test suite
├── docker-compose.yaml  # Docker configuration
├── Dockerfile          # Multi-stage Docker build
├── Makefile            # Development commands
├── pyproject.toml      # Project dependencies
├── pytest.ini          # Pytest configuration
└── ruff.toml           # Ruff linter configuration
```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

### API v1 (prefix: `/api/v1`)

- **Projects**: `/api/v1/projects`
- **Journals**: `/api/v1/journals`
- **Notes**: `/api/v1/notes`
- **Tags**: `/api/v1/tags`
- **AI Jobs**: `/api/v1/ai-jobs`

Visit `/docs` for interactive API documentation.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | `Flowlog` |
| `DEBUG` | Debug mode | `False` |
| `VERSION` | API version | `0.1.0` |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `SECRET_KEY` | Secret key for security | (required) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `11520` (8 days) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`make check && make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.
