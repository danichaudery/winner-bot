from __future__ import annotations

import asyncio
import json
from typing import Dict, Any, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import numpy as np

from ..strategies import STRATEGY_FUNCTIONS
from .market import get_candles
from .db import SessionLocal, SignalLog


TIMEFRAME_SECONDS = {"1m": 60, "5m": 300, "15m": 900}


class SignalsService:
    def __init__(self) -> None:
        with open("bot/config.json", "r") as f:
            self.config = json.load(f)
        self.scheduler: AsyncIOScheduler | None = None
        self.latest: Dict[str, Dict[str, Any]] = {}

    async def start_background_scheduler(self) -> None:
        if self.scheduler is not None:
            return
        self.scheduler = AsyncIOScheduler()
        for timeframe in self.config.get("timeframes", ["1m", "5m", "15m"]):
            seconds = TIMEFRAME_SECONDS.get(timeframe, 60)
            self.scheduler.add_job(self._run_all_pairs, IntervalTrigger(seconds=seconds), args=[timeframe], id=f"run-{timeframe}")
        self.scheduler.start()

    async def shutdown_background_scheduler(self) -> None:
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None

    async def _run_all_pairs(self, timeframe: str) -> None:
        pairs: List[str] = self.config.get("pairs", [])
        results: Dict[str, Any] = {}
        for pair in pairs:
            candles = get_candles(pair, timeframe, limit=200)
            signals = self._evaluate_strategies(candles)
            direction, score = self._combine_signals(signals)
            results[pair] = {"direction": direction, "score": score, "details": signals}
            # Persist log
            with SessionLocal() as session:
                session.add(SignalLog(pair=pair, timeframe=timeframe, direction=direction, score=score))
                session.commit()
        self.latest[timeframe] = results

    def _evaluate_strategies(self, candles: Dict[str, np.ndarray]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        strategies_cfg = self.config.get("strategies", {})
        for name, fn in STRATEGY_FUNCTIONS.items():
            cfg = strategies_cfg.get(name, {"enabled": True})
            if not cfg.get("enabled", True):
                continue
            try:
                result = fn(candles, **{k: v for k, v in cfg.items() if k != "enabled"})
            except TypeError:
                result = fn(candles)
            out[name] = result
        return out

    def _combine_signals(self, signals: Dict[str, Any]) -> tuple[str, int]:
        votes_buy = sum(1 for s in signals.values() if s.get("direction") == "BUY")
        votes_sell = sum(1 for s in signals.values() if s.get("direction") == "SELL")
        min_confirm = int(self.config.get("high_confirmation_min", 2))
        if votes_buy >= min_confirm and votes_buy > votes_sell:
            return ("BUY", votes_buy)
        if votes_sell >= min_confirm and votes_sell > votes_buy:
            return ("SELL", votes_sell)
        return ("HOLD", 0)

    async def get_latest_signals(self, timeframe: str) -> Dict[str, Any]:
        return self.latest.get(timeframe, {})

    async def get_history(self, pair: str | None, timeframe: str | None, limit: int) -> List[Dict[str, Any]]:
        from .db import SessionLocal, SignalLog
        with SessionLocal() as session:
            q = session.query(SignalLog)
            if pair:
                q = q.filter(SignalLog.pair == pair)
            if timeframe:
                q = q.filter(SignalLog.timeframe == timeframe)
            rows = q.order_by(SignalLog.created_at.desc()).limit(limit).all()
            return [
                {
                    "pair": r.pair,
                    "timeframe": r.timeframe,
                    "direction": r.direction,
                    "score": r.score,
                    "created_at": r.created_at.isoformat()
                } for r in rows
            ]

