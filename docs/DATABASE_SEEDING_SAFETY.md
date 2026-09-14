# Database Seeding Safety

## Overview
This document outlines the strict guidelines and architecture protecting the production database from accidental destruction during initialization and seeding phases.

## 1. Normal Seed Command
The application supports idempotent seeding of realistic development/demo data.

**Command:**
```bash
cd backend
python scripts/seed_demo.py
python scripts/seed_documents.py
```

### What it creates:
- Baseline organizational hierarchy (Organizations, Regions, Mines)
- Admin and standard users (e.g., `admin@coalmine.gov.in`, `demo123@gmail.com`)
- A minimal set of demo incidents, reports, inspections, and audit logs.
- 4 mock standard operating documents.

### What it NEVER deletes:
- It **never** issues `DROP TABLE`, `DROP SCHEMA`, or `metadata.drop_all()`.
- It **never** drops the database.
- It **never** runs `DELETE FROM`.
- It **never** overwrites existing mine coordinates or destroys PostGIS layers.
- It **never** deletes genuine user-submitted `SafetyEvent` records or `AuditLog` evidence.

## 2. Idempotency Behavior
- **Check-First Strategy**: The seed script queries the database for existing stable identifiers (like the core Organization name, or a document's `document_number`).
- If an existing record is found, the script gracefully logs `[INFO] Demo data already exists. Skipping seed process to avoid duplicates` and exits.
- Running the script 100 times will result in identical database state as running it once.

## 3. Production Safety
- **No Automatic Destructive Seeding**: Application startup (`main.py` lifespan) does NOT invoke `seed_demo.py`.
- **No Destructive Flags**: The dangerous `--reset` flag historically used to execute `Base.metadata.drop_all` has been completely purged from the codebase.
- Even if a developer accidentally types `python scripts/seed_demo.py --reset`, the script will merely run idempotently and safely exit without dropping any tables.

## 4. Migration vs Seed Responsibilities
- **Alembic**: Strictly and exclusively responsible for all DDL (`CREATE TABLE`, `ALTER`, `CREATE EXTENSION postgis`).
- **Seed Scripts**: Strictly responsible for DML (`INSERT` / `UPDATE` demo records).
- The seed script relies on the schema already existing. It does not attempt `Base.metadata.create_all`.

## 5. Destructive Commands
- **None remain**. If a developer genuinely needs to destroy their local database to start fresh, they must use standard Docker tools:
  ```bash
  docker compose down -v
  docker compose up -d
  ```
- This intentionally requires tearing down the infrastructure volume, ensuring it cannot accidentally occur via a Python script pointing to a remote production URL.

## 6. Weather & GIS Safeties
- The seed system does NOT generate fake live weather observations that would pollute the AI risk engine.
- Missing GIS coordinates are safely left as `NULL` instead of artificially clustering markers at `(0,0)` off the coast of Africa.


