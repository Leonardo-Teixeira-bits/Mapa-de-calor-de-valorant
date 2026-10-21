---
phase: 01-pipeline-de-dados-proje-o-multi-mapa-e-estat-stica-bayesiana
plan: 01
subsystem: ingestion
tags: [pydantic, valorant, coordinates, projection, offline]

requires: []
provides:
  - Pydantic v2 schemas for Match, Round, Player, Kill and EnrichedKillEvent
  - CoordinateTransformer with offline projection using config/maps.json
  - Dynamic time segmenter (Early, Mid, Late)
  - MatchLoader with error boundary for corrupted JSONs and kill events extraction
affects: [analytics, exporter, dashboard]

actuals:
  tokens: 28000
  tasks: 3
  commits: 1

tech-stack:
  added: [pydantic, scipy, pyarrow, pytest]
  patterns: [error-boundary ingestion, offline coordinate projection, dynamic temporal thirds]

key-files:
  created:
    - src/models/match.py
    - src/models/kill.py
    - src/transformers/coordinates.py
    - src/transformers/time_segmenter.py
    - src/ingestion/loader.py
    - tests/test_tracer.py
    - tests/test_ingestion.py
    - tests/test_coordinates.py

key-decisions:
  - "D-01/D-05: Ingestão tolerante com Pydantic v2 capturando kills aninhados em playerStats com coordenadas de atacante e vítima"
  - "D-06: Projeção 100% offline parametrizada via config/maps.json para todos os 9 mapas"
  - "D-07: Segmentação temporal dinâmica por roundResultTimeMillis com fallback para 100.000 ms"

patterns-established:
  - "Ingestão resiliente que retorna None e loga em vez de quebrar a execução por JSON inválido"
  - "Normalização de coordenadas sempre mapeando para o intervalo [0.0, 1.0]"

requirements-completed: [DATA-01, DATA-02, DATA-03, GEO-01, GEO-02]

coverage:
  - id: D1
    description: "Tracer vertical end-to-end comprovando ingestão, projeção normalizada e segmentação temporal em Ascent"
    requirement: "DATA-01"
    verification:
      - kind: integration
        ref: "tests/test_tracer.py#test_tracer_ascent_end_to_end"
        status: pass
    human_judgment: false
  - id: D2
    description: "Carregador em lote com error boundary que ignora arquivos corrompidos e extrai eventos com vínculos de times e vencedor"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "tests/test_ingestion.py#test_load_corrupted_file_error_boundary"
        status: pass
    human_judgment: false
  - id: D3
    description: "Transformador multi-mapa offline com calibração estática para todos os 9 mapas (foco Ascent, Lotus e Haven)"
    requirement: "GEO-01"
    verification:
      - kind: unit
        ref: "tests/test_coordinates.py#test_coordinate_transformer_tier1_maps"
        status: pass
    human_judgment: false
  - id: D4
    description: "Segmentador temporal proporcional de rounds em 3 terços dinâmicos"
    requirement: "GEO-02"
    verification:
      - kind: unit
        ref: "tests/test_coordinates.py#test_time_segmenter"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-21
status: complete
---

# Phase 1: Plan 01-01 Summary

**Ingestão resiliente Pydantic v2, projeção espacial multi-mapa 100% offline e segmentação temporal dinâmica validadas por tracer vertical**

## Performance

- **Duration:** 10 min
- **Started:** 2026-10-21T01:13:00Z
- **Completed:** 2026-10-21T01:23:00Z
- **Tasks:** 3
- **Files modified/created:** 8

## Accomplishments
- Tracer end-to-end executado com sucesso sobre dados reais de Ascent de `data/`.
- Modelagem Pydantic v2 resiliente com suporte a desconexões e coaches sem falhas.
- Carregador de partidas com isolamento de erro por arquivo e extração achatada de kills.
- Transformador de coordenadas multi-mapa com suporte estático a todos os 9 mapas e validação estrita no Tier 1 (Ascent, Lotus, Haven).
- Segmentador temporal dinâmico por terços proporcionais do round ($0 \le t < 1/3$, $1/3 \le t < 2/3$, $t \ge 2/3$).

## Task Commits

1. **Task 1: Tracer end-to-end Ascent** - `feat(01-01): tracer ingestion and coordinates projection`
2. **Task 2: Pydantic v2 models and loader** - `feat(01-01): resilient match loader and kill extraction`
3. **Task 3: Multi-map transformer and time segmenter** - `feat(01-01): multi-map projection and temporal segmenter`

## Files Created/Modified
- `src/models/match.py` - Schemas Pydantic v2 de partida, rounds, jogadores e kills
- `src/models/kill.py` - Schema achatado `EnrichedKillEvent`
- `src/transformers/coordinates.py` - Transformador de coordenadas via `config/maps.json`
- `src/transformers/time_segmenter.py` - Classificador temporal em terços proporcionais
- `src/ingestion/loader.py` - Carregador em lote e extrator com error boundary
- `tests/test_tracer.py` - Teste de integração do tracer
- `tests/test_ingestion.py` - Testes unitários do carregador e tolerância a erros
- `tests/test_coordinates.py` - Testes unitários de projeção e segmentação temporal

## Decisions Made
- None - seguido o plano e o contexto à risca.

## Deviations from Plan
None - plan executed exactly as written.

## Next Phase Readiness
- Fundação de ingestão e projeção 100% testada e pronta para alimentar o cálculo de densidades, KDE e winrate Bayesiano no Plan 01-02.
