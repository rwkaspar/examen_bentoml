import pytest
import httpx

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
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/predict", json=valid_payload)
        assert response.status_code == 200
        data = response.json()
        assert "admission_chance" in data

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

