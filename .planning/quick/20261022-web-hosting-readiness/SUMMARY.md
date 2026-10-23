---
status: complete
date: 2026-10-22
task: web-hosting-readiness
tags: [deployment, hosting, streamlit-cloud, docker, ci-cd, pyproject]
---

# Quick Task Summary: Avaliação e Preparação para Hospedagem Web

**Objetivo:** Avaliar minuciosamente a prontidão do dashboard para hospedagem na nuvem e implementar as configurações estruturais para publicação em produção com zero fricção (Streamlit Community Cloud, Hugging Face Spaces, Render, Docker/VM).

## Diagnóstico Realizado

1. **Dependências (`requirements.txt`):**
   - Todas as dependências essenciais (`pydantic`, `pandas`, `numpy`, `scipy`, `pyarrow`, `streamlit`, `plotly`, `pytest`) estão devidamente declaradas com versões semânticas flexíveis e compatíveis.
   - Nenhuma biblioteca requer compilação nativa em C/C++ ou pacotes de sistema adicionais no momento do build.

2. **Dados e Portabilidade Offline (`data.zip`):**
   - O repositório contém `data.zip` (~13.4 MB) commitado e versionado, contendo tanto os artefatos pré-calculados em `data/processed/` quanto os 350 arquivos brutos dos torneios.
   - A extração automática foi blindada no `app.py` para rodar na importação do módulo, garantindo que mesmo em clones limpos (onde `data/` está no `.gitignore`), a plataforma de hospedagem descompacte os dados antes de qualquer leitura.

3. **Consumo de Memória e Performance:**
   - Consumo de memória medido do dashboard em execução: **~115 MB** de RSS.
   - O plano gratuito do Streamlit Community Cloud fornece 1.024 MB (1 GB). O app utiliza apenas **~11%** da cota disponível, prevenindo qualquer risco de crash por falta de memória (OOM killer).
   - O tempo de carregamento inicial é inferior a 2 segundos graças aos dados pré-processados e ao cache `@st.cache_data`.

4. **Isolamento de Segurança e Credenciais:**
   - Nenhum segredo, chave de API ou credencial está presente no repositório.
   - Nenhum caminho absoluto de sistema de arquivos local (`C:\`, `/home/...`) foi detectado — todas as referências utilizam `Path(__file__).resolve().parent`.
   - Os minimapas são convertidos em Data URIs Base64 offline, dispensando rotas estáticas externas.

## Melhorias Implementadas

1. **Configuração Nativa de Servidor e Tema (`.streamlit/config.toml`):**
   - Adicionado modo headless (`headless = true`), porta 8501 e desativação de coleta de telemetria.
   - Configurado o tema escuro oficial do VALORANT (`#0F1923`, `#FF4655`, `#ECE8E1`), impedindo cintilações claras durante o carregamento de componentes nativos na web.

2. **Compatibilidade com CI/CD e Pytest (`pyproject.toml` & `.python-version`):**
   - Adicionado `pyproject.toml` configurando `pythonpath = ["."]`. Agora `pytest` pode ser executado diretamente em pipelines de CI/CD sem exigir `python -m`.
   - Criado `.python-version` fixando Python 3.11 para plataformas PaaS.

3. **Containerização Portável (`Dockerfile` & `.dockerignore`):**
   - Criado `Dockerfile` leve com base `python:3.11-slim`, expondo a porta 8501 e com healthcheck nativo do Streamlit (`/_stcore/health`).
   - Criado `.dockerignore` para excluir caches e temporários do build.

4. **Blindagem no `app.py`:**
   - Chamada de `ensure_data_extracted()` movida para o carregamento do módulo, assegurando que o diretório `data/processed/` esteja disponível para qualquer importador, teste ou processo.

5. **Documentação de Deploy no `README.md`:**
   - Adicionada a seção **"7. Hospedagem na Web (Deploy em Nuvem / Produção)"** com instruções passo a passo para deploy em 1-clique no Streamlit Community Cloud e via Docker.

## Verificação e Resultados

- **Suíte de Testes:** 26/26 testes passando com 100% de sucesso via `pytest`.
- **Status de Hospedagem:** **100% Pronto para Deploy Web.**
