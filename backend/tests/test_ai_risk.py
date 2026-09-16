import pytest
import uuid
from httpx import AsyncClient
from app.models.user import User, Role
from app.models.analytics import RiskHistory
from sqlalchemy import text
from app.core.security import create_access_token
from app.providers.ai.base import AIProvider, AIResponse
import datetime

@pytest.fixture
async def token_headers(db_session):
    user = User(
        email="test_ai_user2@example.com",
        full_name="AI User 2",
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
async def test_risk_level_determinism(db_session):
    from app.services.risk_engine import RiskEngine
    from app.models.hierarchy import Mine, Organization, Subsidiary, Region
    
    org = Organization(id=uuid.uuid4(), name="Org")
    sub = Subsidiary(id=uuid.uuid4(), name="Sub", organization_id=org.id)
    reg = Region(id=uuid.uuid4(), name="Reg", subsidiary_id=sub.id)
    mine = Mine(id=uuid.uuid4(), name="Test Mine", region_id=reg.id)
    
    db_session.add_all([org, sub, reg, mine])
    await db_session.commit()
    
    engine = RiskEngine(db_session)
    history = await engine.evaluate_mine(mine.id)
    
    assert history.score == 0
    assert history.factors["risk_level"] == "LOW"

@pytest.mark.asyncio
async def test_ai_unavailable_fallback(async_client: AsyncClient, token_headers):
    # We expect 500 or 503 when AI is not reachable
    response = await async_client.get(
        "/api/v1/copilot/daily-brief",
        headers=token_headers
    )
    assert response.status_code in [500, 503]

@pytest.mark.asyncio
async def test_rbac_copilot_chat(async_client: AsyncClient, token_headers, monkeypatch):
    # Mock AI provider
    class MockProvider:
        async def chat(self, messages, *args, **kwargs):
            return AIResponse(content="Mocked answer", model="mock", provider="mock", is_simulated=True)
        async def generate_embeddings(self, text):
            return [0.0] * 1536
    
    from app.api.v1.copilot import get_ai_provider_dep
    from app.main import app
    app.dependency_overrides[get_ai_provider_dep] = lambda: MockProvider()
    
    response = await async_client.post(
        "/api/v1/copilot/chat",
        headers=token_headers,
        json={"message": "What is the compliance status?", "history": []}
    )
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Mocked answer"
