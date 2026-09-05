# Database Migrations

This directory contains Alembic database migrations for the AI Job Tracker application.

## Overview

Alembic is used to manage database schema changes in a version-controlled way. Instead of dropping and recreating tables (which loses all data), migrations allow you to evolve the database schema safely.

## Common Commands

### Create a new migration (after changing models)

```bash
python -m alembic revision --autogenerate -m "Description of changes"
```

This will:
- Compare your SQLAlchemy models with the current database schema
- Generate a new migration file in `alembic/versions/`
- Include both upgrade() and downgrade() functions

### Apply migrations (upgrade to latest)

```bash
python -m alembic upgrade head
```

This runs all pending migrations to bring your database up to date.

### Rollback one migration

```bash
python -m alembic downgrade -1
```

### View migration history

```bash
python -m alembic history
```

### View current migration version

```bash
python -m alembic current
```

## Migration Files

Migration files are stored in `alembic/versions/` and are named with:
- A revision ID (random hash)
- Your description (from the `-m` flag)

Each migration has:
- `upgrade()` - Apply the changes
- `downgrade()` - Revert the changes

## Best Practices

1. **Always review auto-generated migrations** - Alembic does its best but may not catch everything
2. **Test migrations** - Run them on a development database first
3. **Never edit applied migrations** - Create a new migration to fix issues
4. **Keep migrations small** - One logical change per migration
5. **Write descriptive messages** - Future you will thank present you

## Initial Setup (Already Done)

The initial migration has been created and includes:
- `users` table with authentication fields
- `job_applications` table with all application tracking fields
- Foreign key relationships
- Indexes on key columns

## Production Deployment

Before deploying to production:

1. Backup your database
2. Review the migration
3. Apply migrations:
   ```bash
   python -m alembic upgrade head
   ```
4. Verify the application still works

## Troubleshooting

### "Target database is not up to date"

Run: `python -m alembic upgrade head`

### "Can't locate revision identified by..."

Your local migrations might be out of sync. Pull latest code and check `alembic/versions/`.

### Migration conflicts

If multiple developers create migrations simultaneously:
1. Keep both migration files
2. Create a new migration that merges them
3. Use `python -m alembic merge <rev1> <rev2>`

## Environment Configuration

Database URL is loaded from `.env` file:
```
DATABASE_URL=postgresql://user:pass@host/dbname
```

For SQLite (local development):
```
DATABASE_URL=sqlite:///./job_tracker.db
```

For PostgreSQL (production/Supabase):
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```
