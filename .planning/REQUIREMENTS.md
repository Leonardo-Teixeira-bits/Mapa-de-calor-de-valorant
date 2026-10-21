# Requirements: Análise Geoespacial de Partidas de VALORANT

**Defined:** 2026-10-21
**Core Value:** Fornecer visualizações geoespaciais interativas precisas e estatisticamente confiáveis de abates, mortes e vantagem territorial (winrate bayesiano) por fase do round e mapa, utilizando unicamente os dados locais de partidas em um pipeline rápido e leve em Python/pandas, priorizando Ascent, Lotus e Haven (72% das partidas).

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Data Ingestion & Schema Extraction

- [x] **DATA-01**: Pipeline de ingestão em lote dos JSONs em `data/` com Pydantic v2 resiliente a erros (ignora e loga arquivos malformatados sem abortar)
- [x] **DATA-02**: Extração completa de abates a partir de `roundResults[].playerStats[].kills`, mapeando coordenadas do atacante via `playerLocations` e da vítima via `victimLocation`
- [x] **DATA-03**: Extração e associação do desfecho do round (`winningTeam`), associação de time dos jogadores (`Red`/`Blue`), identificadores de mapa e duração real do round (`roundResultTimeMillis`)

### Geospatial & Temporal Transformation

- [x] **GEO-01**: Projeção e normalização de coordenadas ($X,Y \rightarrow [0, 1]$) 100% offline via `config/maps.json`, priorizando e validando primeiramente o núcleo de Ascent, Lotus e Haven (72% das partidas) antes de estender aos demais mapas
- [x] **GEO-02**: Segmentação temporal dinâmica de cada evento de kill em 3 terços proporcionais do round (Início: $0 \le t < 1/3$, Meio: $1/3 \le t < 2/3$, Fim: $2/3 \le t \le 1$)
- [x] **GEO-03**: Processamento e exportação dos dados tabulares limpos em formato Parquet colunar e caches JSON de alta performance utilizando pandas

### Statistical Modeling & Bayesian KDE

- [x] **STAT-01**: Cálculo de matrizes de densidade espacial (grid $100 \times 100$ e KDE 2D) para abates (Mapa A) e mortes (Mapa B) agregados por mapa e fase temporal, com validação primária no trio Ascent, Lotus e Haven
- [x] **STAT-02**: Cálculo de superfície de vantagem posicional (winrate espacial) aplicando KDE com regularização/prior Bayesiano (Beta prior ponderando a probabilidade de vitória do round em relação ao volume de eventos)

### Interactive Dashboard & Delivery

- [x] **UI-01**: Dashboard interativo desenvolvido em Streamlit com seletor de mapa (destacando o núcleo prioritário Ascent, Lotus e Haven), filtros de time/lado e seletor de fases temporais (Início, Meio, Fim, Geral)
- [x] **UI-02**: Renderização de mapas de calor interativos em Plotly com alternância suave entre Mapa de Abates, Mapa de Mortes e Mapa de Vantagem Territorial (Winrate Bayesiano)
- [x] **UI-03**: Painel analítico com KPIs da competição, inspeção de eventos e alerta visual proeminente de amostra reduzida para mapas com menos de 10 partidas ($N < 10$: Breeze, Pearl, Fracture)
- [x] **UI-04**: Documentação técnica completa no README.md com instruções de execução 100% offline, fontes de calibração e roteiro estruturado para o vídeo pitch de 5 minutos até 23/10/2026

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Analytics

- **ADV-01**: Filtro e análise de confrontos isolados por arma (`damageItem`) e utilitários de agentes
- **ADV-02**: Trajetória contínua de movimentação pré-plant a partir das amostras temporais de jogadores vivos
- **ADV-03**: Exportação de relatórios customizados em PDF/HTML para equipes técnicas de esports

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Banco de dados SQLite / DuckDB | Usuário optou estritamente por pandas + Parquet/JSON pela simplicidade e velocidade |
| Frontend em React / Next.js / Deck.gl | Substituído por Streamlit + Plotly para garantir entrega de alta qualidade dentro do prazo |
| Chamadas a APIs web externas em runtime | Regra obrigatória do hackathon: execução 100% offline, apenas dados de partidas dos JSONs locais |
| Suporte a streaming em tempo real / WebSockets | O escopo do projeto é focado no lote de partidas do torneio fornecido |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| DATA-03 | Phase 1 | Complete |
| GEO-01 | Phase 1 | Complete |
| GEO-02 | Phase 1 | Complete |
| GEO-03 | Phase 1 | Complete |
| STAT-01 | Phase 1 | Complete |
| STAT-02 | Phase 1 | Complete |
| UI-01 | Phase 2 | Complete |
| UI-02 | Phase 2 | Complete |
| UI-03 | Phase 2 | Complete |
| UI-04 | Phase 2 | Complete |

**Coverage:**
- v1 requirements: 12 total
- Completed: 12 (100%)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-21*
*Last updated: 2026-10-21 — 100% of v1 requirements completed*
