# Local AI Integration Documentation

## Overview
This document outlines the integration of the local AI model server (serving `Qwen3-0.6B` + `coal-gov-v2` adapter) with the main Coal Gov Application backend.

## Provider Selection & Configuration
The backend connects to AI via the `AIProvider` abstraction. The active provider is determined by the `AI_PROVIDER` environment variable.

### Environment Variables (Backend `.env`)
```
AI_PROVIDER=local
AI_BASE_URL=http://localhost:8001/v1
AI_MODEL=coal-gov-v2
AI_TIMEOUT=30.0
```

To run in isolated mock mode, set `AI_PROVIDER=mock`.

## Starting the System End-to-End

### 1. Start Local Model Server
Navigate to the AI repository where the V2 adapter is stored:
```bash
cd coal-gov-ai
python serve_model.py
```
This boots a FastAPI server exposing an OpenAI-compatible `/v1/chat/completions` endpoint on port `8001`.

### 2. Start the Main Backend
In a new terminal:
```bash
cd coalMine_app/backend
.venv\Scripts\uvicorn app.main:app --reload
```

### 3. Start the Frontend
In a new terminal:
```bash
cd coalMine_app/frontend
npm run dev
```

## Performing the End-to-End AI Test
1. Open the frontend (usually `http://localhost:5173`).
2. Navigate to **Field Operations** > **Report Event**.
3. In the Description box, type a sample field report, e.g., *"Worker slipped on grease near the main crusher."*
4. Click the **"✨ Ask AI Copilot to Classify"** button.
5. The UI will call the backend `/api/v1/copilot/classify`, which calls the `LocalModelProvider`, reaching the local `serve_model.py`.
6. A suggestion box will appear with the inferred `event_type`, `category`, and `severity`. Click "Apply Values" to pre-fill the form.

## Current Model Limitations
The currently integrated model (`Qwen3-0.6B`) is an **experimental/development** assistant. 
* **JSON/Schema Validity:** 100%
* **Hallucination Rate:** 0%
* **Semantic Accuracy (Event/Category/Severity):** ~14% - 30%

Due to its small parameter count, the model struggles with complex semantic distinctions in mining language. **It must not be used for authoritative compliance decisions.** The frontend explicitly flags its suggestions as experimental.

## Future Qwen3-4B Replacement Path
When a stronger GPU (e.g., A10 or T4 with >12GB VRAM) is available:
1. Retrain the model on the existing V2 dataset using `Qwen/Qwen3-4B` in `coal-gov-ai/train_v2.py`.
2. Update `MODEL_NAME` in `serve_model.py` to `Qwen/Qwen3-4B`.
3. Restart the model server.
No changes to the main application frontend or backend are required, as they rely on the OpenAI-compatible HTTP interface via `LocalModelProvider`.
