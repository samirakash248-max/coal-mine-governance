# AI-Based Smart Governance & Compliance Monitoring System for Coal Mines

## Phase 1-11 Completed Architecture

This repository holds the production-ready prototype for the PSID-26024 Coal Mine Governance system.

### Core Stack
- **Frontend**: React + TypeScript + Vite + Tailwind + shadcn/ui. Fully offline-capable (PWA with IndexedDB syncing).
- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL (`pgvector` for RAG).
- **AI Orchestration**: Custom `AIProvider` abstractions isolating the orchestration layer from proprietary APIs. Utilizes native JSON-intent extraction for max compatibility with generic local LLMs.
- **Background Jobs**: Redis-backed async workers (`arq`).

### Production Security & Hardening (Phase 11)
- **Multi-Tenant Boundaries**: Heavy B-Tree indexing on `mine_id` guarantees high-speed organization boundaries.
- **Strict RBAC**: Enforced exclusively on the backend via JWT dependency injection (`get_current_user`). UI state reflects, but does not dictate, security.
- **AI Guardrails**: The `CopilotTools` service executes strictly Read-Only logic. The LLM cannot hallucinate an `UPDATE` or `INSERT` command. Any mutations proposed by the AI require explicitly pressing an "Approve & Execute" button (Human-in-the-loop).
- **Public Transparency**: Isolated `public/` API routes strictly execute aggregation queries to prevent structural PII leakage.

### How to Run Locally

1. **Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   This spins up the custom Postgres instance (with `pgvector` and PostGIS), Redis, and the Backend API.

2. **Connecting a Local AI**:
   The `LocalModelProvider` natively parses generic `v1/chat/completions`.
   Update `backend/.env`:
   ```env
   AI_PROVIDER=local
   AI_BASE_URL=http://localhost:8001/v1
   AI_MODEL=llama-3-8b-instruct
   ```

3. **Frontend Boot**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Critical Demo Flows Verified
- **Inspector Flow**: Submit observation (offline or online) -> Background GPS append -> Risk score elevates -> Corrective Action triggers -> Audit Trail logs SHA-256 hash.
- **Weather Flow**: Open-Meteo fetches API data -> Risk Engine warns of monsoon hazard -> Dashboard visualizes aggregate danger.
- **Knowledge Base Flow**: Upload document -> Local OCR extraction -> `pgvector` embedding -> Chat Copilot retrieves exact citation -> Human-in-loop verification.

### Tests
Run the test suite:
```bash
cd backend
pytest
```
