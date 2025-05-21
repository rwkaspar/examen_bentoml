import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from src import train_model

def test_main_trains_and_saves_model():
    X_train = pd.DataFrame({
        "GRE Score": [320, 310, 300],
        "TOEFL Score": [110, 105, 100]
    })
    y_train = pd.DataFrame({"Chance of Admit ": [0.9, 0.8, 0.7]})
    X_test = pd.DataFrame({
        "GRE Score": [300, 305],
        "TOEFL Score": [100, 102]
    })
    y_test = pd.DataFrame({"Chance of Admit ": [0.7, 0.75]})

    # Patch pd.read_csv so it returns the dummy data in the right order
    with patch("train_model.pd.read_csv", side_effect=[X_train, y_train, X_test, y_test]) as mock_read_csv, \
         patch("train_model.bentoml.sklearn.save_model") as mock_save_model:
        
        train_model.main()

        # Assert read_csv called 4 times with correct filenames
        expected_calls = [
            ("data/processed/X_train.csv",),
            ("data/processed/y_train.csv",),
            ("data/processed/X_test.csv",),
            ("data/processed/y_test.csv",),
        ]

        actual_calls = [call.args for call in mock_read_csv.call_args_list]
        assert actual_calls == expected_calls

        # Check save_model called once with right model name
        mock_save_model.assert_called_once()
        args, kwargs = mock_save_model.call_args
        assert args[0] == "admission_model"
        # The model should be a LinearRegression instance
        from sklearn.linear_model import LinearRegression
        assert isinstance(args[1], LinearRegression)

        # Metadata keys rmse and r2 should exist and be floats
        metadata = kwargs.get("metadata", {})
        assert "rmse" in metadata
        assert isinstance(metadata["rmse"], float)
        assert "r2" in metadata
        assert isinstance(metadata["r2"], float)
