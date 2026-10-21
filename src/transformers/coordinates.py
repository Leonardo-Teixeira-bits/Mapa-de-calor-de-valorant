"""Offline coordinate projection for VALORANT in-game Unreal coordinates to 2D normalized space."""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "maps.json"


class CoordinateTransformer:
    """Projects 3D Unreal Engine coordinates (X, Y) onto a [0.0, 1.0] 2D normalized map grid."""

    def __init__(self, config_path: str | Path | None = None):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.maps_config: Dict[str, Dict[str, Any]] = self._load_config()

    def _load_config(self) -> Dict[str, Dict[str, Any]]:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Map calibration config not found at {self.config_path}. "
                "Ensure config/maps.json is present for 100% offline operation."
            )
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_map_meta(self, map_id: str) -> Optional[Dict[str, Any]]:
        """Returns calibration dict for a given mapId or None if not configured."""
        return self.maps_config.get(map_id)

    def get_display_name(self, map_id: str) -> str:
        """Translates mapId to human-readable map name (e.g. /Game/Maps/Triad/Triad -> Haven)."""
        meta = self.get_map_meta(map_id)
        if meta and "displayName" in meta:
            return meta["displayName"]
        # Fallback to extracting leaf component
        parts = map_id.rstrip("/").split("/")
        return parts[-1] if parts else map_id

    def to_normalized(
        self,
        world_x: int | float,
        world_y: int | float,
        map_id: str,
        clamp: bool = True
    ) -> Tuple[float, float]:
        """
        Converts in-game 3D coordinates (world_x, world_y) into 2D UI space [0.0, 1.0].
        
        Formula per VALORANT engine orientation:
            norm_x = (world_y * xMultiplier) + xScalarToAdd
            norm_y = (world_x * yMultiplier) + yScalarToAdd
        """
        meta = self.get_map_meta(map_id)
        if not meta or meta.get("xMultiplier") == 0:
            # Fallback for uncalibrated maps: return safe placeholder
            return 0.5, 0.5

        x_mult = meta["xMultiplier"]
        y_mult = meta["yMultiplier"]
        x_scalar = meta["xScalarToAdd"]
        y_scalar = meta["yScalarToAdd"]

        norm_x = (float(world_y) * x_mult) + x_scalar
        norm_y = (float(world_x) * y_mult) + y_scalar

        if clamp:
            norm_x = max(0.0, min(1.0, norm_x))
            norm_y = max(0.0, min(1.0, norm_y))

        return norm_x, norm_y
