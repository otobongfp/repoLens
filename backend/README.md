# RepoLens Backend

A FastAPI backend that provides AI-powered code analysis capabilities for the RepoLens platform.

## Quick Start

1. **Choose your development approach:**
   - [Local Development](docs/DEVELOPMENT.md#local-development-backend-runs-locally-databases-in-docker) - Backend runs locally, databases in Docker
   - [Docker Development](docs/DEVELOPMENT.md#docker-development-all-services-in-docker) - All services in Docker
   - [Production](docs/DEVELOPMENT.md#production-environment) - Production deployment

2. **Set up your environment:**
   ```bash
   # For local development
   cp env.local.example .env
   make dev-local && make run
   
   # For Docker development  
   cp env.dev.example .env
   make dev
   ```

## Documentation

All detailed documentation is organized in the [`docs/`](docs/) folder:

- **[docs/README.md](docs/README.md)** - Documentation index and quick start
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Complete development guide
- **[docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)** - Docker configuration details
- **[docs/MIGRATIONS.md](docs/MIGRATIONS.md)** - Database migration guide

## Architecture

This backend provides:
- **AI Code Analysis**: Analyze codebases using OpenAI's GPT models
- **Authentication**: JWT-based user authentication with OAuth support
- **Project Management**: Multi-tenant project organization
- **Database Integration**: PostgreSQL with pgvector, Neo4j graph database
- **Caching**: Redis-based caching for performance

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/oauth/google` - Google OAuth
- `POST /api/v1/auth/oauth/github` - GitHub OAuth

### Projects
- `GET /api/v1/projects` - List user projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details

### AI Analysis
- `POST /api/v1/ai/analyze` - Analyze entire codebase
- `POST /api/v1/ai/analyze-function` - Analyze specific function
- `POST /api/v1/ai/ask` - Ask questions about codebase

## Environment Setup

The backend uses a single `.env` file created from templates:

- `env.local.example` → `.env` (for local development)
- `env.dev.example` → `.env` (for Docker development)  
- `env.prod.example` → `.env` (for production)

## Common Commands

```bash
make dev-local    # Start databases only
make run          # Start backend locally
make dev          # Start all services in Docker
make format       # Format code
make lint         # Lint code
make migrate-up   # Run database migrations
```

## Integration

This backend works with:
- **RepoLens Frontend**: Next.js frontend application
- **External Services**: OpenAI API, OAuth providers
- **Databases**: PostgreSQL (with pgvector), Neo4j, Redis
