
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time, uuid

app = FastAPI()

users_db = {
    "admin": {"username": "admin", "password": "123456", "role": "admin"},
    "test": {"username": "test", "password": "1234", "role": "user"}
}

active_sessions = {}

class SignalRequest(BaseModel):
    symbol: str
    timeframe: str
    risk_reward: float

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    user = users_db.get(data.username)
    if user and user["password"] == data.password:
        token = str(uuid.uuid4())
        active_sessions[token] = {
            "username": user["username"],
            "role": user["role"],
            "timestamp": time.time()
        }
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/generate-signal")
async def generate_signal(data: SignalRequest, token: str):
    if token not in active_sessions:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {
        "signal": "شراء",
        "price": 27500,
        "stop_loss": 27000,
        "take_profit": 28500
    }

@app.get("/subscription")
def get_subscription(token: str):
    username = active_sessions.get(token, {}).get("username")
    if username == "admin":
        return {"plan": "VIP", "expires": "2099-12-31"}
    elif username == "test":
        return {"plan": "Free", "expires": "2025-01-01"}
    return {"plan": "Free", "expires": "N/A"}

@app.get("/api/v1/signal")
def api_get_signal(symbol: str, timeframe: str, risk: float):
    return {
        "symbol": symbol,
        "signal": "شراء",
        "entry": 27700,
        "stop_loss": 27200,
        "take_profit": 28700
    }
