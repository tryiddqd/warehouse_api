# tests/conftest.py
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
import pytest_asyncio
from sqlalchemy import text
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app
from app.core.database import Base, get_db, SessionLocal

# Создаём таблицы в тестовой БД
Base.metadata.create_all(bind=SessionLocal.kw["bind"])

# Переопределение зависимости get_db
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    db.execute(text("DELETE FROM order_items"))
    db.execute(text("DELETE FROM orders"))
    db.execute(text("DELETE FROM products"))
    db.commit()
    db.close()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
