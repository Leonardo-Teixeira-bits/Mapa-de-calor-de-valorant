# Quick Task: Alinhar Design Visual ao VALORANT.html e Mapear Itens de Abate

**ID:** `20261022-valorant-ui-and-weapon-mapping`  
**Objetivo:** Aproximar o design visual do dashboard (Streamlit + Plotly) da identidade oficial do VALORANT extraída de `VALORANT.html` (cores #FF4655, #0F1923, #ECE8E1, tipografia Tungsten/DIN Next) e mapear os códigos UUID dos itens de dano para nomes oficiais de armas e habilidades usando o dicionário baseado no gist de armas da comunidade.

## Tarefas

1. **Sintonização dos Códigos dos Itens de Abate com Nomes de Armas:**
   - Criar `config/weapons.json` com mapeamento consolidado UUID -> Nome Amigável (Vandal, Phantom, Classic, Operator, Outlaw, etc.).
   - Criar módulo de mapeamento `src/transformers/weapons.py` com fallback elegante para habilidades, faca, queda e spike.
   - Atualizar `app.py` para exibir nomes oficiais e legíveis na tabela de inspeção de abates e hovers.

2. **Refinamento Visual e Tipografia Inspirada no VALORANT.html:**
   - Injetar tipografia com fontes geométricas de estilo militar/tático (Bebas Neue / Oswald / DIN Next / Inter) via Google Fonts e CSS customizado no Streamlit.
   - Aplicar a paleta estrita do VALORANT (#0F1923, #FF4655, #ECE8E1, #1B2733, #768079, #00F5D4).
   - Estilizar cards de métricas (HUD-style), seletores e tabela analítica.

3. **Validação, Testes e Documentação:**
   - Criar testes unitários para o mapeador de armas em `tests/test_weapons.py`.
   - Executar a suíte completa de testes (`python -m pytest`).
   - Atualizar o `README.md` refletindo os novos recursos de design e inteligência de armas.
