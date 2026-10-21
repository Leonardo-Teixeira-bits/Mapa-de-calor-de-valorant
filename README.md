#  Análise Geoespacial de Partidas de VALORANT 
### HACKATHON Valorant • Equipe Cão

<p align="center">
  <img width="600" alt="Equipe Cão Banner" src="https://github.com/user-attachments/assets/2d8ca820-ed77-45b7-85a0-f4a1578591f2" />
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

### 3. Execução do Pipeline de Dados
Processa os JSONs brutos da pasta `data/`, calcula as projeções e matrizes espaciais e exporta os artefatos otimizados para `data/processed/` (~12 segundos):
```bash
python src/pipeline.py
```

### 4. Inicialização do Dashboard Web
Inicia o dashboard interativo no navegador:
```bash
python run_app.py
```
*(Ou alternativamente: `streamlit run app.py`)*

### 5. Execução da Suíte de Testes
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
Em células da grade espacial com poucas amostras (ex: 1 abate e 1 vitória), a taxa de vitória empírica não-regularizada atingiria falsos 100%. Para eliminar esse viés, aplicamos uma suavização espacial gaussiana seguida de um **Beta prior bayesiano** centrado na probabilidade neutra do jogo ($\mu_{\text{global}} = 0.5$):

$$\hat{P}(\text{Win} \mid x, y) = \frac{\text{Wins}_{\text{smooth}}(x, y) + \alpha_0}{\text{Total}_{\text{smooth}}(x, y) + \alpha_0 + \beta_0}$$

onde:
* $\alpha_0 = \mu_{\text{global}} \times \text{prior\_weight} = 0.5 \times 5.0 = 2.5$
* $\beta_0 = (1.0 - \mu_{\text{global}}) \times \text{prior\_weight} = 0.5 \times 5.0 = 2.5$
* $\text{Wins}_{\text{smooth}}$ e $\text{Total}_{\text{smooth}}$ resultam de filtro gaussiano 2D com $\sigma = 1.8$.

Células não observadas permanecem no baseline neutro de 50%, enquanto regiões de alto tráfego convergem para sua taxa real empírica.

### 4. Tiers Competitivos e Salvaguarda Estatística
Os mapas são agrupados em 3 níveis no dashboard:
* **Tier 1 (MVP Competitivo):** **Ascent** (86 jogos), **Lotus** (82 jogos) e **Haven** (75 jogos). Somam **243 partidas e 33.497 abates (71.6% do dataset)**, validados prioritariamente com máxima densidade estatística.
* **Tier 2 (Mapas Estendidos):** **Split** (36 jogos), **Sunset** (24 jogos), **Abyss** (13 jogos), **Summit** (10 jogos).
* **Tier 3 (Amostra Reduzida - $N < 10$):** **Breeze** (5 jogos), **Pearl** (3 jogos), **Fracture** (2 jogos). Exibem aviso explícito de confiabilidade amostral limitada no dashboard (`low_sample_warning = True`).

---

##  Estrutura do Projeto

```
├── app.py                      # Dashboard interativo Streamlit
├── run_app.py                  # Script launcher facilitado
├── requirements.txt            # Dependências do projeto
├── config/
│   └── maps.json               # Parâmetros de calibração espacial de todos os mapas
├── assets/
│   └── maps/                   # Imagens oficiais dos minimapas em alta resolução
├── data/
│   ├── processed/              # Artefatos gerados pelo pipeline
│   │   ├── processed_events.parquet    # Base colunar de 46.753 abates (snappy)
│   │   ├── density_winrate_cache.json  # Caches espaciais 100x100 pré-calculados
│   │   └── maps_summary.json           # Resumo de partidas, rounds, kills e tiers
├── src/
│   ├── ingestion/              # Ingestão em lote e tolerância a falhas (Pydantic v2)
│   ├── models/                 # Schemas tipados de Partida, Round e Abates
│   ├── transformers/           # Projeção de coordenadas e segmentador temporal
│   ├── analytics/              # Densidade espacial e Winrate Bayesiano
│   ├── exporter/               # Exportador Parquet e gerador de caches
│   ├── visualization/          # Renderizador geoespacial Plotly sobre minimapas
│   └── pipeline.py             # Orquestrador de ponta a ponta
└── tests/                      # Suíte de 23 testes unitários e de integração
```

