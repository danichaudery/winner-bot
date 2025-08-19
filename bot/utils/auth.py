import os
import random
import string
from datetime import datetime, timedelta
from typing import Dict


_otp_store: Dict[str, Dict[str, str]] = {}


def _generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def send_login_otp(email: str) -> None:
    code = _generate_otp()
    _otp_store[email] = {"code": code, "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()}
    # In production, send via email provider
    print(f"OTP for {email}: {code}")


def verify_login_otp(email: str, code: str) -> bool:
    data = _otp_store.get(email)
    if not data:
        return False
    if data["code"] != code:
        return False
    if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
        return False
    return True

