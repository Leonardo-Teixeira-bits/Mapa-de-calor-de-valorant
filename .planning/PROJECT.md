# Análise Geoespacial de Partidas de VALORANT

## What This Is

Plataforma analítica e visual para exploração geoespacial e temporal de eventos de partidas competitivas de VALORANT, utilizando dados de 268 partidas (5.310 rounds e 37.441 abates) de torneios universitários (UNIVAVA). A aplicação realiza ingestão com tolerância a falhas, projeta coordenadas 3D da Unreal Engine em minimapas 2D normalizados com calibração estática offline, priorizando o núcleo competitivo de **Ascent, Lotus e Haven** (72% das partidas). Calcula densidades de abates/mortes por fase do round (início, meio, fim) e infere vantagem posicional (winrate suavizado por KDE com prior bayesiano), exibindo os resultados através de um dashboard interativo em Streamlit e Plotly.

## Core Value

Fornecer visualizações geoespaciais interativas precisas e estatisticamente confiáveis de abates, mortes e vantagem territorial (winrate bayesiano) por fase do round e mapa, utilizando unicamente os dados locais de partidas em um pipeline rápido e leve em Python/pandas, com validação prioritária em Ascent, Lotus e Haven.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Ingestão resiliente em lote de 268 arquivos JSON (`data/`) via Pydantic v2 com tratamento de nulos e partidas incompletas
- [ ] Extração estruturada de eventos de Kill e Death a partir de `roundResults[].playerStats[].kills`, mapeando posição da vítima (`victimLocation`) e atacante (`playerLocations`)
- [ ] Sistema de projeção multi-mapa com suporte aos 9 mapas do dataset através de calibração estática offline em `config/maps.json` (priorizando Ascent, Lotus e Haven)
- [ ] Segmentação temporal dos rounds em terços dinâmicos (Início: 0 a 1/3, Meio: 1/3 a 2/3, Fim: 2/3 a 1 da duração do round)
- [ ] Cálculo de vantagem posicional: taxa de vitória do round (winrate) espacial suavizada por Kernel Density Estimation (KDE 2D) com regularização/prior bayesiano (Beta prior)
- [ ] Pipeline de dados e exportação colunar compacta em Parquet e cache JSON otimizado com pandas (sem SQLite/DuckDB)
- [ ] Tratamento de amostragem no dashboard: alerta visual de amostra reduzida para mapas com menos de 10 partidas (Breeze: 3, Pearl: 2)
- [ ] Dashboard interativo em Streamlit + Plotly com heatmaps de Abates, Mortes e Vantagem Posicional, filtros de mapa, time/lado, fase do round e jogadores
- [ ] Documentação completa no README citando fontes de calibração, instruções de execução 100% offline e suporte para o vídeo pitch de 5 minutos

### Out of Scope

- Banco de dados relacional / OLAP (SQLite, DuckDB, PostgreSQL) — Uso estrito de pandas + Parquet/JSON para máxima simplicidade e velocidade
- Frontend em React / Next.js / Deck.gl — Substituído por Streamlit + Plotly para garantir entrega ágil no prazo do hackathon
- Requisições a APIs externas em tempo de execução — Regra do hackathon: execução 100% offline, dados de partida exclusivamente dos JSONs locais em `data/`
- Processamento em tempo real / Streaming via WebSockets — Foco na análise histórica do lote do torneio

## Context

- **Dataset**: 268 partidas distribuídas em `Classificatória 1` (55), `Classificatória 2` (39), `Classificatória 3` (43), `Classificatória 4` (62) e `Fase de Grupos` (69), totalizando 5.310 rounds e 37.441 eliminações.
- **Hierarquia de Mapas por Volume**:
  - **Tier 1 (MVP Primário - 72.4% do dataset / 194 partidas)**:
    - `/Game/Maps/Ascent/Ascent` (Ascent): 67 partidas
    - `/Game/Maps/Jam/Jam` (Lotus): 66 partidas
    - `/Game/Maps/Triad/Triad` (Haven): 61 partidas
  - **Tier 2 (Extensão pós-MVP - 24.6% do dataset / 69 partidas)**:
    - `/Game/Maps/Bonsai/Bonsai` (Split): 23 partidas
    - `/Game/Maps/Juliett/Juliett` (Sunset): 23 partidas
    - `/Game/Maps/Infinity/Infinity` (Abyss): 13 partidas
    - `/Game/Maps/Plummet/Plummet` (Summit): 10 partidas
  - **Tier 3 (Amostra Pequena / Alerta no Dashboard - 1.9% do dataset / 5 partidas)**:
    - `/Game/Maps/Foxtrot/Foxtrot` (Breeze): 3 partidas
    - `/Game/Maps/Pitt/Pitt` (Pearl): 2 partidas
- **Estrutura Real do JSON**:
  - Partida: `matchInfo.mapId`, `matchInfo.matchId`, `teams`
  - Rounds: `roundResults[].roundResultTimeMillis`, `roundResults[].winningTeam`, `roundResults[].playerStats[]`
  - Kills: `playerStats[].kills[]` contendo `timeSinceRoundStartMillis`, `victimLocation: {x, y}` e `playerLocations[]` (onde `puuid == killer` fornece a coordenada do atacante).
- **Modelagem Estatística**:
  - O cálculo de winrate territorial bruto sofre de ruído amostral severo em zonas de baixa densidade (ex: 1 kill = 100% winrate). O uso de prior Bayesiano (Beta prior centrado na média global de vitórias) combinado com suavização espacial KDE gera uma superfície contínua e realista de controle de mapa.

## Constraints

- **Tech Stack**: Python 3.11+, Pydantic v2, pandas, SciPy / scikit-learn, Streamlit, Plotly
- **Data Policy & Offline**: Execução 100% offline. Zero chamadas externas para dados de partida ou calibração (parâmetros estáticos estritamente em `config/maps.json`)
- **Map Phasing**: MVP focado e validado primeiro em Ascent, Lotus e Haven; mapas com $N < 10$ recebem badge de alerta estatístico
- **Timeline**: Entrega final do hackathon em 23/10/2026 às 23h59 BRT (protótipo funcional + vídeo pitch de até 5 minutos)
- **Roadmap**: Enxuto (1 a 2 fases focadas em valor direto e entrega ponta a ponta)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Priorização Tier 1: Ascent, Lotus e Haven | Concentram 72% das partidas do torneio, garantindo robustez estatística máxima no MVP | — Pending |
| Salvaguarda de Baixa Amostragem ($N < 10$) | Breeze e Pearl recebem aviso no dashboard para evitar interpretações estatísticas distorcidas | — Pending |
| Streamlit + Plotly para UI | Elimina complexidade de frontend separado, viabilizando mapas de calor interativos e controles em Python | — Pending |
| pandas + Parquet / JSON | Evita overhead de engine de banco de dados e atende perfeitamente ao volume de ~37k eventos | — Pending |
| Winrate por KDE + Prior Bayesiano | Corrige o viés amostral de regiões com poucos eventos, calculando vantagem real de posicionamento | — Pending |
| Calibração Multi-Mapa Offline (`config/maps.json`) | Suporta todos os mapas do torneio sem depender de internet em runtime | — Pending |

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
*Last updated: 2026-10-21 after map prioritization alignment*
