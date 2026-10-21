# Roadmap: Análise Geoespacial de Partidas de VALORANT

## Overview

Desenvolvimento enxuto de uma plataforma analítica geoespacial de ponta a ponta em 2 fases (Vertical MVP): primeiro estabelecendo o pipeline analítico 100% offline com ingestão resiliente dos 268 JSONs, priorizando o núcleo competitivo de **Ascent, Lotus e Haven (72.4% das partidas / 194 jogos)** para validação de projeção 2D e modelagem estatística de winrate via KDE com prior Bayesiano antes de estender aos demais mapas; em seguida entregando o dashboard interativo em Streamlit + Plotly com destaque para o trio principal, salvaguarda de baixa amostragem ($N < 10$) e documentação estruturada para o pitch de 5 minutos do hackathon.

## Phases

- [x] **Phase 1: Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana** - Ingestão de partidas, validação prioritária de projeção e KDE Bayesiano no trio Ascent, Lotus e Haven (72%), extensão para os demais mapas e exportação colunar Parquet/JSON 100% offline. (Concluída em 2026-10-21)
- [ ] **Phase 2: Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch** - Interface analítica completa com mapas Plotly, alternância de modos (Abates, Mortes, Vantagem), destaque para mapas prioritários, alerta de amostra reduzida ($N < 10$) e guia para vídeo pitch.

## Phase Details

### Phase 1: Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana

**Goal:** Processar os JSONs em `data/`, converter coordenadas 3D para 2D via `config/maps.json` 100% offline, validar o pipeline e a modelagem espacial de KDE e Winrate Bayesiano primeiramente para o trio principal (Ascent, Lotus e Haven - 194 partidas) e em seguida para os demais mapas, exportando Parquet e caches JSON.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, GEO-01, GEO-02, GEO-03, STAT-01, STAT-02
**Success Criteria** (what must be TRUE):

  1. Pipeline processa os arquivos JSON em `data/` com Pydantic v2 sem interrupção por erros, tratando jogadores desconectados ou dados ausentes.
  2. Coordenadas de atacante (`playerLocations`) e vítima (`victimLocation`) são extraídas e projetadas no espaço normalizado $[0, 1]$ 100% offline via `config/maps.json`, com o trio Ascent, Lotus e Haven validado primeiro com precisão milimétrica.
  3. Eventos de abate são segmentados dinamicamente nos 3 terços do round baseados em `roundResultTimeMillis`.
  4. Cálculo de densidades espaciais e vantagem posicional por KDE 2D com regularização Bayesiana (Beta prior) gera superfícies de probabilidade de vitória estáveis e exporta artefatos compactos em Parquet e JSON.
  5. Metadados de amostragem por mapa são gerados automaticamente, marcando mapas com menos de 10 partidas ($N < 10$) com flag de amostra reduzida.

**Plans**: 2 plans

Plans:
**Wave 1**

- [x] 01-01: Ingestão resiliente, extração de abates e projeção normalizada multi-mapa (tracer inicial em Ascent)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02: Modelagem estatística espacial (KDE 2D + Winrate Bayesiano com Beta prior) e exportação Parquet/JSON

### Phase 2: Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch

**Goal:** Disponibilizar uma interface web intuitiva e responsiva em Streamlit com gráficos Plotly interativos, navegação destacada para Ascent, Lotus e Haven, filtros por mapa, lado e fase do round, alerta estatístico para mapas $N < 10$, KPIs consolidados e roteiro do pitch de 5 minutos.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Success Criteria** (what must be TRUE):

  1. Usuário pode navegar entre mapas, com Ascent, Lotus e Haven em posição prioritária de destaque, alternando dinamicamente entre visualizações de Abates (Mapa A), Mortes (Mapa B) e Vantagem Territorial (Winrate Bayesiano).
  2. Mapas com amostragem reduzida ($N < 10$: Breeze, Pearl, Fracture) exibem aviso explícito de confiabilidade estatística limitada no dashboard.
  3. Filtros de fase do round (Início, Meio, Fim, Total) e equipe/lado atualizam instantaneamente os mapas e as estatísticas.
  4. Painel analítico exibe KPIs globais do torneio (volume de abates, rounds e balanceamento de mapa) e tabela de eventos detalhados.
  5. README.md fornece instruções reproduzíveis de execução 100% offline, detalhamento da calibração e guia estruturado para o vídeo pitch de 5 minutos até o prazo de 23/10/2026.

**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana | 2/2 | Complete | 2026-10-21 |
| 2. Dashboard Interativo em Streamlit + Plotly e Pacote de Pitch | 0/TBD | Not started | - |
