# tests/test_product_race.py
import asyncio
import pytest

# Этот тест требует PostgreSQL и уникальности по products.name
# См. миграцию "add unique constraint on products.name"

@pytest.mark.asyncio
async def test_parallel_create_same_name(client):
    name = "race-item"
    n = 10  # сколько параллельных запросов
    payload = {
        "name": name,
        "description": None,
        "price": 1.0,
        "quantity": 1,
    }

    async def create_once():
        # небольшая уступка планировщику, чтобы повысить шанс гонки
        await asyncio.sleep(0)
        resp = await client.post("/products/", json=payload)
        # при upsert обычно 201, но на всякий случай допускаем 200
        assert resp.status_code in (200, 201)
        return resp.json()

    # Шлём n запросов одновременно
    results = await asyncio.gather(*[create_once() for _ in range(n)])

    # Убедимся, что сервер отвечал валидным JSON с нужным именем
    assert all(item["name"] == name for item in results)

    # Получаем список товаров и проверяем агрегированный результат
    resp_list = await client.get("/products/")
    assert resp_list.status_code == 200
    items = resp_list.json()

    # Находим нужный продукт
    target = [p for p in items if p["name"] == name]
    assert len(target) == 1, "Должна остаться одна строка с таким именем"
    assert target[0]["quantity"] == n, f"Количество должно суммироваться до {n}"
