"""Unit and integration tests for the ingestion loader."""

import json
import glob
from pathlib import Path
import pytest

from src.ingestion.loader import MatchLoader
from src.models.match import Match


def _get_raw_match_files():
    all_files = glob.glob("data/**/*.json", recursive=True)
    return [f for f in all_files if "processed" not in Path(f).parts]


def test_load_match_real_file():
    files = _get_raw_match_files()
    assert len(files) > 0

    loader = MatchLoader()
    match = loader.load_match_file(files[0])
    assert match is not None
    assert isinstance(match, Match)
    assert match.matchInfo.matchId is not None


def test_load_corrupted_file_error_boundary(tmp_path):
    bad_file = tmp_path / "corrupted.json"
    bad_file.write_text("{ incomplete json content ...", encoding="utf-8")

    loader = MatchLoader()
    result = loader.load_match_file(bad_file)
    assert result is None, "Corrupted file must return None without raising exception"

    matches, errors = loader.load_matches_batch([bad_file])
    assert len(matches) == 0
    assert len(errors) == 1
    assert errors[0]["file"] == str(bad_file)


def test_extract_kill_events():
    files = _get_raw_match_files()
    loader = MatchLoader()
    match = loader.load_match_file(files[0])
    assert match is not None

    events = loader.extract_kill_events(match)
    assert len(events) > 0

    e0 = events[0]
    assert e0.match_id == match.matchInfo.matchId
    assert e0.map_id == match.matchInfo.mapId
    assert e0.map_name is not None
    assert e0.round_phase in ("Early", "Mid", "Late")
    # Check that victim norm is populated if victimLocation existed
    if e0.victim_raw_x is not None:
        assert 0.0 <= e0.victim_norm_x <= 1.0
        assert 0.0 <= e0.victim_norm_y <= 1.0
    # Check that killer_won_round is a bool or None
    assert e0.killer_won_round in (True, False, None)
