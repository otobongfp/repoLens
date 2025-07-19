# Backend Development Guide

## Overview

This guide covers backend development for RepoLens, including setup, architecture, and best practices. **Note:** As of the latest update, we no longer use custom Tree-sitter grammars or build scripts. We now use pre-built Tree-sitter language packages for code parsing, and the AI analysis system is being upgraded to support advanced token limit strategies.

---

## 1. Setup

### Prerequisites

- Python 3.9+
- (Recommended) Virtual environment
- OpenAI API key (for AI features)

### Installation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and set your OpenAI API key and other settings as needed.

---

## 2. Architecture

- **FastAPI** backend
- **Tree-sitter** (pre-built language packages) for code parsing
- **OpenAI** for AI-powered code analysis
- **Modular features**: code analysis, AI analysis, etc.

---

## 3. Code Parsing

- We **no longer build or compile grammars**.
- The backend uses **pre-built Tree-sitter language packages** (e.g., `tree-sitter-typescript`).
- All grammar build scripts and custom grammar directories have been removed.
- If you need to support a new language, install the appropriate pre-built Tree-sitter package.

---

## 4. AI Analysis

- The AI analysis system uses OpenAI's GPT models.
- We are moving towards **advanced token limit strategies** (see `TOKEN_LIMIT_STRATEGIES.md`).
- The system is designed to handle large codebases by chunking, hierarchical context, and semantic search.

---

## 5. Running the Backend

```bash
uvicorn app.main:app --reload
```

---

## 6. Testing

- Use `pytest` for backend tests (if/when available).
- Ensure your environment variables are set for any tests that require OpenAI.

---

## 7. Contributing

- Follow standard Python best practices.
- Write clear, modular code.
- Document new features and update this guide as needed.

---

## 8. Troubleshooting

- If AI analysis is disabled, check your OpenAI API key and environment variables.
- For code parsing issues, ensure the correct pre-built Tree-sitter packages are installed.

---

## 9. References

- [AI Setup Guide](AI_SETUP.md)
- [Token Limit Strategies](docs/TOKEN_LIMIT_STRATEGIES.md)
