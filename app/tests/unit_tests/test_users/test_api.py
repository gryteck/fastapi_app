from httpx import AsyncClient


async def test_register_user(ac: AsyncClient):
    body = {
        "email": "kot@pes.com",
        "password": "kotopes",
    }

    response = await ac.post("/auth/register", json=body)
    assert response.status_code == 200
