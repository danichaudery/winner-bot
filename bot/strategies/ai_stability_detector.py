from typing import Dict, Any
import numpy as np


def ai_stability_signal(candles: Dict[str, np.ndarray]) -> Dict[str, Any]:
    # Placeholder heuristic: lower recent volatility -> HOLD, spike -> signal with low confidence
    close = candles["close"].astype(float)
    if close.shape[0] < 30:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    returns = np.diff(close) / (close[:-1] + 1e-9)
    if returns.shape[0] < 20:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    vol = float(np.std(returns[-20:]))
    ma10 = float(np.mean(close[-10:]))
    if vol > 0.02:
        direction = "SELL" if close[-1] > ma10 else "BUY"
        return {"direction": direction, "score": 1, "confidence": min((vol - 0.02) / 0.05, 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

