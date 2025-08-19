from typing import Dict, Any
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def ema_crossover_signal(candles: pd.DataFrame, fast: int = 9, slow: int = 21) -> Dict[str, Any]:
    if len(candles) < slow + 2:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    close = candles["close"]
    e_fast = ema(close, fast)
    e_slow = ema(close, slow)
    last_fast, last_slow = float(e_fast.iloc[-1]), float(e_slow.iloc[-1])
    prev_fast, prev_slow = float(e_fast.iloc[-2]), float(e_slow.iloc[-2])
    if prev_fast <= prev_slow and last_fast > last_slow:
        return {"direction": "BUY", "score": 1, "confidence": min(abs(last_fast - last_slow) / (abs(prev_slow) + 1e-6), 1.0)}
    if prev_fast >= prev_slow and last_fast < last_slow:
        return {"direction": "SELL", "score": 1, "confidence": min(abs(last_fast - last_slow) / (abs(prev_slow) + 1e-6), 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

