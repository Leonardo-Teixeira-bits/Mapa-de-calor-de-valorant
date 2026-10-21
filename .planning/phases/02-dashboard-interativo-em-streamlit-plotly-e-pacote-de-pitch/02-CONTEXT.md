# Phase 2: Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch - Context

**Gathered:** 2026-10-21
**Status:** In planning

<domain>
## Phase Boundary

Interface analítica e visual para exploração geoespacial e temporal de partidas de VALORANT com Streamlit e Plotly. A interface consome exclusivamente os artefatos pré-calculados (`data/processed/processed_events.parquet`, `data/processed/density_winrate_cache.json` e `data/processed/maps_summary.json`), renderizando mapas de calor e superfícies de vantagem territorial sobre as imagens oficiais dos minimapas locais em `assets/maps/`. Apresenta navegação destacada para o núcleo competitivo de Tier 1 (Ascent, Lotus e Haven - 71.6% dos abates), alerta estatístico para mapas com amostragem reduzida ($N < 10$), painel de KPIs e documentação completa com roteiro para o vídeo pitch de 5 minutos.

</domain>

<decisions>
## Implementation Decisions

### Arquitetura da Interface (Streamlit + Plotly)
- **D-11:** Aplicação em `app.py` com navegação lateral responsiva (`st.sidebar`), tema moderno escuro com paleta de cores inspirada no VALORANT (vermelho carmesim, cinza escuro, ciano).
- **D-12:** Seletor de mapas com agrupamento visual:
  - **Tier 1 (MVP Competitivo):** Ascent, Lotus e Haven (em destaque no topo da lista).
  - **Tier 2 (Mapas Estendidos):** Split, Sunset, Abyss, Summit.
  - **Tier 3 (Amostra Reduzida):** Breeze, Pearl, Fracture acompanhados de badge de alerta visual explícito (`st.warning` / tag estilizada).

### Renderização Geoespacial (Plotly)
- **D-13:** Módulo `src/visualization/map_renderer.py` encapsula a criação das figuras Plotly:
  - Renderiza a imagem do minimapa local (`assets/maps/<map>.png`) como background na camada inferior (`layer="below"`).
  - Eixos normalizados $[0.0, 1.0]$ com aspect ratio fixo 1:1 (`scaleanchor="x"`, `scaleratio=1`).
  - Suporta três modos de visualização com alternância instantânea:
    1. **Mapa de Abates (Kills - Mapa A):** Escala de calor quente (ex: `Hot` ou `Plasma`) mostrando onde os atacantes efetuaram os abates.
    2. **Mapa de Mortes (Deaths - Mapa B):** Escala de calor (ex: `Inferno` ou `Reds`) mostrando onde as vítimas caíram.
    3. **Mapa de Vantagem Territorial (Winrate Bayesiano):** Escala divergente centrada em 50% (ex: `RdBu_r` ou `Spectral`, onde azul/verde indica alta probabilidade de vitória e vermelho indica baixa).
  - Suporte a visualização contínua (KDE / Heatmap) e visualização de pontos dispersos (*scatter points*) com hover detalhado (vítima, atacante, arma, tempo).

### Métricas e KPIs
- **D-14:** Cards de KPI no topo da tela:
  - Total de Partidas do mapa selecionado
  - Total de Rounds analisados
  - Total de Abates registrados
  - Balanceamento de Rounds (Taxa de Vitória Atacantes vs Defensores)
- **D-15:** Aba ou seção colapsável com Tabela de Eventos Filtrados (`st.dataframe`) permitindo ordenar e inspecionar eliminações específicas.

### Pacote de Entrega e Pitch (Hackathon)
- **D-16:** `README.md` reestruturado para o comitê avaliador contendo:
  - Instruções de inicialização em 1 comando 100% offline (`streamlit run app.py`).
  - Explicação matemática acessível do winrate espacial e regularização Bayesiana.
  - Demonstração visual (GIF/Prints) da interface.
  - Roteiro estruturado de 5 minutos para o vídeo pitch.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md` — Visão, restrições e regras do hackathon.
- `.planning/REQUIREMENTS.md` — Requisitos v1 rastreáveis para UI-01, UI-02, UI-03 e UI-04.
- `data/processed/maps_summary.json` — Resumo estatístico e tiers dos mapas.
- `data/processed/density_winrate_cache.json` — Caches de matrizes espaciais.
- `data/processed/processed_events.parquet` — Base de eventos de eliminações.
- `assets/maps/*.png` — Imagens oficiais locais de minimapas.

</canonical_refs>
