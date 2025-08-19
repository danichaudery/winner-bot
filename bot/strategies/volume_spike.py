from typing import Dict, Any
import numpy as np


def volume_spike_signal(candles: Dict[str, np.ndarray], multiplier: float = 2.0) -> Dict[str, Any]:
    vol = candles.get("volume")
    if vol is None or vol.shape[0] < 30:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    last = float(vol[-1])
    last_avg = float(np.mean(vol[-20:]))
    spike = last_avg > 0 and (last / last_avg) >= multiplier
    if spike:
        # Direction unknown based on volume alone
        return {"direction": "HOLD", "score": 1, "confidence": min((last / (last_avg + 1e-6) - multiplier) / multiplier, 1.0)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

