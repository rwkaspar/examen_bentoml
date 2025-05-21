import pytest
from unittest.mock import patch, MagicMock, mock_open

from src import import_data

@pytest.fixture(autouse=True)
def clear_mocks():
    yield
    patch.stopall()

def test_main_calls_requests_and_makedirs():
    with patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("requests.get") as mock_get:
        
        def side_effect(path):
            if path == "./data/raw":
                return False
            elif path == "./data/raw/admission.csv":
                return False
            else:
                return True

        
        mock_exists.side_effect = side_effect

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "fake csv content"
        mock_get.return_value = mock_response
        
        import_data.main()

        mock_makedirs.assert_called_once_with("./data/raw")

        expected_url = "https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv"
        mock_get.assert_called_once_with(expected_url)
