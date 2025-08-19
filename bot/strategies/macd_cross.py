from typing import Dict, Any
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def macd_cross_signal(candles: pd.DataFrame) -> Dict[str, Any]:
    if len(candles) < 35:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    close = candles["close"]
    macd = ema(close, 12) - ema(close, 26)
    signal = ema(macd, 9)
    hist = macd - signal
    last = float(hist.iloc[-1])
    prev = float(hist.iloc[-2])
    if prev <= 0 and last > 0:
        return {"direction": "BUY", "score": 1, "confidence": min(abs(last) / (abs(prev) + 1e-6), 1.0)}
    if prev >= 0 and last < 0:
        return {"direction": "SELL", "score": 1, "confidence": min(abs(last) / (abs(prev) + 1e-6), 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

