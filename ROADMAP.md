# Roadmap — Customer App Learning Analytics (Revisado)

Este roadmap organiza a evolução do pipeline analítico considerando explicitamente as **fontes de verdade**, as **restrições do dado de origem** e o objetivo acadêmico de **Learning Analytics baseado em eventos (xAPI-inspired)**.

## Fontes de Verdade (Source of Truth)

1. **Fonte operacional derivada (imutável)**
   - `execution_log_yyyymmdd.csv` (ex.: `execution_log_20260107.csv`)
   - Dataset *wide* derivado de query SQL (não é “evento puro”)
2. **Fonte semântica/contratual (normativa)**
   - `contexts_lrs_event_logs.xlsx`
   - Abas-chave: `event_dictionary (andre)`, `local-collections-tables`, `lists`, `global-tables`
3. **Fonte de geração**
   - Query SQL que gera o `execution_log_yyyymmdd.csv`
   - Usada como evidência metodológica e explicação de limitações (não como dado do Lakehouse)

---

## 📍 Status Geral do Projeto

- EPIC P - Contextos e Dicionários: ✅ Concluído
- EPIC 1 - Bronze (Ingestão Raw Governada): ✅ Concluído
- EPIC 2 - Silver (Reconciliação Semântica): ✅ Concluído
- EPIC 3 - Gold (Fato + Views Analíticas): ✅ Concluído
- EPIC 4 - Gold Hardening & Semantic Coverage: 🔜
- EPIC 5 - Dashboard + Validação: 🔜
- EPIC 6 - Machine Learning Não Supervisionado (Exploratório): 🔜
- EPIC 7 - Documentação + TCC (Resultados Preliminares): 🔜

---

## 🟦 EPIC 0 — Preparação e Convenções

**Objetivo:** estabelecer decisões estruturais e contratos antes da execução técnica.

- [x] 0.1 Definir naming convention e estrutura de tabelas
- [x] 0.2A Definir **proposta** de estratégia de chaves (`event_key`) *(pré-EPIC 1.1)*
- [x] 0.2B Definir **critérios de ativação** da `event_key` *(implementado no EPIC 2.6)*
- [ ] 0.3 Definir política de partição e incremental load *(documental)*

---

## 🟪 EPIC P — Contextos e Dicionários (Contrato Semântico)

**Objetivo:** materializar o significado do log e reduzir ambiguidade semântica.

**Status:** ✅ Concluído  
**Contrato ativo:** `ctx_manifest v1`

- [x] P.1 Ingerir Excel normativo (1 aba = 1 tabela)
- [x] P.2 Criar ctx_event_fields
- [x] P.3 Criar ctx_event_categories
- [x] P.4 Criar ctx_list_items e local collections
- [x] P.5 Criar global tables
- [x] P.6 Validar PKs (heurística + overrides)
- [x] P.7 Gerar manifest versionado (manifest_ctx_v1.yml)

---

## 🟫 EPIC 1 — Bronze (Ingestão Raw Governada)

**Objetivo:** preservar fielmente as fontes derivadas, com evidência e lineage.

**Status:** ✅ DONE  
**Pré-requisito:** EPIC P concluído e validado

- [x] 1.1 Refatorar ingest para `execution_log_yyymmdd.csv` (delimiter `,`)
- [x] 1.2 Adicionar lineage (`source_file`, `ingested_at_utc`)
- [x] 1.3 Garantir schema estável (tudo string, sem inferência)
- [x] 1.4 Executar diagnósticos:
  - [x] total de linhas (101.802)
  - [x] linhas por `registration_id` (dataset wide e esparso)
  - [x] evidência de explosão por join (sem duplicidade estrutural)

> **Nota técnica:** Os diagnósticos confirmaram que o Bronze representa um dataset derivado, wide e esparso por design, adequado como camada raw governada, porém inadequado para consumo analítico direto. A reconciliação semântica e a normalização de ausências (`""` → `NULL`) devem ocorrer apenas no Silver.


---

## 🟩 EPIC 2 — Silver (Reconciliação Semântica)

**Objetivo:** tornar os dados confiáveis **e semanticamente interpretáveis**.

**Status:** ✅ DONE  
**Pré-requisito:** EPIC 1 concluído e validado

- [x] 2.1 Criar `event_ts`
- [x] 2.2 Normalizar vazios, strings e status
- [x] 2.3 Derivar `event_family` (usando `ctx_*`)
- [x] 2.4 Aplicar política MVP de deduplicação por família
- [x] 2.5 Executar métricas antes/depois (impacto do tratamento)
- [x] 2.6 Ativar `event_key` (gate explícito + evidência de unicidade)

📌 **Resultado:** tabela `silver_execution_log` criada, validada semanticamente e persistida.  
📌 Evidência técnica detalhada registrada em checkpoint dedicado.


---
## 🟨 EPIC 3 — Gold (Fato + Views Analíticas)

**Objetivo:** estruturar consumo analítico sem distorcer o grão.

**Status:** ✅ DONE  
**Pré-requisito:** EPIC 2 concluído e validado

- [x] **3.1 Gold / Modelagem**
  - gd_dim_event_category (view)
  - gd_fact_execution_events (view) — 1:1 com silver_execution_log
  - Derivação de category_id (parcial + controlada) + monitoramento
- [x] **3.2 Gold / Consumo**
  - vw_execution_events
  - vw_daily_metrics
  - vw_registration_funnel
  - vw_category_mapping_health

📘 Inventário oficial do modelo disponível em docs/catalog/OBJECT_REGISTRY.md.

---

## 🟧 EPIC 4 — Gold Hardening & Semantic Coverage

