# RepoLens

> **AI-Powered Codebase Analysis Platform**

RepoLens is an **AI-powered codebase analysis platform** that transforms repositories into interactive learning experiences. By combining **advanced code analysis**, **requirement mapping**, and **intelligent insights**, RepoLens helps developers understand, maintain, and learn from complex codebases.

Whether you're analyzing a new codebase, identifying technical debt, or learning from real-world projects, RepoLens provides the tools to **understand, analyze, and improve** code quality.

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Clone the repository

```bash
git clone https://github.com/otobongfp/repolens.git
cd repolens
```

### 2. Set up environment variables

**Backend:**
```bash
cd backend
cp example.env .env
# Edit .env with your configuration
```

**Frontend:**
```bash
cd frontend
cp env.example .env.local
# Edit .env.local with your API URL
```

### 3. Start services with Docker Compose

```bash
# Start all services (PostgreSQL, Redis, Neo4j, Backend)
docker-compose up -d

# Or start individual services
docker-compose up -d postgres redis neo4j
```

### 4. Set up the database

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Create initial data
python -c "from app.database.connection import init_db; import asyncio; asyncio.run(init_db())"
```

### 5. Start the development servers

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 6. Access the application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Documentation

- [Project Info & Vision](docs/INFO.md) – Project goals, milestones, and technical stack
- [Authentication Setup](AUTHENTICATION.md) – Configure OAuth and JWT authentication
- [Database Schema](docs/SCHEMA.md) – Database models and relationships
- [API Documentation](http://localhost:8000/docs) – Interactive API documentation

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

- Check issues labeled **good first issue** or **help wanted**
- Improve analysis accuracy, visualization quality, or user experience
- Add new analysis types, integrations, or enterprise features

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** - see the [LICENSE](LICENSE) file for details.


For commercial use or enterprise licensing, please contact the maintainers.
