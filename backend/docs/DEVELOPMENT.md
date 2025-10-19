# Development Guide

This guide explains how to set up and run RepoLens backend in different environments.

## Environment Configurations

### Local Development (Backend runs locally, databases in Docker)

**Use case**: When you want to run the backend with uvicorn for hot reloading and debugging, but use Docker for databases.

**Setup**:
1. Copy environment template:
   ```bash
   cp env.local.example .env
   ```

2. Start databases only:
   ```bash
   make dev-local
   ```

3. Start backend locally:
   ```bash
   make run
   ```

**Environment Variables** (`.env`):
- Uses `env.local.example` as template
- Database URLs point to `localhost` with exposed ports:
  - `NEO4J_URI=bolt://localhost:7687`
  - `PGVECTOR_DB_URL=postgresql://repolens:password@localhost:5433/vectordb`
  - `REDIS_URL=redis://localhost:6379`
- Backend runs on `localhost:8000`

**Ports**:
- Neo4j: `localhost:7474` (HTTP), `localhost:7687` (Bolt)
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6379`
- Backend: `localhost:8000`

### Docker Development (All services in Docker)

**Use case**: When you want everything running in Docker containers for consistency.

**Setup**:
1. Copy environment template:
   ```bash
   cp env.dev.example .env
   ```

2. Start all services:
   ```bash
   make dev
   ```

**Environment Variables** (`.env`):
- Uses `env.dev.example` as template
- Database URLs use Docker service names:
  - `NEO4J_URI=bolt://neo4j:7687`
  - `PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb`
  - `REDIS_URL=redis://redis:6379`
- Backend runs in Docker container

**Ports**:
- Neo4j: `localhost:7474` (HTTP), `localhost:7687` (Bolt)
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6379`
- Backend: `localhost:8000`

### Production Environment

**Use case**: Production deployment with external services.

**Setup**:
1. Copy environment template:
   ```bash
   cp env.prod.example .env
   ```

2. Configure production values in `.env`

3. Start production services:
   ```bash
   make prod
   ```

**Environment Variables** (`.env`):
- Uses `env.prod.example` as template
- Database URLs point to production services
- Security settings enabled
- Production logging and monitoring

## Environment File Templates

### env.local.example
For local backend development with Docker databases:
- Database URLs use `localhost` with exposed ports
- Development-friendly settings
- Debug logging enabled

### env.dev.example
For Docker development environment:
- Database URLs use Docker service names
- Development settings
- Hot reload enabled

### env.prod.example
For production deployment:
- External database URLs
- Production security settings
- Optimized logging

## Database Migrations

### Local Backend (with Docker databases)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run migrations
make migrate-up

# Create new migration
make migrate-revision

# Check status
make migrate-current
```

### Docker Backend
```bash
# Run migrations in Docker container
make docker-migrate-up

# Create new migration in Docker
make docker-migrate-revision

# Check status in Docker
make docker-migrate-current
```

## Common Commands

### Starting Services
```bash
# Local backend with Docker databases
cp env.local.example .env && make dev-local && make run

# All services in Docker
cp env.dev.example .env && make dev

# Production
cp env.prod.example .env && make prod
```

### Stopping Services
```bash
# Stop local databases
make dev-local-stop

# Stop Docker development
make dev-stop

# Stop production
make prod-stop
```

### Logs and Debugging
```bash
# View Docker logs
make dev-logs

# View production logs
make prod-logs
```

## Troubleshooting

### Port Conflicts
If you get port conflicts:
- Check what's running: `lsof -i :8000`
- Stop conflicting services
- Use different ports in environment files

### Database Connection Issues
- Verify databases are running: `docker ps`
- Check environment variables match your setup
- Ensure correct URLs (localhost vs Docker service names)

### Migration Issues
- Ensure database is running before migrations
- Check environment variables are loaded correctly
- Use `make migrate-check` to verify migration status

## Environment Variable Priority

1. System environment variables (highest priority)
2. `.env` file in backend directory
3. Default values in `config.py` (lowest priority)

## Development Workflow

### Recommended: Local Backend + Docker Databases
1. `cp env.local.example .env` - Setup environment
2. `make dev-local` - Start databases
3. `make run` - Start backend with hot reload
4. Make changes to code
5. Backend automatically reloads

### Alternative: Full Docker Development
1. `cp env.dev.example .env` - Setup environment
2. `make dev` - Start all services
3. Make changes to code
4. Rebuild container: `docker compose build backend`

## Security Notes

- Never commit `.env` files to version control
- Use strong passwords in production
- Enable HTTPS in production
- Configure proper CORS origins
- Use environment-specific secrets

## File Structure

```
backend/
├── .env                    # Active environment file (copied from examples)
├── env.local.example      # Template for local development
├── env.dev.example        # Template for Docker development
├── env.prod.example       # Template for production
├── docker-compose.yml     # Base Docker configuration
├── docker-compose.dev.yml # Development overrides
├── docker-compose.prod.yml# Production overrides
└── Makefile              # Common commands
```
