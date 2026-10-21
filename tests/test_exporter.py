"""Unit tests for Parquet and JSON exporters."""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.exporter.parquet_exporter import (
    export_events_parquet,
    export_density_cache,
    export_maps_summary,
)


def test_export_events_parquet(tmp_path: Path):
    df = pd.DataFrame({
        "match_id": ["m1", "m2"],
        "map_name": ["Ascent", "Ascent"],
        "killer_norm_x": [0.25, 0.75],
        "killer_norm_y": [0.30, 0.60],
        "killer_won_round": [True, False],
    })
    out_file = tmp_path / "events.parquet"
    res = export_events_parquet(df, out_file)
    assert res.exists()

    # Verify readback with pandas pyarrow
    loaded = pd.read_parquet(out_file)
    assert len(loaded) == 2
    assert list(loaded["map_name"]) == ["Ascent", "Ascent"]


def test_export_density_cache(tmp_path: Path):
    cache = {
        "Ascent": {
            "Total": {
                "kills_density": np.zeros((10, 10)),
                "deaths_density": np.ones((10, 10)),
                "bayesian_winrate": np.full((10, 10), 0.5),
            }
        }
    }
    out_file = tmp_path / "cache.json"
    res = export_density_cache(cache, out_file)
    assert res.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "Ascent" in data
    assert len(data["Ascent"]["Total"]["kills_density"]) == 10
    assert data["Ascent"]["Total"]["bayesian_winrate"][0][0] == 0.5


def test_export_maps_summary(tmp_path: Path):
    summary = {
        "Ascent": {
            "matches_count": 67,
            "rounds_count": 1340,
            "kills_count": 9400,
            "low_sample_warning": False,
            "tier": 1,
        },
        "Breeze": {
            "matches_count": 3,
            "rounds_count": 60,
            "kills_count": 420,
            "low_sample_warning": True,
            "tier": 3,
        }
    }
    out_file = tmp_path / "summary.json"
    res = export_maps_summary(summary, out_file)
    assert res.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["Ascent"]["low_sample_warning"] is False
    assert data["Breeze"]["low_sample_warning"] is True
