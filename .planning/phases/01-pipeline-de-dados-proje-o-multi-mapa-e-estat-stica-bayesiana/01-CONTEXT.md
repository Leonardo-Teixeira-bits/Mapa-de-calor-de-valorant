# Phase 1: Pipeline de Dados, Projeção Multi-Mapa e Estatística Bayesiana - Context

**Gathered:** 2026-10-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Ingestão robusta em lote das 268 partidas de VALORANT (`data/`), projeção matemática 2D offline para todos os mapas via `config/maps.json` (com foco e validação prioritária em Ascent, Lotus e Haven — 72% das partidas), segmentação temporal dos rounds em 3 terços e modelagem estatística de densidade de abates/mortes e vantagem posicional (winrate suavizado por KDE com prior Bayesiano), exportando artefatos compactos em Parquet e JSON para o dashboard.

</domain>

<decisions>
## Implementation Decisions

### Priorização e Amostragem de Mapas
- **D-01 (Tier 1 MVP):** Validação primária e estrita do pipeline de ponta a ponta no trio **Ascent, Lotus e Haven** (194 partidas, 72.4% do dataset total).
- **D-02 (Extensão Tier 2):** Após o funcionamento comprovado do Tier 1, o pipeline processa os mapas restantes (Split, Sunset, Abyss, Summit).
- **D-03 (Salvaguarda $N < 10$):** Mapas com menos de 10 partidas no dataset (Breeze com 3 partidas e Pearl com 2 partidas) recebem flag explícita `low_sample_warning: true` nos metadados de exportação.

### Ingestão e Validação de Schema (Pydantic v2)
- **D-04:** Modelo Pydantic tolerante a falhas (skip em arquivos corrompidos com log de erros, campos nulos/opcionais tratados para desconexões e coaches).
- **D-05:** Extração dos eventos de kill a partir da estrutura real validada: `roundResults[].playerStats[].kills`. Coordenada da vítima via `victimLocation: {x, y}` e coordenada do atacante via busca em `playerLocations` onde `puuid == killer`. Suicídios/mortes por utilitários sem atacante identificado mantêm apenas a coordenada da vítima para o Mapa B.

### Projeção Espacial e Segmentação Temporal
- **D-06 (100% Offline):** Uso estrito das constantes locais em `config/maps.json` para projeção $X, Y \rightarrow X_{norm}, Y_{norm} \in [0.0, 1.0]$. Zero chamadas de rede.
- **D-07 (Segmentação Temporal Dinâmica):** Divisão proporcional da duração real de cada round (`roundResultTimeMillis`) em 3 fases: Início ($0 \le t < 1/3$), Meio ($1/3 \le t < 2/3$) e Fim ($2/3 \le t \le 1$). Fallback para 100.000 ms se duração for nula ou zero.

### Modelagem Estatística: Winrate Espacial Bayesiano com KDE
- **D-08:** Cálculo de densidade espacial de abates (Mapa A) e mortes (Mapa B) em grade normalizada ($100 \times 100$) ou KDE 2D Contínuo (SciPy `gaussian_kde`).
- **D-09:** Cálculo de vantagem territorial: taxa de vitória do round associada à posição do evento, regularizada por prior Bayesiano (Beta prior centrado na média global de vitórias $\approx 0.5$, com pseudocounts $\alpha_0, \beta_0$) combinado com suavização por KDE espacial. Isso elimina picos espúrios de 100% winrate em células com apenas 1 evento.

### Formato de Saída e Persistência
- **D-10 (Sem bancos SQL/DuckDB):** Persistência colunar leve em Parquet (`processed_events.parquet`) para os eventos brutos enriquecidos, e JSON compactado (`density_winrate_cache.json`) contendo as matrizes agregadas para carregamento instantâneo no Streamlit.

### the agent's Discretion
- Estrutura exata de classes e funções dentro de `src/` (ex: `src/models/`, `src/ingestion/`, `src/transformers/`, `src/analytics/`).
- Otimização de parâmetros do KDE (bandwidth via regra de Scott/Silverman).
- Formatação dos logs de execução e barra de progresso durante a ingestão do lote.

</decisions>

<canonical_refs>
## Canonical References

### Especificações e Regras do Projeto
- `planejamento.md` — Especificação técnica original com arquitetura modular, fórmulas de conversão e segmentação temporal.
- `config/maps.json` — Constantes oficiais de calibração espacial de todos os mapas de VALORANT (multipliers e scalars).
- `.planning/PROJECT.md` — Visão, restrições e regras do hackathon (prazo 23/10/2026, 100% offline, dados apenas dos JSONs).
- `.planning/REQUIREMENTS.md` — Requisitos v1 rastreáveis para DATA, GEO e STAT.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config/maps.json`: Dicionário completo de calibração para projeção 2D de todos os 9 mapas do dataset.
- `data/`: 268 arquivos JSON distribuídos entre Classificatórias 1 a 4 e Fase de Grupos.

### Established Patterns
- Python 3.11+ com tipagem estrita via Pydantic v2.
- Manipulação de dados com pandas / NumPy / SciPy.
- Execução isolada offline.

</code_context>

<specifics>
## Specific Ideas
- Validar primeiro com script de teste em Ascent (`/Game/Maps/Ascent/Ascent`), Lotus (`/Game/Maps/Jam/Jam`) e Haven (`/Game/Maps/Triad/Triad`).
- Exibir sumário detalhado ao final da ingestão com total de partidas válidas, total de abates extraídos por mapa e tempo total de processamento.

</specifics>

<deferred>
## Deferred Ideas
- Construção dos componentes de UI do Streamlit e Plotly (pertence à Fase 2).
- Vídeo de pitch de 5 minutos e documentação final de apresentação (Fase 2).

</deferred>

---
*Phase: 01-pipeline-de-dados-proje-o-multi-mapa-e-estat-stica-bayesiana*
*Context gathered: 2026-10-21*
