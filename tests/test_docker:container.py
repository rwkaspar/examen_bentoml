# import pytest
# from unittest.mock import patch, MagicMock
# import pandas as pd
# import os
# import httpx

# from src import import_data, prepare_data, train_model

# ## import_data
# @pytest.fixture(autouse=True)
# def clear_mocks():
#     yield
#     patch.stopall()

# def test_main_calls_requests_and_makedirs():
#     with patch("os.path.exists") as mock_exists, \
#          patch("os.makedirs") as mock_makedirs, \
#          patch("requests.get") as mock_get:
        
#         def side_effect(path):
#             if path == "./data/raw":
#                 return False
#             elif path == "./data/raw/admission.csv":
#                 return False
#             else:
#                 return True

        
#         mock_exists.side_effect = side_effect

#         mock_response = MagicMock()
#         mock_response.status_code = 200
#         mock_response.text = "fake csv content"
#         mock_get.return_value = mock_response
        
#         import_data.main()

#         mock_makedirs.assert_called_once_with("./data/raw")

#         expected_url = "https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv"
#         mock_get.assert_called_once_with(expected_url)

# ## prepare_data
# def test_main_creates_output_dir_and_saves_files(tmp_path):
#     data = {
#         "Serial No.": [1, 2, 3, 4, 5],
#         "GRE Score": [320, 310, 300, 330, 340],
#         "TOEFL Score": [110, 105, 100, 115, 120],
#         "University Rating": [4, 3, 3, 5, 4],
#         "SOP": [4.0, 3.0, 3.5, 4.5, 4.0],
#         "LOR": [4.5, 3.5, 3.0, 4.0, 4.5],
#         "CGPA": [9.0, 8.5, 8.0, 9.5, 9.7],
#         "Research": [1, 0, 1, 1, 1],
#         "Chance of Admit ": [0.9, 0.8, 0.7, 0.95, 0.99]
#     }
#     df_mock = pd.DataFrame(data)

#     with patch("prepare_data.pd.read_csv", return_value=df_mock) as mock_read_csv, \
#          patch("os.makedirs") as mock_makedirs, \
#          patch.object(pd.DataFrame, "to_csv") as mock_df_to_csv, \
#          patch.object(pd.Series, "to_csv") as mock_series_to_csv:

#         prepare_data.SAVE_PATH = str(tmp_path)
#         prepare_data.main()

#         # Check read_csv called with correct path
#         mock_read_csv.assert_called_once_with(prepare_data.DATA_PATH)

#         # Check directory creation was attempted
#         mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)

#         # Check that to_csv was called 4 times (X_train, X_test, y_train, y_test)
#         total_calls = mock_df_to_csv.call_count + mock_series_to_csv.call_count
#         assert total_calls == 4


# ## train_model
# def test_main_trains_and_saves_model():
#     X_train = pd.DataFrame({
#         "GRE Score": [320, 310, 300],
#         "TOEFL Score": [110, 105, 100],
#         "University Rating": [4, 3, 3],
#         "SOP": [4.0, 3.0, 3.5],
#         "LOR": [4.5, 3.5, 3.0],
#         "CGPA": [9.0, 8.5, 8.0],
#         "Research": [1, 0, 1]
#     })
#     y_train = pd.DataFrame({"Chance of Admit ": [0.9, 0.8, 0.7]})
#     X_test = pd.DataFrame({
#         "GRE Score": [300, 305],
#         "TOEFL Score": [100, 102],
#         "University Rating": [3, 4],
#         "SOP": [3.0, 4.0],
#         "LOR": [3.5, 4.5],
#         "CGPA": [8.0, 8.5],
#         "Research": [0, 1]
#     })
#     y_test = pd.DataFrame({"Chance of Admit ": [0.7, 0.75]})

#     # Patch pd.read_csv so it returns the dummy data in the right order
#     with patch("train_model.pd.read_csv", side_effect=[X_train, y_train, X_test, y_test]) as mock_read_csv, \
#          patch("train_model.bentoml.sklearn.save_model") as mock_save_model:
        
#         train_model.main()

#         # Assert read_csv called 4 times with correct filenames
#         expected_calls = [
#             ("data/processed/X_train.csv",),
#             ("data/processed/y_train.csv",),
#             ("data/processed/X_test.csv",),
#             ("data/processed/y_test.csv",),
#         ]

#         actual_calls = [call.args for call in mock_read_csv.call_args_list]
#         assert actual_calls == expected_calls

#         # Check save_model called once with right model name
#         mock_save_model.assert_called_once()
#         args, kwargs = mock_save_model.call_args
#         assert args[0] == "admission_model"
#         # The model should be a LinearRegression instance
#         from sklearn.linear_model import LinearRegression
#         assert isinstance(args[1], LinearRegression)

#         # Metadata keys rmse and r2 should exist and be floats
#         metadata = kwargs.get("metadata", {})
#         assert "rmse" in metadata
#         assert isinstance(metadata["rmse"], float)
#         assert "r2" in metadata
#         assert isinstance(metadata["r2"], float)


# ## service
# BASE_URL = "http://localhost:3000"

# skip_service_tests = os.getenv("RUN_SERVICE_TESTS", "false").lower() != "true"

# valid_payload = {
# "input_data":{
#     "GRE_Score": 320,
#     "TOEFL_Score": 110,
#     "University_Rating": 4,
#     "SOP": 4.0,
#     "LOR": 4.5,
#     "CGPA": 9.0,
#     "Research": 1}
# }

# @pytest.mark.service
# @pytest.mark.asyncio
# async def test_predict_success():
#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{BASE_URL}/predict", json=valid_payload)
#         assert response.status_code == 200
#         data = response.json()
#         assert "admission_chance" in data

# @pytest.mark.service
# @pytest.mark.asyncio
# async def test_predict_missing_field():
#     payload = valid_payload.copy()
#     del payload["input_data"]["GRE_Score"]
#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{BASE_URL}/predict", json=payload)
#     assert response.status_code == 400

# @pytest.mark.service
# @pytest.mark.asyncio
# async def test_predict_invalid_type():
#     payload = valid_payload.copy()
#     payload["input_data"]["GRE_Score"] = "not_a_number"
#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{BASE_URL}/predict", json=payload)
#     assert response.status_code == 400

