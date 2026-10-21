"""Integration smoke tests for the Streamlit dashboard components and data caches."""

import json
from pathlib import Path
import pandas as pd
import pytest

from app import load_maps_summary, load_density_cache, load_events_df
from src.visualization.map_renderer import render_map_figure


def test_app_data_artifacts_exist():
    summary = load_maps_summary()
    cache = load_density_cache()
    events = load_events_df()

    assert len(summary) > 0, "maps_summary must not be empty"
    assert len(cache) > 0, "density_winrate_cache must not be empty"
    assert len(events) > 0, "events DataFrame must not be empty"

    # Verify Tier 1 maps present
    assert "Ascent" in summary
    assert "Lotus" in summary
    assert "Haven" in summary

    # Verify columns in events
    expected_cols = [
        "match_id", "map_name", "round_num", "round_phase",
        "killer_norm_x", "killer_norm_y", "victim_norm_x", "victim_norm_y"
    ]
    for col in expected_cols:
        assert col in events.columns


def test_app_render_all_modes_for_tier1_maps():
    cache = load_density_cache()
    tier1_maps = ["Ascent", "Lotus", "Haven"]
    modes = ["kills", "deaths", "winrate"]
    phases = ["Total", "Early", "Mid", "Late"]

    for m in tier1_maps:
        for phase in phases:
            for mode in modes:
                matrix = cache[m][phase][
                    "kills_density" if mode == "kills" else
                    "deaths_density" if mode == "deaths" else
                    "bayesian_winrate"
                ]
                fig = render_map_figure(matrix=matrix, mode=mode, map_name=m)
                assert fig is not None
                assert len(fig.data) >= 1
