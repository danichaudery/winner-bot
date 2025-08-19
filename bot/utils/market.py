from __future__ import annotations

from typing import List, Dict
import random
import numpy as np


def get_candles(pair: str, timeframe: str, limit: int = 200) -> Dict[str, np.ndarray]:
    # Placeholder: generate synthetic candle data
    random.seed(f"{pair}-{timeframe}")
    prices = [100.0]
    for _ in range(limit - 1):
        prices.append(prices[-1] * (1 + random.uniform(-0.005, 0.005)))
    prices = np.array(prices, dtype=float)
    opens = np.concatenate(([prices[0]], prices[:-1]))
    highs = prices * (1 + np.random.uniform(0, 0.002, size=prices.shape))
    lows = prices * (1 - np.random.uniform(0, 0.002, size=prices.shape))
    volumes = np.random.uniform(100, 1000, size=prices.shape).astype(float)
    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": prices,
        "volume": volumes,
    }

