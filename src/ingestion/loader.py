"""Batch and streaming ingestion engine for VALORANT match JSONs with error boundaries."""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from src.models.match import Match
from src.models.kill import EnrichedKillEvent
from src.transformers.coordinates import CoordinateTransformer
from src.transformers.time_segmenter import classify_round_phase

logger = logging.getLogger(__name__)


class MatchLoader:
    """Ingests match JSONs with fault tolerance, extracting structured and normalized kill events."""

    def __init__(self, transformer: Optional[CoordinateTransformer] = None):
        self.transformer = transformer or CoordinateTransformer()

    def load_match_file(self, filepath: str | Path) -> Optional[Match]:
        """Loads and validates a single match JSON. Catches errors without crashing."""
        path = Path(filepath)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Match.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to load match JSON at {path}: {e}")
            return None

    def load_matches_batch(
        self,
        filepaths: List[str | Path]
    ) -> Tuple[List[Match], List[Dict[str, str]]]:
        """
        Loads multiple match files, returning successful matches and a log of corrupted files.
        """
        matches: List[Match] = []
        errors: List[Dict[str, str]] = []

        for fp in filepaths:
            match = self.load_match_file(fp)
            if match is not None:
                matches.append(match)
            else:
                errors.append({"file": str(fp), "error": "Invalid or corrupted JSON"})

        return matches, errors

    def extract_kill_events(self, match: Match) -> List[EnrichedKillEvent]:
        """
        Flattens all kill events within a match into EnrichedKillEvent records,
        correlating killer/victim positions, round outcomes, and normalized coordinates.
        """
        events: List[EnrichedKillEvent] = []
        map_id = match.matchInfo.mapId
        match_id = match.matchInfo.matchId
        map_name = self.transformer.get_display_name(map_id)

        # Player puuid -> teamId mapping
        player_teams = {p.puuid: p.teamId for p in match.players if p.puuid and p.teamId}

        for r in match.roundResults:
            round_num = r.roundNum
            duration_ms = r.roundResultTimeMillis or 100000
            winning_team = r.winningTeam

            for ps in r.playerStats:
                for k in ps.kills:
                    round_time_ms = k.timeSinceRoundStartMillis
                    phase = classify_round_phase(round_time_ms, duration_ms)

                    # Victim details
                    victim_puuid = k.victim
                    victim_team = player_teams.get(victim_puuid) if victim_puuid else None
                    v_raw_x, v_raw_y = None, None
                    v_norm_x, v_norm_y = None, None

                    if k.victimLocation:
                        v_raw_x = k.victimLocation.x
                        v_raw_y = k.victimLocation.y
                        v_norm_x, v_norm_y = self.transformer.to_normalized(v_raw_x, v_raw_y, map_id)

                    # Killer details
                    killer_puuid = k.killer
                    killer_team = player_teams.get(killer_puuid) if killer_puuid else None
                    k_raw_x, k_raw_y = None, None
                    k_norm_x, k_norm_y = None, None

                    if killer_puuid:
                        for pl in k.playerLocations:
                            if pl.puuid == killer_puuid and pl.location:
                                k_raw_x = pl.location.x
                                k_raw_y = pl.location.y
                                k_norm_x, k_norm_y = self.transformer.to_normalized(k_raw_x, k_raw_y, map_id)
                                break

                    # Round win correlation
                    killer_won = (killer_team == winning_team) if (killer_team and winning_team) else None
                    victim_won = (victim_team == winning_team) if (victim_team and winning_team) else None

                    # Finishing damage
                    damage_type = None
                    damage_item = None
                    if k.finishingDamage:
                        damage_type = k.finishingDamage.get("damageType")
                        damage_item = k.finishingDamage.get("damageItem")

                    event = EnrichedKillEvent(
                        match_id=match_id,
                        map_id=map_id,
                        map_name=map_name,
                        round_num=round_num,
                        round_duration_ms=duration_ms,
                        round_time_ms=round_time_ms,
                        round_phase=phase,
                        killer_puuid=killer_puuid,
                        killer_team=killer_team,
                        killer_raw_x=k_raw_x,
                        killer_raw_y=k_raw_y,
                        killer_norm_x=k_norm_x,
                        killer_norm_y=k_norm_y,
                        victim_puuid=victim_puuid,
                        victim_team=victim_team,
                        victim_raw_x=v_raw_x,
                        victim_raw_y=v_raw_y,
                        victim_norm_x=v_norm_x,
                        victim_norm_y=v_norm_y,
                        winning_team=winning_team,
                        killer_won_round=killer_won,
                        victim_won_round=victim_won,
                        damage_type=damage_type,
                        damage_item=damage_item,
                    )
                    events.append(event)

        return events
