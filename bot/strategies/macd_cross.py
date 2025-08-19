from typing import Dict, Any
import numpy as np


def ema(series: np.ndarray, span: int) -> np.ndarray:
    alpha = 2 / (span + 1)
    out = np.empty_like(series, dtype=float)
    out[0] = series[0]
    for i in range(1, series.shape[0]):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out


def macd_cross_signal(candles: Dict[str, np.ndarray]) -> Dict[str, Any]:
    close = candles["close"]
    if close.shape[0] < 35:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    macd = ema(close, 12) - ema(close, 26)
    signal = ema(macd, 9)
    hist = macd - signal
    last = float(hist[-1])
    prev = float(hist[-2])
    if prev <= 0 and last > 0:
        return {"direction": "BUY", "score": 1, "confidence": min(abs(last) / (abs(prev) + 1e-6), 1.0)}
    if prev >= 0 and last < 0:
        return {"direction": "SELL", "score": 1, "confidence": min(abs(last) / (abs(prev) + 1e-6), 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

