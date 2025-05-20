import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error, r2_score
import bentoml

def main():
    # Daten laden
    X_train = pd.read_csv("data/processed/X_train.csv")
    y_train = pd.read_csv("data/processed/y_train.csv")
    X_test = pd.read_csv("data/processed/X_test.csv")
    y_test = pd.read_csv("data/processed/y_test.csv")

    # Modell trainieren
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Vorhersage und Bewertung
    y_pred = model.predict(X_test)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")

    # Modell speichern
    bentoml.sklearn.save_model(
        "admission_model",
        model,
        metadata={"rmse": rmse, "r2": r2}
    )

if __name__ == "__main__":
    main()
