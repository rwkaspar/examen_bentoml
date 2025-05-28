import bentoml
from pydantic import BaseModel
import numpy as np
from bentoml.models import BentoModel
import joblib

class AdmissionInput(BaseModel):
    GRE_Score: int
    TOEFL_Score: int
    University_Rating: int
    SOP: float
    LOR: float
    CGPA: float
    Research: int

runner = bentoml.sklearn.get("admission_model:latest").to_runner()

service = bentoml.Service("admission_prediction", runners=[runner])



@bentoml.service(name="admission_prediction")
class AdmissionService:

    model = BentoModel("admission_model:latest")
    def __init__(self):
        # Modell innerhalb der Serviceklasse laden
        # self.model = bentoml.sklearn.get("admission_model:latest")
        self.model = joblib.load(self.model.path_of("saved_model.pkl"))  # Modell mit joblib laden

@service.api(input=bentoml.io.JSON(), output=bentoml.io.JSON())
async def predict(input_data: AdmissionInput) -> dict:
#async def predict(input_data: AdmissionInput, ctx: bentoml.Context) -> dict:
    # request = ctx.request
    features = np.array([[
        input_data.GRE_Score,
        input_data.TOEFL_Score,
        input_data.University_Rating,
        input_data.SOP,
        input_data.LOR,
        input_data.CGPA,
        input_data.Research,
    ]])
    prediction = await runner.predict.async_run(features) # self.model verwenden
    return {"admission_chance": float(prediction[0])}