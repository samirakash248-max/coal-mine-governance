import pytest
import os
import json
from httpx import AsyncClient
from app.main import app
from app.providers.ai.local import LocalModelProvider
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_local_provider_timeout_or_offline():
    # Force an invalid URL to simulate offline/timeout
    os.environ["AI_BASE_URL"] = "http://localhost:9999/invalid"
    provider = LocalModelProvider()
    
    with pytest.raises(Exception) as exc:
        await provider.classify_event("Should fail")
    assert exc.value.status_code == 503

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_local_provider_successful_inference(mock_post):
    provider = LocalModelProvider()
    
    # Mock successful response
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={
        "choices": [{"message": {"content": '{"event_type": "incident", "category": "safety", "severity": "medium", "needs_human_review": true}'}}]
    })
    mock_post.return_value = mock_response
    
    result = await provider.classify_event("Worker tripped.")
    
    assert result["is_simulated"] is False
    assert result["event_type"] == "incident"
    assert result["severity"] == "medium"
    assert result["needs_human_review"] is True

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_local_provider_malformed_json(mock_post):
    provider = LocalModelProvider()
    
    # Mock malformed response
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={
        "choices": [{"message": {"content": 'This is not json { "event_type": "incident"'}}]
    })
    mock_post.return_value = mock_response
    
    result = await provider.classify_event("Worker tripped.")
    
    assert result["is_simulated"] is True
    assert "error" in result
