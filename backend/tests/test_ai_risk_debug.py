import pytest
import uuid
import logging
from httpx import AsyncClient
from app.models.user import User, Role
from app.models.analytics import RiskHistory
from sqlalchemy import text
from app.core.security import create_access_token
from app.providers.ai.base import AIProvider, AIResponse
import datetime

logging.basicConfig(level=logging.ERROR)

@pytest.fixture
async def token_headers(db_session):
    user = User(
        email="test_ai_user5@example.com",
        full_name="AI User 5",
        hashed_password="fake",
        role=Role.MINE_MANAGER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=datetime.timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.mark.asyncio
async def test_rbac_copilot_chat(async_client: AsyncClient, token_headers, monkeypatch):
    class MockProvider:
        async def chat(self, messages, *args, **kwargs):
            return AIResponse(content="Mocked answer", model="mock", provider="mock", is_simulated=True)
        async def generate_embeddings(self, text):
            return [0.0] * 1536
    
    from app.api.v1.copilot import get_ai_provider_dep
    from app.main import app
    app.dependency_overrides[get_ai_provider_dep] = lambda: MockProvider()
    
    # We will temporarily remove the SQLAlchemyError handler to see the real traceback
    from app.core.exceptions import SQLAlchemyError
    app.exception_handlers.pop(SQLAlchemyError, None)
    
    try:
        response = await async_client.post(
            "/api/v1/copilot/chat",
            headers=token_headers,
            json={"message": "What is the compliance status?", "history": []}
        )
    except Exception as e:
        print("REAL ERROR IS:", e)
        raise
        
    app.dependency_overrides.clear()
    
    if response.status_code != 200:
        print("ERROR RESPONSE:", response.json())
        
    assert response.status_code == 200
