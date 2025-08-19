from typing import Dict, Any
import pandas as pd


def volume_spike_signal(candles: pd.DataFrame, multiplier: float = 2.0) -> Dict[str, Any]:
    if "volume" not in candles.columns or len(candles) < 30:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    vol = candles["volume"]
    avg = vol.rolling(window=20).mean()
    last, last_avg = float(vol.iloc[-1]), float(avg.iloc[-1])
    spike = last_avg > 0 and (last / last_avg) >= multiplier
    if spike:
        # Direction unknown based on volume alone
        return {"direction": "HOLD", "score": 1, "confidence": min((last / (last_avg + 1e-6) - multiplier) / multiplier, 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

