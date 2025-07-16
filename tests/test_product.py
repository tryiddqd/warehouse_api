# tests/test_product.py
import pytest

@pytest.mark.asyncio
async def test_create_product_success(client):
    response = await client.post("/products/", json={
        "name": "Тестовый продукт",
        "price": 150.0,
        "quantity": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Тестовый продукт"
    assert data["price"] == 150.0
    assert data["quantity"] == 5

@pytest.mark.asyncio
async def test_add_product_success(client):
    await client.post("/products/", json={
        "name": "Объединяемый продукт",
        "price": 150.0,
        "quantity": 5
    })

    response = await client.post("/products/", json={
        "name": "Объединяемый продукт",
        "price": 150.0,
        "quantity": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Объединяемый продукт"
    assert data["price"] == 150.0
    assert data["quantity"] == 10
