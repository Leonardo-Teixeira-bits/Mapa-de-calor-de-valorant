# Quick Task: Avaliação e Preparação do Dashboard para Hospedagem Web

**ID:** `20261022-web-hosting-readiness`  
**Objetivo:** Verificar e garantir que o dashboard (Streamlit + Plotly) esteja 100% pronto para ser hospedado na nuvem (Streamlit Community Cloud, Hugging Face Spaces, Render, Docker/VM), com configuração nativa de tema e servidor, suporte a CI/CD, containerização e documentação de deploy.

## Tarefas

1. **Configuração Nativa de Servidor e Tema Streamlit (.streamlit/config.toml):**
   - Criar `.streamlit/config.toml` com modo headless habilitado, desativação de telemetria e tema escuro VALORANT configurado nativamente para evitar oscilações ou inconsistências visuais em widgets na web.

2. **Garantia de Execução e CI/CD (pyproject.toml & .python-version):**
   - Criar `pyproject.toml` definindo `pythonpath = ["."]` para que `pytest` funcione diretamente tanto localmente quanto em pipelines de CI/CD de hospedagem.
   - Criar `.python-version` fixando Python 3.11 para plataformas de nuvem (Render, Streamlit Cloud, Pyenv).

3. **Containerização Portável (Dockerfile & .dockerignore):**
   - Criar `Dockerfile` otimizado (Python 3.11-slim) com healthcheck oficial do Streamlit (`/_stcore/health`) para deploy em plataformas de containers (Hugging Face Spaces, Render, Railway, AWS/GCP).
   - Criar `.dockerignore` para manter a imagem leve e limpa.

4. **Blindagem de Extração de Dados no app.py:**
   - Garantir que `ensure_data_extracted()` seja acionado na inicialização do módulo, assegurando que `load_maps_summary()`, testes de integração e execuções no Streamlit Cloud encontrem imediatamente `data/processed/` extraído do `data.zip`.

5. **Documentação de Deploy no README.md e Verificação Completa:**
   - Adicionar guia prático de deploy passo a passo no `README.md` para Streamlit Community Cloud e Docker.
   - Executar a suíte de testes (`pytest` e `python -m pytest`) e validar o consumo de memória e inicialização.
