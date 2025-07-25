# RepoLens

RepoLens is a full-stack codebase visualization and AI analysis tool. It helps developers understand, navigate, and improve large codebases by providing interactive visualizations, dependency graphs, function flows, and AI-powered code quality insights.

## Features

- **Code Graph Visualization**: Explore your codebase as a graph of files, functions, classes, and imports.
- **Dependency Matrix**: See file-to-file import relationships in a matrix view.
- **Function Flow**: Visualize function call chains and cross-file interactions.
- **Heatmap**: Identify code hotspots and complexity visually.
- **AI Code Analysis**: Get AI-generated code quality scores, vulnerability reports, and refactoring suggestions (powered by OpenAI).
- **Modern UI**: Built with Next.js, React, and D3.js for a beautiful, interactive experience.

## Architecture

- **Frontend**: Next.js (React, TypeScript, D3.js)
- **Backend**: FastAPI (Python), for AI analysis
- **Repolens-agent**: CLI Background agent (Rust), Tree-sitter for code parsing, and file analysis with local API exposed to web (Repo)[https://github.com/otobongfp/repolens-agent]

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-org/repolens.git
cd repolens
```

### 2. Install dependencies

- **Backend**:
  ```bash
  cd backend
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- **Frontend**:
  ```bash
  cd ../frontend
  npm install
  ```

### 3. Configure environment variables

- Copy `.env.example` to `.env` in the backend directory and set your OpenAI API key if you want AI features.

### 4. Start the servers

- **Backend**:
  ```bash
  cd backend
  uvicorn app.main:app --reload
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```

### 5. Open the app

Go to [http://localhost:3000](http://localhost:3000) in your browser.

## Documentation

- [Development Guide](backend/DEVELOPMENT.md): How to contribute, backend setup, grammar building, and more.
- [AI Setup](backend/AI_SETUP.md): How to enable and configure AI analysis.

## License

MIT
