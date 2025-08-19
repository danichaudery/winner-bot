from __future__ import annotations

from typing import List, Dict
import random
import pandas as pd


def get_candles(pair: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
    # Placeholder: generate synthetic candle data
    random.seed(f"{pair}-{timeframe}")
    prices = [100.0]
    for _ in range(limit - 1):
        prices.append(prices[-1] * (1 + random.uniform(-0.005, 0.005)))
    df = pd.DataFrame({
        "open": pd.Series(prices).shift(1).fillna(method="bfill"),
        "high": [p * (1 + random.uniform(0, 0.002)) for p in prices],
        "low": [p * (1 - random.uniform(0, 0.002)) for p in prices],
        "close": prices,
        "volume": [random.uniform(100, 1000) for _ in range(len(prices))],
    })
    return df

