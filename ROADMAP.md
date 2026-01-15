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

## 🟦 EPIC 0 — Preparação e Convenções

**Objetivo:** estabelecer decisões estruturais e contratos antes da execução técnica.

- [x] 0.1 Definir naming convention e estrutura de tabelas
- [x] 0.2A Definir **proposta** de estratégia de chaves (`event_key`) *(pré-EPIC 1.1)*
- [ ] 0.2B Definir **critérios de ativação** da `event_key` *(pós-Silver)*
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
**Status:** 🟡 Em preparação  
**Pré-requisito:** EPIC P concluído e validado

- [ ] 1.1 Refatorar ingest para `execution_log_yyymmdd.csv` (delimiter `,`)
- [ ] 1.2 Adicionar lineage (`source_file`, `ingested_at`)
- [ ] 1.3 Garantir schema estável (tudo string, sem inferência)
- [ ] 1.4 Executar diagnósticos:
  - total de linhas
  - linhas por `registration_id`
  - evidência de explosão por join

---

## 🟩 EPIC 2 — Silver (Reconciliação Semântica)

**Objetivo:** tornar os dados confiáveis **e semanticamente interpretáveis**.

- [ ] 2.1 Criar `event_ts`
- [ ] 2.2 Normalizar vazios, strings e status
- [ ] 2.3 Derivar `event_family` (usando `ctx_*`)
- [ ] 2.4 Aplicar política MVP de deduplicação por família
- [ ] 2.5 Executar métricas antes/depois (impacto do tratamento)
- [ ] 2.6 Ativar `event_key` *(se critérios do EPIC 0.2B forem atendidos)*

---

## 🟨 EPIC 3 — Gold (Fato + Views Analíticas)

**Objetivo:** estruturar consumo analítico sem distorcer o grão.

- [ ] 3.1 Criar fato MVP wide: `gd_fact_execution_events`
- [ ] 3.2 Criar views analíticas:
  - `vw_execution_events`
  - `vw_daily_metrics`
  - `vw_registration_funnel`
- [ ] 3.3 (Opcional) Criar fatos por `event_family`

---

## 🟧 EPIC 4 — Star Schema + Semantic Model

**Objetivo:** consolidar modelo dimensional para BI e ML.

- [ ] 4.1 Dimensões MVP (date, user, org, registration, sco, meeting)
- [ ] 4.2 Estratégia para múltiplos papéis de usuário
- [ ] 4.3 Relacionamentos corretos no Semantic Model
- [ ] 4.4 Medidas DAX mínimas
- [ ] 4.5 Validação SQL × Power BI

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
