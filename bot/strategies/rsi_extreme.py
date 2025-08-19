from typing import List, Dict, Any
import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss.replace(0, 1e-9))
    rsi = 100 - (100 / (1 + rs))
    return rsi


def rsi_extreme_signal(candles: pd.DataFrame, oversold: int = 30, overbought: int = 70) -> Dict[str, Any]:
    if len(candles) < 20:
        return {"direction": "HOLD", "score": 0, "confidence": 0.0}
    rsi = compute_rsi(candles["close"], period=14)
    last_rsi = float(rsi.iloc[-1])
    if last_rsi <= oversold:
        return {"direction": "BUY", "score": 1, "confidence": (oversold - last_rsi) / oversold}
    if last_rsi >= overbought:
        return {"direction": "SELL", "score": 1, "confidence": (last_rsi - overbought) / (100 - overbought)}
    return {"direction": "HOLD", "score": 0, "confidence": 0.0}

