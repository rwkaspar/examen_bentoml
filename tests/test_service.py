import pytest
import httpx

BASE_URL = "http://localhost:3000"

valid_credentials = {"username": "user123", "password": "password123"}

@pytest.mark.asyncio
async def test_login_success():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/login", json=valid_credentials)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0

@pytest.mark.asyncio
async def test_login_failure():
    invalid_credentials = {"username": "user123", "password": "wrongpassword"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/login", json=invalid_credentials)
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Invalid credentials"

@pytest.mark.asyncio
async def test_predict_requires_auth():
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.0,
        "LOR": 4.5,
        "CGPA": 9.0,
        "Research": 1,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Missing authentication token"

@pytest.mark.asyncio
async def test_predict_success():
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.0,
        "LOR": 4.5,
        "CGPA": 9.0,
        "Research": 1,
    }
    async with httpx.AsyncClient() as client:
        login_resp = await client.post(f"{BASE_URL}/login", json=valid_credentials)
        assert login_resp.status_code == 200
        token = login_resp.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(f"{BASE_URL}/predict", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "admission_chance" in data
    assert isinstance(data["admission_chance"], float)

@pytest.mark.asyncio
async def test_predict_invalid_token():
    payload = {
        "GRE_Score": 320,
        "TOEFL_Score": 110,
        "University_Rating": 4,
        "SOP": 4.0,
        "LOR": 4.5,
        "CGPA": 9.0,
        "Research": 1,
    }
    headers = {"Authorization": "Bearer invalid.token.value"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/predict", json=payload, headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Invalid token"