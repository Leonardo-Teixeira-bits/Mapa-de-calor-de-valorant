"""Unit tests for Plotly geospatial map renderer."""

import numpy as np
import pandas as pd
import pytest
import plotly.graph_objects as go

from src.visualization.map_renderer import (
    get_minimap_base64_uri,
    render_map_figure,
)


def test_get_minimap_base64_uri():
    # Ascent minimap was downloaded to assets/maps/ascent.png
    uri = get_minimap_base64_uri("Ascent")
    assert uri is not None
    assert uri.startswith("data:image/png;base64,")

    # Non-existent map returns None
    missing = get_minimap_base64_uri("NonExistentMap999")
    assert missing is None


def test_render_map_figure_kills_mode():
    matrix = np.zeros((50, 50))
    matrix[25, 25] = 10.0  # Center kill hotspot

    fig = render_map_figure(matrix, mode="kills", map_name="Ascent", grid_size=50)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "heatmap"
    assert fig.layout.yaxis.scaleanchor == "x"
    assert fig.layout.yaxis.autorange == "reversed"
    assert len(fig.layout.images) == 1
    assert fig.layout.images[0].source.startswith("data:image/png;base64,")


def test_render_map_figure_winrate_mode():
    matrix = np.full((50, 50), 0.5)
    matrix[10, 10] = 0.65  # Advantageous point

    fig = render_map_figure(matrix, mode="winrate", map_name="Lotus", grid_size=50)
    assert isinstance(fig, go.Figure)
    assert fig.data[0].type == "heatmap"
    assert fig.data[0].zmin == 0.35
    assert fig.data[0].zmax == 0.65


def test_render_map_figure_with_scatter_points():
    matrix = np.zeros((30, 30))
    df_pts = pd.DataFrame({
        "killer_norm_x": [0.2, 0.8],
        "killer_norm_y": [0.3, 0.7],
        "round_num": [1, 2],
        "round_phase": ["Early", "Late"],
        "killer_won_round": [True, False]
    })
    fig = render_map_figure(
        matrix, mode="kills", map_name="Haven",
        points_df=df_pts, show_points=True, grid_size=30
    )
    assert len(fig.data) == 2  # Heatmap + Scatter
    assert fig.data[1].type == "scatter"
    assert len(fig.data[1].x) == 2
