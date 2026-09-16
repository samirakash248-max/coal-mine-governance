import pytest
from httpx import AsyncClient
from sqlalchemy import text
from app.models.user import User, Role

@pytest.mark.asyncio
async def test_database_health(db_session):
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_422_validation_error_format(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "not_an_email"}
    )
    assert response.status_code == 422
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "detail" in data
