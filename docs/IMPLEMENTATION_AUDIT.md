# Implementation Audit Report: coalMine_app (Smart India Hackathon)

## A. Current Architecture
### 1. Frontend
- **Framework:** React 18 with TypeScript, bundled via Vite.
- **Routing:** React Router v6 using a robust layouts system (`AppShell`, `PublicLayout`, `ProtectedRoute`).
- **State Management & Data Fetching:** `@tanstack/react-query` handles async state, caching, and retries.
- **Styling:** Tailwind CSS with a custom shadcn/ui-like component library.
- **API Client:** Custom Axios instance (`apiClient`) centralized in `frontend/src/api/client.ts`.

### 2. Backend
- **Framework:** FastAPI with Python 3.11+.
- **Database:** PostgreSQL (with `pgvector` for document chunks) managed via SQLAlchemy 2.0 (async).
- **Authentication:** JWT-based auth + Google OAuth integration.
- **Caching/Queueing:** Redis is integrated for caching and potential pub/sub tasks.
- **AI Integration:** Abstraction layer for AI processing (`AIProvider`), configurable to route to a local `model-server` or mock endpoints.

## B. Working Features
- **Authentication:** Email/Password and Google OAuth login flows.
- **Dashboard:** High-level analytics and counts successfully fetch from `/api/v1/dashboard/summary`.
- **Safety / Incidents:** `SafetyEvent` listing, reporting, and detail views are properly mapped to the backend.
- **Inspections:** Create, list, and detail views successfully communicate with the `inspections` router.
- **Documents Library:** Fully functioning vector-based document storage (recently patched to use correct API paths and seeded with data).
- **Grievances:** Listing and AI-triage suggestion endpoints are active and aligned.

## C. Partially Working Features
- **Daily Brief (Copilot):** The feature works when the AI `model-server` is active. However, if the local AI container is down, the 60s backend timeout exceeds the 30s Axios timeout, causing aggressive React Query retries and locking the UI in a "Loading..." state for over 2 minutes before failing.
- **Governance Map:** Migrated to real DB coordinates, but a schema mismatch remains (frontend expects `location: string` but `MineResponse` lacks it, leaving map popups slightly empty).
- **Weather Widget:** Connects to `/api/v1/weather/risk/...` but returns statically mocked data (`MODERATE`) in the background.

## D. UI-Only / Mock Features
- **Executive Analytics:** `frontend/src/pages/analytics/ExecutiveDashboard.tsx` utilizes completely hardcoded array data (`regionalData`, `incidentData`) and bypasses the backend API.
- **Reports Manager:** `frontend/src/pages/reports/ReportsManager.tsx` utilizes static dummy data (`initialReports`) and has no backend integration hooks.

## E. Backend-Only Features
- **Audit Logging Engine:** Substantial audit trail models and logic exist, but the frontend lacks a dedicated dashboard to view these logs.
- **Risk Engine:** Analyzes safety incidents and generates `risk_score` / `risk_level`, but the UI doesn't have a dedicated risk visualization drill-down.

## F. Frontend/Backend Integration Problems
- **Schema Contracts:** `MineResponse` (in `hierarchy.py`) is missing the `location` field expected by `MineList.tsx` and `GovernanceMap.tsx`.
- **Timeout Management:** Axios 30s timeouts clash with AI-driven endpoints (60s+ execution times).
- **Error Boundaries:** Several components (e.g., `DailyBrief.tsx`, lists) lack robust `isError` boundaries, leading to empty white spaces instead of user-friendly error messages upon network failure.

## G. Database Problems
- **No PostGIS Usage:** Despite being an SIH GIS-based governance app, `Mine` coordinates (`latitude`, `longitude`) are stored as plain `Float` columns, preventing advanced geospatial queries (e.g., "Find all events within 50km of Mine X").
- **Seeding Hazards:** `seed_demo.py` requires `--reset` to update data, which performs an aggressive `Base.metadata.drop_all`, destroying manual modifications.

## H. Critical Bugs
- **Docker Compose Syntax Error:** `docker-compose.yml` line 15 contains an invalid YAML escape sequence (`test: ["CMD-SHELL", "pg_isready -U \ -d \"]`), which causes `docker-compose up` to crash immediately with a parser error. The application currently cannot boot via the standard Docker workflow.

## I. Recommended Upgrade Order
1. **Fix Docker Compose YAML Syntax:** Immediately repair `docker-compose.yml` to unblock containerized development.
2. **Schema & Seed Enhancements:** Add the missing `location` field to `Mine` and `MineResponse`.
3. **Connect Analytics to API:** Replace static JSON in `ExecutiveDashboard.tsx` and `ReportsManager.tsx` with actual FastAPI routes.
4. **Resilience & Timeouts:** Implement `isError` handling in React Query hooks and adjust Axios timeouts for AI endpoints.
5. **Geospatial Migration:** (Optional/Stretch) Upgrade coordinate columns to `PostGIS Geometry` types for spatial dashboard analytics.

## J. Target Files for Recommended Upgrades
1. **Docker Fix:** `docker-compose.yml`
2. **Schema Fix:** `backend/app/models/hierarchy.py`, `backend/app/schemas/hierarchy.py`, `frontend/src/hooks/useMines.ts`
3. **Analytics Integration:** `frontend/src/pages/analytics/ExecutiveDashboard.tsx`, `backend/app/api/v1/analytics.py` (needs implementation)
4. **Reports Integration:** `frontend/src/pages/reports/ReportsManager.tsx`, `backend/app/api/v1/reports.py`
5. **Timeout Fixes:** `frontend/src/api/client.ts`, `frontend/src/hooks/useCopilot.ts`
