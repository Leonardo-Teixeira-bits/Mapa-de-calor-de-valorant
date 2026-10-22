#  Análise Geoespacial de Partidas de VALORANT 
### HACKATHON Valorant • Equipe Cão

<p align="center">
 <img width="1024" height="1024" alt="e1f07474-7807-4442-8c3c-1ed9a1c57cb5" src="https://github.com/user-attachments/assets/08c58ad7-f22b-443b-9f5c-60f4da478233" />
</p>

Plataforma analítica e visual para exploração geoespacial e temporal de eventos de partidas competitivas de VALORANT, desenvolvida para o Hackathon de Análise de Partidas Universitárias.

A aplicação processa **336 partidas reais** (5.068 rounds e 46.753 abates), projeta coordenadas 3D da Unreal Engine em minimapas 2D normalizados com calibração estática **100% offline**, priorizando o núcleo competitivo de **Ascent, Lotus e Haven** (71.6% do volume de dados). Modela densidades de abates e mortes por fase temporal do round e infere a vantagem territorial através de **Winrate suavizado por KDE com regularização Bayesiana (Beta prior)** em um dashboard interativo construído em **Streamlit e Plotly**.

---

##  Quickstart (Execução 100% Offline)

A aplicação foi projetada para operar em modo estritamente **offline**, sem nenhuma dependência de APIs externas em tempo de execução.

### 1. Pré-requisitos
* Python 3.11 ou superior
* Gerenciador de pacotes `pip`

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Base de Dados Inclusa e Testes Imediatos (`data.zip`)
Para permitir que qualquer avaliador teste a aplicação imediatamente **sem necessidade de baixar arquivos de fontes externas**, o repositório já inclui na raiz o arquivo compactado **`data.zip`** (~13 MB). Ele contém:
* Os artefatos pré-calculados (`data/processed/`) para abertura instantânea do dashboard.
* Todas as 336 partidas reais em JSON distribuídas nas pastas de torneios: `Rush Series Esquenta`, `Rush Series Esquenta 2`, `Rush Series Inclusivo` e `Univavá`.

> **Descompactação Automática:** Os scripts `run_app.py`, `app.py` e `src/pipeline.py` detectam e extraem automaticamente o `data.zip` caso a pasta `data/processed/` ainda não exista no ambiente.

Caso queira descompactar manualmente via linha de comando:
* **Windows (PowerShell):**
  ```powershell
  Expand-Archive -Path data.zip -DestinationPath . -Force
  ```
* **Linux / macOS:**
  ```bash
  unzip -o data.zip
  ```
* **Python (Multiplataforma):**
  ```bash
  python -m zipfile -e data.zip .
  ```

### 4. Execução do Pipeline de Dados (Opcional - Recomputação)
Processa os JSONs brutos da pasta `data/`, calcula as projeções e matrizes espaciais e exporta os artefatos otimizados para `data/processed/` (~12 segundos):
```bash
python src/pipeline.py
```

### 5. Inicialização do Dashboard Web
Inicia o dashboard interativo no navegador:
```bash
python run_app.py
```
*(Ou alternativamente: `streamlit run app.py`)*

### 6. Execução da Suíte de Testes
```bash
python -m pytest -v
```

---

## 📐 Metodologia Científica e Matemática

### 1. Projeção Espacial 3D para 2D
O motor de VALORANT utiliza coordenadas tridimensionais da *Unreal Engine*. A conversão para o plano cartesiano normalizado $[0.0, 1.0]$ do minimapa oficial utiliza os parâmetros estáticos definidos em `config/maps.json`:

$$\text{Norm}_X = (\text{World}_Y \times \text{xMultiplier}) + \text{xScalarToAdd}$$
$$\text{Norm}_Y = (\text{World}_X \times \text{yMultiplier}) + \text{yScalarToAdd}$$

*Nota: $\text{Norm}_X$ e $\text{Norm}_Y$ são limitados ao intervalo $[0.0, 1.0]$. A renderização inverte o eixo vertical para alinhar a origem $(0, 0)$ ao canto superior esquerdo da imagem.*

### 2. Segmentação Temporal Dinâmica
Cada round possui duração variável em função de desarmes ou eliminações antecipadas. A segmentação divide proporcionalmente a duração real do round ($\text{roundResultTimeMillis}$) em 3 fases:
* **Início (Early):** $0 \le t < \frac{1}{3} \cdot T_{\text{round}}$ (Disputa de primeiras posições e *first bloods*)
* **Meio (Mid):** $\frac{1}{3} \cdot T_{\text{round}} \le t < \frac{2}{3} \cdot T_{\text{round}}$ (Rotações, queima de utilitários e avanço nos bombsites)
* **Fim (Late):** $t \ge \frac{2}{3} \cdot T_{\text{round}}$ (Situações de pós-plant, desarmes e retakes sob pressão)

