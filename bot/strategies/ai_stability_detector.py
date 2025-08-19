from typing import Dict, Any
import pandas as pd


def ai_stability_signal(candles: pd.DataFrame) -> Dict[str, Any]:
    # Placeholder heuristic: lower recent volatility -> HOLD, spike -> signal with low confidence
    if len(candles) < 30:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    close = candles["close"].astype(float)
    returns = close.pct_change().dropna()
    vol = returns.rolling(window=20).std().iloc[-1]
    if vol is None:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    if vol > 0.02:
        # High volatility, attempt mean-reversion bias
        direction = "SELL" if close.iloc[-1] > close.rolling(window=10).mean().iloc[-1] else "BUY"
        return {"direction": direction, "score": 1, "confidence": min((vol - 0.02) / 0.05, 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

