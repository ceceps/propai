# Running Database Migrations

This project uses **Alembic** to manage database schema versions.

## Automated Migrations

To apply pending migrations, run:

```bash
alembic -c alembic.ini upgrade head
```

To create a new migration based on changes in `packages/propai_core/src/propai_core/models/`, run:

```bash
alembic -c alembic.ini revision --autogenerate -m "Description of changes"
```

## Manual SQL Migrations

Some schema changes are managed via raw SQL scripts in the `sql/` directory to ensure they remain idempotent and compatible with existing tables. 

If you add a new SQL migration script:
1. Create the file in `sql/` (e.g., `sql/002_new_feature.sql`).
2. Add a new Alembic migration step: `alembic revision -m "Add new feature SQL"`
3. Update the `upgrade()` function in the generated migration file to execute your SQL script:

```python
def upgrade() -> None:
    with open('/path/to/sql/002_new_feature.sql', 'r') as f:
        op.execute(f.read())
```
