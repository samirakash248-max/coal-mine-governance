# AI Resilience Implementation

## 1. Previous Timeout Architecture
- **Frontend `apiClient`:** Global Axios instance set to a hard 30-second timeout.
- **Backend AI Services:** The `model-server` local AI implementation was susceptible to ~60-second timeouts if spinning up from a cold start or during heavy load.
- **Mismatch Result:** Axios aborted the connection at 30s before the backend finished processing. React Query, seeing a network failure, aggressively re-fired the query up to 3 times (the default), causing the UI to hang in a loading state for >2 minutes while overloading the backend.

## 2. New Timeout Architecture
- Created `aiApiClient`, a specialized Axios client dedicated exclusively to AI-based inference calls.
- Configured `aiApiClient` with a `timeout: 90000` (90 seconds).
- Normal backend requests remain on `apiClient` (`timeout: 30000`) so they fail fast if the standard database server is down.

## 3. Retry Policy
- Global React Query defaults updated in `AppProviders.tsx`:
  - `retry` is disabled for `401`, `403`, and `404` errors immediately.
  - Mutations (e.g., POST/PUT requests) explicitly have `retry: false` configured, ensuring non-idempotent operations and expensive AI jobs do not loop.
- `useDailyBrief` (GET request for AI summary) was explicitly configured with `retry: false` and `staleTime: 5 * 60 * 1000` to prevent redundant background fetching.

## 4. AI Loading Behavior
- Upgraded `DailyBrief.tsx` to include an indeterminate progress visualizer. Instead of a static "Loading..." string, the user now sees dynamic updates every 5 seconds ("Compiling daily governance data...", "AI is analyzing recent safety events...", "Almost finished...").

## 5. Error Handling
- Daily Brief now safely catches `isError` boundaries. Instead of a blank white component, it distinguishes between:
  - **Timeout Error:** "AI analysis is taking longer than expected. The backend AI model might be cold-starting or overwhelmed."
  - **Unavailable Error:** "The governance service is temporarily unavailable."
- A prominent "Retry Analysis" button was added to easily trigger a manual `refetch()`.
- `CopilotDrawer.tsx` error states similarly intercept Axios timeout conditions to render contextual failure text directly in the chat window.

## 6. Error Boundary Implementation
- Created `ErrorBoundary.tsx`, a robust class component capturing unexpected React rendering exceptions.
- Wrapped the entire layout inside `App.tsx` (`<ErrorBoundary> <RouterProvider /> </ErrorBoundary>`).
- If an unhandled exception occurs, the user is presented with a safe recovery UI and a "Reload Application" button, masking technical stack traces in production while retaining them in development.

## 7. Daily Brief Changes
- Graceful failure fallbacks.
- Dynamic loading stages.
- Manual retry integration.

## 8. Copilot Changes
- Replaced the global `apiClient` with `aiApiClient` for chat completions.
- Ensured `isError` correctly evaluates and displays conversational error bounds.
- Explicitly disabled React Query retries on the `chatMutation`.

## 9. Logging/Observability
- Added structured logging across `backend/app/api/v1/copilot.py`.
- Logs include: Request Started, Duration (in seconds), Provider used, and clear error trace/timeout alerts using Python's `logging` module (`ai.observability`).
- Designed the logs to capture execution times without exposing inner chat prompt details or raw PII from the field.

## 10. Verification Results
- **TypeScript:** Compiled successfully (`npm run build` completed).
- **Python Check:** Re-verified API modules without import failures.
- **Docker/PostgreSQL:** Skipped execution due to host daemon being offline (preventing live integration tests of the timeout mechanisms).

## 11. Remaining Limitations
- While React Query's `retry: false` prevents duplicated requests originating from the frontend, there is currently no distributed task queue (like Celery) managing the backend. A single request connection drop will still cause the active FastAPI thread to orphan the AI generation, as background processing hasn't been architected yet.
