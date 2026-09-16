# AI-Powered Compliance and Risk Intelligence

This document details the architecture and responsibility boundaries of the AI and deterministic components within the Coal Mine Governance platform.

## Deterministic Risk Engine
The `RiskEngine` calculates a 0-100 score utilizing completely deterministic business rules derived from PostGIS/PostgreSQL data (e.g., overdue corrective actions, critical incident counts, weather severity). 
It generates a categorized `risk_level` (LOW, MEDIUM, HIGH, CRITICAL) mapping that is exposed in the UI. **The AI does NOT decide risk scores or levels.**

## Retrieval-Augmented Generation (RAG)
Vector similarity search utilizes the `pgvector` HNSW index on the `DocumentChunk.embedding` column.
- **Security Barrier:** Queries strictly enforce the `mine_id` to prevent cross-tenant document data leaks, regardless of user input.
- **Citation Rendering:** Results expose the document title, specific section, and page number to strictly trace AI claims to authoritative sources. Only `DocumentStatus.VERIFIED` material is retrieved.

## AI Prompts & Hallucination Defense
The `CopilotService` structures the LLM payloads via the `AIMessage` schema rather than raw f-string text replacements, isolating untrusted user input within the `USER` role.
The `SYSTEM` instruction enforces that context is treated as untrusted and blocks prompt injections (e.g. "Ignore previous instructions"). The model is explicitly constrained from fabricating compliance facts.

## Failure Resilience
If the local AI server (`coal-gov-4b`) goes offline, the `RiskEngine` and standard Dashboards continue to run identically. Copilot queries fail gracefully via Axios interceptors displaying a user-friendly UI timeout rather than collapsing the React SPA.
