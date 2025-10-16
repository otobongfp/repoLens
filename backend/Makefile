.PHONY: install test run clean init-db docker-up docker-down docker-build docker-logs docker-shell

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
