# Análise Geoespacial de Partidas de VALORANT

## What This Is

Plataforma analítica e visual para exploração geoespacial e temporal de eventos de partidas competitivas de VALORANT, utilizando dados de 268 partidas (5.310 rounds e 37.441 abates) de torneios universitários (UNIVAVA). A aplicação realiza ingestão com tolerância a falhas, projeta coordenadas 3D da Unreal Engine em minimapas 2D normalizados para todos os mapas do dataset, calcula densidades de abates/mortes por fase do round (início, meio, fim) e infere vantagem posicional (winrate suavizado por KDE com prior bayesiano), exibindo os resultados através de um dashboard interativo em Streamlit e Plotly.

## Core Value

Fornecer visualizações geoespaciais interativas precisas e estatisticamente confiáveis de abates, mortes e vantagem territorial (winrate bayesiano) por fase do round e mapa, utilizando unicamente os dados locais de partidas em um pipeline rápido e leve em Python/pandas.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Ingestão resiliente em lote/streaming de 268 arquivos JSON (`data/`) via Pydantic v2 com tratamento de nulos e partidas incompletas
- [ ] Extração estruturada de eventos de Kill e Death a partir de `roundResults[].playerStats[].kills`, mapeando posição da vítima (`victimLocation`) e atacante (`playerLocations`)
- [ ] Sistema de projeção multi-mapa com suporte aos 9 mapas do dataset através de calibração estática offline em `config/maps.json`
- [ ] Segmentação temporal dos rounds em terços dinâmicos (Início: 0 a 1/3, Meio: 1/3 a 2/3, Fim: 2/3 a 1 da duração do round)
- [ ] Cálculo de vantagem posicional: taxa de vitória do round (winrate) espacial suavizada por Kernel Density Estimation (KDE 2D) com regularização/prior bayesiano
- [ ] Pipeline de dados e exportação colunar compacta em Parquet e cache JSON otimizado com pandas (sem SQLite/DuckDB)
- [ ] Dashboard interativo em Streamlit + Plotly com heatmaps de Abates, Mortes e Vantagem Posicional, filtros de mapa, time/lado, fase do round e jogadores
- [ ] Documentação completa no README citando fontes de calibração, instruções de execução e suporte para o vídeo pitch de 5 minutos

### Out of Scope

- Banco de dados relacional / OLAP (SQLite, DuckDB, PostgreSQL) — Usuário definiu uso estrito de pandas + Parquet/JSON para máxima simplicidade
- Frontend em React / Next.js / Deck.gl — Substituído por Streamlit + Plotly para garantir entrega ágil no prazo do hackathon
- Requisições a APIs externas em tempo de execução — Regra do hackathon: dados de partida exclusivamente dos JSONs locais fornecidos
- Processamento em tempo real / Streaming via WebSockets — Foco na análise histórica do lote do torneio

## Context

- **Dataset**: 268 partidas distribuídas em `Classificatória 1` (55), `Classificatória 2` (39), `Classificatória 3` (43), `Classificatória 4` (62) e `Fase de Grupos` (69), totalizando 5.310 rounds e 37.441 eliminações.
- **Mapas do Dataset**: Ascent (67), Lotus/Jam (66), Haven/Triad (61), Split/Bonsai (23), Sunset/Juliett (23), Abyss/Infinity (13), Summit/Plummet (10), Breeze/Foxtrot (3), Pearl/Pitt (2).
- **Estrutura Real do JSON**:
  - Partida: `matchInfo.mapId`, `matchInfo.matchId`, `teams`
  - Rounds: `roundResults[].roundResultTimeMillis`, `roundResults[].winningTeam`, `roundResults[].playerStats[]`
  - Kills: `playerStats[].kills[]` contendo `timeSinceRoundStartMillis`, `victimLocation: {x, y}` e `playerLocations[]` (onde `puuid == killer` fornece a coordenada do atacante).
- **Modelagem Estatística**:
  - O cálculo de winrate territorial bruto sofre de ruído amostral severo em zonas de baixa densidade (ex: 1 kill = 100% winrate). O uso de prior Bayesiano (Beta prior centrado na média global de vitórias) combinado com suavização espacial KDE gera uma superfície contínua e realista de controle de mapa.

## Constraints

- **Tech Stack**: Python 3.11+, Pydantic v2, pandas, SciPy / scikit-learn, Streamlit, Plotly
- **Data Policy**: Zero chamadas externas para dados de partida durante a execução (apenas parâmetros estáticos de calibração locais em `config/maps.json`)
- **Timeline**: Entrega final do hackathon em 23/10/2026 às 23h59 BRT (protótipo funcional + vídeo pitch de até 5 minutos)
- **Roadmap**: Enxuto (1 a 2 fases focadas em valor direto e entrega ponta a ponta)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Streamlit + Plotly para UI | Elimina complexidade de frontend separado, viabilizando mapas de calor interativos e controles em Python | — Pending |
| pandas + Parquet / JSON | Evita overhead de engine de banco de dados e atende perfeitamente ao volume de ~37k eventos | — Pending |
| Winrate por KDE + Prior Bayesiano | Corrige o viés amostral de regiões com poucos eventos, calculando vantagem real de posicionamento | — Pending |
| Calibração Multi-Mapa Offline (`config/maps.json`) | Suporta todos os 9 mapas presentes no torneio sem depender de internet em runtime | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-21 after initialization*
