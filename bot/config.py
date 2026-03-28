"""Configuration loader for the Poly-Trade bot."""
import json
import os
from dataclasses import dataclass, field
from typing import List

DEFAULT_CONFIG: dict = {
    "token_ids": [],
    "seed_pct": 0.3,
    "spread_cents": 4,
    "size_per_level_usd": 5.0,
    "skew_factor": 1.0,
    "max_position_usd": 20.0,
    "daily_loss_limit": 8.0,
    "max_drawdown": 15.0,
    "duration_keywords": ["1-hour", "1 hour", "hourly"],
    "clob_api_url": "https://clob.polymarket.com",
    "ws_url": "wss://ws-subscriptions-clob.polymarket.com/ws/market",
}


@dataclass
class Config:
    token_ids: List[str] = field(default_factory=list)
    seed_pct: float = 0.3
    spread_cents: int = 4
    size_per_level_usd: float = 5.0
    skew_factor: float = 1.0
    max_position_usd: float = 20.0
    daily_loss_limit: float = 8.0
    max_drawdown: float = 15.0
    duration_keywords: List[str] = field(
        default_factory=lambda: ["1-hour", "1 hour", "hourly"]
    )
    clob_api_url: str = "https://clob.polymarket.com"
    ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


def load_config(path: str = "config.json") -> Config:
    """Load config from *path*, falling back to defaults for missing keys."""
    data = {**DEFAULT_CONFIG}
    if os.path.exists(path):
        with open(path) as fh:
            data.update(json.load(fh))
    fields = Config.__dataclass_fields__
    return Config(**{k: data[k] for k in fields if k in data})