---

## 🎬 Roteiro Oficial do Vídeo Pitch (5 Minutos)

Guia minuto a minuto para a gravação da apresentação do Hackathon:

### Minuto 0:00 - 0:45 • Abertura, Gancho e o Problema
* **Apresentação:** "Olá comissão avaliadora! No VALORANT competitivo, saber *onde* o time adversário mata ou morre é básico. O verdadeiro diferencial tático está em responder: **qual posicionamento garante maior probabilidade real de vitória em cada segundo do round?**"
* **Desafio:** Dados brutos de partidas contêm ruídos, desconexões e mapas com poucas partidas que geram distorções ilusórias de 100% de winrate quando analisados de forma simplista.
* **Proposta:** Apresentamos a **Plataforma Geoespacial de VALORANT da UNIVAVA** — uma solução analítica rápida, 100% offline e com rigor estatístico bayesiano.

### Minuto 0:45 - 1:45 • Arquitetura e Engenharia de Dados
* **Volume:** Ingestão de 336 arquivos de partidas universitárias, totalizando mais de 5.000 rounds e 46.700 eliminações.
* **Resiliência e Desempenho:** Pipeline construído com Pydantic v2 com isolamento de falhas (*error boundary*).
* **Projeção Precisa:** Conversão matemática das coordenadas tridimensionais da Unreal Engine para o plano 2D normalizado via `maps.json` sem precisar de internet ou chamadas externas.
* **Exportação Otimizada:** Banco colunar em Parquet e caches em JSON que carregam em milissegundos no dashboard.

### Minuto 1:45 - 3:15 • Demonstração Prática do Dashboard
* **Destaque do Tier 1:** Mostrar o seletor destacando o trio competitivo de ouro: **Ascent, Lotus e Haven** (71.6% dos confrontos).
* **Alternância dos 3 Modos:**
  1. *Mapa de Abates (Kills):* Mostrar no mapa Ascent os ângulos dominantes de controle de Meio (Mid Courtyard) e A Main.
  2. *Mapa de Mortes (Deaths):* Contrastar imediatamente com os locais onde as vítimas caem (chokepoints e entradas de bombsites).
  3. *Vantagem Territorial (Winrate Bayesiano):* Destacar a escala divergente. Mostrar como certas áreas geram abates, mas não convertem rounds; enquanto posições como o Pátio de Ascent garantem mais de 65% de vitória.
* **Segmentação Temporal:** Filtrar por *Início (Early)* para ver disputas de abertura e alternar para *Fim (Late)* para visualizar o controle pós-plant.

### Minuto 3:15 - 4:15 • Rigor Científico e Salvaguarda Estatística
* **O Dilema de Baixa Amostragem:** Mostrar como mapas com poucas partidas (ex: Breeze com 5 jogos ou Pearl com 3 jogos) são tratados com transparência através do badge de alerta `$N < 10$`.
* **A Matemática que Protege:** Explicar sucintamente o **Beta Prior Bayesiano**: células com apenas 1 abate não explodem em 100% ou 0%, mas são puxadas de volta ao equilíbrio de 50%, prevenindo conclusões táticas precipitadas da comissão técnica.

### Minuto 4:15 - 5:00 • Impacto Competitivo e Conclusão
* **Valor para Times Universitários:** Coaches e analistas podem preparar vetos de mapa, desenhar execuções de round e ajustar posicionamentos defensivos com precisão cirúrgica.
* **Entrega Concluída:** Código 100% testado (23 testes automatizados aprovados), interface fluida, documentação completa e execução offline pronta para implantação.
* **Fechamento:** "Transformamos logs brutos em vantagem competitiva comprovada. Muito obrigado!"