### 3. Vantagem Territorial com Regularização Bayesiana
Em células da grade espacial com poucas amostras (ex: 1 abate e 1 vitória), a taxa de vitória empírica não-regularizada atingiria falsos 100%. Para eliminar esse viés, aplicamos uma suavização espacial gaussiana seguida de um **Beta prior bayesiano** centrado na probabilidade neutra do jogo (`μ_global = 0.5`):

```text
                  Wins_smooth(x, y) + α₀
P̂(Win | x, y) = ──────────────────────────────────
                Total_smooth(x, y) + α₀ + β₀
```

$$\hat{P}(\text{Win} \mid x, y) = \frac{\text{Wins}_{\text{smooth}}(x, y) + \alpha_0}{\text{Total}_{\text{smooth}}(x, y) + \alpha_0 + \beta_0}$$

**Onde:**
* **α₀** = `μ_global × prior_weight = 0.5 × 5.0 = 2.5`
* **β₀** = `(1.0 - μ_global) × prior_weight = 0.5 × 5.0 = 2.5`
* **Wins_smooth** e **Total_smooth** resultam da aplicação de filtro gaussiano 2D com `σ = 1.8`.

Células não observadas permanecem no baseline neutro de 50%, enquanto regiões de alto tráfego convergem para sua taxa real empírica.

### 4. Tiers Competitivos e Salvaguarda Estatística
Os mapas são agrupados em 3 níveis no dashboard:
* **Tier 1 (MVP Competitivo):** **Ascent** (86 jogos), **Lotus** (82 jogos) e **Haven** (75 jogos). Somam **243 partidas e 33.497 abates (71.6% do dataset)**, validados prioritariamente com máxima densidade estatística.
* **Tier 2 (Mapas Estendidos):** **Split** (36 jogos), **Sunset** (24 jogos), **Abyss** (13 jogos), **Summit** (10 jogos).
* **Tier 3 (Amostra Reduzida - $N < 10$):** **Breeze** (5 jogos), **Pearl** (3 jogos), **Fracture** (2 jogos). Exibem aviso explícito de confiabilidade amostral limitada no dashboard (`low_sample_warning = True`).

### 5. Resolução Amigável de Itens e Armas de Abate
Os identificadores originais de telemetria da Unreal Engine (GUIDs/UUIDs) como `9C82E19D-4575-0200-1A81-3EACF00CF872` são traduzidos automaticamente para os nomes oficiais do arsenal (ex: **Vandal**, **Phantom**, **Operator**, **Classic**, **Sheriff**, **Outlaw**) e categorias de dano (Habilidades Q/C/E/X, Spike, Faca e Queda) utilizando o módulo `src/transformers/weapons.py` com dicionário estático offline.

---

##  Estrutura do Projeto

```
├── app.py                      # Dashboard interativo Streamlit
├── run_app.py                  # Script launcher facilitado
├── requirements.txt            # Dependências do projeto
├── config/
│   ├── maps.json               # Parâmetros de calibração espacial de todos os mapas
│   ├── weapons.json            # Catálogo oficial de armas do ecossistema VALORANT
│   └── weapons_map.json        # Mapeamento indexado UUID -> Nome Amigável de Arma
├── assets/
│   └── maps/                   # Imagens oficiais dos minimapas em alta resolução
├── data.zip                    # Pacote de dados compactado (~13MB, matches brutos + processados)
├── data/                       # Diretório de dados (extraído a partir de data.zip)
│   ├── processed/              # Artefatos gerados pelo pipeline
│   │   ├── processed_events.parquet    # Base colunar de 46.753 abates (snappy)
│   │   ├── density_winrate_cache.json  # Caches espaciais 100x100 pré-calculados
│   │   └── maps_summary.json           # Resumo de partidas, rounds, kills e tiers
│   ├── Rush Series Esquenta/   # JSONs brutos do torneio Rush Series Esquenta
│   ├── Rush Series Esquenta 2/ # JSONs brutos do torneio Rush Series Esquenta 2
│   ├── Rush Series Inclusivo/  # JSONs brutos do torneio Rush Series Inclusivo
│   └── Univavá/                # JSONs brutos das etapas classificatórias da UNIVAVA
├── src/
│   ├── ingestion/              # Ingestão em lote e tolerância a falhas (Pydantic v2)
│   ├── models/                 # Schemas tipados de Partida, Round e Abates
│   ├── transformers/           # Projeção, segmentador temporal e resolvedor de armas
│   ├── analytics/              # Densidade espacial e Winrate Bayesiano
│   ├── exporter/               # Exportador Parquet e gerador de caches
│   ├── visualization/          # Renderizador geoespacial Plotly sobre minimapas
│   └── pipeline.py             # Orquestrador de ponta a ponta
└── tests/                      # Suíte de 26 testes unitários e de integração
```

---

