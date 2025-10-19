# RepoLens Backend Documentation

Welcome to the RepoLens backend documentation. This directory contains all the documentation for setting up, developing, and deploying the RepoLens backend service.

## Quick Start

1. **Choose your development approach:**
   - [Local Development](DEVELOPMENT.md#local-development-backend-runs-locally-databases-in-docker) - Backend runs locally, databases in Docker
   - [Docker Development](DEVELOPMENT.md#docker-development-all-services-in-docker) - All services in Docker
   - [Production](DEVELOPMENT.md#production-environment) - Production deployment

2. **Set up your environment:**
   ```bash
   # For local development
   cp env.local.example .env
   make dev-local && make run
   
   # For Docker development  
   cp env.dev.example .env
   make dev
   
   # For production
   cp env.prod.example .env
   make prod
   ```

## Documentation Index

### Core Documentation
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Complete development guide with environment setup, commands, and workflows
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Detailed Docker Compose configuration and service management
- **[MIGRATIONS.md](MIGRATIONS.md)** - Database migration guide using Alembic

### Legacy Documentation
- **[DOCKER.md](DOCKER.md)** - Legacy Docker documentation (may be outdated)

## Project Structure

```
backend/
├── docs/                   # All documentation files
├── app/                    # FastAPI application code
├── alembic/               # Database migrations
├── docker-compose*.yml    # Docker configurations
├── env.*.example          # Environment templates
├── .env                   # Active environment file
├── Makefile              # Development commands
└── requirements.txt      # Python dependencies
```

## Common Commands

### Development
```bash
make dev-local    # Start databases only
make run          # Start backend locally
make dev          # Start all services in Docker
```

### Database Migrations
```bash
make migrate-up           # Run migrations locally
make docker-migrate-up    # Run migrations in Docker
```

### Code Quality
```bash
make format      # Format code with Black/isort
make lint        # Lint with Ruff
make type-check  # Type check with MyPy
```

## Getting Help

- Check the [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions
- Review [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker-specific issues
- See [MIGRATIONS.md](MIGRATIONS.md) for database migration help
- Look at the main [README.md](../README.md) for project overview

## Environment Files

The backend uses a single `.env` file that you create by copying the appropriate template:

- `env.local.example` → `.env` (for local development)
- `env.dev.example` → `.env` (for Docker development)  
- `env.prod.example` → `.env` (for production)

All `make` commands use this single `.env` file, making it simple to switch between environments.
