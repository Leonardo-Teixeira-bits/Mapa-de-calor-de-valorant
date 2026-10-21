"""Bayesian regularized spatial winrate surface estimation with Gaussian smoothing."""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from typing import Optional, Dict, Any


def compute_bayesian_winrate_grid(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    win_col: str = "killer_won_round",
    grid_size: int = 100,
    prior_weight: float = 5.0,
    smooth_sigma: float = 1.8,
    global_prior_mean: Optional[float] = 0.5
) -> np.ndarray:
    """
    Computes a spatially regularized winrate map using a Bayesian Beta prior:
    
        P_hat(Win | x, y) = (Wins_smooth(x, y) + alpha_0) / (Total_smooth(x, y) + alpha_0 + beta_0)
    
    where:
        - alpha_0 = global_prior_mean * prior_weight
        - beta_0  = (1 - global_prior_mean) * prior_weight
        - Wins_smooth and Total_smooth are 2D Gaussian filtered counts.
        
    This eliminates sharp 0% or 100% artifacts in cells with sparse data,
    reverting naturally to the global baseline (default 0.5) when unobserved.
    """
    valid = df[[x_col, y_col, win_col]].dropna()
    if len(valid) == 0:
        return np.full((grid_size, grid_size), 0.5, dtype=float)

    # Convert win_col to numeric boolean (1 or 0)
    wins = valid[win_col].astype(bool).astype(float).to_numpy()
    x = valid[x_col].clip(0.0, 1.0).to_numpy()
    y = valid[y_col].clip(0.0, 1.0).to_numpy()

    # Global prior parameters
    if global_prior_mean is not None:
        mean_val = max(0.1, min(0.9, float(global_prior_mean)))
    else:
        mean_val = float(np.mean(wins)) if len(wins) > 0 else 0.5
        mean_val = max(0.1, min(0.9, mean_val))

    alpha_0 = mean_val * prior_weight
    beta_0 = (1.0 - mean_val) * prior_weight

    # Discretize onto grid matching standard histogram binning:
    # Bin index = floor(coord * grid_size), clipped to [0, grid_size - 1]
    x_bins = np.clip(np.floor(x * grid_size).astype(int), 0, grid_size - 1)
    y_bins = np.clip(np.floor(y * grid_size).astype(int), 0, grid_size - 1)

    total_grid = np.zeros((grid_size, grid_size), dtype=float)
    wins_grid = np.zeros((grid_size, grid_size), dtype=float)

    for i in range(len(x)):
        r = y_bins[i]
        c = x_bins[i]
        total_grid[r, c] += 1.0
        if wins[i] > 0.5:
            wins_grid[r, c] += 1.0

    # Apply 2D spatial smoothing if requested
    if smooth_sigma > 0:
        total_smooth = gaussian_filter(total_grid, sigma=smooth_sigma, mode="constant", cval=0.0)
        wins_smooth = gaussian_filter(wins_grid, sigma=smooth_sigma, mode="constant", cval=0.0)
    else:
        total_smooth = total_grid
        wins_smooth = wins_grid

    # Bayesian posterior expected value
    posterior_winrate = (wins_smooth + alpha_0) / (total_smooth + alpha_0 + beta_0)
    return np.clip(posterior_winrate, 0.0, 1.0)
