"""Unit and integration tests for MatchProcessingPipeline."""

import json
from pathlib import Path
import pytest
import pandas as pd

from src.pipeline import MatchProcessingPipeline, TIER_1_MAPS


def test_tier_determination():
    pipeline = MatchProcessingPipeline()
    assert pipeline.determine_tier("Ascent", 67) == 1
    assert pipeline.determine_tier("Lotus", 1) == 1  # Always Tier 1
    assert pipeline.determine_tier("Haven", 20) == 1  # Always Tier 1
    assert pipeline.determine_tier("Split", 36) == 2  # N >= 10
    assert pipeline.determine_tier("Breeze", 5) == 3  # N < 10
    assert pipeline.determine_tier("Pearl", 2) == 3  # N < 10


def test_file_map_identification(tmp_path: Path):
    pipeline = MatchProcessingPipeline()
    p1 = tmp_path / "match_001_ascent.json"
    p2 = tmp_path / "match_002_haven.json"
    p3 = tmp_path / "match_003_pearl.json"

    assert pipeline.identify_file_map(p1) == "Ascent"
    assert pipeline.identify_file_map(p2) == "Haven"
    assert pipeline.identify_file_map(p3) == "Pearl"


def test_pipeline_run_on_subset(tmp_path: Path):
    # Locate one real Ascent file from data/
    real_files = list(Path("data").rglob("*_ascent.json"))
    if not real_files:
        pytest.skip("No real Ascent files found in data/")

    # Setup dummy data folder with 1 real Ascent file
    data_dir = tmp_path / "input_data"
    data_dir.mkdir()
    sample_source = real_files[0]
    sample_dest = data_dir / "sample_ascent.json"
    sample_dest.write_text(sample_source.read_text(encoding="utf-8"), encoding="utf-8")

    out_dir = tmp_path / "output_data"
    pipeline = MatchProcessingPipeline(
        data_dir=data_dir,
        output_dir=out_dir,
        grid_size=20  # smaller grid for fast unit test
    )

    result = pipeline.run()

    assert result["total_files"] == 1
    assert result["total_events"] > 0
    assert "Ascent" in result["maps"]
    ascent_info = result["maps"]["Ascent"]
    assert ascent_info["tier"] == 1
    assert ascent_info["matches_count"] == 1

    # Check exported artifacts
    parquet_path = Path(result["parquet_path"])
    cache_path = Path(result["cache_path"])
    summary_path = Path(result["summary_path"])

    assert parquet_path.exists()
    assert cache_path.exists()
    assert summary_path.exists()

    df = pd.read_parquet(parquet_path)
    assert len(df) == result["total_events"]

    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
    assert "Ascent" in summary_data
