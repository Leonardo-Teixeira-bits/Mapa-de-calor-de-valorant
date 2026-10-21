"""Spatial density estimation (2D Grid and Gaussian KDE) for VALORANT kill and death events."""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from typing import Optional, Tuple


def compute_density_grid(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    grid_size: int = 100
) -> np.ndarray:
    """
    Computes a 2D histogram grid of event counts over the normalized [0.0, 1.0] domain.
    Returns a float array of shape (grid_size, grid_size).
    """
    valid = df[[x_col, y_col]].dropna()
    if len(valid) == 0:
        return np.zeros((grid_size, grid_size), dtype=float)

    x = valid[x_col].clip(0.0, 1.0).to_numpy()
    y = valid[y_col].clip(0.0, 1.0).to_numpy()

    # 2D histogram bins: y drives rows (0 to 1), x drives columns (0 to 1)
    hist, _, _ = np.histogram2d(
        y, x,
        bins=grid_size,
        range=[[0.0, 1.0], [0.0, 1.0]]
    )
    return hist.astype(float)


def compute_kde_surface(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    grid_size: int = 100,
    bw_method: Optional[str | float] = "scott"
) -> np.ndarray:
    """
    Computes a continuous 2D Gaussian Kernel Density Estimation (KDE) surface
    evaluated across a regular (grid_size, grid_size) grid.
    """
    valid = df[[x_col, y_col]].dropna()
    if len(valid) < 3:
        # Fallback to discrete density grid if insufficient data for covariance inversion
        return compute_density_grid(df, x_col, y_col, grid_size=grid_size)

    x = valid[x_col].clip(0.0, 1.0).to_numpy()
    y = valid[y_col].clip(0.0, 1.0).to_numpy()

    # Add minute jitter to prevent singular covariance matrix if points are identical
    if np.allclose(np.var(x), 0) or np.allclose(np.var(y), 0):
        x = x + np.random.normal(0, 1e-4, size=len(x))
        y = y + np.random.normal(0, 1e-4, size=len(y))

    try:
        kde = gaussian_kde(np.vstack([x, y]), bw_method=bw_method)
        # Generate grid coordinates: linspace for x and y
        xi = np.linspace(0.0, 1.0, grid_size)
        yi = np.linspace(0.0, 1.0, grid_size)
        xx, yy = np.meshgrid(xi, yi)

        grid_coords = np.vstack([xx.ravel(), yy.ravel()])
        z = kde(grid_coords).reshape((grid_size, grid_size))
        # Normalize sum to 1.0
        s = z.sum()
        return z / s if s > 0 else z
    except Exception:
        return compute_density_grid(df, x_col, y_col, grid_size=grid_size)
