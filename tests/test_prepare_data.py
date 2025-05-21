import pandas as pd
from unittest.mock import patch
from src import prepare_data

def test_main_creates_output_dir_and_saves_files(tmp_path):
    data = {
        "Serial No.": [1, 2, 3, 4, 5],
        "GRE Score": [320, 310, 300, 330, 340],
        "TOEFL Score": [110, 105, 100, 115, 120],
        "University Rating": [4, 3, 3, 5, 4],
        "SOP": [4.0, 3.0, 3.5, 4.5, 4.0],
        "LOR": [4.5, 3.5, 3.0, 4.0, 4.5],
        "CGPA": [9.0, 8.5, 8.0, 9.5, 9.7],
        "Research": [1, 0, 1, 1, 1],
        "Chance of Admit ": [0.9, 0.8, 0.7, 0.95, 0.99]
    }
    df_mock = pd.DataFrame(data)

    with patch("prepare_data.pd.read_csv", return_value=df_mock) as mock_read_csv, \
         patch("os.makedirs") as mock_makedirs, \
         patch.object(pd.DataFrame, "to_csv") as mock_df_to_csv, \
         patch.object(pd.Series, "to_csv") as mock_series_to_csv:

        prepare_data.SAVE_PATH = str(tmp_path)
        prepare_data.main()

        # Check read_csv called with correct path
        mock_read_csv.assert_called_once_with(prepare_data.DATA_PATH)

        # Check directory creation was attempted
        mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)

        # Check that to_csv was called 4 times (X_train, X_test, y_train, y_test)
        total_calls = mock_df_to_csv.call_count + mock_series_to_csv.call_count
        assert total_calls == 4
