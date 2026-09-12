# Deployment Guide

This guide describes how to deploy the AI-Based Smart Governance & Compliance System for Coal Mines.

## Architecture Overview

The system consists of three independently deployable services:
1. **Frontend**: Vite + React PWA
2. **Backend API**: FastAPI (Python)
3. **GPU Model Server**: Dedicated Qwen3-4B Inference Service (Python, PyTorch)

## A. Local Development Setup (SQLite)

For local development or SIH demo purposes, you can run all services using `docker-compose.yml`.

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU (at least 4GB VRAM) & NVIDIA Container Toolkit (if running the model server locally via Docker)

### Startup
1. **Create Environment File**:
   Copy `.env.example` to `.env` and adjust values (e.g. `SECRET_KEY`).
2. **Start Services**:
   ```bash
   docker compose up --build
   ```
   *Note: If you do not have an NVIDIA GPU, you can run the model server natively outside Docker or configure `AI_PROVIDER=mock` in your backend `.env`.*

3. **Reset Demo Data** (Development Only):
   ```bash
   docker compose exec backend python scripts/seed_demo.py --reset
   ```

## B. Cloud / Production Deployment

In a production environment, the three services should be separated.

### 1. Database
Deploy a managed PostgreSQL database. Update the backend environment variable:
`DATABASE_URL=postgresql+asyncpg://user:password@hostname/dbname`

### 2. GPU Model Server (Qwen3-4B)
This service **requires an NVIDIA GPU**.
1. Build the Docker image from `model-server/Dockerfile`.
2. Provision a GPU-backed cloud instance (e.g., AWS g4dn, GCP T4, RunPod, or Lambda Cloud).
3. The instance must have the base Qwen3-4B model and your trained LoRA adapter.
4. Mount the adapter directory and configure environment variables:
   - `MODEL_NAME=Qwen/Qwen3-4B`
   - `ADAPTER_PATH=/path/to/mounted/adapter`
   - `PORT=8001`
5. Expose the API privately to the Backend API. **Do not expose this service directly to the public internet**.

### 3. Backend API
1. Build the Docker image from `backend/Dockerfile`.
2. Deploy to a standard container hosting service (e.g., AWS ECS, Google Cloud Run).
3. Configure environment variables:
   - `AI_BASE_URL=http://<model-server-internal-ip>:8001/v1`
   - `AI_PROVIDER=local`
   - `DATABASE_URL=...`
   - `SECRET_KEY=...`
   - `CORS_ORIGINS=["https://coal-core-frontend.com"]`

### 4. Frontend
1. Set the API URL during build:
   `VITE_API_BASE_URL=https://api.yourdomain.com/api/v1 npm run build`
2. Deploy the static `dist/` directory to a CDN or static hosting provider (e.g., Vercel, Netlify, AWS S3+CloudFront).

## Health Checks
- **Backend**: `GET /health` (Returns JSON status, handles DB ping)
- **Model Server**: `GET /health` (Returns JSON status if the model is fully loaded onto the GPU)

> **Note**: The backend health check will not fail if the AI service goes offline, ensuring your governance web application remains up even if the AI copilot degrades.
