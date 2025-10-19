.PHONY: install test run clean init-db docker-up docker-down docker-build docker-logs docker-shell format lint type-check

# Set virtualenv activation command if needed
VENV_ACTIVATE=.venv/bin/activate

install:
	@echo "📦 Installing dependencies..."
	python3 -m venv .venv
	. $(VENV_ACTIVATE) && pip install --upgrade pip
	. $(VENV_ACTIVATE) && pip install -r requirements.txt
	@echo "✅ Environment ready"

test:
	@echo "🧪 Testing Tree-sitter grammars via tree-sitter-languages..."
	@python -c "\
from tree_sitter_languages import get_language;\
langs = ['python', 'javascript', 'typescript', 'tsx'];\
[print(f'✅ {lang} loaded') for lang in langs if get_language(lang)]"

run:
	@echo "🚀 Starting FastAPI server..."
	@. $(VENV_ACTIVATE) && uvicorn app.main:app --reload

clean:
	@echo "🧹 Cleaning virtualenv and pycache..."
	rm -rf __pycache__ */__pycache__ .venv .mypy_cache .pytest_cache .ruff_cache
	@echo "✅ Cleaned."

# Database commands
init-db:
	@echo "🗄️  Initializing database..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Please copy example.env to .env and configure your database URL"; \
		exit 1; \
	fi
	@if [ ! -d .venv ]; then \
		echo "⚠️  Virtual environment not found. Creating it first..."; \
		python3 -m venv .venv; \
		.venv/bin/pip install --upgrade pip; \
		.venv/bin/pip install psycopg2-binary python-dotenv; \
	fi
	@.venv/bin/python -c "\
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
import psycopg2; \
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT; \
\
# Get database URL from environment \
db_url = os.getenv('PGVECTOR_DB_URL'); \
if not db_url: \
    print('❌ PGVECTOR_DB_URL not found in environment'); \
    exit(1); \
\
print(f'📡 Connecting to: {db_url.split(\"@\")[1] if \"@\" in db_url else \"localhost\"}'); \
\
try: \
    # Connect to PostgreSQL \
    conn = psycopg2.connect(db_url); \
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT); \
    cursor = conn.cursor(); \
    \
    # Read and execute init script \
    with open('init-scripts/01-init-database.sql', 'r') as f: \
        sql_script = f.read(); \
    \
    # Split script into individual statements \
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]; \
    \
    for statement in statements: \
        if statement: \
            try: \
                cursor.execute(statement); \
                print(f'✅ Executed: {statement[:50]}...'); \
            except Exception as e: \
                if 'already exists' in str(e) or 'duplicate' in str(e).lower(): \
                    print(f'⚠️  Skipped (already exists): {statement[:50]}...'); \
                else: \
                    print(f'❌ Error: {e}'); \
                    raise; \
    \
    cursor.close(); \
    conn.close(); \
    print('✅ Database initialization completed successfully'); \
\
except Exception as e: \
    print(f'❌ Database initialization failed: {e}'); \
    exit(1); \
"
	@echo "✅ Database ready!"

# Docker commands
docker-up:
	@echo "🐳 Starting RepoLens services with Docker..."
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found. Copying example.env to .env"; \
		cp example.env .env; \
		echo "📝 Please edit .env with your actual values"; \
	fi
	docker compose up -d
	@echo "✅ Services started. Check status with 'make docker-logs'"

docker-down:
	@echo "🛑 Stopping RepoLens services..."
	docker compose down
	@echo "✅ Services stopped"

docker-build:
	@echo "🔨 Building Docker images..."
	docker compose build
	@echo "✅ Images built"

docker-logs:
	@echo "📋 Showing service logs..."
	docker compose logs -f

docker-shell:
	@echo "🐚 Opening backend container shell..."
	docker compose exec backend bash

docker-reset:
	@echo "🔄 Resetting all Docker data..."
	docker compose down -v
	docker compose build --no-cache
	@echo "✅ Reset complete. Run 'make docker-up' to start fresh"

# Docker Compose Commands
.PHONY: dev prod dev-db prod-db dev-backend prod-backend dev-stop prod-stop dev-logs prod-logs

# Development Environment
dev:
	@echo "🚀 Starting development environment..."
	@docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env --profile all up -d
	@echo "✅ Development environment started"
	@echo "✅ Backend: http://localhost:8000"
	@echo "✅ Neo4j: http://localhost:7474"
	@echo "✅ PostgreSQL: localhost:5433"
	@echo "✅ Redis: localhost:6379"

