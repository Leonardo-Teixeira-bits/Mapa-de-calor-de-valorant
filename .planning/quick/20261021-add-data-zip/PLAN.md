---
task_id: quick-add-data-zip
status: in_progress
created_at: "2026-10-21T04:40:00Z"
description: Adicionar data.zip ao repositório, atualizar README.md com instruções de teste offline e garantir compatibilidade
---

# Quick Task: Adicionar data.zip e Atualizar README

## Objetivo
Adicionar `data.zip` contendo os dados brutos (`Rush Series Esquenta`, `Rush Series Esquenta 2`, `Rush Series Inclusivo`, `Univavá`) e os artefatos processados (`processed/`) ao repositório git. Atualizar o `README.md` documentando o arquivo compactado para permitir testes autônomos e 100% offline, levando em conta o contexto de continuidade pós interrupção por tokens.

## Tarefas
1. [x] Verificar integridade e estrutura do `data.zip` (336 partidas + artefatos em `data/processed`).
2. [ ] Ajustar `tests/test_ingestion.py` e `src/pipeline.py` para ignorar subdiretórios com terminação `.json` e garantir resiliência.
3. [ ] Adicionar rotina de extração automática transparente em `run_app.py` e `app.py` caso `data/processed/` não tenha sido descompactado manualmente.
4. [ ] Atualizar `README.md` destacando a presença do `data.zip`, comandos de descompactação e o contexto do pipeline.
5. [ ] Rodar suíte de 23 testes automatizados via `pytest` e certificar 100% de aprovação.
6. [ ] Registrar resumo em `SUMMARY.md`, atualizar `STATE.md` e commitar as alterações.
