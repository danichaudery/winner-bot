import os
from fastapi import Depends, HTTPException, status


def verify_api_key_dependency(x_api_key: str | None = None):
    expected = os.getenv("API_KEY", "")
    if not expected:
        return ""
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return x_api_key

