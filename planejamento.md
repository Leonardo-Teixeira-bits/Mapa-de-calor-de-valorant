Aqui está a especificação técnica detalhada e o planejamento arquitetural para o projeto de **Análise Geoespacial de Partidas de VALORANT**, estruturado para dar suporte total ao desenvolvimento por *vibecoding*.

## **1\. Análise dos Requisitos** 

### **Resumo do Problema e Objetivos**

Analisar múltiplos arquivos JSON de histórico de partidas de VALORANT para extrair dados geoespaciais e temporais de abates e mortes. O objetivo é mapear visualmente a densidade de eventos (onde jogadores matam e morrem) ao longo dos rounds, preparando uma base sólida de dados para um site interativo futuro.

### **Funcionalidades Obrigatórias (Phase 1 / MVP Data Pipeline)**

* **Ingestão Multi-JSON com Tolerância a Falhas:** Leitura em lote (*batch/streaming*) de múltiplos arquivos sem travar a execução por erros em arquivos isolados.  
* **Extração e Mapeamento de Eventos (Kills/Deaths):**  
  * **Mapa A (Abates):** Posição espacial do atacante (killer) no instante da eliminação.  
  * **Mapa B (Mortes):** Posição espacial da vítima (victimLocation) no instante da morte.  
* **Transformação de Coordenadas de Jogo para Minimapa:** Converter coordenadas da *Unreal Engine* ($X,Y$) para coordenadas normalizadas em pixels/percentual do mapa Ascent (${X}_{pct},{Y}_{pct}$).  
* **Segmentação Temporal de Rounds:** Agrupar eventos de cada round em 3 fases: **Início**, **Meio** e **Final**.  
* **Exportação de Dados Prontos para Web:** Gerar arquivos de saída estruturados (JSON pre-agregado ou SQLite/DuckDB) otimizados para consumo por frontend web sem necessidade de reprocessamento.

### **Funcionalidades Opcionais / Futuras (Phase 2 / Web App)**

* Interface gráfica interativa para alternar entre Mapa A/B e fases temporais.  
* Filtros dinâmicos por Jogador, Agente, Arma, Equipe/Lado (Atacante/Defensor) e ID da Partida.  
* Sobreposição do minimapa em alta resolução do Ascent.

### **Restrições Identificadas**

* **Ausência do Canvas/Imagem do Mapa no JSON:** O JSON contém apenas coordenadas brutas da engine; os *offsets* e a imagem do mapa Ascent devem ser parametrizados externamente.  
* **Disparidade de Formato/Campos Opcionais:** Partidas com *coaches*, desistências (*surrenders*) ou desconexões podem conter listas vazias ou nulas (null).

## **2\. Análise dos Dados (Estrutura do JSON de VALORANT)**

Com base no esquema padrão da API de partidas de VALORANT:

### **Campos Essenciais Mapeados**

> 1. **Identificação e Contexto da Partida:**  
   * matchInfo.matchId: ID único da partida.  
   * matchInfo.mapId: Caminho do mapa (ex: /Game/Maps/Ascent/Ascent).  
   * matchInfo.gameLengthMillis: Duração total da partida.  
> 2. **Dados Estruturados de Rounds (roundResults):**  
   * roundNum: Índice do round.  
   * roundResultTimeMillis: Duração exata do round em milissegundos.  
> 3. **Eventos de Abate (playerKills dentro de cada round):**  
   * timeSinceRoundStartMillis: Timestamp exato em que o abate ocorreu a partir do início do round.  
   * killer: PUUID/Tag do jogador que realizou o abate.  
   * victim: PUUID/Tag do jogador abatido.  
   * victimLocation: Objeto { x: int, y: int } referente à **posição da vítima**.  
   * playerLocations: Lista contendo a posição de todos os jogadores vivos no momento da morte.  
     * *Extração do Atacante:* Localiza-se na lista o item onde puuid \== killer para obter a coordenada { x, y } do **atacante**.

### **Informações Ausentes ou Dependências Externas**

