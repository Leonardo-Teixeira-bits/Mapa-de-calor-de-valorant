"""Main data pipeline orchestrator for VALORANT match ingestion, spatial analysis and export."""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

from src.ingestion.loader import MatchLoader
from src.transformers.coordinates import CoordinateTransformer
from src.analytics.density import compute_density_grid
from src.analytics.bayesian_winrate import compute_bayesian_winrate_grid
from src.exporter.parquet_exporter import (
    export_events_parquet,
    export_density_cache,
    export_maps_summary,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TIER_1_MAPS = ["Ascent", "Lotus", "Haven"]


class MatchProcessingPipeline:
    """
    Orchestrates batch ingestion, multi-map coordinate projection,
    temporal segmentation, Bayesian winrate estimation, and artifact export.
    """

    def __init__(
        self,
        data_dir: str | Path = "data",
        output_dir: str | Path = "data/processed",
        grid_size: int = 100,
        transformer: Optional[CoordinateTransformer] = None,
        loader: Optional[MatchLoader] = None,
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.grid_size = grid_size
        self.transformer = transformer or CoordinateTransformer()
        self.loader = loader or MatchLoader(self.transformer)

        # Build map suffix lookup from CoordinateTransformer config
        # e.g., 'ascent' -> 'Ascent', 'lotus' -> 'Lotus'
        self.map_name_lookup: Dict[str, str] = {}
        for map_id, info in self.transformer.maps_config.items():
            name = info.get("displayName", "")
            if name:
                self.map_name_lookup[name.lower()] = name

    def discover_match_files(self) -> List[Path]:
        """Finds all JSON match files recursively within data_dir, excluding output_dir."""
        # Auto-extract data.zip if data directory is missing
        if not self.data_dir.exists() and Path("data.zip").exists():
            import zipfile
            logger.info("Extracting data.zip into repository root...")
            with zipfile.ZipFile("data.zip", "r") as z:
                z.extractall(".")

        if not self.data_dir.exists():
            return []
        output_abs = self.output_dir.resolve()
        discovered = []
        for f in self.data_dir.rglob("*.json"):
            if not f.is_file():
                continue
            try:
                if f.resolve().is_relative_to(output_abs):
                    continue
            except (ValueError, RuntimeError):
                pass
            discovered.append(f)
        return sorted(discovered)

    def identify_file_map(self, filepath: Path) -> str:
        """
        Identifies the map name from the file name suffix or falls back
        to fast inspection of the mapId inside the JSON.
        """
        suffix = filepath.stem.split("_")[-1].lower()
        if suffix in self.map_name_lookup:
            return self.map_name_lookup[suffix]

        # Fallback: load file header
        match = self.loader.load_match_file(filepath)
        if match and match.matchInfo and match.matchInfo.mapId:
            return self.transformer.get_display_name(match.matchInfo.mapId)
        return "Unknown"

    def group_files_by_map(self, filepaths: List[Path]) -> Dict[str, List[Path]]:
        """Groups list of file paths by canonical map name."""
        grouped: Dict[str, List[Path]] = {}
        for fp in filepaths:
            map_name = self.identify_file_map(fp)
            if map_name not in grouped:
                grouped[map_name] = []
            grouped[map_name].append(fp)
        return grouped

    def determine_tier(self, map_name: str, matches_count: int) -> int:
        """Determines the competitive and statistical tier of the map."""
        if map_name in TIER_1_MAPS:
            return 1
        elif matches_count >= 10:
            return 2
        else:
            return 3

    def compute_map_cache(
        self,
        map_events_df: pd.DataFrame
    ) -> Dict[str, Dict[str, Any]]:
        """
        Computes 100x100 spatial density grids (kills, deaths) and Bayesian winrate
        grids for all round phases ('Total', 'Early', 'Mid', 'Late').
        """
        cache: Dict[str, Dict[str, Any]] = {}
        phases = ["Total", "Early", "Mid", "Late"]

        for phase in phases:
            if phase == "Total":
                phase_df = map_events_df
            else:
                phase_df = map_events_df[map_events_df["round_phase"] == phase]

            kills_grid = compute_density_grid(
                phase_df,
                x_col="killer_norm_x",
                y_col="killer_norm_y",
                grid_size=self.grid_size
            )
            deaths_grid = compute_density_grid(
                phase_df,
                x_col="victim_norm_x",
                y_col="victim_norm_y",
                grid_size=self.grid_size
            )
            winrate_grid = compute_bayesian_winrate_grid(
                phase_df,
                x_col="killer_norm_x",
                y_col="killer_norm_y",
                win_col="killer_won_round",
                grid_size=self.grid_size
            )

            cache[phase] = {
                "kills_density": kills_grid,
                "deaths_density": deaths_grid,
                "bayesian_winrate": winrate_grid,
            }

        return cache

    def run(self) -> Dict[str, Any]:
        """
        Executes end-to-end pipeline processing:
        1. Discovers and groups match files by map.
        2. Stage 1: Processes Tier 1 MVP maps (Ascent, Lotus, Haven).
        3. Stage 2 & 3: Processes Tier 2 and Tier 3 maps with N < 10 safeguards.
        4. Calculates density & Bayesian winrate matrices.
        5. Exports Parquet events and JSON caches to output_dir.
        """
        logger.info(f"Starting MatchProcessingPipeline from '{self.data_dir}'...")
        all_files = self.discover_match_files()
        logger.info(f"Discovered {len(all_files)} match files.")

        grouped_files = self.group_files_by_map(all_files)

        all_events_records: List[Dict[str, Any]] = []
        maps_summary: Dict[str, Dict[str, Any]] = {}
        density_cache: Dict[str, Any] = {}

        # Separate maps into Tier 1 and Others
        tier1_maps = [m for m in TIER_1_MAPS if m in grouped_files]
        other_maps = [m for m in grouped_files if m not in TIER_1_MAPS and m != "Unknown"]

        # Execution order: Tier 1 first, then Tier 2/3
        execution_stages = [
            ("Stage 1 (Tier 1 MVP)", tier1_maps),
            ("Stage 2 & 3 (Extended Tiers)", other_maps)
        ]

        total_corrupted = 0

        for stage_name, maps_in_stage in execution_stages:
            logger.info(f"--- Executing {stage_name} ({len(maps_in_stage)} maps) ---")
            for map_name in maps_in_stage:
                files = grouped_files[map_name]
                matches, errors = self.loader.load_matches_batch(files)
                total_corrupted += len(errors)

                map_events: List[Dict[str, Any]] = []
                rounds_count = 0
                for match in matches:
                    rounds_count += len(match.roundResults)
                    events = self.loader.extract_kill_events(match)
                    for ev in events:
                        map_events.append(ev.model_dump())

                matches_count = len(matches)
                kills_count = len(map_events)
                tier = self.determine_tier(map_name, matches_count)
                low_sample = matches_count < 10

                logger.info(
                    f"[{map_name}] Tier {tier} | Matches: {matches_count} | "
                    f"Rounds: {rounds_count} | Kills: {kills_count} | "
                    f"Low sample warning: {low_sample}"
                )

                maps_summary[map_name] = {
                    "map_name": map_name,
                    "tier": tier,
                    "matches_count": matches_count,
                    "rounds_count": rounds_count,
                    "kills_count": kills_count,
                    "low_sample_warning": low_sample,
                }

                all_events_records.extend(map_events)

                # Compute spatial density and winrate cache for this map
                if map_events:
                    map_df = pd.DataFrame(map_events)
                    density_cache[map_name] = self.compute_map_cache(map_df)
                else:
                    density_cache[map_name] = {}

        # Consolidate all events into DataFrame
        logger.info(f"Consolidating {len(all_events_records)} total kill events...")
        consolidated_df = pd.DataFrame(all_events_records)

        # Export artifacts
        logger.info(f"Exporting artifacts to '{self.output_dir}'...")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        parquet_path = export_events_parquet(
            consolidated_df,
            self.output_dir / "processed_events.parquet"
        )
        cache_path = export_density_cache(
            density_cache,
            self.output_dir / "density_winrate_cache.json"
        )
        summary_path = export_maps_summary(
            maps_summary,
            self.output_dir / "maps_summary.json"
        )

        logger.info(f"Export complete:")
        logger.info(f" - Parquet events: {parquet_path} ({parquet_path.stat().st_size / (1024*1024):.2f} MB)")
        logger.info(f" - Density cache:  {cache_path} ({cache_path.stat().st_size / (1024*1024):.2f} MB)")
        logger.info(f" - Maps summary:   {summary_path}")

        return {
            "total_files": len(all_files),
            "total_corrupted": total_corrupted,
            "total_events": len(all_events_records),
            "maps": maps_summary,
            "parquet_path": str(parquet_path),
            "cache_path": str(cache_path),
            "summary_path": str(summary_path),
        }


if __name__ == "__main__":
    pipeline = MatchProcessingPipeline()
    summary = pipeline.run()
    print("Pipeline run completed successfully.")
