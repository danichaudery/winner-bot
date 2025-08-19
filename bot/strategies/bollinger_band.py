from typing import Dict, Any
import pandas as pd


def bollinger_band_signal(candles: pd.DataFrame, period: int = 20, stddev: int = 2) -> Dict[str, Any]:
    if len(candles) < period + 1:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    close = candles["close"]
    ma = close.rolling(window=period).mean()
    sd = close.rolling(window=period).std(ddof=0)
    upper = ma + stddev * sd
    lower = ma - stddev * sd
    last_close = float(close.iloc[-1])
    last_upper = float(upper.iloc[-1])
    last_lower = float(lower.iloc[-1])
    if last_close <= last_lower:
        return {"direction": "BUY", "score": 1, "confidence": min((last_lower - last_close) / (abs(last_lower) + 1e-6), 1.0)}
    if last_close >= last_upper:
        return {"direction": "SELL", "score": 1, "confidence": min((last_close - last_upper) / (abs(last_upper) + 1e-6), 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

