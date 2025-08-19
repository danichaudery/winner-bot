from typing import Dict, Any
import numpy as np


def compute_rsi(series: np.ndarray, period: int = 14) -> np.ndarray:
    delta = np.diff(series, prepend=series[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    gain_ma = np.convolve(gain, np.ones(period)/period, mode='same')
    loss_ma = np.convolve(loss, np.ones(period)/period, mode='same')
    rs = gain_ma / (loss_ma + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def rsi_extreme_signal(candles: Dict[str, np.ndarray], oversold: int = 30, overbought: int = 70) -> Dict[str, Any]:
    close = candles["close"]
    if close.shape[0] < 20:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    rsi = compute_rsi(close, period=14)
    last_rsi = float(rsi[-1])
    if last_rsi <= oversold:
        return {"direction": "BUY", "score": 1, "confidence": (oversold - last_rsi) / oversold}
    if last_rsi >= overbought:
        return {"direction": "SELL", "score": 1, "confidence": (last_rsi - overbought) / (100 - overbought)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

