import pytest
import httpx
from unittest.mock import AsyncMock, patch

BASE_URL = "http://localhost:3000"

valid_payload = {
"input_data":{
    "GRE_Score": 320,
    "TOEFL_Score": 110,
    "University_Rating": 4,
    "SOP": 4.0,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1}
}

@pytest.mark.asyncio
async def test_predict_success():
    valid_payload = {...}  # deine payload

    # Mock AsyncClient.post, damit kein echter Request ausgeführt wird
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json = lambda: {"prediction": 0.85}

        async with httpx.AsyncClient() as client:
            response = await client.post("http://fake-url/predict", json=valid_payload)
            assert response.status_code == 200
            assert "prediction" in response.json()

@pytest.mark.asyncio
async def test_predict_missing_field():
    payload = valid_payload.copy()
    del payload["input_data"]["GRE_Score"]
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_predict_invalid_type():
    payload = valid_payload.copy()
    payload["input_data"]["GRE_Score"] = "not_a_number"
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 400

