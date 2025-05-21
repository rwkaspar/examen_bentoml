import os
import builtins
import logging
import pytest
from unittest.mock import patch, MagicMock, mock_open

from src import import_data  # Pfad anpassen je nach Struktur

@pytest.fixture(autouse=True)
def clear_mocks():
    yield
    patch.stopall()

def test_main_calls_requests_and_makedirs():
    with patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("requests.get") as mock_get:
        
        # Simuliere, dass der Ordner nicht existiert, aber die Datei schon
        def side_effect(path):
            if path == "./data/raw":
                return False  # Ordner nicht da → wird erstellt
            elif path == "./data/raw/admission.csv":
                return False  # Datei nicht da → Download startet
            else:
                return True  # andere Pfade (falls welche) existieren

        
        mock_exists.side_effect = side_effect
        
        # Mock Antwort von requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "fake csv content"
        mock_get.return_value = mock_response
        
        import_data.main()
        
        # Prüfe, dass os.makedirs für den Ordner aufgerufen wurde
        mock_makedirs.assert_called_once_with("./data/raw")
        
        # Prüfe, dass requests.get für die korrekte URL aufgerufen wurde
        expected_url = "https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv"
        mock_get.assert_called_once_with(expected_url)

# def test_main_creates_directory_and_downloads_file():
#     with patch("os.path.exists", side_effect=lambda x: False) as mock_exists, \
#          patch("os.makedirs") as mock_makedirs, \
#          patch("requests.get") as mock_get, \
#          patch("builtins.open", mock_open()) as mock_file, \
#          patch("import_data.logger") as mock_logger:

#         mock_response = MagicMock()
#         mock_response.status_code = 200
#         mock_response.text = "some,csv,content"
#         mock_get.return_value = mock_response

#         import_data.main()

#         mock_makedirs.assert_called_once_with("./data/raw")
#         mock_get.assert_called_once_with(
#             "https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv"
#         )
#         mock_file().write.assert_called_once_with(b"some,csv,content")
#         mock_logger.info.assert_called_once_with('making raw data set')

# def test_main_skips_download_if_file_exists():
#     # Simulate that raw_data folder exists and output file exists
#     def exists_side_effect(path):
#         if path == "./data/raw":
#             return True
#         if path.endswith("admission.csv"):
#             return True
#         return False

#     with patch("os.path.exists", side_effect=exists_side_effect) as mock_exists, \
#          patch("os.makedirs") as mock_makedirs, \
#          patch("requests.get") as mock_get, \
#          patch.object(logging.getLogger(__name__), 'info') as mock_log_info:

#         import_data.main()

#         # Directory creation and download should NOT happen
#         mock_makedirs.assert_not_called()
#         mock_get.assert_not_called()
#         mock_log_info.assert_called_once_with("making raw data set")

# def test_main_logs_error_on_bad_response(caplog):
#     with patch("os.path.exists", side_effect=lambda x: False), \
#          patch("os.makedirs") as mock_makedirs, \
#          patch("requests.get") as mock_get:

#         # Setup mock response for requests.get with error status code
#         mock_response = MagicMock()
#         mock_response.status_code = 404
#         mock_get.return_value = mock_response

#         with caplog.at_level(logging.INFO):
#             import_data.main()
#             assert "Error accessing the object" in caplog.text
