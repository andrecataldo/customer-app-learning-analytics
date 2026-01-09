# Roadmap — Customer App Learning Analytics

Este roadmap organiza a evolução do pipeline analítico, da ingestão dos dados
até os Resultados Preliminares do TCC, incluindo uma etapa exploratória de
Machine Learning não supervisionado.

---

## 🟦 EPIC 0 — Preparação e Convenções

Objetivo: estabelecer padrões e decisões estruturais antes da evolução técnica.

- [x] 0.1 Definir naming convention e estrutura de tabelas  
  (bronze / silver / gold / dims / views)
- [ ] 0.2 Definir estratégia de chaves (event_key)
- [ ] 0.3 Definir política de partição e incremental load

---

## 🟪 EPIC P — Contextos e Dicionários (Periféricos)

Objetivo: materializar o contrato semântico do log de eventos.

- [ ] P.1 Ingerir planilha “[CONTEXTS] lrs-event-logs” no Lakehouse
- [ ] P.2 Criar tabelas de dicionário de eventos e campos
- [ ] P.3 Criar tabelas de listas (status, tipos, skills, perguntas)
- [ ] P.4 Criar views de apoio (`vw_event_dictionary`, etc.)

---

## 🟫 EPIC 1 — Bronze (Ingestão Raw)

Objetivo: ingestão fiel e governada do `execution_log_yyymmdd.csv`.

- [ ] 1.1 Refatorar ingest para `execution_log_yyymmdd.csv` (delimiter `;`)
- [ ] 1.2 Adicionar colunas de linhagem (`source_file`, `ingested_at`)
- [ ] 1.3 Tratar registros corrompidos (se aplicável)

---

## 🟩 EPIC 2 — Silver (Limpeza e Tipagem)

Objetivo: tornar os dados confiáveis, tipados e semanticamente consistentes.

- [ ] 2.1 Criar `event_ts` a partir de `event_date` + `event_time`
- [ ] 2.2 Normalizar strings, vazios e status/tipos
- [ ] 2.3 Garantir tipagem mínima e schema estável
- [ ] 2.4 Gerar `event_key` (hash determinístico)
- [ ] 2.5 Executar checks de qualidade de dados (DQ)

---

## 🟨 EPIC 3 — Gold (Fato + Views)

Objetivo: estruturar o consumo analítico.

- [ ] 3.1 Criar fato base (MVP wide): `gd_fact_execution_events`
- [ ] 3.2 Criar views analíticas mínimas:
  - `vw_execution_events`
  - `vw_daily_metrics`
  - `vw_interaction_metrics`
  - `vw_registration_funnel`
- [ ] 3.3 (Opcional) Criar fatos por família de avaliação

---

## 🟧 EPIC 4 — Star Schema + Semantic Model

Objetivo: consolidar o modelo dimensional e o Semantic Model.

- [ ] 4.1 Criar dimensões MVP (date, user, organization, registration, interaction, sco, meeting)
- [ ] 4.2 Definir estratégia para múltiplos papéis de usuário
- [ ] 4.3 Criar relacionamentos corretos no Semantic Model
- [ ] 4.4 Criar hierarquias e medidas DAX mínimas
- [ ] 4.5 Validar SQL Analytics × Power BI

---

## 🟥 EPIC 5 — Dashboard + Validação

Objetivo: validar o pipeline de ponta a ponta via visualização.

- [ ] 5.1 Dashboard — Visão Geral (MVP)
- [ ] 5.2 Dashboard — Engajamento e Funil
- [ ] 5.3 Validação de performance (DirectLake / DirectQuery)

---

## 🟦 EPIC 6 — Machine Learning Não Supervisionado (Exploratório)

Objetivo: identificar padrões emergentes de comportamento de aprendizagem.

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

Objetivo: transformar a base técnica em narrativa científica.

- [ ] 7.1 Documentar arquitetura e pipeline reprodutível
- [ ] 7.2 Redigir seção “Coleta e Preparação dos Dados”
- [ ] 7.3 Redigir seção “Análise Descritiva Preliminar”
- [ ] 7.4 Consolidar Resultados Preliminares (template do MBA)
- [ ] 7.5 Revisão final para submissão

---

## 📌 Observações finais

- O EPIC 6 é **exploratório e complementar**.
- Não há inferência causal ou predição supervisionada.
- O foco do trabalho permanece em **Learning Analytics baseado em eventos (xAPI-inspired)**.