* **Parâmetros de Calibragem do Minimapa (Ascent):** A API do VALORANT não fornece as constantes de projeção geográfica no JSON da partida. É necessário utilizar o parâmetro oficial de conversão de Ascent:  
  * xMultiplier \= 0.00007  
  * yMultiplier \= \-0.00007  
  * xScalarToAdd \= 0.81389  
  * yScalarToAdd \= 0.524241

## **3\. Perguntas Pendentes para o Usuário**

> 1. **Volume Esperado de Dados:** Quantos arquivos JSON são previstos para o lote padrão do MVP (ex: 10 partidas \~ 5MB ou 10.000 partidas \~ 5GB)?  
> 2. **Atribuição em Suicídios/Abates de Utilitários sem Atacante Direto:** Quando killer for nulo ou igual a victim (ex: morte por queda ou dano de área próprio), o evento deve ser desconsiderado do Mapa A (Abates)?

## **4\. Comparação e Seleção de Tecnologias**

| Componente | Opções Avaliadas | Escolha Recomendada | Justificativa |
| :---- | :---- | :---- | :---- |
| **Linguagem / Processing** | Python vs Node.js/TypeScript vs Rust | **Python 3.11+** | Excelente ecossistema de dados (Pydantic, Polars/Pandas), altíssima compatibilidade e velocidade de escrita com *vibecoding* (LLMs geram código Python limpo e tipado com facilidade). |
| **Validação de Schema** | Manual/Dicts vs Pydantic | **Pydantic v2** | Tipagem estrita, parsing ultrarrápido em C e tratamento nativo de campos ausentes/nulos com mensagens de erro claras. |
| **Data Engine** | Pandas vs Polars vs DuckDB | **DuckDB \+ Polars** | Permite consultas SQL/Dataframe direto sobre arquivos JSON sem estourar memória RAM, facilitando agregações temporais e espaciais. |
| **Formato de Saída (Web)** | PostgreSQL/PostGIS vs GeoJSON / SQLite | **SQLite / Parquet \+ JSON Estático** | Elimina a necessidade de subir servidores de banco de dados na Phase 1; possibilita exportar arquivos JSON pré-calculados para a Web. |
| **Web Frontend (Futuro)** | React \+ Leaflet/Deck.gl vs Streamlit | **Next.js (React) \+ Deck.gl / Chart.js** | Deck.gl renderiza mapas de calor baseados em WebGL com alta performance para milhares de pontos espaciais. |
| **Testes** | Unittest vs Pytest | **Pytest** | Padrão da indústria, sintaxe simples e suporte nativo a *fixtures* de JSONs de teste. |

## **5\. Arquitetura Recomendada do Sistema**

┌────────────────────────┐      ┌──────────────────────────┐      ┌─────────────────────────┐  
│ Multiples JSONs        │ ───► │ Data Pipeline (Python)   │ ───► │ Storage Outputs         │  
│ (Partidas / Rounds)    │      │ \- Ingestão & Pydantic    │      │ \- processed\_events.sqlite│  
└────────────────────────┘      │ \- Conversor Coordenadas  │      │ \- heatmap\_cache.json    │  
                                │ \- Time-Segmenter Engine  │      └────────────┬────────────┘  
                                └──────────────────────────┘                   │  
                                                                               ▼  
                                                                  ┌─────────────────────────┐  
                                                                  │ Web Dashboard (Futuro)  │  
                                                                  │ Next.js \+ Deck.gl       │  
                                                                  └─────────────────────────┘

### **Divisão de Módulos (Backend Python)**

> 1. models/: Definição dos Schemas de Dados usando Pydantic.  
> 2. transformers/:  
   * coordinate\_converter.py: Projeção ($X,Y\rightarrow Minima{p}_{x,y}$).  
   * time\_segmenter.py: Classificação do momento do round.  
> 3. ingestion/: Leitor de arquivos com tratamento de exceções (*error boundary* por arquivo).  
> 4. exporter/: Gerador de base SQLite/JSON compactado.

## **6\. Estratégia de Análise**

### **6.1. Conversão de Coordenadas**

Para transformar as coordenadas puras da Unreal Engine ($X,Y$) para a grade normalizada ($0.0\rightarrow 1.0$) do minimapa de **Ascent**:

$${X}_{norm}=(Y\cdot xMultiplier)+xScalarToAdd$$

