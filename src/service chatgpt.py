import bentoml
from pydantic import BaseModel
import numpy as np

class AdmissionInput(BaseModel):
    GRE_Score: int
    TOEFL_Score: int
    University_Rating: int
    SOP: float
    LOR: float
    CGPA: float
    Research: int

@bentoml.service(name="admission_prediction")
class AdmissionService:
    def __init__(self):
        # Modell innerhalb der Serviceklasse laden
        self.model = bentoml.sklearn.get("admission_model:latest")

    @bentoml.api
    async def predict(self, input_data: AdmissionInput) -> dict:
        features = np.array([[
            input_data.GRE_Score,
            input_data.TOEFL_Score,
            input_data.University_Rating,
            input_data.SOP,
            input_data.LOR,
            input_data.CGPA,
            input_data.Research,
        ]])
        prediction = self.model.predict(features) # self.model verwenden
        return {"admission_chance": float(prediction[0])}