dev-db:
	@echo "🗄️ Starting development databases only..."
	@docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env --profile databases up -d
	@echo "✅ Development databases started"

dev-backend:
	@echo "🔧 Starting development backend..."
	@docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env --profile backend up -d
	@echo "✅ Development backend started"

dev-stop:
	@echo "🛑 Stopping development environment..."
	@docker compose -f docker-compose.yml -f docker-compose.dev.yml down
	@echo "✅ Development environment stopped"

dev-logs:
	@echo "📋 Development logs..."
	@docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Production Environment
prod:
	@echo "🚀 Starting production environment..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env up -d
	@echo "✅ Production environment started"

prod-db:
	@echo "🗄️ Starting production databases only..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env --profile databases-only up -d
	@echo "✅ Production databases started"

prod-backend:
	@echo "🔧 Starting production backend..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env --profile backend up -d
	@echo "✅ Production backend started"

prod-stop:
	@echo "🛑 Stopping production environment..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml down
	@echo "✅ Production environment stopped"

prod-logs:
	@echo "📋 Production logs..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Local Development (without Docker backend)
dev-local:
	@echo "🏠 Starting local development..."
	@docker compose -f docker-compose.yml --profile databases up -d
	@echo "✅ Databases started. Run 'make run' to start backend locally"
	@echo "📊 Neo4j: http://localhost:7474"
	@echo "📊 PostgreSQL: localhost:5433"
	@echo "📊 Redis: localhost:6379"

dev-local-stop:
	@echo "🛑 Stopping local development databases..."
	@docker compose -f docker-compose.yml --profile databases down
	@echo "✅ Local development databases stopped"

# Database Migration Commands
.PHONY: migrate-up migrate-down migrate-revision migrate-history migrate-current migrate-check

migrate-up:
	@echo "🔄 Running database migrations..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && alembic upgrade head
	@echo "✅ Migrations completed"

migrate-down:
	@echo "⬇️ Rolling back database migrations..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && alembic downgrade -1
	@echo "✅ Migration rollback completed"

migrate-revision:
	@echo "📝 Creating new migration..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	@read -p "Enter migration message: " message; \
	. $(VENV_ACTIVATE) && alembic revision --autogenerate -m "$$message"
	@echo "✅ New migration created"

migrate-history:
	@echo "📋 Migration history..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && alembic history

migrate-current:
	@echo "📍 Current migration status..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && alembic current

migrate-check:
	@echo "🔍 Checking migration status..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && alembic check

# Docker Migration Commands
.PHONY: docker-migrate-up docker-migrate-down docker-migrate-revision docker-migrate-history docker-migrate-current

docker-migrate-up:
	@echo "🔄 Running database migrations in Docker..."
	@docker compose exec backend alembic upgrade head
	@echo "✅ Docker migrations completed"

docker-migrate-down:
	@echo "⬇️ Rolling back database migrations in Docker..."
	@docker compose exec backend alembic downgrade -1
	@echo "✅ Docker migration rollback completed"

docker-migrate-revision:
	@echo "📝 Creating new migration in Docker..."
	@read -p "Enter migration message: " message; \
	docker compose exec backend alembic revision --autogenerate -m "$$message"
	@echo "✅ New Docker migration created"

docker-migrate-history:
	@echo "📋 Docker migration history..."
	@docker compose exec backend alembic history

docker-migrate-current:
	@echo "📍 Current Docker migration status..."
	@docker compose exec backend alembic current

docker-migrate-check:
	@echo "🔍 Checking Docker migration status..."
	@docker compose exec backend alembic check

# Code formatting and linting commands
format:
	@echo "🎨 Formatting code with black and isort..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && black app/
	. $(VENV_ACTIVATE) && isort app/
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Linting code with ruff..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && ruff check app/ --fix
	@echo "✅ Linting complete"

type-check:
	@echo "🔬 Type checking with mypy..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && mypy app/
	@echo "✅ Type checking complete"

format-check:
	@echo "🔍 Checking code formatting..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first"; \
		exit 1; \
	fi
	. $(VENV_ACTIVATE) && black --check app/
	. $(VENV_ACTIVATE) && isort --check-only app/
	. $(VENV_ACTIVATE) && ruff check app/
	@echo "✅ All formatting checks passed"

pre-commit:
	@echo "🚀 Running pre-commit checks..."
	@make format-check
	@make type-check
	@echo "✅ All pre-commit checks passed"
