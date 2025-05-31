
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
import time, uuid

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

users_db = {
    "admin": {"username": "admin", "password": "123456", "role": "admin"},
    "test": {"username": "test", "password": "1234", "role": "user"}
}

active_sessions = {}

class SignalRequest(BaseModel):
    symbol: str
    timeframe: str
    risk_reward: float

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if user and user["password"] == form_data.password:
        token = str(uuid.uuid4())
        active_sessions[token] = {"username": user["username"], "role": user["role"], "timestamp": time.time()}
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/generate-signal")
async def generate_signal(data: SignalRequest, token: str = Depends(oauth2_scheme)):
    if token not in active_sessions:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {
        "signal": "شراء",
        "price": 27500,
        "stop_loss": 27000,
        "take_profit": 28500
    }

@app.get("/api/v1/signal")
def api_get_signal(symbol: str, timeframe: str, risk: float):
    return {
        "symbol": symbol,
        "signal": "شراء",
        "entry": 27700,
        "stop_loss": 27200,
        "take_profit": 28700
    }
