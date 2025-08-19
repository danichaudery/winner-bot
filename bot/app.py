from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

# Local imports
from .utils.security import verify_api_key_dependency
from .utils.db import init_db, get_user_status, get_admin_metrics
from .utils.signals import SignalsService
from .utils.content import get_contact, get_terms, get_privacy
from .utils.auth import send_login_otp, verify_login_otp
from .utils.payments import process_incoming_payments
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger


load_dotenv()

app = FastAPI(title="Winner Bot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class SignalsLatestResponse(BaseModel):
    timeframe: str
    pairs: Dict[str, Dict[str, Any]]


class SignalsHistoryQuery(BaseModel):
    pair: Optional[str] = None
    timeframe: Optional[str] = None
    limit: int = 100


class CandlesResponse(BaseModel):
    pair: str
    timeframe: str
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[float]


signals_service = SignalsService()
payments_scheduler: AsyncIOScheduler | None = None


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    await signals_service.start_background_scheduler()
    # Kick off first payment check (non-blocking)
    try:
        await process_incoming_payments()
    except Exception:
        pass
    # Schedule recurring TRC20 payment polling
    global payments_scheduler
    if payments_scheduler is None:
        payments_scheduler = AsyncIOScheduler()
        payments_scheduler.add_job(process_incoming_payments, IntervalTrigger(seconds=60))
        payments_scheduler.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await signals_service.shutdown_background_scheduler()
    global payments_scheduler
    if payments_scheduler:
        payments_scheduler.shutdown(wait=False)
        payments_scheduler = None


@app.get("/signals/latest", response_model=SignalsLatestResponse)
async def signals_latest(api_key: str = Depends(verify_api_key_dependency), timeframe: str = "1m"):
    data = await signals_service.get_latest_signals(timeframe=timeframe)
    return {"timeframe": timeframe, "pairs": data}


@app.get("/signals/history")
async def signals_history(pair: Optional[str] = None, timeframe: Optional[str] = None, limit: int = 100, api_key: str = Depends(verify_api_key_dependency)):
    return await signals_service.get_history(pair=pair, timeframe=timeframe, limit=limit)


@app.get("/user/status")
async def user_status(email: str, api_key: str = Depends(verify_api_key_dependency)):
    return get_user_status(email)


@app.get("/admin/metrics")
async def admin_metrics(api_key: str = Depends(verify_api_key_dependency)):
    return get_admin_metrics()


@app.get("/contact")
async def contact():
    return get_contact()


@app.get("/terms")
async def terms():
    return get_terms()


@app.get("/privacy")
async def privacy():
    return get_privacy()


@app.post("/auth/request-otp")
async def request_otp(email: str):
    send_login_otp(email)
    return {"ok": True}


@app.post("/auth/verify-otp")
async def verify_otp(email: str, code: str):
    ok = verify_login_otp(email, code)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"ok": True}


@app.get("/candles", response_model=CandlesResponse)
async def candles(pair: str, timeframe: str = "1m", limit: int = 200, api_key: str = Depends(verify_api_key_dependency)):
    data = await signals_service.get_candles(pair=pair, timeframe=timeframe, limit=limit)
    return {
        "pair": pair,
        "timeframe": timeframe,
        "open": data.get("open", []).tolist() if hasattr(data.get("open"), "tolist") else data.get("open", []),
        "high": data.get("high", []).tolist() if hasattr(data.get("high"), "tolist") else data.get("high", []),
        "low": data.get("low", []).tolist() if hasattr(data.get("low"), "tolist") else data.get("low", []),
        "close": data.get("close", []).tolist() if hasattr(data.get("close"), "tolist") else data.get("close", []),
        "volume": data.get("volume", []).tolist() if hasattr(data.get("volume"), "tolist") else data.get("volume", []),
    }

