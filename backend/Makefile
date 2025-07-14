.PHONY: install test run clean

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
