# Authentication and RBAC Testing Guide

## Test Database Architecture

The test suite runs against a dedicated PostgreSQL database named `coalmine_test`.
This completely isolates test data from the development database (`coalmine_db`), ensuring that destructive testing operations (such as deleting users or altering roles) never impact your working environment.

### Why SQLite is Not Used
Previous iterations of the test suite attempted to use an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`). However, the CoalMine application models contain native PostGIS/GeoAlchemy2 geometry columns (e.g., `Geometry(Point)` for Mine Digital Twins) and `pgvector` columns. SQLite does not natively support these extensions without complex external compilation of SpatiaLite. Running against the actual PostgreSQL/PostGIS engine guarantees that tests validate the true production behavior and migrations.

### PostgreSQL/PostGIS Requirements
The test database requires:
1. PostgreSQL 15+
2. PostGIS extension
3. pgvector extension

These are automatically bundled in the project's custom `postgres.Dockerfile`.

## Setting Up the Test Environment

1. **Start the Database Infrastructure**
   Start the local Docker containers for PostgreSQL and Redis:
   ```bash
   docker compose up -d postgres redis
   ```

2. **Create the Test Database**
   Connect to your local postgres instance and create the test database:
   ```bash
   docker compose exec postgres psql -U coalmine -d postgres -c "CREATE DATABASE coalmine_test;"
   ```

3. **Install Extensions**
   The test database needs the required extensions before Alembic migrations can run:
   ```bash
   docker compose exec postgres psql -U coalmine -d coalmine_test -c "CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS vector;"
   ```

## Running the Complete Test Suite

The test suite leverages `pytest` and `pytest-asyncio`. The configuration in `backend/tests/conftest.py` automatically applies `alembic upgrade head` to the test database and uses nested SQL transactions (`SAVEPOINT`) to rollback changes after every single test.

To execute the suite:
```bash
cd backend
# Make sure your virtual environment is active
pytest tests/test_auth_rbac.py -v
```

### Authentication Tests
The suite validates:
* **Valid Login:** Returns JWT and authenticates protected endpoints.
* **Invalid Login:** Verifies invalid password, nonexistent user, and deactivated user all safely return a generic `401 Unauthorized` without leaking account states.
* **JWT Integrity:** Verifies expired, missing, and malformed JWTs are strictly rejected.
* **Rate Limiting:** Confirms progressive delays apply to brute-force attempts.

### RBAC Tests
The suite validates:
* **Role Verification:** `ADMIN` users can hit `/api/v1/users/`, while non-admin roles (e.g., `SAFETY_OFFICER`) are rejected with `403 Forbidden`.
* **Privilege Escalation:** Explicitly prevents standard users from elevating their own role via the `/me` update endpoint.
* **Last Admin Protection:** Validates that the system safely rejects requests to deactivate or delete the last remaining active `ADMIN` user.

## Known Limitations

- **Rate Limiting Context**: The brute-force progressive delay is currently stored in application memory. If the backend is running with multiple Uvicorn workers, the delay is tracked per-worker.
- **Stateless JWTs**: JWTs cannot be selectively revoked mid-session immediately (e.g., following a password change). They remain valid until the `ACCESS_TOKEN_EXPIRE_MINUTES` duration elapses.
- **Docker Dependency**: The test suite **requires** Docker Desktop or a native PostgreSQL/PostGIS instance to be running. It cannot fall back to SQLite.
