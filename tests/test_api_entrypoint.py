
import pytest

@pytest.mark.asyncio
async def test_docs_endpoint(client):
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_openapi_json(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/products/" in data["paths"]


@pytest.mark.asyncio
async def test_healthcheck_root(client):
    response = await client.get("/")
    # Если у вас есть обработчик на "/", то замените на правильную проверку:
    assert response.status_code in (200, 404)