import os
import torch
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import uvicorn
import sys

# Suppress overly verbose logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Configurable environment variables for Production & Local
BASE_MODEL = os.environ.get("MODEL_NAME", "Qwen/Qwen3-4B")
ADAPTER_DIR = os.environ.get("ADAPTER_PATH") # No hardcoded Windows path default
MODEL_ALIAS = os.environ.get("MODEL_ALIAS", "coal-gov-qwen3-4b")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8001"))

# Global references
model = None
tokenizer = None
is_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer, is_ready
    
    if not ADAPTER_DIR:
        logger.error("FATAL: ADAPTER_PATH environment variable is not set. Refusing to start.")
        sys.exit(1)
        
    if not os.path.exists(ADAPTER_DIR):
        logger.error(f"FATAL: Adapter directory {ADAPTER_DIR} not found. Refusing to run the wrong model.")
        sys.exit(1)

    has_gpu = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if has_gpu else "CPU"
    
    logger.info("=========================================")
    logger.info(f"Base model: {BASE_MODEL}")
    logger.info(f"Adapter: {ADAPTER_DIR}")
    logger.info(f"Device: {device_name}")
    logger.info(f"Quantization: 4-bit NF4")
    logger.info("=========================================")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL, 
            quantization_config=quant_config if has_gpu else None, 
            device_map="auto" if has_gpu else "cpu", 
            trust_remote_code=True
        )
        
        logger.info("Loading LoRA Adapter...")
        model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
        model.eval()
        is_ready = True
        logger.info("Model loaded successfully and is ready to serve.")
    except Exception as e:
        logger.error(f"FATAL: Failed to initialize model: {e}")
        sys.exit(1)
        
    yield
    logger.info("Shutting down inference service.")

app = FastAPI(lifespan=lifespan)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: int = Field(default=256, le=1024)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    
@app.get("/health")
async def health_check():
    if is_ready and model is not None:
        return {"status": "ok", "model": MODEL_ALIAS, "device": str(model.device)}
    raise HTTPException(status_code=503, detail="Model is loading or failed to load")

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    if not is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
        
    try:
        messages_dict = [{"role": m.role, "content": m.content} for m in req.messages]
        prompt = tokenizer.apply_chat_template(messages_dict, tokenize=False, add_generation_prompt=True)
        tokenized = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in tokenized.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=req.max_tokens,
                temperature=req.temperature,
                pad_token_id=tokenizer.pad_token_id,
                do_sample=req.temperature > 0,
                top_p=1.0 if req.temperature == 0.0 else 0.95 
            )
            
        gen_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        
        return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "model": MODEL_ALIAS,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": gen_text}, "finish_reason": "stop"}],
            "usage": {}
        }
    except Exception as e:
        logger.error("Inference failure.")
        raise HTTPException(status_code=500, detail="Internal inference error")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
