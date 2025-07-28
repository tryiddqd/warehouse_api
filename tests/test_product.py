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
    # Создаём товар
    response1 = await client.post("/products/", json={
        "name": "Объединяемый продукт",
        "price": 150.0,
        "quantity": 5
    })
    assert response1.status_code == 200
    data1 = response1.json()
    product_id = data1["id"]
    assert data1["quantity"] == 5

    # Повторный запрос
    response2 = await client.post("/products/", json={
        "name": "Объединяемый продукт",
        "price": 150.0,
        "quantity": 5
    })
    assert response2.status_code == 200
    data2 = response2.json()

    assert data2["quantity"] == 10
    assert data2["id"] == product_id

# ------------------
# 💥 Валидные и невалидные значения
# ------------------

@pytest.mark.asyncio
async def test_product_with_comma_in_price(client):
    response = await client.post("/products/", json={
        "name": "Запятая",
        "price": "150,5",  # ← неправильный формат
        "quantity": 1
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_product_with_zero_quantity(client):
    response = await client.post("/products/", json={
        "name": "С нулевым количеством",
        "price": 100.0,
        "quantity": 0
    })
    # Тут зависит от бизнес-логики: допустим ли 0?
    # Если нет — должен быть 422
    assert  response.status_code == 200

@pytest.mark.asyncio
async def test_product_with_empty_name(client):
    response = await client.post("/products/", json={
        "name": "",
        "price": 100.0,
        "quantity": 5
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_product_with_negative_price(client):
    response = await client.post("/products/", json={
        "name": "Минус цена",
        "price": -10.0,
        "quantity": 5
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_product_with_negative_quantity(client):
    response = await client.post("/products/", json={
        "name": "Минус количество",
        "price": 100.0,
        "quantity": -1
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_product_with_non_number_price(client):
    response = await client.post("/products/", json={
        "name": "Не число",
        "price": "abc",
        "quantity": 1
    })
    assert response.status_code == 422
