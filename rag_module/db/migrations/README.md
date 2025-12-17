# Database Migrations

Alembic migrations for SearchNewsRAG database schema.

## Setup

Migrations are automatically configured to use `DATABASE_URL` from environment variables.

## Common Commands

### Check current version
```bash
poetry run alembic current
```

### View migration history
```bash
poetry run alembic history
```

### Upgrade to latest
```bash
poetry run alembic upgrade head
```

### Downgrade one version
```bash
poetry run alembic downgrade -1
```

### Create new migration
```bash
poetry run alembic revision --autogenerate -m "description"
```

## Migration Files

- `env.py` - Alembic environment configuration
- `versions/` - Migration scripts (auto-generated)

## Schema Overview

### Main Tables

- **sources** - News sources (Telegram channels)
- **news_articles** - Articles with analysis metadata
  - Indexed: `category`, `date`
  - Contains: `image_url`, LLM analysis fields
- **news_chunks** - Article chunks for vector search

### Taxonomy Tables

- **subcategories**, **topics**, **keywords**, **entities**
- Bridge tables for many-to-many relationships

## Notes

- All migrations auto-formatted with black
- Database URL loaded from `.env` file
- Initial schema matches existing production database
