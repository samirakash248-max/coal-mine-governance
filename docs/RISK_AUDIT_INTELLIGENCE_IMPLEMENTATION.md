# Risk & Audit Intelligence Implementation

## 1. Existing Risk Architecture
The backend `SafetyEvent` model (`app.models.field`) natively supports risk engine outputs including:
- `risk_score` (Float, 0-100)
- `risk_level` (String: LOW, MEDIUM, HIGH, CRITICAL)
- `risk_factors` (JSONB)
- `is_ai_overridden` (Boolean)

These fields are calculated and persisted dynamically by the backend, rather than on-the-fly, ensuring consistent reporting and explainability across the platform.

## 2. Existing AuditEvent Architecture
The backend `AuditLog` model (`app.models.workflow`) serves as an immutable chronological record of platform events. It contains:
- `user_id` and `role` (capturing if it was a human or `AI_AGENT`)
- `action` (e.g., CREATE, UPDATE, APPROVE, ESCALATE)
- `entity_type` & `entity_id`
- `before_state` & `after_state` (JSONB)
- `hash_signature` (Cryptographic verification)

## 3. Existing APIs Reused
- **Dashboard Metrics:** Reused `GET /api/v1/dashboard/summary` for aggregate stats (`critical_findings_count`, `high_critical_risk_cases`, `ai_overrides_count`).
- **Audit Detail:** Reused `GET /api/v1/audit/{entity_type}/{entity_id}` to fetch the historical timeline for specific risk cases directly inside the detail view.

## 4. New APIs Created
- **Risk Cases:** Added `GET /api/v1/analytics/risk/cases` in `analytics.py`. Returns the top 50 Safety Events where `risk_level` is `HIGH` or `CRITICAL`, strictly scoped by `current_user.mine_id`.
- **Global Audit:** Added `GET /api/v1/audit/` in `audit.py`. Implements pagination (`skip`, `limit`) and filtering (`action`, `entity_type`), enabling the Audit Trail page without overloading memory.

## 5. Risk Intelligence UI
Created `frontend/src/pages/risk/RiskIntelligence.tsx`.
Provides a two-pane layout:
1. A scrollable list of high-risk cases showing Mine/Event title, risk level, score, and date.
2. A detailed view presenting the explainable risk breakdown and the dedicated timeline.

## 6. Explainable Risk Visualization
The detail view parses the existing JSONB `risk_factors`. For each factor (e.g., severity, recurrence), it renders the factor name, the engine's reasoned contribution/impact, and the descriptive text exactly as stored by the backend. No factor weights or explanations were fabricated.

## 7. Audit Trail UI
Created `frontend/src/pages/audit/AuditTrail.tsx`.
- Implements a paginated data table.
- Dropdown filters for `Action` and `Entity`.
- Selecting an audit row opens a detailed read-only pane displaying exact `before_state` and `after_state` JSON diffs alongside the cryptographic `hash_signature`.

## 8. AI vs Human Decision Separation
The Audit Trail explicitly checks the `role` field. If `role === 'AI_AGENT'`, it is visually highlighted with distinct styling indicating an "AI Recommendation System". Human actions reflect the actual user's role/ID.

## 9. Dashboard Integration
Enhanced `ExecutiveDashboard.tsx` to make the high/critical risk and overdue action stat-cards interactive. Clicking these cards now routes the user directly to the `/risk` center.

## 10. Pagination/Filtering
Implemented server-side pagination and SQL `WHERE` clauses for the global audit trail. Data is requested in chunks of 20, ensuring the React client does not crash on large databases.

## 11. RBAC/Security Considerations
The new endpoints explicitly enforce `current_user.mine_id` constraints where applicable. Global audit logs query raw entities, preserving the existing read-only boundary. All UI views are strictly read-only; no manual "edit risk" capabilities were exposed.

## 12. Verification Results
- **Frontend:** TypeScript compilation succeeded cleanly via `npm run build`.
- **Backend:** Python syntax checks passed natively.
- **Docker Integration:** Skipped due to local Docker daemon unavailability, but standard SQLAlchemy routing conventions were strictly adhered to.

## 13. Remaining Limitations
- Advanced charting (e.g., historical risk score drift over time) is deferred until historical score snapshots are modeled in the database, as currently, only the *latest* risk score is persisted on the `SafetyEvent`.
