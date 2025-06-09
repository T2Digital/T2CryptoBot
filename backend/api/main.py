from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uuid
import time
import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator

app = FastAPI()

# بيانات المستخدمين
users_db = {
    "admin": {"username": "admin", "password": "123456", "role": "admin"},
    "test": {"username": "test", "password": "1234", "role": "user"}
}

# تخزين الجلسات
active_sessions = {}

# موديلات
class LoginRequest(BaseModel):
    username: str
    password: str

class SignalRequest(BaseModel):
    symbol: str
    timeframe: str
    risk_reward: float

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
    raise HTTPException(status_code=401, detail="بيانات الدخول غير صحيحة")

@app.get("/symbols")
def get_symbols():
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    pairs = [symbol for symbol in markets if "/USDT" in symbol and not "." in symbol]
    return {"symbols": sorted(pairs)}

@app.post("/generate-signal")
def generate_signal(data: SignalRequest, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "").strip()
    if token not in active_sessions:
        raise HTTPException(status_code=403, detail="انتهت الجلسة أو غير مصرح")

    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(data.symbol, timeframe=data.timeframe, limit=200)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # المؤشرات الفنية
    df['rsi'] = RSIIndicator(df['close']).rsi()
    macd = MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['ema_20'] = EMAIndicator(df['close'], 20).ema_indicator()
    df['ema_50'] = EMAIndicator(df['close'], 50).ema_indicator()

    last = df.iloc[-1]
    signal = "حيادي"
    confidence = 50

    if last['rsi'] < 30 and last['macd'] > last['macd_signal'] and last['ema_20'] > last['ema_50']:
        signal = "شراء قوي"
        confidence = 90
    elif last['rsi'] > 70 and last['macd'] < last['macd_signal'] and last['ema_20'] < last['ema_50']:
        signal = "بيع قوي"
        confidence = 90

    return {
        "signal": signal,
        "confidence": confidence,
        "rsi": float(last['rsi']),
        "macd": float(last['macd']),
        "macd_signal": float(last['macd_signal']),
        "ema_20": float(last['ema_20']),
        "ema_50": float(last['ema_50']),
        "last_price": float(last['close'])
    }

@app.get("/subscription")
def get_subscription(token: str):
    username = active_sessions.get(token, {}).get("username")
    if username == "admin":
        return {"plan": "VIP", "expires": "2099-12-31"}
    elif username == "test":
        return {"plan": "Free", "expires": "2025-01-01"}
    return {"plan": "Free", "expires": "N/A"}
