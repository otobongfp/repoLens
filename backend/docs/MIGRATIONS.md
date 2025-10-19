# Database Migrations Guide

This guide explains how to run database migrations in different environments using Alembic.

## Quick Start

### Docker Environment (Recommended)
```bash
# Run migrations in Docker
make docker-migrate-up

# Check migration status
make docker-migrate-current

# View migration history
make docker-migrate-history
```

### Local Environment
```bash
# Run migrations locally
make migrate-up

# Check migration status
make migrate-current
```

## Available Commands

### Docker Commands
- `make docker-migrate-up` - Run all pending migrations
- `make docker-migrate-down` - Rollback last migration
- `make docker-migrate-revision` - Create new migration
- `make docker-migrate-history` - Show migration history
- `make docker-migrate-current` - Show current migration
- `make docker-migrate-check` - Check migration status

### Local Commands
- `make migrate-up` - Run all pending migrations
- `make migrate-down` - Rollback last migration
- `make migrate-revision` - Create new migration
- `make migrate-history` - Show migration history
- `make migrate-current` - Show current migration
- `make migrate-check` - Check migration status

## Manual Commands

### Docker Manual Commands
```bash
# Run migrations (with correct Docker database URL)
docker compose exec backend bash -c "PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb alembic upgrade head"

# Rollback migration
docker compose exec backend bash -c "PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb alembic downgrade -1"

# Create new migration
docker compose exec backend bash -c "PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb alembic revision --autogenerate -m \"Your message\""

# Check current status
docker compose exec backend bash -c "PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb alembic current"

# Show history
docker compose exec backend bash -c "PGVECTOR_DB_URL=postgresql://repolens:password@postgres:5432/vectordb alembic history"
```

### Local Manual Commands
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "Your message"

# Check current status
alembic current

# Show history
alembic history
```

## Environment Configuration

### Database URLs
Migrations automatically use the correct database URL based on environment:

**Docker Environment:**
- Uses `PGVECTOR_DB_URL` from Docker environment
- Default: `postgresql://repolens:password@postgres:5432/vectordb`

**Local Environment:**
- Uses `PGVECTOR_DB_URL` from `.env` file
- Default: `postgresql://repolens:password@localhost:5433/vectordb`

**External Environment:**
- Uses `PGVECTOR_DB_URL` from environment variables
- Example: `postgresql://user:pass@your-host:5432/vectordb`

## Creating New Migrations

### 1. Make Model Changes
Edit your SQLAlchemy models in `app/database/models/`

### 2. Generate Migration
```bash
# Docker
make docker-migrate-revision

# Local
make migrate-revision
```

### 3. Review Generated Migration
Check the generated file in `alembic/versions/`

### 4. Apply Migration
```bash
# Docker
make docker-migrate-up

# Local
make migrate-up
```

## Migration Workflow

### Development Workflow
1. **Make model changes** in `app/database/models/`
2. **Generate migration**: `make docker-migrate-revision`
3. **Review migration** file in `alembic/versions/`
4. **Apply migration**: `make docker-migrate-up`
5. **Test changes** with your application

### Production Workflow
1. **Test migrations** in staging environment
2. **Backup database** before applying migrations
3. **Apply migrations**: `make docker-migrate-up`
4. **Verify application** works correctly
5. **Monitor** for any issues

## 🚨 Important Notes

### Before Running Migrations
- **Backup your database** in production
- **Test migrations** in staging environment first
- **Review generated migration files** before applying
- **Ensure database is accessible** and running

### Migration Best Practices
- **One migration per feature** - don't bundle multiple changes
- **Descriptive migration messages** - explain what the migration does
- **Test rollback procedures** - ensure you can undo changes
- **Version control migrations** - commit migration files to git

### Common Issues

**Connection Refused:**
```bash
# Check if database is running
docker compose ps

# Check database URL
echo $PGVECTOR_DB_URL
```

**Migration Conflicts:**
```bash
# Check current status
make docker-migrate-current

# Resolve conflicts manually
docker compose exec backend alembic merge -m "Merge conflict resolution"
```

**Inconsistent Migration State:**
```bash
# Check if Alembic version matches actual database
make docker-migrate-current
docker compose exec postgres psql -U repolens -d vectordb -c "\dt"

# If tables are missing but migration shows "applied", reset and re-run:
docker compose exec postgres psql -U repolens -d vectordb -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
make docker-migrate-up
```

**Permission Issues:**
```bash
# Ensure proper database permissions
# Check user has CREATE/ALTER privileges
```

## 🔍 Troubleshooting

### Check Migration Status
```bash
# Docker
make docker-migrate-current

# Local
make migrate-current
```

### View Migration History
```bash
# Docker
make docker-migrate-history

# Local
make migrate-history
```

### Check Database Connection
```bash
# Test connection
docker compose exec backend python -c "
import asyncio
import asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://repolens:password@postgres:5432/vectordb')
    print('Database connected successfully')
    await conn.close()
asyncio.run(test())
"
```

### Reset Migrations (Development Only)
```bash
# WARNING: This will delete all data!
docker compose down -v
docker compose up -d postgres
make docker-migrate-up
```

## Migration Files Location

- **Migration files**: `alembic/versions/`
- **Configuration**: `alembic.ini`
- **Environment setup**: `alembic/env.py`
- **Models**: `app/database/models/`

## Environment-Specific Examples

### Development
```bash
# Start development environment
make dev

# Run migrations
make docker-migrate-up

# Create new migration
make docker-migrate-revision
# Enter: "Add user preferences table"
```

### Production
```bash
# Start production environment
make prod

# Run migrations
make docker-migrate-up

# Check status
make docker-migrate-current
```

### Local Development
```bash
# Start databases only
make dev-local

# Run migrations locally
make migrate-up

# Create migration
make migrate-revision
```
