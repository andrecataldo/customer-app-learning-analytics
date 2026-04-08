# Roadmap - Customer App Learning Analytics (Atualizado)

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
- EPIC 4 - Gold Hardening & Semantic Coverage: ✅ DONE (v1) / 🟨 4.2.2 STAND BY
- EPIC 5 - Dashboard + Validação: 💤 BACKLOG
- EPIC 6 - Machine Learning Não Supervisionado (Exploratório): ⚙️ WIP avançado
- EPIC 7 - TCC (Resultados Finais) + Documentação Final: ⚙️ WIP avançado

---

## 🟦 EPIC 0 - Preparação e Convenções

**Objetivo:** estabelecer decisões estruturais e contratos antes da execução técnica.

- [x] 0.1 Definir naming convention e estrutura de tabelas
- [x] 0.2A Definir **proposta** de estratégia de chaves (`event_key`) *(pré-EPIC 1.1)*
- [x] 0.2B Definir **critérios de ativação** da `event_key` *(implementado no EPIC 2.6)*
- [ ] 0.3 Definir política de partição e incremental load *(documental)*

---

## 🟪 EPIC P - Contextos e Dicionários (Contrato Semântico)

**Objetivo:** materializar o significado do log e reduzir ambiguidade semântica.  
**Status:** ✅ Concluído  
**Contrato ativo:** `ctx_manifest v1`

- [x] P.1 Ingerir Excel normativo (1 aba = 1 tabela)
- [x] P.2 Criar ctx_event_fields
- [x] P.3 Criar ctx_event_categories
- [x] P.4 Criar ctx_list_items e local collections
- [x] P.5 Criar global tables
- [x] P.6 Validar PKs (heurística + overrides)
- [x] P.7 Gerar manifest versionado (`manifest_ctx_v1.yml`)

---

## 🟫 EPIC 1 - Bronze (Ingestão Raw Governada)

**Objetivo:** preservar fielmente as fontes derivadas, com evidência e lineage.  
**Status:** ✅ DONE

- [x] 1.1 Refatorar ingest para `execution_log_yyymmdd.csv`
- [x] 1.2 Adicionar lineage (`source_file`, `ingested_at_utc`)
- [x] 1.3 Garantir schema estável (tudo string, sem inferência)
- [x] 1.4 Executar diagnósticos estruturais e de completude

> **Nota técnica:** O Bronze representa um dataset derivado, wide e esparso por design, adequado como camada raw governada, porém inadequado para consumo analítico direto.

---

## 🟩 EPIC 2 - Silver (Reconciliação Semântica)

**Objetivo:** tornar os dados confiáveis **e semanticamente interpretáveis**.  
**Status:** ✅ DONE

- [x] 2.1 Criar `event_ts`
- [x] 2.2 Normalizar vazios, strings e status
- [x] 2.3 Derivar `event_family`
- [x] 2.4 Aplicar política MVP de deduplicação por família
- [x] 2.5 Executar métricas antes/depois
- [x] 2.6 Ativar `event_key`

📌 Resultado: `silver_execution_log` criada e validada semanticamente.

---

## 🟨 EPIC 3 - Gold (Fato + Views Analíticas)

**Objetivo:** estruturar consumo analítico sem distorcer o grão.  
**Status:** ✅ DONE

- [x] 3.1 Gold / Modelagem
  - `gd_dim_event_category`
  - `gd_fact_execution_events`
- [x] 3.2 Gold / Consumo
  - `vw_execution_events`
  - `vw_daily_metrics`
  - `vw_registration_funnel`
  - `vw_category_mapping_health`

📘 Inventário oficial do modelo disponível em `docs/catalog/OBJECT_REGISTRY.md`.

---

## 🟧 EPIC 4 - Gold Hardening & Semantic Coverage

**Objetivo:** consolidar o Gold com foco em governança, explicabilidade e evolução segura da cobertura semântica.  
**Status:** ✅ DONE (v1) / 🟨 4.2.2 STAND BY

### 4.1 Gold Hardening (Governança & Explicabilidade)
- [x] 4.1.1 Hardening de classificação de `meeting` via regras explícitas

### 4.2 Meeting Unknown Qualification & Semantic Coverage
- [x] 4.2.1 Qualificação estrutural de `meeting unknown` (sem redução)
- [ ] 4.2.2 Semantic recovery via contexto externo (condicional)

### 4.3 Estratégia para múltiplos papéis de usuário
- [ ] Modelagem futura, se necessária

### 4.4 Relacionamentos corretos no Semantic Model
- [ ] Backlog

### 4.5 Medidas DAX mínimas
- [ ] Backlog

### 4.6 Validação SQL × Power BI
- [ ] Backlog

---

