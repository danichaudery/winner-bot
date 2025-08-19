from typing import Dict, Any
import numpy as np


def ema(series: np.ndarray, span: int) -> np.ndarray:
    alpha = 2 / (span + 1)
    out = np.empty_like(series, dtype=float)
    out[0] = series[0]
    for i in range(1, series.shape[0]):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out


def ema_crossover_signal(candles: Dict[str, np.ndarray], fast: int = 9, slow: int = 21) -> Dict[str, Any]:
    close = candles["close"]
    if close.shape[0] < slow + 2:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    e_fast = ema(close, fast)
    e_slow = ema(close, slow)
    last_fast, last_slow = float(e_fast[-1]), float(e_slow[-1])
    prev_fast, prev_slow = float(e_fast[-2]), float(e_slow[-2])
    if prev_fast <= prev_slow and last_fast > last_slow:
        return {"direction": "BUY", "score": 1, "confidence": min(abs(last_fast - last_slow) / (abs(prev_slow) + 1e-6), 1.0)}
    if prev_fast >= prev_slow and last_fast < last_slow:
        return {"direction": "SELL", "score": 1, "confidence": min(abs(last_fast - last_slow) / (abs(prev_slow) + 1e-6), 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

