from .base import AIProvider, AIMessage, AIResponse
from typing import Optional
from app.config import get_settings
from fastapi import HTTPException
import httpx
import json

class LocalModelProvider(AIProvider):
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.AI_BASE_URL or "http://localhost:11434/v1"
        self.model = self.settings.AI_MODEL or "llama3"

    async def chat(
        self, 
        messages: list[AIMessage],
        context: Optional[dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AIResponse:
        async with httpx.AsyncClient() as client:
            formatted_messages = [
                {"role": m.role.value, "content": m.content} for m in messages
            ]
            
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                return AIResponse(
                    content=content,
                    model=self.model,
                    provider="local",
                    usage=usage,
                    is_simulated=False
                )
            except Exception as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Unable to reach local AI inference server at {self.base_url}"
                )
    
    async def process_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Connects to a generic OpenAI-compatible local API (e.g. vLLM or Ollama)."""
        import httpx
        try:
            import os
            base_url = os.environ.get("AI_BASE_URL", "http://localhost:8001/v1")
            model = os.environ.get("AI_MODEL", "local-model")
            
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{base_url}/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ]
                    },
                    timeout=30.0
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Unable to reach local AI inference server at {self.base_url}"
            )

    async def generate_embeddings(self, text: str) -> list[float]:
        # Fallback 1536-d vector since local embedding models might have varying endpoints
        return [0.1] * 1536

    async def summarize(self, text: str, max_length: int = 200) -> str:
        messages = [
            AIMessage(role="system", content=f"Summarize the following text in under {max_length} characters."),
            AIMessage(role="user", content=text)
        ]
        response = await self.chat(messages, max_tokens=150)
        return response.content
    
    async def explain(
        self, 
        data: dict, 
        context: str,
        explanation_type: str = "general"
    ) -> str:
        prompt = f"Context: {context}\nData: {json.dumps(data)}\nProvide a {explanation_type} explanation of this data."
        messages = [
            AIMessage(role="system", content="You are a helpful AI explaining data."),
            AIMessage(role="user", content=prompt)
        ]
        response = await self.chat(messages, max_tokens=300)
        return response.content
    
    async def extract_compliance_info(
        self,
        text: str,
        regulation_context: Optional[str] = None
    ) -> dict:
        prompt = f"Text: {text}\nRegulation Context: {regulation_context or 'None'}\nExtract compliance information as JSON with keys: potential_violations, requirements_met, risk_score_estimate (1-100)."
        messages = [
            AIMessage(role="system", content="You are a strict compliance extraction AI. Always return valid JSON."),
            AIMessage(role="user", content=prompt)
        ]
        response = await self.chat(messages, max_tokens=500)
        
        try:
            # Very basic JSON extraction logic. In production, use structured output if supported by local model.
            content = response.content
            # Try to parse directly or extract json block
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                return json.loads(content[start_idx:end_idx])
            return {"error": "Failed to parse JSON from local model"}
        except Exception:
            return {"error": "Invalid JSON returned by local model"}
            
    async def classify_event(self, text: str) -> dict:
        prompt = f"Classify this mining field report. Return STRICT JSON with keys: event_type, category, severity, needs_human_review.\n\n{text}"
        messages = [
            AIMessage(role="user", content=prompt)
        ]
        
        # We need to make sure the chat template is applied via httpx in chat(), but our local.py's chat() sends the list 
        # of dicts, which our serve_model.py WILL apply the chat_template to!
        # Because we fixed serve_model.py to use `tokenizer.apply_chat_template` on the incoming messages array!
        response = await self.chat(messages, max_tokens=150, temperature=0.1)
        
        try:
            content = response.content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                parsed = json.loads(content[start_idx:end_idx])
                parsed["is_simulated"] = False
                return parsed
            return {"error": "Failed to parse JSON", "raw": content, "is_simulated": True}
        except Exception as e:
            return {"error": str(e), "is_simulated": True}
