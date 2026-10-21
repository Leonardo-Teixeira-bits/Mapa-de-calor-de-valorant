"""Unit tests for spatial density and Bayesian winrate calculation."""

import numpy as np
import pandas as pd
import pytest

from src.analytics.density import compute_density_grid, compute_kde_surface
from src.analytics.bayesian_winrate import compute_bayesian_winrate_grid


def test_density_grid_shape_and_bounds():
    df = pd.DataFrame({
        "norm_x": [0.1, 0.2, 0.5, 0.9],
        "norm_y": [0.1, 0.3, 0.5, 0.9]
    })
    grid = compute_density_grid(df, "norm_x", "norm_y", grid_size=100)
    assert grid.shape == (100, 100)
    assert grid.sum() == 4.0


def test_kde_surface_normalized():
    # Generate 50 synthetic points around center (0.5, 0.5)
    np.random.seed(42)
    df = pd.DataFrame({
        "norm_x": np.random.normal(0.5, 0.1, 50).clip(0, 1),
        "norm_y": np.random.normal(0.5, 0.1, 50).clip(0, 1)
    })
    kde = compute_kde_surface(df, "norm_x", "norm_y", grid_size=50)
    assert kde.shape == (50, 50)
    assert np.isclose(kde.sum(), 1.0, atol=1e-3)
    # Peak should be near center
    assert kde[25, 25] > kde[0, 0]


def test_bayesian_winrate_regularization():
    # Scenario A: Region with only 1 kill (won).
    # Unregularized would be 100% winrate.
    # Regularized with Beta prior (global mean = 0.5, weight = 5)
    # should be pulled strongly toward 0.5: (1 + 2.5) / (1 + 5) = 3.5 / 6 ~ 0.583
    df_sparse = pd.DataFrame({
        "norm_x": [0.5],
        "norm_y": [0.5],
        "won": [True]
    })
    winrate_map = compute_bayesian_winrate_grid(
        df_sparse, "norm_x", "norm_y", win_col="won",
        grid_size=100, prior_weight=5.0, smooth_sigma=0.0
    )
    center_wr = winrate_map[50, 50]
    assert center_wr < 0.70, f"Expected sparse single-win cell to be regularized < 0.70, got {center_wr}"
    assert center_wr > 0.50

    # Scenario B: High sample size (50 wins, 5 losses at (0.2, 0.2))
    df_dense = pd.DataFrame({
        "norm_x": [0.2] * 55,
        "norm_y": [0.2] * 55,
        "won": [True] * 50 + [False] * 5
    })
    dense_map = compute_bayesian_winrate_grid(
        df_dense, "norm_x", "norm_y", win_col="won",
        grid_size=100, prior_weight=5.0, smooth_sigma=0.0
    )
    dense_wr = dense_map[20, 20]
    # (50 + 2.5) / (55 + 5) = 52.5 / 60 = 0.875 ~ 87.5%
    assert dense_wr > 0.80, f"Expected high-volume cell to reflect empirical rate > 0.80, got {dense_wr}"
