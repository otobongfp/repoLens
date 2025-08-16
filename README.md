# RepoLens

> **Learn, Build, Improve**

RepoLens is an **open-source education and developer improvement platform**. It helps learners, students, and developers **understand codebases, complete coding tasks, get scored on their work, and continuously improve** through AI-powered feedback and visualization tools.

Whether you're a beginner learning to code, a student completing assignments, or a developer navigating a large codebase, RepoLens provides the tools to **learn, practice, and grow**.

---

## Features

### Learning & Education

- **Learning Paths** – structured challenges and project-based tasks to guide learners.
- **Task Management** – create, assign, and track coding exercises or projects.
- **Automated Scoring** – correctness tests, style checks, and AI-driven evaluations.
- **Progress Tracking** – dashboards showing improvement, scores, and completion rates.
- **AI Feedback & Hints** – contextual suggestions, resources, and improvement tips.

### Code Understanding

- **Code Graph Visualization** – explore files, functions, classes, and imports as an interactive graph.
- **Dependency Matrix** – view file-to-file import relationships in a clear matrix view.
- **Function Flow** – trace function calls across files and modules.
- **Heatmaps** – visually identify complexity hotspots in the codebase.
- **AI Code Insights** – detect vulnerabilities, measure quality, and receive refactoring suggestions.

### Collaboration & Community

- **Assignments for Educators** – instructors can create tasks, auto-grade submissions, and share resources.
- **Peer & AI Review** – students and developers receive both human and AI feedback.
- **Open Learning** – learn from public repos and share your progress.

---

## Architecture

RepoLens is a hybrid stack designed for extensibility:

- **Frontend** – Next.js (React, TypeScript, D3.js) for interactive UI.
- **Backend** – FastAPI (Python) for API and orchestration.
- **Local Agent** – Rust (Axum) for secure, high-performance repo parsing and analysis.
- **AI Layer** – OpenAI (or other LLMs) for feedback, scoring, and suggestions.
- **Database** – PostgreSQL for user data, progress tracking, and reports.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/otobongfp/repolens.git
cd repolens
```

### 2. Install dependencies

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**

```bash
cd ../frontend
npm install
```

### 3. Configure environment variables

Copy `.env.example` → `.env` in `backend` and set your variables (e.g., API keys).

### 4. Start the servers

**Backend:**

```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Documentation

- [Development Guide](backend/DEVELOPMENT.md) – backend setup, grammar building, contributing.
- [AI Setup](backend/AI_SETUP.md) – enable and configure AI features.
- [Education Module](docs/LEARNING.md) – manage tasks, scoring, and progress.

---

## Roadmap

- ✅ Repo visualization & AI code analysis
- 🚧 Automated scoring engine (tests + AI evaluation)
- 🔜 Learning paths & task management
- 🔜 Student dashboards & progress reports
- 🌍 Open community of learners, educators, and contributors

---

## 📄 License

Apache License 2.0
