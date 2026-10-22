---
task_id: quick-add-data-zip
status: complete
completed_at: "2026-10-21T04:47:00Z"
description: Inclusão do data.zip no repositório com suporte a auto-extração e atualização do README.md
---

# Quick Task Summary: Inclusão do data.zip e Atualização do README

## O que foi realizado
1. **Adicionado `data.zip` ao repositório**: O pacote compactado (~13.4 MB) contém as 336 partidas reais divididas nas pastas de torneios (`Rush Series Esquenta`, `Rush Series Esquenta 2`, `Rush Series Inclusivo` e `Univavá`) e os artefatos calculados em `data/processed/`.
2. **Auto-extração transparente**: Adicionado fallback automático em `run_app.py`, `app.py` e `src/pipeline.py` para detectar e descompactar o `data.zip` caso os dados ainda não estejam presentes no ambiente local.
3. **Resiliência aprimorada**: Ajustado o filtro de arquivos em `tests/test_ingestion.py` e `src/pipeline.py` com checagem explícita `f.is_file()` para evitar colisão com eventuais pastas.
4. **Atualização do README.md**: Seções de Quickstart e Estrutura do Projeto atualizadas com instruções de descompactação multiplataforma (PowerShell, Linux/macOS e Python) e destaque para teste autônomo e offline.
5. **Validação**: Todos os 23 testes automatizados executados e 100% aprovados (`23 passed in 6.15s`), além da validação ponta a ponta do pipeline.
