.PHONY: install test run clean docker-up docker-down docker-build docker-logs docker-shell

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
