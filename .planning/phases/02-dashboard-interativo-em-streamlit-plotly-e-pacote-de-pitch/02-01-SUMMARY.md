---
phase: 02-dashboard-interativo-em-streamlit-plotly-e-pacote-de-pitch
plan: 01
subsystem: ui-dashboard
tags: [streamlit, plotly, heatmap, geospatial, offline]

requires: [01-02]
provides:
  - Renderizador geoespacial Plotly com suporte aos minimapas oficiais em assets/maps/
  - Modos de visualização para Abates, Mortes e Vantagem Territorial (Winrate Bayesiano)
  - Dashboard web interativo Streamlit em app.py
  - Navegação segmentada por Tiers (Tier 1 MVP no topo e alerta N < 10)
  - Cards de KPIs e tabela detalhada de eliminações
affects: [pitch, documentation]

actuals:
  tasks: 3
  files: 5

tech-stack:
  added: [streamlit, plotly]
  patterns: [offline-base64-image-overlay, divergent-winrate-colorscale, tiered-map-selector]

key-files:
  created:
    - src/visualization/map_renderer.py
    - src/visualization/__init__.py
    - app.py
    - tests/test_visualization.py
    - tests/test_app_integration.py

key-decisions:
  - "D-11: Dashboard Streamlit com tema escuro e layout em duas colunas (70% mapa / 30% inteligência tática)"
  - "D-12: Seletor de mapas agrupado destacando Tier 1 (Ascent, Lotus, Haven) e acionando badge de alerta em mapas N < 10"
  - "D-13: Renderizador Plotly com sobreposição de imagem local via data URI base64, garantindo operação 100% offline"
  - "D-14/D-15: Cards de KPIs consolidados e tabela interativa de eventos de abates"

requirements-completed: [UI-01, UI-02, UI-03]

coverage:
  - id: UI-01
    description: "Dashboard interativo em Streamlit com seletor de mapas agrupado por Tiers e filtros temporais"
    requirement: "UI-01"
    verification:
      - kind: integration
        ref: "tests/test_app_integration.py#test_app_data_artifacts_exist"
        status: pass
  - id: UI-02
    description: "Renderização de mapas de calor e winrate Bayesiano com Plotly sobre minimapas oficiais"
    requirement: "UI-02"
    verification:
      - kind: unit
        ref: "tests/test_visualization.py"
        status: pass
      - kind: integration
        ref: "tests/test_app_integration.py#test_app_render_all_modes_for_tier1_maps"
        status: pass
  - id: UI-03
    description: "Painel analítico com KPIs e alerta estatístico proeminente para mapas com N < 10"
    requirement: "UI-03"
    verification:
      - kind: code_review
        ref: "app.py"
        status: pass

duration: 15min
completed: 2026-10-21
status: complete
---

# Phase 2: Plan 02-01 Summary

**Dashboard Web Interativo Streamlit e Renderizador Geoespacial Plotly com Minimapas Oficiais Concluídos**

## Performance

- **Tasks:** 3
- **Files Created/Modified:** 5
- **Automated Tests:** 23 passed (100%)
- **Modos de Exibição:** Abates (Kills), Mortes (Deaths), Vantagem Territorial (Winrate Bayesiano)

## Accomplishments

1. **Renderizador Geoespacial Plotly (`src/visualization/map_renderer.py`):**
   - Incorpora as imagens oficiais locais dos minimapas (`assets/maps/*.png`) como background base64 data URI (100% offline).
   - Eixos normalizados $[0.0, 1.0]$ com aspect ratio 1:1 e $Y$ invertido para encaixe preciso das coordenadas do jogo.
   - Suporte a 3 modos de renderização:
     - **Abates (Kills):** mapa de calor destacando posições dos atacantes.
     - **Mortes (Deaths):** mapa de calor indicando onde as vítimas tombaram.
     - **Vantagem Territorial:** mapa de calor divergente centrado em 50% de probabilidade de vitória com escala Bayesiana.
   - Camada opcional de eventos individuais com hover detalhado.

2. **Dashboard Web Streamlit (`app.py`):**
   - Interface com tema escuro imersivo inspirado na identidade visual de VALORANT.
   - Seletor de mapas com destaque no topo para o Tier 1 competitivo (**Ascent, Lotus, Haven**).
   - Alerta visual explícito para mapas com amostragem reduzida ($N < 10$: Breeze, Pearl, Fracture).
   - Filtros dinâmicos por fase do round (`Total`, `Early`, `Mid`, `Late`).
   - Cards de métricas com total de partidas, rounds, abates e winrate posicional médio.
   - Tabela interativa para inspeção detalhada de eventos.

## Next Phase Readiness

- Plan 02-01 100% concluído. Pronto para executar o Plan 02-02 (README.md, roteiro do pitch de 5 minutos e script launcher `run_app.py`).
