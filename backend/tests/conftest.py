from sqlalchemy import pool
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from alembic import command
from alembic.config import Config

# Force test database URL for local docker PostgreSQL
TEST_DB_URL = "postgresql+asyncpg://coalmine:coalmine_dev_password@localhost:5432/coalmine_test"
os.environ["DATABASE_URL"] = TEST_DB_URL

from app.database import get_db
from app.main import app
from app.config import get_settings

engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=pool.NullPool)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield

@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.begin_nested()
        
        async_session = async_sessionmaker(conn, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session
            
        await conn.rollback()

@pytest.fixture(autouse=True)
def override_dependency(db_session):
    async def _get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

