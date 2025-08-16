import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("payload, exp_msg", [
    ({"message": "Hi"}, "Hi"),
    ({"message": "Hi", "uppercase": True}, "HI"),
    ({"message": "Hi", "times": 3}, "HiHiHi"),
])
async def test_echo(client, payload, exp_msg):
    response = await client.post("/system/echo", json=payload)
    assert response.status_code == 200
    data= response.json()
    assert data["message"] == exp_msg
    assert data["length"] == len(exp_msg)

@pytest.mark.asyncio
async def test_healthz(client):
    response = await client.get("/system/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["version"] == "0.1"

@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [
    {"message": ""},
    {"message": "Hi", "times": 0},
    {"message": "Hi", "times": 11},
])
async def test_echo_validation_error(client, payload):
    resp = await client.post("/system/echo", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert "detail" in data

