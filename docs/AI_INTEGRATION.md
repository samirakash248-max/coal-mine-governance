# AI Integration Guide

This application is built with a strictly vendor-agnostic AI orchestration layer. 
The core logic resides in `app.services.copilot` and `app.providers.ai`.

## Connecting Your Custom Model

To plug in a custom, locally-trained governance model (e.g., Llama-3-Governance fine-tune), you do not need to rewrite the orchestration logic. We support any model served behind an OpenAI-compatible HTTP inference server.

### 1. Serving the Model
You can serve your model using tools like **vLLM** or **Ollama**.

Example using vLLM:
```bash
python -m vllm.entrypoints.openai.api_server --model your-finetuned-model-path --port 8001
```

Example using Ollama:
```bash
OLLAMA_HOST=0.0.0.0:8001 ollama run your-model
```

### 2. Environment Variables
In your backend `.env` file, configure the following variables to point to your inference server:

```env
AI_PROVIDER=local
AI_BASE_URL=http://localhost:8001/v1
AI_MODEL=your-finetuned-model-path
```

### 3. Tool Calling Strategy
The orchestration layer (`app/services/copilot.py`) uses a prompt-based structured JSON injection to trigger backend tools. This maximizes compatibility across open-source models that may not natively support OpenAI's proprietary `tools`/`function_calling` REST schemas perfectly. 

When your model outputs a specific JSON intent, the orchestration layer intercepts it, triggers the deterministic python function (e.g., `get_overdue_actions`), applies RBAC security, and feeds the raw JSON response back into the context window for your model to synthesize.

## Security Constraints
- **Human-in-the-Loop**: Your model can generate `recommended_actions`, but cannot write to the database automatically.
- **Data Boundaries**: The backend Python layer injects `current_user` into every tool. Your model will *never* receive data the requesting user is not authorized to see.
