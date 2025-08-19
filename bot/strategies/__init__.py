from .rsi_extreme import rsi_extreme_signal
from .macd_cross import macd_cross_signal
from .ema_crossover import ema_crossover_signal
from .bollinger_band import bollinger_band_signal
from .volume_spike import volume_spike_signal
from .pattern_recognition import pattern_recognition_signal
from .ai_stability_detector import ai_stability_signal

STRATEGY_FUNCTIONS = {
    "rsi_extreme": rsi_extreme_signal,
    "macd_cross": macd_cross_signal,
    "ema_crossover": ema_crossover_signal,
    "bollinger_band": bollinger_band_signal,
    "volume_spike": volume_spike_signal,
    "pattern_recognition": pattern_recognition_signal,
    "ai_stability_detector": ai_stability_signal,
}