## 🟥 EPIC 5 - Dashboard + Validação

**Objetivo:** validar pipeline de ponta a ponta via BI.  
**Status:** 💤 BACKLOG

- [ ] 5.1 Dashboard - Visão Geral (MVP)
- [ ] 5.2 Dashboard - Engajamento e Funil
- [ ] 5.3 Validação de performance (DirectLake / DirectQuery)

> **Observação:** EPIC despriorizado em função do foco acadêmico do TCC.

---

## 🟦 EPIC 6 - Machine Learning Não Supervisionado (Exploratório)

**Objetivo:** segmentar alunos em perfis de desempenho, com participação utilizada como apoio descritivo complementar.  
**Status:** ✅ DONE

### Decisões congeladas do EPIC 6
- Unidade de análise: **aluno (`user_id`)**
- Variáveis do agrupamento: **cinco dimensões de desempenho**
- Participação: **não entra diretamente na clusterização**
- Método final interpretado: **K-Means**
- Método complementar para apoio à escolha de `k`: **hierárquico com critério de Ward**

### Itens do EPIC 6
- [x] 6.0 Gerar snapshot reprodutível do dataset por usuário
- [x] 6.1 Definir unidade de análise (`user_id`)
- [x] 6.2 Feature engineering (dataset agregado)
- [x] 6.3 Normalização e preparação para ML
- [x] 6.4 Clusterização exploratória (K-Means baseline + refinamentos)
- [x] 6.5 Critérios de qualidade do agrupamento
  - [x] silhouette
  - [x] interpretabilidade
  - [x] apoio via dendrograma (Ward)
- [x] 6.6 Tratamento de caso extremo de participação (~90k eventos em um único dia)
- [x] 6.7 Redução de dimensionalidade por PCA
- [x] 6.8 Definição da solução principal com `k = 4`
- [x] 6.9 Identificação de quatro perfis analíticos
- [x] 6.10 Fechamento técnico formal via checkpoint do EPIC 6

### Estado técnico atual do EPIC 6
- Base final de modelagem: **77 alunos**
- PCA: **2 componentes explicam ~92,5% da variabilidade**
- Comparação principal:
  - `k = 5` → silhouette ~0,367, porém com cluster unitário
  - `k = 4` → silhouette ~0,354, adotado por maior interpretabilidade
- Perfis finais em consolidação textual:
  - Desempenho intermediário com participação regular
  - Alto desempenho com menor participação observada
  - Alto desempenho com maior participação observada
  - Desempenho mais baixo em argumentação e comunicação

---

## 🟦 EPIC 7 - TCC (Resultados Finais) + Documentação Final

**Objetivo:** consolidar o estudo em narrativa científica final e fechar os artefatos documentais do projeto.  
**Status:** ⚙️ WIP avançado

### Decisões congeladas do EPIC 7
- O TCC final será orientado por:
  - objetivo claro e coerente com a unidade de análise no nível do aluno;
  - Material e Métodos reforçado teoricamente;
  - Resultados e Discussão com foco em achados e interpretação;
  - participação tratada como leitura complementar posterior;
  - apêndice com link para os artefatos computacionais.

### Itens do EPIC 7
- [x] 7.0 Gate acadêmico final (alinhamento do estudo)
- [x] 7.1 Revisão do Resumo / Abstract / Keywords
- [x] 7.2 Revisão da Introdução e objetivo
- [x] 7.3 Reestruturação de Material e Métodos
- [x] 7.4 Reestruturação de Resultados e Discussão
- [x] 7.5 Revisão das Conclusões
- [x] 7.6 Definição do Apêndice A (artefatos computacionais)
- [x] 7.7 Envio da versão v1.5 à orientadora
- [x] 7.8 Incorporar comentários da orientadora na v1.6
- [ ] 7.9 Revisão final de consistência, formatação e submissão
- [ ] 7.10 Atualizar `README.md`, `OBJECT_REGISTRY.md` e checkpoint final do EPIC 7

### Estado acadêmico atual
- Versão v1.6 enviada à orientadora
- Retorno positivo: “está ficando muito bom”, com pedidos de reforço pontual
- Foco imediato:
  - reforço metodológico
  - encadeamento da análise
  - estatística descritiva nos perfis
  - fechamento do apêndice com link para código

---

## Observações

- O foco principal do projeto, nesta fase, está em **EPIC 6 + EPIC 7**.
- O EPIC 5 permanece em backlog, sem bloquear a conclusão acadêmica.
- O trabalho não tem objetivo causal nem supervisionado; trata-se de análise exploratória não supervisionada orientada a perfis.
- O uso de xAPI/LRS permanece como base empírica do estudo, e não como objeto de avaliação tecnológica.