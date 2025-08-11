# tests/conftest.py
import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from httpx import AsyncClient
from httpx import ASGITransport


# --- env ---
load_dotenv()
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not set. Example: "
        "postgresql+psycopg://postgres:postgres@localhost:5432/warehouse_test"
    )

# Safety: требуем отдельную тестовую БД
if "warehouse_test" not in TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL must point to a dedicated test DB (expected name like 'warehouse_test')."
    )

# --- async engine / session strictly for tests ---
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
SessionTest = sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


# --- FastAPI dependency override: всегда отдаём тестовую сессию ---
async def override_get_db():
    async with SessionTest() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


# --- schema lifecycle ---

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Создаём чистую схему один раз на сьют.
    """
    async with engine_test.begin() as conn:
        # Гарантированно чистим перед созданием (на случай предыдущих запусков)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Закрываем engine после всех тестов
    await engine_test.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clear_db():
    """
    Очищаем все таблицы перед каждым тестом.
    Вариант с DELETE по всем таблицам прозрачен и независим от транзакций клиента.
    """
    async with engine_test.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


# --- HTTP клиент для тестов ---
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
