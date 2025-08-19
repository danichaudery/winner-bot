from typing import Dict, Any
import numpy as np


def pattern_recognition_signal(candles: Dict[str, np.ndarray]) -> Dict[str, Any]:
    # Simple bullish/bearish engulfing detection as placeholder
    open_ = candles["open"]
    close = candles["close"]
    if open_.shape[0] < 3 or close.shape[0] < 3:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    prev_open, prev_close = float(open_[-2]), float(close[-2])
    cur_open, cur_close = float(open_[-1]), float(close[-1])
    prev_bearish = prev_close < prev_open
    cur_bullish = cur_close > cur_open
    prev_bullish = prev_close > prev_open
    cur_bearish = cur_close < cur_open

    if prev_bearish and cur_bullish and (cur_close > prev_open) and (cur_open < prev_close):
        return {"direction": "BUY", "score": 1, "confidence": 0.6}
    if prev_bullish and cur_bearish and (cur_open > prev_close) and (cur_close < prev_open):
        return {"direction": "SELL", "score": 1, "confidence": 0.6}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

