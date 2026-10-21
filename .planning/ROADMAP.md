# Roadmap: Análise Geoespacial de Partidas de VALORANT

## Overview

Desenvolvimento enxuto de uma plataforma analítica geoespacial de ponta a ponta em 2 fases (Vertical MVP): primeiro estabelecendo o pipeline analítico de alta performance com ingestão resiliente dos 268 JSONs, projeção multi-mapa offline e modelagem estatística de winrate via KDE com prior Bayesiano; em seguida entregando o dashboard interativo em Streamlit + Plotly, filtros multidimensionais e documentação estruturada para o pitch de 5 minutos do hackathon.

## Phases

- [ ] **Phase 1: Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana** - Ingestão de 268 partidas, projeção normalizada dos 9 mapas, segmentação temporal e cálculo de densidades e winrate espacial com KDE Bayesiano.
- [ ] **Phase 2: Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch** - Interface analítica completa com mapas Plotly, alternância de modos (Abates, Mortes, Vantagem), filtros, KPIs e guia para vídeo pitch.

## Phase Details

### Phase 1: Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana
**Goal:** Processar o lote de 268 partidas em `data/`, converter coordenadas 3D para o plano 2D dos 9 mapas via `config/maps.json`, segmentar eventos temporalmente e calcular matrizes de densidade espacial e probabilidade bayesiana de vitória por posição.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, GEO-01, GEO-02, GEO-03, STAT-01, STAT-02
**Success Criteria** (what must be TRUE):
  1. Pipeline processa os 268 arquivos JSON em `data/` com Pydantic v2 sem interrupção por erros, tratando jogadores desconectados ou dados ausentes.
  2. Coordenadas de atacante (`playerLocations`) e vítima (`victimLocation`) são extraídas e projetadas no espaço normalizado $[0, 1]$ para os 9 mapas do dataset com calibração estática offline.
  3. Eventos de abate são segmentados dinamicamente nos 3 terços do round baseados em `roundResultTimeMillis`.
  4. Cálculo de vantagem posicional por KDE 2D com regularização Bayesiana (Beta prior) gera superfícies de probabilidade suaves e exporta artefatos compactos em Parquet e JSON.
**Plans**: TBD

### Phase 2: Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch
**Goal:** Disponibilizar uma interface web intuitiva e responsiva em Streamlit com gráficos Plotly interativos, filtros por mapa, lado e fase do round, KPIs consolidados e roteiro completo para a gravação do pitch.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Success Criteria** (what must be TRUE):
  1. Usuário pode navegar entre qualquer um dos 9 mapas e alternar dinamicamente entre visualizações de Abates (Mapa A), Mortes (Mapa B) e Vantagem Territorial (Winrate Bayesiano).
  2. Filtros de fase do round (Início, Meio, Fim, Total) e equipe/lado atualizam instantaneamente os mapas e as estatísticas.
  3. Painel analítico exibe KPIs globais do torneio (volume de abates, rounds e balanceamento de mapa) e tabela de eventos detalhados.
  4. README.md fornece instruções reproduzíveis de execução offline, detalhamento da calibração e guia estruturado para o vídeo pitch de 5 minutos até o prazo de 23/10/2026.
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana | 0/TBD | Not started | - |
| 2. Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch | 0/TBD | Not started | - |
