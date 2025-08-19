from typing import Dict, Any
import numpy as np


def bollinger_band_signal(candles: Dict[str, np.ndarray], period: int = 20, stddev: int = 2) -> Dict[str, Any]:
    close = candles["close"]
    if close.shape[0] < period + 1:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    window = close[-period:]
    mean = float(np.mean(window))
    sd = float(np.std(window))
    last_close = float(close[-1])
    last_upper = mean + stddev * sd
    last_lower = mean - stddev * sd
    if last_close <= last_lower:
        return {"direction": "BUY", "score": 1, "confidence": min((last_lower - last_close) / (abs(last_lower) + 1e-6), 1.0)}
    if last_close >= last_upper:
        return {"direction": "SELL", "score": 1, "confidence": min((last_close - last_upper) / (abs(last_upper) + 1e-6), 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

