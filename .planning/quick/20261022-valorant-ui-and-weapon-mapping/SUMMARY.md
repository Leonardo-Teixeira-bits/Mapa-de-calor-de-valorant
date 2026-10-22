---
status: complete
date: 2026-10-22
task: valorant-ui-and-weapon-mapping
tags: [ui, valorant-brand, styling, typography, weapons, translation]
---

# Quick Task Summary: Design Visual VALORANT e Mapeamento de Armas

**Objetivo:** Alinhar o design do dashboard às diretrizes visuais do VALORANT (`VALORANT.html`) e mapear os identificadores UUID de itens de dano para nomes amigáveis baseados no gist de armas da comunidade.

## Conquistas

1. **Sintonização dos Itens de Dano / Armas:**
   - Adicionados `config/weapons.json` (do gist da comunidade com 18 armas base) e `config/weapons_map.json` (21 armas mapeadas incluindo Outlaw, Bandit, Warden e Melee).
   - Implementado o módulo `src/transformers/weapons.py` com o método `resolve_damage_item_name` e a função vetorial `format_damage_events`.
   - Mapeamento robusto com suporte a:
     - Armas clássicas: Vandal, Phantom, Operator, Classic, Sheriff, Outlaw, Spectre, etc.
     - Habilidades de Agentes: Habilidade 1 (Q), Habilidade 2 (C), Assinatura (E), Ultimate (X).
     - Tipos de Dano Especiais: Spike (Detonação), Dano de Queda, Esmagamento, Faca (Melee).
   - Cobertura com testes unitários em `tests/test_weapons.py` (3 novos testes, total de 26 na suíte).

2. **Identidade Visual e Tipografia Oficial (VALORANT):**
   - Fontes Web injetadas:
     - **Títulos e Métricas:** `Bebas Neue` / `Oswald` (equivalentes de display geométrico ao `Tungsten-Bold`).
     - **Labels, Badges e HUD:** `Rajdhani` (correspondente ao `DIN Next LT Pro`).
     - **Corpo e Textos:** `Inter`.
   - Paleta de Cores Estrita:
     - Background Central: Deep Dark Navy `#0F1923`
     - Barra Lateral: `#111822`
     - Cartões de Métricas (HUD): `#18222C` com borda lateral `#FF4655` (Valorant Coral) e hover tático.
     - Tipografia Primária: Off-White `#ECE8E1`
     - Metadados e Legendas: `#8B978F` / `#768079`
     - Badges de Tier: `#00F5D4` (Tier 1 Radiant Cyan), `#FFB703` (Tier 2 Tactical Amber), `#FF4655` (Tier 3 Crimson).
   - Tabela de Inspeção de Abates no `app.py`:
     - Colunas traduzidas e enriquecidas: `Round`, `Fase`, `Tempo (s)`, `Arma / Item`, `Time Atacante`, `Time Vítima`, `Vencedor`.
     - Tooltips dos pontos no mapa agora exibem a arma utilizada.

3. **Proteção de Dados e Privacidade no Git:**
   - Adicionados `VALORANT.html`, `valorant.html` e `VALORANT_files/` ao `.gitignore` para garantir que o snapshot HTML de referência nunca seja enviado ao repositório remoto.
   - Atualizado o `README.md` refletindo os 26 testes unitários e os módulos de catálogo de armas.

## Verificação

- Todos os 26 testes automatizados passaram com 100% de sucesso (`pytest -v`).
