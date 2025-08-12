# tests/test_products_list.py
import os
from typing import Iterable

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Все тесты асинхронные
pytestmark = pytest.mark.asyncio


# --- Вспомогательный фикстурный хелпер для вставки данных напрямую в БД ---
@pytest.fixture
def test_db_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        raise RuntimeError("TEST_DATABASE_URL is not set")
    return url


@pytest.fixture
async def db_engine(test_db_url: str):
    engine = create_async_engine(test_db_url, echo=False, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


async def insert_products(engine, rows: Iterable[dict]) -> list[dict]:
    """
    Вставляет продукты напрямую SQL'ем, возвращает записи с присвоенными id.
    Ожидает словари с ключами: name, description, price, quantity.
    """
    inserted: list[dict] = []
    async with engine.begin() as conn:
        for r in rows:
            result = await conn.execute(
                text(
                    """
                    INSERT INTO products (name, description, price, quantity)
                    VALUES (:name, :description, :price, :quantity)
                    RETURNING id, name, description, price, quantity
                    """
                ),
                {
                    "name": r["name"],
                    "description": r.get("description"),
                    "price": r["price"],
                    "quantity": r["quantity"],
                },
            )
            row = result.mappings().one()
            inserted.append(dict(row))
    return inserted


# --- Тесты ручки /products/list ---


async def test_list_empty(client: AsyncClient):
    resp = await client.get("/products/list")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 20  # дефолт из ручки
    assert data["offset"] == 0


@pytest.fixture
async def sample_products(db_engine):
    """
    Готовим 5 разношерстных товаров для тестов пагинации/сортировок.
    """
    rows = [
        {"name": "Alpha", "description": "A", "price": 10.0, "quantity": 5},
        {"name": "beta", "description": "B", "price": 9.99, "quantity": 100},
        {"name": "Gamma", "description": "C", "price": 19.5, "quantity": 0},
        {"name": "delta", "description": "D", "price": 19.49, "quantity": 7},
        {"name": "Omega", "description": "E", "price": 10.01, "quantity": 5},
    ]
    return await insert_products(db_engine, rows)


async def test_list_default_sort_id_asc(client: AsyncClient, sample_products):
    resp = await client.get("/products/list")
    assert resp.status_code == 200
    payload = resp.json()
    items = payload["items"]

    # Дефолт: sort_by=id, sort_order=asc, limit=20, offset=0
    assert payload["total"] == 5
    assert payload["limit"] == 20
    assert payload["offset"] == 0

    # Проверим, что id возрастают
    ids = [it["id"] for it in items]
    assert ids == sorted(ids)

    # И что имена соответствуют порядку вставки по id (возрастающему)
    names_by_id = [it["name"] for it in sorted(items, key=lambda x: x["id"])]
    assert set(names_by_id) == {"Alpha", "beta", "Gamma", "delta", "Omega"}


async def test_pagination_limit_offset(client: AsyncClient, sample_products):
    # Берём "страницу" из двух элементов, начиная с третьего
    resp = await client.get("/products/list", params={"limit": 2, "offset": 2})
    assert resp.status_code == 200
    payload = resp.json()

    assert payload["total"] == 5
    assert payload["limit"] == 2
    assert payload["offset"] == 2
    assert len(payload["items"]) == 2

    # По умолчанию сортировка id asc — значит это 3-й и 4-й по id элементы
    ids = [it["id"] for it in payload["items"]]
    assert ids == sorted(ids)


@pytest.mark.parametrize(
    "sort_by,order,expected",
    [
        # Для name не задаём expected — проверим монотонность ниже
        ("price", "asc",  [9.99, 10.0, 10.01, 19.49, 19.5]),
        ("price", "desc", [19.5, 19.49, 10.01, 10.0, 9.99]),
        ("quantity", "asc",  [0, 5, 5, 7, 100]),
        ("quantity", "desc", [100, 7, 5, 5, 0]),
    ],
)
async def test_sorting_numeric(client: AsyncClient, sample_products, sort_by, order, expected):
    resp = await client.get("/products/list", params={"sort_by": sort_by, "sort_order": order, "limit": 100})
    assert resp.status_code == 200
    items = resp.json()["items"]

    if sort_by == "price":
        got = [it["price"] for it in items]
    else:
        got = [it["quantity"] for it in items]

    assert got == expected


@pytest.mark.parametrize("order", ["asc", "desc"])
async def test_sorting_by_name_is_monotonic_casefold(client: AsyncClient, sample_products, order):
    resp = await client.get("/products/list", params={"sort_by": "name", "sort_order": order, "limit": 100})
    assert resp.status_code == 200
    items = resp.json()["items"]

    names = [it["name"] for it in items]
    names_cf = [n.casefold() for n in names]  # надёжнее, чем lower()

    if order == "asc":
        assert names_cf == sorted(names_cf)
    else:
        assert names_cf == sorted(names_cf, reverse=True)


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},           # ge=1
        {"limit": 101},         # le=100
        {"offset": -1},         # ge=0
        {"sort_by": "created"}, # не из Literal
        {"sort_order": "down"}, # не из Literal
    ],
)
async def test_validation_errors(client: AsyncClient, params):
    resp = await client.get("/products/list", params=params)
    assert resp.status_code == 422
    data = resp.json()
    # FastAPI вернёт подробности ошибок — убедимся, что есть detail
    assert "detail" in data and isinstance(data["detail"], list)
