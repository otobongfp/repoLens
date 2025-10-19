# RepoLens Docker Setup

This setup provides flexible Docker Compose configurations for both development and production environments.

## 🚀 Quick Start

### Development Mode
```bash
# Start all services (databases + backend)
make dev

# Start only databases (for local backend development)
make dev-db

# Start only backend (if databases are already running)
make dev-backend

# Stop development environment
make dev-stop

# View logs
make dev-logs
```

### Production Mode
```bash
# Start production environment
make prod

# Start only databases
make prod-db

# Start only backend
make prod-backend

# Stop production environment
make prod-stop

# View logs
make prod-logs
```

## Manual Commands

### Development
```bash
# Start all services
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up -d

# Start only databases
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev --profile databases up -d

# Start only backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev --profile backend up -d
```

### Production
```bash
# Start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d

# Start only databases
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod --profile databases-only up -d

# Start only backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod --profile backend up -d
```

## Configuration Files

- `docker-compose.yml` - Base configuration with environment variables
- `docker-compose.dev.yml` - Development overrides
- `docker-compose.prod.yml` - Production overrides
- `env.dev.example` - Development environment template
- `env.prod.example` - Production environment template

## Environment Flexibility

### Development Scenarios

1. **Full Docker Development**: All services in Docker
   ```bash
   make dev
   # Uses Docker service names: neo4j:7687, postgres:5432, redis:6379
   ```

2. **Local Backend + Docker Databases**: Run backend locally, databases in Docker
   ```bash
   make dev-local
   # Then run backend locally: make run
   # Uses localhost with exposed ports: localhost:7687, localhost:5433, localhost:6379
   ```

3. **External Databases**: Use external database services
   ```bash
   # Edit .env.dev to use external URLs:
   # NEO4J_URI=bolt://your-neo4j-host:7687
   # PGVECTOR_DB_URL=postgresql://user:pass@your-postgres-host:5432/vectordb
   # REDIS_URL=redis://your-redis-host:6379
   make dev-backend
   ```

### Production Scenarios

1. **Full Docker Production**: All services in Docker
   ```bash
   make prod
   ```

2. **External Databases**: Use external database services
   ```bash
   # Edit .env.prod to use external URLs
   make prod-backend
   ```

3. **Database-Only**: Run databases in Docker, backend elsewhere
   ```bash
   make prod-db
   ```

## Service URLs

### Development (with port exposure)
- **Backend API**: http://localhost:8000
- **Neo4j Browser**: http://localhost:7474
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6379

### Production (internal networking)
- **Backend API**: http://backend:8000 (internal)
- **Neo4j**: bolt://neo4j:7687 (internal)
- **PostgreSQL**: postgres:5432 (internal)
- **Redis**: redis:6379 (internal)

## Environment Variables

### Key Configuration Options

- `ENVIRONMENT`: `development` or `production`
- `NEO4J_URI`: Neo4j connection string
- `PGVECTOR_DB_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `CORS_ORIGINS`: Allowed frontend origins
- `OPENAI_API_KEY`: OpenAI API key
- `JWT_SECRET_KEY`: JWT signing key

### Database URLs

**Docker Backend + Docker Databases**:
- `NEO4J_URI=bolt://neo4j:7687`
- `PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb`
- `REDIS_URL=redis://redis:6379`

**Local Backend + Docker Databases**:
- `NEO4J_URI=bolt://localhost:7687`
- `PGVECTOR_DB_URL=postgresql://repolens:password@localhost:5433/vectordb`
- `REDIS_URL=redis://localhost:6379`

**External Services**:
- `NEO4J_URI=bolt://your-neo4j-host:7687`
- `PGVECTOR_DB_URL=postgresql://user:pass@your-postgres-host:5432/vectordb`
- `REDIS_URL=redis://your-redis-host:6379`

## Profiles

- `databases`: Start only database services
- `backend`: Start only backend service
- `all`: Start all services (default)
- `databases-only`: Production databases only

## Troubleshooting

### CORS Issues
Make sure your frontend URL is in `CORS_ORIGINS`:
```bash
# Development
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Production
CORS_ORIGINS=["https://yourdomain.com"]
```

### Database Connection Issues
Check that database URLs are correct:
```bash
# Test Neo4j connection
docker compose exec backend python -c "import asyncio; import asyncpg; asyncio.run(asyncpg.connect('postgresql://repolens:password@postgres:5432/vectordb'))"
```

### Port Conflicts
Change ports in environment file:
```bash
POSTGRES_PORT=5434  # Instead of 5433
REDIS_PORT=6380     # Instead of 6379
```

## Monitoring

```bash
# View service status
docker compose ps

# View logs
docker compose logs -f [service-name]

# Health checks
curl http://localhost:8000/api/v1/health/
```
