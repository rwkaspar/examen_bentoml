import bentoml
from pydantic import BaseModel
import numpy as np
from bentoml.models import BentoModel
import joblib
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt

# Secret key and algorithm for JWT authentication
JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"

# User credentials for authentication
USERS = {
    "user123": "password123",
    "user456": "password456"
}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/v1/models/rf_classifier/predict":
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})

            try:
                token = token.split()[1]  # Remove 'Bearer ' prefix
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

            request.state.user = payload.get("sub")

        response = await call_next(request)
        return response

# Pydantic model to validate input data
class AdmissionInput(BaseModel):
    GRE_Score: int
    TOEFL_Score: int
    University_Rating: int
    SOP: float
    LOR: float
    CGPA: float
    Research: int

# Get the model from the Model Store
runner = bentoml.sklearn.get("admission_model:latest").to_runner()

# Create a service API
service = bentoml.Service("admission_prediction", runners=[runner])

# Add the JWTAuthMiddleware to the service
service.add_asgi_middleware(JWTAuthMiddleware)

# Create an API endpoint for the service
@service.api(input=bentoml.io.JSON(), output=bentoml.io.JSON())
def login(credentials: dict) -> dict:
    username = credentials.get("username")
    password = credentials.get("password")

    if username in USERS and USERS[username] == password:
        token = create_jwt_token(username)
        return {"token": token}
    else:
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})


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

# Function to create a JWT token
def create_jwt_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token