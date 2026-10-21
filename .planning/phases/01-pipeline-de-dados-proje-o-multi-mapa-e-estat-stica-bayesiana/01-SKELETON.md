# Walking Skeleton — Análise Geoespacial de Partidas de VALORANT

**Phase:** 1
**Generated:** 2026-10-21

## Capability Proven End-to-End

O pipeline ingere arquivos JSON reais de partidas de VALORANT, extrai eventos de eliminações com posições de atacante e vítima, projeta as coordenadas 3D para o plano 2D normalizado via `config/maps.json`, segmenta os abates nas fases do round (Início, Meio e Fim) e calcula a superfície de densidade e vantagem territorial via KDE com prior Bayesiano, persistindo o resultado em Parquet e JSON offline.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Ingestão e Schemas | Pydantic v2 | Parsing ultrarrápido com validação tipada e tolerância a dados ausentes/desconexões (D-04, D-05) |
| Projeção Espacial | Calibração Estática Offline (`config/maps.json`) | Execução 100% offline sem chamadas a APIs externas, convertendo Unreal Units para $[0, 1]$ (D-06) |
| Segmentação Temporal | Terços proporcionais dinâmicos | Adapta-se à duração real de cada round baseada em `roundResultTimeMillis` (D-07) |
| Estatística de Vantagem | KDE 2D + Beta Prior Bayesiano | Elimina anomalias de winrate em células com poucos eventos através de regularização estatística (D-09) |
| Armazenamento | pandas + Parquet & JSON compactado | Alta performance colunar e cache pré-agregado sem dependência de SQLite ou DuckDB (D-10) |
| Estrutura de Código | Módulos desacoplados em `src/` | `models`, `ingestion`, `transformers`, `analytics`, `exporter` (D-01) |

## Stack Touched in Phase 1

- [ ] Project scaffold (estrutura modular `src/`, dependências em `pyproject.toml` ou `requirements.txt`, testes com `pytest`)
- [ ] Ingestão de dados — parsing de JSON com Pydantic v2 e captura de logs de erros
- [ ] Transformação matemática — projeção 2D multi-mapa e segmentador temporal dinâmico
- [ ] Modelagem estatística — matriz de densidade $100 \times 100$, SciPy `gaussian_kde` e Beta prior
- [ ] Persistência de saída — geração de `processed_events.parquet` e `density_winrate_cache.json`

## Out of Scope (Deferred to Later Slices)

- Interface gráfica interativa web em Streamlit e Plotly (Fase 2)
- Filtros visuais dinâmicos de mapa, time e jogador na UI (Fase 2)
- Vídeo pitch de 5 minutos e documentação final de apresentação do hackathon (Fase 2)
- Trajetórias completas de movimentação antes do plant (v2)

## Subsequent Slice Plan

Cada fase posterior adiciona uma fatia vertical sobre este esqueleto arquitetural comprovado:

- Phase 2: Dashboard Interativo em Streamlit + Plotly, seletor de mapas com destaque para o trio principal (Ascent, Lotus, Haven), aviso de baixa amostragem ($N < 10$) e pacote de pitch de 5 minutos.
