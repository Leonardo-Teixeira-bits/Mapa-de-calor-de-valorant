"""Flattened Kill Event schema for enriched downstream analytics."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EnrichedKillEvent(BaseModel):
    """Normalized, enriched single elimination event with full match context."""
    model_config = ConfigDict(extra="ignore")

    match_id: str
    map_id: str
    map_name: str
    round_num: int
    round_duration_ms: int
    round_time_ms: int
    round_phase: str  # 'Early', 'Mid', 'Late'

    killer_puuid: Optional[str] = None
    killer_team: Optional[str] = None
    killer_raw_x: Optional[int] = None
    killer_raw_y: Optional[int] = None
    killer_norm_x: Optional[float] = None
    killer_norm_y: Optional[float] = None

    victim_puuid: Optional[str] = None
    victim_team: Optional[str] = None
    victim_raw_x: Optional[int] = None
    victim_raw_y: Optional[int] = None
    victim_norm_x: Optional[float] = None
    victim_norm_y: Optional[float] = None

    winning_team: Optional[str] = None
    killer_won_round: Optional[bool] = None
    victim_won_round: Optional[bool] = None

    damage_type: Optional[str] = None
    damage_item: Optional[str] = None
