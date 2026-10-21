"""Unit tests for multi-map coordinate projection and temporal segmentation."""

import pytest
from src.transformers.coordinates import CoordinateTransformer
from src.transformers.time_segmenter import classify_round_phase


def test_coordinate_transformer_tier1_maps():
    transformer = CoordinateTransformer()

    # Ascent
    ascent_id = "/Game/Maps/Ascent/Ascent"
    assert transformer.get_display_name(ascent_id) == "Ascent"
    x_norm, y_norm = transformer.to_normalized(world_x=0, world_y=0, map_id=ascent_id)
    assert 0.0 <= x_norm <= 1.0
    assert 0.0 <= y_norm <= 1.0

    # Lotus (Jam)
    lotus_id = "/Game/Maps/Jam/Jam"
    assert transformer.get_display_name(lotus_id) == "Lotus"
    x_norm, y_norm = transformer.to_normalized(world_x=4000, world_y=1000, map_id=lotus_id)
    assert 0.0 <= x_norm <= 1.0
    assert 0.0 <= y_norm <= 1.0

    # Haven (Triad)
    haven_id = "/Game/Maps/Triad/Triad"
    assert transformer.get_display_name(haven_id) == "Haven"
    x_norm, y_norm = transformer.to_normalized(world_x=1000, world_y=-6000, map_id=haven_id)
    assert 0.0 <= x_norm <= 1.0
    assert 0.0 <= y_norm <= 1.0


def test_coordinate_transformer_all_nine_maps():
    transformer = CoordinateTransformer()
    expected_maps = [
        ("/Game/Maps/Ascent/Ascent", "Ascent"),
        ("/Game/Maps/Jam/Jam", "Lotus"),
        ("/Game/Maps/Triad/Triad", "Haven"),
        ("/Game/Maps/Bonsai/Bonsai", "Split"),
        ("/Game/Maps/Juliett/Juliett", "Sunset"),
        ("/Game/Maps/Infinity/Infinity", "Abyss"),
        ("/Game/Maps/Plummet/Plummet", "Summit"),
        ("/Game/Maps/Foxtrot/Foxtrot", "Breeze"),
        ("/Game/Maps/Pitt/Pitt", "Pearl"),
    ]

    for map_id, expected_name in expected_maps:
        assert transformer.get_display_name(map_id) == expected_name
        meta = transformer.get_map_meta(map_id)
        assert meta is not None
        assert meta["xMultiplier"] != 0
        assert meta["yMultiplier"] != 0

        # Test normalization returns values within [0.0, 1.0]
        x_norm, y_norm = transformer.to_normalized(world_x=2000, world_y=-2000, map_id=map_id)
        assert 0.0 <= x_norm <= 1.0
        assert 0.0 <= y_norm <= 1.0


def test_coordinate_clipping_extreme_values():
    transformer = CoordinateTransformer()
    ascent_id = "/Game/Maps/Ascent/Ascent"

    # Extreme void / out of bounds coordinates
    x_norm, y_norm = transformer.to_normalized(world_x=-999999, world_y=-999999, map_id=ascent_id, clamp=True)
    assert x_norm == 0.0 or x_norm == 1.0
    assert y_norm == 0.0 or y_norm == 1.0


def test_time_segmenter():
    # 90s round (90000 ms) -> Early: < 30000 ms, Mid: 30000 - 60000 ms, Late: >= 60000 ms
    assert classify_round_phase(10000, 90000) == "Early"
    assert classify_round_phase(29999, 90000) == "Early"
    assert classify_round_phase(30000, 90000) == "Mid"
    assert classify_round_phase(59999, 90000) == "Mid"
    assert classify_round_phase(60000, 90000) == "Late"
    assert classify_round_phase(85000, 90000) == "Late"

    # Fallback to 100s standard round when duration is None or 0
    assert classify_round_phase(15000, None) == "Early"
    assert classify_round_phase(45000, 0) == "Mid"
    assert classify_round_phase(80000, -1) == "Late"
