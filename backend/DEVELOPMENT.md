# Backend Development Guide

This guide explains how to set up, develop, and extend the RepoLens backend, including working with Tree-sitter grammars and enabling AI features.

---

## 1. Backend Overview

- **Framework:** FastAPI (Python)
- **Parsing:** Tree-sitter (for TypeScript, TSX, and more)
- **AI Analysis:** OpenAI GPT (optional, for code quality and security insights)

---

## 2. Getting Started

### 2.1. Clone and Install

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.2. Environment Variables

- Copy `.env.example` to `.env` and set your OpenAI API key if you want AI features.

### 2.3. Running the Backend

```bash
uvicorn app.main:app --reload
```

---

## 3. Tree-sitter Grammar Setup

### 3.1. What is Tree-sitter?

Tree-sitter is a fast, incremental parsing system for programming tools. RepoLens uses it to extract files, functions, classes, imports, and call relationships from your codebase.

### 3.2. Building Grammars

#### **Option 1: Use Prebuilt Grammars (Recommended)**

- Install `tree_sitter_languages`:
  ```bash
  pip install tree_sitter-languages
  ```
- In your code, use:
  ```python
  from tree_sitter_languages import get_language
  ts_lang = get_language("typescript")
  ```

#### **Option 2: Build Your Own .so File**

- Clone the grammar repo (e.g., [tree-sitter-typescript](https://github.com/tree-sitter/tree-sitter-typescript))
- Build the shared library:
  ```python
  from tree_sitter import Language
  Language.build_library(
    'build/my-languages.so',
    [
      'tree-sitter-typescript/typescript',
      'tree-sitter-typescript/tsx',
    ]
  )
  ```
- Load the language (API depends on your tree_sitter version):
  - For **tree_sitter < 0.20.0**:
    ```python
    ts_lang = Language('build/my-languages.so', 'typescript')
    ```
  - For **tree_sitter >= 0.20.0**:
    ```python
    ts_lang = Language.load('build/tree-sitter-typescript.so')
    ```

---

## 4. Contributing

- Fork the repo and create a feature branch
- Write clear, well-documented code
- Add or update tests if needed
- Open a pull request with a clear description

---

## 5. Troubleshooting

- **Grammar loading errors:**
  - Ensure your `tree_sitter` and `tree_sitter_languages` versions are compatible
  - Rebuild your `.so` file if you change grammars
- **AI analysis errors:**
  - Check your OpenAI API key and environment variables
  - See [AI_SETUP.md](AI_SETUP.md) for more
- **General Python issues:**
  - Use a virtual environment
  - Check for missing dependencies

---

## 7. Useful Links

- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- [tree-sitter-languages PyPI](https://pypi.org/project/tree-sitter-languages/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
