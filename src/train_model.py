import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error, r2_score
import bentoml
from datetime import datetime # Import datetime for optional timestamp

def main():
    X_train = pd.read_csv("data/processed/X_train.csv")
    y_train = pd.read_csv("data/processed/y_train.csv")
    X_test = pd.read_csv("data/processed/X_test.csv")
    y_test = pd.read_csv("data/processed/y_test.csv")

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")

    saved_model = bentoml.sklearn.save_model(
        "admission_model",
        model,
        metadata={
            "rmse": float(rmse),
            "r2": float(r2),
            "training_date": datetime.now().isoformat()
        }
    )
    print(f"Model saved: {saved_model}")

if __name__ == "__main__":
    main()