**Objetivo:** consolidar o Gold Layer com foco em governança, explicabilidade
e evolução segura da cobertura semântica para BI e ML, respeitando as
restrições do dado de origem.

- Tornar explícitas e auditáveis regras já existentes no Gold
- Qualificar e, quando possível, reduzir `category_unknown` com evidência
- Evitar inferência implícita ou regressão do modelo

**Status:** ⏳ IN PROGRESS  
**Pré-requisito:** EPIC 3 concluído e validado

---

### 4.1 Gold Hardening (Governança & Explicabilidade)

**Objetivo:** fortalecer o Gold v1 sem alterar grão, fatos ou histórico,
transformando regras implícitas em artefatos explícitos e versionáveis.

- [x] **4.1.1 Hardening de classificação de _meeting_ via regras explícitas**
  - Análise determinística de `meeting_group_code`
  - Identificação de códigos semanticamente estáveis
  - Declaração explícita de regras (`rule_id`, `rationale`, `source`)
  - Aplicação via overlay semântico (sem reprocessamento)
  - Auditoria por evento (`applied_rule_id`)
  - **Resultado:** hardening do modelo, sem redução de `category_unknown`
  - Evidência registrada em:
    - `CHECKPOINT_2026-01-24_EPIC-4.1.1.md`

Critério de aceite:
- Regras explícitas, rastreáveis e auditáveis
- Não regressão do Gold v1
- Overlay sem duplicação de linhas

---

### 4.2 Meeting Unknown Qualification & Semantic Coverage (orientado a evidência)

**Objetivo:** qualificar e, quando suportado por contexto adicional verificável,
reduzir `category_unknown` para eventos do tipo *meeting*, preservando rigor
metodológico e evitando inferência implícita.

- [x] **4.2.1 Qualificação estrutural de `meeting unknown` (sem redução)** — ✅ CONCLUÍDO
  - Análise empírica de eventos `meeting` com `category_unknown`
  - Identificação de causas predominantes de ausência semântica:
    - `meeting_code = 'CODIGO'` (placeholder estrutural)
    - ausência de `sco_categories` (falta de dicionário semântico)
  - Criação de subtipos explicativos de unknown:
    - `STRUCTURAL_CODE_PLACEHOLDER`
    - `NO_SCO_CATEGORIES`
  - Medição do limite superior teórico de *semantic recovery* (~33%)
  - Aumento de explicabilidade **sem alterar `category_id`**
  - Evidência documentada em:
    - `CHECKPOINT_2026-01-26_EPIC-4.2.1.md`

- [ ] **4.2.2 Semantic recovery via contexto externo (condicional)** — 🟨 STAND BY
  - Execução condicionada à obtenção de dicionário externo confiável
  - Investigação de metadados funcionais do sistema de origem
  - Criação de `ctx_` explícito somente quando houver evidência determinística
  - Aplicação via overlay auditável e reversível
  - Medição de impacto real na redução de `category_unknown`
  - Sem compromisso prévio de redução percentual

**Critérios de aceite:**
- Redução de `category_unknown` **apenas** quando suportada por evidência externa
- Regras explícitas, versionáveis, explicáveis e auditáveis
- Não regressão do Gold v1

---

### 4.3 Estratégia para múltiplos papéis de usuário
- Identificação de papéis por evento (ator vs sujeito)
- Modelagem consistente para análise de engajamento e desempenho

---

### 4.4 Relacionamentos corretos no Semantic Model
- Cardinalidade adequada entre fato e dimensões
- Direção de filtros consistente
- Eliminação de ambiguidade

---

### 4.5 Medidas DAX mínimas
- Métricas de volume, recorrência e cobertura
- Métricas educacionais básicas
- Validação cruzada com SQL

---

### 4.6 Validação SQL × Power BI
- Consistência entre views SQL e visualizações
- Checks de não-regressão
- Prontidão para BI e ML

---

## 🟥 EPIC 5 — Dashboard + Validação

**Objetivo:** validar pipeline de ponta a ponta.

- [ ] 5.1 Dashboard — Visão Geral (MVP)
- [ ] 5.2 Dashboard — Engajamento e Funil
- [ ] 5.3 Validação de performance (DirectLake / DirectQuery)

---

## 🟦 EPIC 6 — Machine Learning Não Supervisionado (Exploratório)

**Objetivo:** identificar padrões emergentes de comportamento de aprendizagem.

- [ ] 6.1 Definir unidade de análise (MVP: `user_id`)
- [ ] 6.2 Feature engineering (dataset agregado)
- [ ] 6.3 Normalização e preparação para ML
- [ ] 6.4 Clustering (K-Means baseline)
- [ ] 6.5 Avaliação e escolha do número de clusters
- [ ] 6.6 Interpretação educacional dos clusters
- [ ] 6.7 Visualização exploratória (PCA / UMAP)
- [ ] 6.8 Documentar metodologia e resultados exploratórios

---

## 🟦 EPIC 7 — Documentação + TCC (Resultados Preliminares)

**Objetivo:** transformar a base técnica em narrativa científica.

- [ ] 7.1 Documentar arquitetura e pipeline reprodutível (inclui fontes de verdade)
- [ ] 7.2 Redigir seção “Coleta e Preparação dos Dados”
- [ ] 7.3 Redigir seção “Análise Descritiva Preliminar”
- [ ] 7.4 Consolidar Resultados Preliminares (template do MBA + FDE/CEP)
- [ ] 7.5 Revisão final para submissão

---

## Observações

- O EPIC 6 é **exploratório e complementar**.
- Não há inferência causal ou predição supervisionada.
- O foco do trabalho permanece em **Learning Analytics baseado em eventos (xAPI-inspired)**.
