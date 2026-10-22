"""Streamlit Web Dashboard for VALORANT Geospatial Match Analysis."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import streamlit as st

from src.visualization.map_renderer import render_map_figure
from src.transformers.weapons import format_damage_events

# Project paths
PROCESSED_DIR = Path(__file__).resolve().parent / "data" / "processed"
SUMMARY_PATH = PROCESSED_DIR / "maps_summary.json"
CACHE_PATH = PROCESSED_DIR / "density_winrate_cache.json"
EVENTS_PATH = PROCESSED_DIR / "processed_events.parquet"

# Page configuration
st.set_page_config(
    page_title="VALORANT GeoAnalytics | UNIVAVA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom VALORANT Dark Theme CSS with Typography & Colors from VALORANT.html
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Oswald:wght@500;600;700&display=swap');

    /* Global Body and Container Styling */
    html, body, [class*="css"], .reportview-container, .main, .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0F1923 !important;
        color: #ECE8E1 !important;
    }

    /* Headings with VALORANT Tungsten / Bold Condensed Aesthetic */
    h1, h2, h3, .valorant-title {
        font-family: 'Bebas Neue', 'Oswald', sans-serif !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: #ECE8E1 !important;
        font-weight: 700 !important;
    }

    h1 {
        font-size: 2.6rem !important;
        border-left: 5px solid #FF4655;
        padding-left: 14px;
        margin-bottom: 0.3rem !important;
    }

    h2, h3 {
        font-size: 1.45rem !important;
        letter-spacing: 0.06em !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111822 !important;
        border-right: 1px solid rgba(236, 232, 225, 0.08);
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        font-family: 'Bebas Neue', 'Oswald', sans-serif !important;
        letter-spacing: 0.06em !important;
        color: #ECE8E1 !important;
    }

    /* HUD-Style Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #18222C 0%, #111822 100%) !important;
        border: 1px solid rgba(236, 232, 225, 0.12) !important;
        border-radius: 4px !important;
        padding: 14px 18px !important;
        border-left: 4px solid #FF4655 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 70, 85, 0.4) !important;
    }

    div[data-testid="stMetric"] label {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8B978F !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Bebas Neue', 'Oswald', sans-serif !important;
        color: #ECE8E1 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
    }

    /* VALORANT Tier Badges */
    .tier-badge-1 {
        display: inline-block;
        background-color: #00F5D4;
        color: #0F1923;
        padding: 4px 12px;
        border-radius: 2px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .tier-badge-2 {
        display: inline-block;
        background-color: #FFB703;
        color: #0F1923;
        padding: 4px 12px;
        border-radius: 2px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .tier-badge-3 {
        display: inline-block;
        background-color: #FF4655;
        color: #FFFFFF;
        padding: 4px 12px;
        border-radius: 2px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* Tactical Box */
    .tactical-box {
        background-color: #18222C;
        border: 1px solid rgba(236, 232, 225, 0.1);
        border-radius: 4px;
        padding: 16px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_maps_summary() -> Dict[str, Any]:
    if not SUMMARY_PATH.exists():
        return {}
    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_density_cache() -> Dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_events_df() -> pd.DataFrame:
    if not EVENTS_PATH.exists():
        return pd.DataFrame()
    return pd.read_parquet(EVENTS_PATH)


def ensure_data_extracted():
    zip_path = Path(__file__).resolve().parent / "data.zip"
    if (not SUMMARY_PATH.exists() or not EVENTS_PATH.exists()) and zip_path.exists():
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(Path(__file__).resolve().parent)


def main():
    ensure_data_extracted()
    summary = load_maps_summary()
    cache = load_density_cache()
    events_df = load_events_df()

    if not summary or not cache:
        st.error(
            "Artefatos processados não encontrados em `data/processed/`. "
            "Por favor, execute o pipeline primeiro: `python src/pipeline.py`."
        )
        return

    # Categorize available maps into tiers
    tier1_maps = [m for m, d in summary.items() if d.get("tier") == 1]
    tier2_maps = [m for m, d in summary.items() if d.get("tier") == 2]
    tier3_maps = [m for m, d in summary.items() if d.get("tier") == 3]

    # Map selection options with visual indicators
    map_options = []
    for m in tier1_maps:
        map_options.append((m, f" {m} (Tier 1 MVP - {summary[m]['matches_count']} partidas)"))
    for m in tier2_maps:
        map_options.append((m, f" {m} (Tier 2 - {summary[m]['matches_count']} partidas)"))
    for m in tier3_maps:
        map_options.append((m, f" {m} (Tier 3 - Amostra reduzida: {summary[m]['matches_count']} jogos)"))

    # Sidebar Controls
    st.sidebar.image(
        "https://logopng.com.br/logos/valorant-192.svg?dpl=dpl_83xWKUBiCCc88zqvgK1XNSG8JXgj",
        width=50
    )
    st.sidebar.title("VALORANT Analytics")
    st.sidebar.caption("Plataforma Geoespacial Universitária (UNIVAVA)")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Seleção de Mapa")
    selected_option_idx = st.sidebar.selectbox(
        "Mapa:",
        range(len(map_options)),
        format_func=lambda idx: map_options[idx][1]
    )
    selected_map = map_options[selected_option_idx][0]
    map_meta = summary.get(selected_map, {})

    st.sidebar.subheader("Modo de Análise")
    mode_choice = st.sidebar.radio(
        "Visualização Geoespacial:",
        [
            ("kills", " Mapa de Abates (Kills - Atacante)"),
            ("deaths", " Mapa de Mortes (Deaths - Vítima)"),
            ("winrate", " Vantagem Territorial (Winrate Bayesiano)")
        ],
        format_func=lambda x: x[1]
    )
    selected_mode = mode_choice[0]

    st.sidebar.subheader("Filtro Temporal do Round")
    phase_choice = st.sidebar.selectbox(
        "Fase do Round:",
        [
            ("Total", "⏱ Round Completo (Total)"),
            ("Early", "🟢 Início (0 - 33% da duração)"),
            ("Mid", "🟡 Meio (33% - 66% da duração)"),
            ("Late", "🔴 Fim / Pós-Plant (66% - 100%)")
        ],
        format_func=lambda x: x[1]
    )
    selected_phase = phase_choice[0]

    show_points = st.sidebar.checkbox("Sobrepor pontos de eventos individuais", value=False)

    # Main Header
    st.title(f"Análise Geoespacial: {selected_map}")
    
    tier_num = map_meta.get("tier", 1)
    if tier_num == 1:
        st.markdown(
            '<span class="tier-badge-1">TIER 1 • NÚCLEO COMPETITIVO PRIORITÁRIO</span>',
            unsafe_allow_html=True
        )
    elif tier_num == 2:
        st.markdown(
            '<span class="tier-badge-2">TIER 2 • MAPA ESTENDIDO</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="tier-badge-3">TIER 3 • AMOSTRA REDUZIDA</span>',
            unsafe_allow_html=True
        )

    # Low sample size alert
    if map_meta.get("low_sample_warning", False):
        st.warning(
            f"⚠️ **Aviso de Amostra Reduzida ($N < 10$)**: O mapa **{selected_map}** possui apenas "
            f"**{map_meta.get('matches_count', 0)} partidas** no histórico do torneio. "
            "A superfície de calor e o winrate espacial recebem regularização Bayesiana "
            "com prior neutro (50%) para atenuar ruídos de baixa amostragem."
        )

    st.write("")

    # KPI Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Partidas Analisadas", map_meta.get("matches_count", 0))
    with m_col2:
        st.metric("Rounds Registrados", map_meta.get("rounds_count", 0))
    with m_col3:
        st.metric("Total de Eliminações", f"{map_meta.get('kills_count', 0):,}")
    with m_col4:
        # Compute map kill/win empirical winrate
        filtered_events = events_df[events_df["map_name"] == selected_map] if not events_df.empty else pd.DataFrame()
        if not filtered_events.empty and "killer_won_round" in filtered_events:
            valid_wins = filtered_events["killer_won_round"].dropna()
            winrate_pct = f"{valid_wins.mean():.1%}" if len(valid_wins) > 0 else "50.0%"
        else:
            winrate_pct = "N/A"
        st.metric("Winrate Médio da Posição", winrate_pct)

    st.write("")

    # Geospatial Canvas & Tactical Insights Layout
    map_col, insights_col = st.columns([1.6, 1.0])

    with map_col:
        # Retrieve precomputed spatial matrix
        map_cache = cache.get(selected_map, {})
        phase_cache = map_cache.get(selected_phase, {})

        if selected_mode == "kills":
            matrix = phase_cache.get("kills_density", [])
        elif selected_mode == "deaths":
            matrix = phase_cache.get("deaths_density", [])
        else:
            matrix = phase_cache.get("bayesian_winrate", [])

        # Filter events dataframe for scatter points overlay
        if show_points and not filtered_events.empty:
            if selected_phase != "Total":
                pts_df = filtered_events[filtered_events["round_phase"] == selected_phase]
            else:
                pts_df = filtered_events
        else:
            pts_df = None

        fig = render_map_figure(
            matrix=matrix,
            mode=selected_mode,
            map_name=selected_map,
            points_df=pts_df,
            show_points=show_points,
            grid_size=100
        )
        st.plotly_chart(fig, use_container_width=True)

    with insights_col:
        st.subheader("Inteligência Tática & Leitura")

        if selected_mode == "kills":
            st.markdown("""
            **Mapa de Densidade de Abates:**
            * Exibe as posições geográficas exatas onde os **atacantes efetuaram as eliminações**.
            * Concentrações intensas revelam os ângulos mais favoráveis para troca de dano (*first engagements* e *crossfires*).
            """)
        elif selected_mode == "deaths":
            st.markdown("""
            **Mapa de Densidade de Mortes:**
            * Mapeia os locais onde os **jogadores foram eliminados**.
            * Zonas quentes indicam gargalos (*chokepoints*), áreas de penetração vulneráveis a utilitários e linhas de tiro desfavoráveis.
            """)
        else:
            st.markdown("""
            **Superfície de Vantagem Territorial (Winrate Bayesiano):**
            * Calcula a probabilidade condicionada de vitória do round com base na posição do abate: $\\hat{P}(\\text{Win} \\mid x, y)$.
            * **Regularização Bayesiana (Beta Prior):** Regiões com amostras isoladas convergem suavemente para 50%, prevenindo picos espúrios de 100%.
            * **Azul Escuro:** Controle territorial com vantagem decisiva ($> 60\\%$ de conversão).
            * **Vermelho:** Trocas em posições de alto risco que resultam frequentemente em derrota ($< 40\\%$ de vitória).
            """)

        st.markdown("---")
        st.markdown(f"**Fase Analisada:** `{selected_phase}`")
        if selected_phase == "Early":
            st.caption("Fase inicial: tomada de espaços, disputas por orbe e abates de abertura (*first bloods*).")
        elif selected_phase == "Mid":
            st.caption("Fase intermediária: rotações, uso de utilitários secundários e transições para os bombsites.")
        elif selected_phase == "Late":
            st.caption("Fase final: execuções pós-plant, desarme da Spike e retakes sob pressão de tempo.")
        else:
            st.caption("Visão agregada consolidando todos os confrontos da partida.")

    # Detailed Events Inspection Table with Friendly Weapon Names
    with st.expander("Inspecionar Registros de Abates Detalhados"):
        if not filtered_events.empty:
            # Resolve weapon and item names
            enriched_events = format_damage_events(filtered_events)

            display_cols = [
                "round_num", "round_phase", "round_time_ms",
                "weapon_name", "killer_team", "victim_team", "killer_won_round"
            ]
            avail_cols = [c for c in display_cols if c in enriched_events.columns]
            table_df = enriched_events[avail_cols].copy()

            rename_map = {}
            if "round_num" in table_df:
                rename_map["round_num"] = "Round"
            if "round_phase" in table_df:
                rename_map["round_phase"] = "Fase"
            if "round_time_ms" in table_df:
                table_df["Time (sec.)"] = (table_df["round_time_ms"] / 1000).round(1)
                table_df.drop(columns=["round_time_ms"], inplace=True)
            if "weapon_name" in table_df:
                rename_map["weapon_name"] = "Arma / Item"
            if "killer_team" in table_df:
                rename_map["killer_team"] = "Time Atacante"
            if "victim_team" in table_df:
                rename_map["victim_team"] = "Time Vítima"
            if "killer_won_round" in table_df:
                table_df["Vencedor"] = table_df["killer_won_round"].apply(
                    lambda w: "Atacante" if w is True else "Defensor" if w is False else "Indeterminado"
                )
                table_df.drop(columns=["killer_won_round"], inplace=True)

            table_df.rename(columns=rename_map, inplace=True)
            st.dataframe(table_df.head(250), use_container_width=True)
        else:
            st.info("Nenhum evento registrado para o filtro atual.")


if __name__ == "__main__":
    main()
