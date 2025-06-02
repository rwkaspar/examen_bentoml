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
        # Ohne Token
        response = await client.post(f"{BASE_URL}/v1/models/rf_classifier/predict", json=payload)
    assert response.status_code == 401
    assert "Missing authentication token" in response.text or "detail" in response.json()

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
        # Login zuerst
        login_resp = await client.post(f"{BASE_URL}/login", json=valid_credentials)
        token = login_resp.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}

        # Jetzt Predict mit Token
        response = await client.post(f"{BASE_URL}/v1/models/rf_classifier/predict", json=payload, headers=headers)

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
        response = await client.post(f"{BASE_URL}/v1/models/rf_classifier/predict", json=payload, headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") in ["Invalid token", "Token has expired"]

