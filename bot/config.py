"""Configuration loading for the paper trading bot."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)


@dataclass
class StrategyConfig:
    spread_cents: float = 4.0
    num_levels: int = 3
    size_per_level_usd: float = 5.0
    requote_interval_seconds: float = 30.0
    inventory_skew_factor: float = 1.0


@dataclass
class RiskConfig:
    max_position_usd: float = 20.0
    daily_loss_limit_usd: float = 8.0
    max_drawdown_usd: float = 15.0
    circuit_breaker_losses: int = 3
    circuit_breaker_pause_seconds: float = 300.0
    min_time_before_expiry_seconds: float = 120.0


@dataclass
class APIConfig:
    gamma_url: str = "https://gamma-api.polymarket.com"
    clob_url: str = "https://clob.polymarket.com"
    poll_interval_seconds: float = 5.0
    market_scan_interval_seconds: float = 60.0
    request_timeout_seconds: float = 10.0


@dataclass
class MarketFilterConfig:
    keywords: List[str] = field(
        default_factory=lambda: ["BTC", "Bitcoin", "bitcoin"]
    )
    duration_keywords: List[str] = field(
        default_factory=lambda: ["15 minute", "15-minute", "15min"]
    )
    fallback_to_any_crypto: bool = True


@dataclass
class Config:
    starting_capital_usd: float = 100.0
    seed_pct: float = 0.3
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    api: APIConfig = field(default_factory=APIConfig)
    market_filter: MarketFilterConfig = field(default_factory=MarketFilterConfig)

    @classmethod
    def load(cls, path: str | None = None) -> Config:
        """Load config from JSON file, falling back to defaults."""
        config = cls()
        file_path = path or DEFAULT_CONFIG_PATH
        if os.path.exists(file_path):
            with open(file_path) as f:
                data = json.load(f)
            config = cls._from_dict(data)
        return config

    @classmethod
    def _from_dict(cls, data: dict) -> Config:
        config = cls()
        if "starting_capital_usd" in data:
            config.starting_capital_usd = float(data["starting_capital_usd"])
        if "seed_pct" in data:
            config.seed_pct = float(data["seed_pct"])

        s = data.get("strategy", {})
        for key in (
            "spread_cents",
            "num_levels",
            "size_per_level_usd",
            "requote_interval_seconds",
            "inventory_skew_factor",
        ):
            if key in s:
                setattr(config.strategy, key, float(s[key]) if key != "num_levels" else int(s[key]))

        r = data.get("risk", {})
        for key in (
            "max_position_usd",
            "daily_loss_limit_usd",
            "max_drawdown_usd",
            "circuit_breaker_losses",
            "circuit_breaker_pause_seconds",
            "min_time_before_expiry_seconds",
        ):
            if key in r:
                val = r[key]
                setattr(config.risk, key, int(val) if key == "circuit_breaker_losses" else float(val))

        a = data.get("api", {})
        for key in (
            "gamma_url",
            "clob_url",
            "poll_interval_seconds",
            "market_scan_interval_seconds",
            "request_timeout_seconds",
        ):
            if key in a:
                setattr(config.api, key, a[key] if isinstance(a[key], str) else float(a[key]))

        mf = data.get("market_filter", {})
        if "keywords" in mf:
            config.market_filter.keywords = mf["keywords"]
        if "duration_keywords" in mf:
            config.market_filter.duration_keywords = mf["duration_keywords"]
        if "fallback_to_any_crypto" in mf:
            config.market_filter.fallback_to_any_crypto = bool(mf["fallback_to_any_crypto"])

        return config
