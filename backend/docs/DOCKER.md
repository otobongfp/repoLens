# RepoLens Backend - Docker Setup

This directory contains Docker configuration for running the RepoLens backend with all required services.

## Services Included

- **Backend**: FastAPI application (Python 3.11)
- **Neo4j**: Graph database for code relationships
- **PostgreSQL**: Vector database with pgvector extension
- **Redis**: Caching and session storage

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (for AI features)
- AWS credentials (for S3 storage)

### 2. Environment Setup

```bash
# Copy the example environment file
cp example.env .env

# Edit .env with your actual values
nano .env
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `JWT_SECRET_KEY`: A secure random string for JWT tokens

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Verify Installation

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (neo4j/password)
- **PostgreSQL**: localhost:5432 (repolens/password)
- **Redis**: localhost:6379

## Service Details

### Backend Service
- **Port**: 8000
- **Health Check**: `/health`
- **Auto-reload**: Enabled in development
- **Storage**: Mounted to `./storage` for local projects

### Neo4j Database
- **Version**: 5.15 Community
- **Ports**: 7474 (HTTP), 7687 (Bolt)
- **Credentials**: neo4j/password
- **Plugins**: APOC procedures enabled
- **Memory**: 2GB heap, 1GB page cache

### PostgreSQL Database
- **Version**: 16 with pgvector extension
- **Port**: 5432
- **Database**: vectordb
- **Credentials**: repolens/password
- **Extensions**: vector (for embeddings)

### Redis Cache
- **Version**: 7 Alpine
- **Port**: 6379
- **Memory**: 256MB with LRU eviction
- **Persistence**: AOF enabled

## Volumes

- `neo4j_data`: Neo4j database files
- `postgres_data`: PostgreSQL database files
- `redis_data`: Redis persistence files
- `./storage`: Local project storage (mounted from host)

## Troubleshooting

### Check Service Status
```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs backend
docker-compose logs neo4j
docker-compose logs postgres
docker-compose logs redis
```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

### Common Issues

1. **Port Conflicts**: Make sure ports 8000, 7474, 7687, 5432, 6379 are available
2. **Memory Issues**: Ensure Docker has enough memory allocated (4GB+ recommended)
3. **Permission Issues**: Check file permissions on the `./storage` directory

## Development

### Rebuild Backend
```bash
# Rebuild only the backend service
docker-compose build backend

# Restart backend service
docker-compose up -d backend
```

### Access Service Shells
```bash
# Backend container
docker-compose exec backend bash

# PostgreSQL
docker-compose exec postgres psql -U repolens -d vectordb

# Redis
docker-compose exec redis redis-cli
```

### Database Management
```bash
# Backup Neo4j
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/tmp/backup.dump

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U repolens vectordb > backup.sql
```

## Security Notes

- Change default passwords in production
- Use strong JWT secret keys
- Restrict network access in production
- Regularly update base images
- Use Docker secrets for sensitive data

## Monitoring

### Health Checks
All services include health checks that Docker Compose monitors:
- Backend: HTTP endpoint check
- Neo4j: Cypher query test
- PostgreSQL: Connection test
- Redis: Ping test

### Logs
```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f backend
```
