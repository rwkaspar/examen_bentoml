import bentoml
from pydantic import BaseModel
import numpy as np
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt

JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"
USERS = {"user123": "password123", "user456": "password456"}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/predict":
            token = request.headers.get("Authorization")
            if not token:
                # return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})
                return {"error": "Missing authentication token", "status_code": 401}
            try:
                token = token.split()[1]
                jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                # return JSONResponse(status_code=401, content={"detail": "Token has expired"})
                return {"error": "Token has expired", "status_code": 401}
            except jwt.InvalidTokenError:
                # return JSONResponse(status_code=401, content={"detail": "Invalid token"})
                return {"error": "Invalid token", "status_code": 401}
        response = await call_next(request)
        return response

class AdmissionInput(BaseModel):
    GRE_Score: int
    TOEFL_Score: int
    University_Rating: int
    SOP: float
    LOR: float
    CGPA: float
    Research: int

runner = bentoml.sklearn.get("admission_model:latest").to_runner()
AdmissionService = bentoml.Service("admission_prediction", runners=[runner])
AdmissionService.add_asgi_middleware(JWTAuthMiddleware)

@AdmissionService.api(input=bentoml.io.JSON(), output=bentoml.io.JSON(), route="/login")
def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")
    if username in USERS and USERS[username] == password:
        token = create_jwt_token(username)
        return {"token": token}
    else:
        # return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
        return {"error": "Invalid credentials", "status_code": 401}

@AdmissionService.api(input=bentoml.io.JSON(), output=bentoml.io.JSON(), route="/predict")
async def predict(input_data: AdmissionInput):
    features = np.array([[
        input_data.GRE_Score,
        input_data.TOEFL_Score,
        input_data.University_Rating,
        input_data.SOP,
        input_data.LOR,
        input_data.CGPA,
        input_data.Research,
    ]])
    prediction = await runner.predict.async_run(features)
    return {"admission_chance": float(prediction[0])}

def create_jwt_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": user_id, "exp": expiration}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token
