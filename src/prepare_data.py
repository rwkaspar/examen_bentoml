import pandas as pd
from sklearn.model_selection import train_test_split
import os

DATA_PATH = "data/raw/admission.csv"
SAVE_PATH = "data/processed"

def main():
    df = pd.read_csv(DATA_PATH)

    df = df.dropna()

    X = df.drop(columns=["Chance of Admit ", "Serial No."])
    y = df["Chance of Admit "]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    os.makedirs(SAVE_PATH, exist_ok=True)
    X_train.to_csv(f"{SAVE_PATH}/X_train.csv", index=False)
    X_test.to_csv(f"{SAVE_PATH}/X_test.csv", index=False)
    y_train.to_csv(f"{SAVE_PATH}/y_train.csv", index=False)
    y_test.to_csv(f"{SAVE_PATH}/y_test.csv", index=False)

if __name__ == "__main__":
    main()
