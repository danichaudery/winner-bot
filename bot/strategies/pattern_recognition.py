from typing import Dict, Any
import pandas as pd


def pattern_recognition_signal(candles: pd.DataFrame) -> Dict[str, Any]:
    # Simple bullish/bearish engulfing detection as placeholder
    if len(candles) < 3:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    prev = candles.iloc[-2]
    cur = candles.iloc[-1]
    prev_bearish = prev["close"] < prev["open"]
    cur_bullish = cur["close"] > cur["open"]
    prev_bullish = prev["close"] > prev["open"]
    cur_bearish = cur["close"] < cur["open"]

    if prev_bearish and cur_bullish and cur["close"] > prev["open"] and cur["open"] < prev["close"]:
        return {"direction": "BUY", "score": 1, "confidence": 0.6}
    if prev_bullish and cur_bearish and cur["open"] > prev["close"] and cur["close"] < prev["open"]:
        return {"direction": "SELL", "score": 1, "confidence": 0.6}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

