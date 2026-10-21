"""Plotly interactive geospatial map renderer for VALORANT match analysis."""

from __future__ import annotations
import base64
from pathlib import Path
from typing import Optional, Dict, Any, Union
import numpy as np
import pandas as pd
import plotly.graph_objects as go

ASSETS_MAPS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "maps"


def get_minimap_base64_uri(map_name: str, assets_dir: Optional[Path] = None) -> Optional[str]:
    """
    Returns a base64 encoded data URI for the map's minimap PNG image.
    Enables 100% offline rendering within Plotly without external HTTP requests.
    """
    folder = assets_dir or ASSETS_MAPS_DIR
    img_path = folder / f"{map_name.lower()}.png"
    if not img_path.exists():
        return None

    try:
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None


def render_map_figure(
    matrix: np.ndarray | list,
    mode: str,
    map_name: str,
    points_df: Optional[pd.DataFrame] = None,
    show_points: bool = False,
    grid_size: int = 100,
    assets_dir: Optional[Path] = None
) -> go.Figure:
    """
    Creates an interactive Plotly Figure with the official VALORANT minimap background
    and an overlay of spatial density (Kills/Deaths) or Bayesian territorial winrate.

    Modes:
      - 'kills': Heatmap of attacker kill positions
      - 'deaths': Heatmap of victim death positions
      - 'winrate': Bayesian regularized winrate surface (divergent around 0.5)
    """
    z_data = np.array(matrix, dtype=float) if not isinstance(matrix, np.ndarray) else matrix.copy()
    if z_data.ndim != 2:
        z_data = np.zeros((grid_size, grid_size), dtype=float)

    fig = go.Figure()

    # Coordinates: x and y in [0.0, 1.0]
    x_coords = np.linspace(0.0, 1.0, z_data.shape[1])
    y_coords = np.linspace(0.0, 1.0, z_data.shape[0])

    mode_lower = mode.lower()

    if mode_lower == "winrate":
        # Divergent scale centered at 0.5 (neutral prior)
        colorscale = [
            [0.0, "rgb(178, 24, 43)"],    # 0.3: Deep Red (Strong Deficit)
            [0.25, "rgb(239, 138, 98)"],  # 0.4: Orange
            [0.5, "rgba(247, 247, 247, 0.15)"], # 0.5: Translucent (Baseline / Neutral)
            [0.75, "rgb(103, 169, 207)"], # 0.6: Light Blue
            [1.0, "rgb(33, 102, 172)"]    # 0.7: Deep Blue (Dominant Advantage)
        ]
        colorbar_title = "Prob. Vitória (Bayes)"
        zmin, zmax = 0.35, 0.65

        fig.add_trace(
            go.Heatmap(
                z=z_data,
                x=x_coords,
                y=y_coords,
                colorscale=colorscale,
                zmin=zmin,
                zmax=zmax,
                zmid=0.5,
                opacity=0.72,
                colorbar=dict(
                    title=dict(text=colorbar_title, side="right"),
                    tickvals=[0.35, 0.42, 0.5, 0.58, 0.65],
                    ticktext=["35%", "42%", "50%", "58%", "65%+"],
                    len=0.75,
                    thickness=15
                ),
                hovertemplate="X: %{x:.2f}<br>Y: %{y:.2f}<br>Winrate Estimado: %{z:.1%}<extra></extra>"
            )
        )

    else:
        # Density Heatmaps (Kills or Deaths)
        # Mask out zero or baseline values with NaN so map is clearly visible
        max_val = np.max(z_data) if z_data.size > 0 else 0.0
        threshold = max_val * 0.02 if max_val > 0 else 0.0
        masked_z = np.where(z_data <= threshold, np.nan, z_data)

        if mode_lower == "kills":
            colorscale = "Hot"
            colorbar_title = "Densidade Abates"
        else:
            colorscale = "Inferno"
            colorbar_title = "Densidade Mortes"

        fig.add_trace(
            go.Heatmap(
                z=masked_z,
                x=x_coords,
                y=y_coords,
                colorscale=colorscale,
                reversescale=True if colorscale == "Hot" else False,
                opacity=0.68,
                colorbar=dict(
                    title=dict(text=colorbar_title, side="right"),
                    len=0.75,
                    thickness=15
                ),
                hovertemplate="X: %{x:.2f}<br>Y: %{y:.2f}<br>Densidade: %{z:.2f}<extra></extra>"
            )
        )

    # Optional Raw Events Scatter Layer
    if show_points and points_df is not None and len(points_df) > 0:
        if mode_lower == "deaths":
            px = points_df["victim_norm_x"].dropna()
            py = points_df["victim_norm_y"].dropna()
            color_col = points_df.loc[px.index, "victim_won_round"]
        else:
            px = points_df["killer_norm_x"].dropna()
            py = points_df["killer_norm_y"].dropna()
            color_col = points_df.loc[px.index, "killer_won_round"]

        colors = ["#00F5D4" if w is True else "#FF0055" if w is False else "#FEE440" for w in color_col]

        fig.add_trace(
            go.Scatter(
                x=px,
                y=py,
                mode="markers",
                marker=dict(
                    size=6,
                    color=colors,
                    opacity=0.8,
                    line=dict(width=0.5, color="#111111")
                ),
                text=[
                    f"Round: {r}<br>Fase: {p}<br>Resultado: {'Vitória' if w else 'Derrota'}"
                    for r, p, w in zip(
                        points_df.loc[px.index, "round_num"],
                        points_df.loc[px.index, "round_phase"],
                        color_col
                    )
                ],
                hoverinfo="text",
                name="Eventos de Abate"
            )
        )

    # Add background minimap image if available
    img_uri = get_minimap_base64_uri(map_name, assets_dir)
    if img_uri:
        fig.add_layout_image(
            dict(
                source=img_uri,
                xref="x",
                yref="y",
                x=0.0,
                y=0.0,
                sizex=1.0,
                sizey=1.0,
                sizing="stretch",
                opacity=0.90,
                layer="below"
            )
        )

    # Layout configuration
    fig.update_layout(
        width=700,
        height=700,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="#0F1923",   # VALORANT dark background
        paper_bgcolor="#0F1923",
        xaxis=dict(
            range=[0.0, 1.0],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[0.0, 1.0],
            autorange="reversed",  # Aligns (0, 0) to top-left image origin
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color="#ECE8E1")
        )
    )

    return fig
