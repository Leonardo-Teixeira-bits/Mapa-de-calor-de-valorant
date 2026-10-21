"""Tracer verification test: End-to-end ingestion and projection for a real Ascent match."""

import json
import glob
from pathlib import Path
import pytest

from src.models.match import Match
from src.transformers.coordinates import CoordinateTransformer
from src.transformers.time_segmenter import classify_round_phase


def test_tracer_ascent_end_to_end():
    # 1. Locate an actual Ascent match from data/
    ascent_files = glob.glob("data/**/*ascent.json", recursive=True)
    assert len(ascent_files) > 0, "At least one Ascent JSON file must exist in data/"

    sample_file = ascent_files[0]
    with open(sample_file, "r", encoding="utf-8") as f:
        raw_json = json.load(f)

    # 2. Pydantic validation
    match = Match.model_validate(raw_json)
    assert match.matchInfo.mapId == "/Game/Maps/Ascent/Ascent"
    assert len(match.roundResults) > 0

    # 3. Coordinate transformer
    transformer = CoordinateTransformer()
    assert transformer.get_display_name(match.matchInfo.mapId) == "Ascent"

    # 4. Extract kills and verify projection and phase classification
    extracted_events = []
    for r in match.roundResults:
        round_duration = r.roundResultTimeMillis or 100000
        for ps in r.playerStats:
            for k in ps.kills:
                # Victim location
                v_x, v_y = None, None
                if k.victimLocation:
                    v_x, v_y = transformer.to_normalized(
                        k.victimLocation.x,
                        k.victimLocation.y,
                        match.matchInfo.mapId
                    )
                    assert 0.0 <= v_x <= 1.0
                    assert 0.0 <= v_y <= 1.0

                # Killer location (search in playerLocations for puuid == killer)
                k_x, k_y = None, None
                if k.killer:
                    for pl in k.playerLocations:
                        if pl.puuid == k.killer and pl.location:
                            k_x, k_y = transformer.to_normalized(
                                pl.location.x,
                                pl.location.y,
                                match.matchInfo.mapId
                            )
                            assert 0.0 <= k_x <= 1.0
                            assert 0.0 <= k_y <= 1.0
                            break

                phase = classify_round_phase(k.timeSinceRoundStartMillis, round_duration)
                assert phase in ("Early", "Mid", "Late")

                extracted_events.append({
                    "victim_norm": (v_x, v_y),
                    "killer_norm": (k_x, k_y),
                    "phase": phase
                })

    assert len(extracted_events) > 0
    phases = {e["phase"] for e in extracted_events}
    assert len(phases) >= 2, f"Expected multiple round phases, got {phases}"