$${Y}_{norm}=(X\cdot yMultiplier)+yScalarToAdd$$

*(A inversão de $X$ e $Y$ na fórmula reflete a rotação dos eixos da engine do jogo em relação à imagem do minimapa).*

### **6.2. Segmentação Temporal dos Rounds**

A regra de divisão será baseada na duração real do round (roundResultTimeMillis), dividida dinamicamente em 3 terços proporcionais (${T}_{max}=roundResultTimeMillis$):

* **Início do Round (Early Game):** $0\leq t<\frac{1}{3}{T}_{max}$ (Tipicamente confrontos de dominância de mapa/orbes).  
* **Meio do Round (Mid Game):** $\frac{1}{3}{T}_{max}\leq t<\frac{2}{3}{T}_{max}$ (Execuções de site, rotações e *retakes* iniciais).  
* **Final do Round (Late Game):** $\frac{2}{3}{T}_{max}\leq t\leq {T}_{max}$ (Pós-plant, clutches e tempo esgotando).

**Tratamento de Exceções Temporais:** Se roundResultTimeMillis for ausente ou zero, adota-se o padrão competitivo de VALORANT ($100.000ms$ para fase de compra/combate base).

### **6.3. Estratégia para o Mapa de Calor**

* **Grade de Densidade Espacial (Grid Aggregation):** O mapa do jogo será dividido em uma grade (*grid*) de $100\times 100$ células. Cada evento (${X}_{norm},{Y}_{norm}$) é agrupado em sua respectiva célula, contando a frequência de ocorrências. Isso reduz o tamanho do JSON transferido para a Web em até 90% se comparado ao envio de pontos brutos.

## **7\. Plano de Implementação Incremental**

* \[ \] **Etapa 1: Modelagem e Parsing Seguro**  
  * Criar modelos Pydantic tolerantes a campos None/ausentes.  
  * *Critério de Aceite:* Script processa um lote de JSONs com erros sem interromper a execução e gera log de arquivos corrompidos.  
* \[ \] **Etapa 2: Mapeamento Geográfico e Testes de Projeção**  
  * Criar o módulo de conversão ($X,Y\rightarrow Minima{p}_{x,y}$).  
  * *Critério de Aceite:* Teste unitário confirmando que coordenadas de kills no Bomb B caem dentro do quadrante correto do minimapa de Ascent.  
* \[ \] **Etapa 3: Segmentador Temporal de Eventos**  
  * Implementar módulo de classificação de tempo proporcional do round.  
  * *Critério de Aceite:* Função classifica corretamente kills ocorridos aos 10s, 45s e 80s em um round de 90s.  
* \[ \] **Etapa 4: Exportador de Agregações (SQLite / JSON Cache)**  
  * Salvar os dados extraídos estruturados em SQLite e exportar o JSON consolidado para os Mapas A e B.  
  * *Critério de Aceite:* Arquivo JSON exportado contendo as frequências por célula para os filtros: \[Mapa A|Mapa B\] $\times$ \[Início|Meio|Fim|Total\].

## **8\. Estratégia de Testes e Validação**

> 1. **Testes Unitários (pytest):**  
   * Validação matemática da conversão de coordenadas com pontos de borda ($0,0$, limites do mapa).  
   * Validação da regra temporal para rounds normais ($100s$), curtos ($20s$ \- rendição) e longos.  
> 2. **Testes de Integração com Dados Mapeados:**  
   * Ingestão do JSON fornecido anteriormente na conversa para validar se o total de Kills/Deaths bate exatamente com o placar final do resumo ($17$ kills do jogador top fragger, etc.).

## **9\. Recomendação Final de Stack**

* **Linguagem:** Python 3.11+  
* **Parsing / Validação:** Pydantic v2  
* **Análise de Dados:** DuckDB / Polars  
* **Testes Automatizados:** Pytest  
* **Formato de Entrega de Dados (para Web):** SQLite \+ JSONs pré-calculados por *grid* de calor.

## **10\. Próximas Ações**

Para dar início imediato ao desenvolvimento do código (Etapa 1 do plano incremental), confirme se o plano atende a suas necessidades e solicite a criação do primeiro módulo.