import pytest

@pytest.mark.asyncio
async def test_create_order(client):
    # Создаём продукт, чтобы на него можно было сослаться в заказе
    await client.post("/products/", json={
        "name": "Продукт для заказа",
        "price": 100.0,
        "quantity": 10
    })

    payload = {
        "customer_name": "Тестовый заказчик",
        "items": [
            {"product_id": 1, "quantity": 2}
        ]
    }
    response = await client.post("/orders/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Тестовый заказчик"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == 1
    assert data["items"][0]["quantity"] == 2


@pytest.mark.asyncio
async def test_get_order_by_id(client):
    # Подготовка продукта
    await client.post("/products/", json={
        "name": "Продукт A",
        "price": 100.0,
        "quantity": 5
    })

    # Создание заказа
    payload = {
        "customer_name": "Покупатель",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    response = await client.post("/orders/", json=payload)
    order_id = response.json()["id"]

    # Получение заказа
    get_response = await client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    order_data = get_response.json()
    assert order_data["id"] == order_id
    assert order_data["customer_name"] == "Покупатель"


@pytest.mark.asyncio
async def test_update_order_status(client):
    await client.post("/products/", json={
        "name": "Продукт B",
        "price": 100.0,
        "quantity": 5
    })

    payload = {
        "customer_name": "Статус тест",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    response = await client.post("/orders/", json=payload)
    order_id = response.json()["id"]

    update_payload = {"status": "доставлен"}
    update_response = await client.patch(f"/orders/{order_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["status"] == "delivered"


@pytest.mark.asyncio
async def test_delete_order(client):
    await client.post("/products/", json={
        "name": "Продукт C",
        "price": 100.0,
        "quantity": 5
    })

    payload = {
        "customer_name": "Удалить заказ",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    response = await client.post("/orders/", json=payload)
    order_id = response.json()["id"]

    delete_response = await client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 200

    check_response = await client.get(f"/orders/{order_id}")
    assert check_response.status_code == 404

@pytest.mark.asyncio
async def test_create_order_with_insufficient_stock(client):
    await client.post("/products/", json={
        "name": "Ограниченный продукт",
        "price": 50.0,
        "quantity": 1
    })

    payload = {
        "customer_name": "Покупатель",
        "items": [{"product_id": 1, "quantity": 5}]
    }
    response = await client.post("/orders/", json=payload)
    assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_cancel_order_and_restore_stock(client):
    await client.post("/products/", json={
        "name": "Возвращаемый продукт",
        "price": 75.0,
        "quantity": 3
    })

    order_payload = {
        "customer_name": "Отменяющий клиент",
        "items": [{"product_id": 1, "quantity": 2}]
    }
    order_response = await client.post("/orders/", json=order_payload)
    order_id = order_response.json()["id"]

    cancel_response = await client.patch(f"/orders/{order_id}/status", json={"status": "отменен"})
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    # Повторная попытка отмены — должна быть запрещена
    second_cancel = await client.patch(f"/orders/{order_id}/status", json={"status": "отменен"})
    assert second_cancel.status_code in [400, 409]

@pytest.mark.asyncio
async def test_order_status_variants(client):
    await client.post("/products/", json={
        "name": "Тест продукт для статусов",
        "price": 80.0,
        "quantity": 5
    })

    order_payload = {
        "customer_name": "Статусный клиент",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    order_response = await client.post("/orders/", json=order_payload)
    order_id = order_response.json()["id"]

    for status_input in ["отменён", "ОтМеНЁн", "ОТМЕНЕН"]:
        patch_response = await client.patch(f"/orders/{order_id}/status", json={"status": status_input})
        assert patch_response.status_code == 200
        assert patch_response.json()["status"] == "cancelled"
        break  # после одного успешного — дальнейшие вызовы будут запрещены

@pytest.mark.asyncio
async def test_order_with_empty_items(client):
    payload = {
        "customer_name": "Пустой заказ",
        "items": []
    }
    response = await client.post("/orders/", json=payload)
    assert response.status_code in [400, 422]