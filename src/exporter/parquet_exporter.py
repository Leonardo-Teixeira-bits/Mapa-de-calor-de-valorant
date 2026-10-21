"""Export utilities for processed events Parquet and density/winrate JSON caches."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Union
import numpy as np
import pandas as pd


def export_events_parquet(
    df: pd.DataFrame,
    output_path: Union[str, Path] = "data/processed/processed_events.parquet"
) -> Path:
    """
    Exports enriched kill events DataFrame to Parquet format with snappy compression.
    Creates parent directories if necessary.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, engine="pyarrow", compression="snappy", index=False)
    return path


def _convert_numpy(obj: Any) -> Any:
    """Helper to convert NumPy arrays and scalars into JSON-serializable types."""
    if isinstance(obj, np.ndarray):
        return np.round(obj, 4).tolist()
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        return round(float(obj), 4)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_numpy(item) for item in obj]
    return obj


def export_density_cache(
    cache_dict: Dict[str, Any],
    output_path: Union[str, Path] = "data/processed/density_winrate_cache.json"
) -> Path:
    """
    Exports pre-aggregated spatial density matrices (kills/deaths) and Bayesian winrate
    matrices per map and round phase into a single compact JSON file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = _convert_numpy(cache_dict)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, separators=(",", ":"))
    return path


def export_maps_summary(
    summary_dict: Dict[str, Any],
    output_path: Union[str, Path] = "data/processed/maps_summary.json"
) -> Path:
    """
    Exports map metadata summary (counts of matches, rounds, kills, low_sample_warning, tier)
    to a readable JSON file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = _convert_numpy(summary_dict)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    return path
