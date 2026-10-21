<!-- GSD:project-start source:PROJECT.md -->

## Project

**Análise Geoespacial de Partidas de VALORANT**

Plataforma analítica e visual para exploração geoespacial e temporal de eventos de partidas competitivas de VALORANT, utilizando dados de 268 partidas (5.310 rounds e 37.441 abates) de torneios universitários (UNIVAVA). A aplicação realiza ingestão com tolerância a falhas, projeta coordenadas 3D da Unreal Engine em minimapas 2D normalizados com calibração estática offline, priorizando o núcleo competitivo de **Ascent, Lotus e Haven** (72% das partidas). Calcula densidades de abates/mortes por fase do round (início, meio, fim) e infere vantagem posicional (winrate suavizado por KDE com prior bayesiano), exibindo os resultados através de um dashboard interativo em Streamlit e Plotly.

**Core Value:** Fornecer visualizações geoespaciais interativas precisas e estatisticamente confiáveis de abates, mortes e vantagem territorial (winrate bayesiano) por fase do round e mapa, utilizando unicamente os dados locais de partidas em um pipeline rápido e leve em Python/pandas, com validação prioritária em Ascent, Lotus e Haven.

### Constraints

- **Tech Stack**: Python 3.11+, Pydantic v2, pandas, SciPy / scikit-learn, Streamlit, Plotly
- **Data Policy & Offline**: Execução 100% offline. Zero chamadas externas para dados de partida ou calibração (parâmetros estáticos estritamente em `config/maps.json`)
- **Map Phasing**: MVP focado e validado primeiro em Ascent, Lotus e Haven; mapas com $N < 10$ recebem badge de alerta estatístico
- **Timeline**: Entrega final do hackathon em 23/10/2026 às 23h59 BRT (protótipo funcional + vídeo pitch de até 5 minutos)
- **Roadmap**: Enxuto (1 a 2 fases focadas em valor direto e entrega ponta a ponta)

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
