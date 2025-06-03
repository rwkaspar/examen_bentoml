import bentoml
from pydantic import BaseModel
import numpy as np
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from starlette.exceptions import HTTPException
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.requests import Request
import jwt
from bentoml.io import JSON

JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"

USERS = {
    "user123": "password123",
    "user456": "password456"
}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(f"[DEBUG] Middleware: Request path: {request.url.path}")
        if request.url.path == "/predict":
            print("[DEBUG] Middleware: Authenticating /predict endpoint.")
            token = request.headers.get("Authorization")
            if not token:
                print("[DEBUG] Middleware: Missing authentication token.")
                return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"detail": "Missing authentication token"})

            try:
                scheme, _, token_value = token.partition(" ")
                if scheme.lower() != "bearer" or not token_value:
                    print("[DEBUG] Middleware: Invalid authorization scheme.")
                    return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"detail": "Invalid authorization scheme"})

                payload = jwt.decode(token_value, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                print(f"[DEBUG] Middleware: Token decoded for user: {payload.get('sub')}")
            except jwt.ExpiredSignatureError:
                print("[DEBUG] Middleware: Token has expired.")
                return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                print("[DEBUG] Middleware: Invalid token.")
                return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token"})

            request.state.user = payload.get("sub")

        response = await call_next(request)
        print(f"[DEBUG] Middleware: Response status: {response.status_code}")
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

async def http_exception_handler(request: Request, exc: HTTPException):
    print(f"[DEBUG] Exception Handler: Caught HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

AdmissionService.add_asgi_middleware(JWTAuthMiddleware)
AdmissionService.add_asgi_middleware(
    ExceptionMiddleware,
    handlers={HTTPException: http_exception_handler}
)

@AdmissionService.api(input=JSON(), output=JSON(), route="/login")
def login(credentials: dict, ctx: bentoml.Context):
    print("[DEBUG] Login API: Function called.")
    username = credentials.get("username")
    password = credentials.get("password")

    if username in USERS and USERS[username] == password:
        print(f"[DEBUG] Login API: Successful login for user: {username}")
        token = create_jwt_token(username)
        ctx.response.status_code = HTTP_200_OK
        return {"token": token}
    else:
        print(f"[DEBUG] Login API: Invalid credentials for user: {username}")
        ctx.response.status_code = HTTP_401_UNAUTHORIZED
        return {"detail": "Invalid credentials"}

@AdmissionService.api(
    input=JSON(pydantic_model=AdmissionInput),
    output=JSON(),
    route='/predict'
)
async def predict(input_data: AdmissionInput, ctx: bentoml.Context) -> dict:
    print("[DEBUG] Predict API: Function called.")
    request = ctx.request
    user = request.state.user if hasattr(request.state, 'user') else None
    print(f"[DEBUG] Predict API: User from state: {user}")

    features = np.array([[
        input_data.GRE_Score,
        input_data.TOEFL_Score,
        input_data.University_Rating,
        input_data.SOP,
        input_data.LOR,
        input_data.CGPA,
        input_data.Research,
    ]])
    print(f"[DEBUG] Predict API: Features prepared: {features}")

    prediction = await runner.predict.async_run(features)
    print(f"[DEBUG] Predict API: Prediction result: {prediction}")

    return {
        "admission_chance": float(prediction[0]),
        "user": user
    }

def create_jwt_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token
