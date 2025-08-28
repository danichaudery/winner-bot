from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal, User


USDT_TRON_CONTRACT = os.getenv("USDT_TRON_CONTRACT", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
RECIPIENT = os.getenv("USER_WALLET_ADDRESS", "")
TRON_API_KEY = os.getenv("TRON_API_KEY", "")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    txid = Column(String, unique=True, nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


async def fetch_tron_transfers(address: str) -> list[dict[str, Any]]:
    if not TRON_API_KEY or not address:
        return []
    headers = {"TRON-PRO-API-KEY": TRON_API_KEY}
    # Using TronGrid TRC20 transaction API
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?only_to=true&limit=50&contract_address={USDT_TRON_CONTRACT}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=headers)
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("data", [])


async def process_incoming_payments() -> None:
    if not RECIPIENT:
        return
    transfers = await fetch_tron_transfers(RECIPIENT)
    if not transfers:
        return
    with SessionLocal() as session:
        for t in transfers:
            txid = t.get("transaction_id") or t.get("transaction_id_str") or t.get("transaction_id")
            if not txid:
                continue
            exists = session.query(Payment).filter(Payment.txid == txid).first()
            if exists:
                continue
            to_address = t.get("to")
            from_address = t.get("from")
            raw_value = t.get("value") or t.get("amount") or "0"
            try:
                amount = float(raw_value) / (10 ** 6)  # USDT on Tron has 6 decimals
            except Exception:
                amount = 0.0
            pay = Payment(txid=txid, from_address=from_address, to_address=to_address, amount=amount, confirmed=True)
            session.add(pay)
            # Auto-unblock: extend subscription 30 days for monthly, or set far future for lifetime
            # Heuristic: amount >= 80 -> lifetime, elif >= 25 -> monthly
            plan = "lifetime" if amount >= 80 else ("monthly" if amount >= 25 else None)
            if plan:
                # Assign to earliest trial user as placeholder. In production, include memo or unique amount tags.
                user = session.query(User).order_by(User.id.asc()).first()
                if user:
                    if plan == "lifetime":
                        user.subscription_expires_at = datetime.utcnow() + timedelta(days=3650)
                    else:
                        base = user.subscription_expires_at or datetime.utcnow()
                        user.subscription_expires_at = base + timedelta(days=30)
            session.commit()

