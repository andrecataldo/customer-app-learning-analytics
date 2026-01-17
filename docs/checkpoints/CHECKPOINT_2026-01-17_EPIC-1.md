# 📌 CHECKPOINT — EPIC 1 concluído (Bronze)  

**Projeto:** Customer App — Learning Analytics (Microsoft Fabric + Lakehouse)  
**Data:** 17/01/2026  
**Estado:** EPIC 1 finalizado e congelado  
**EPIC seguinte:** EPIC 2 — Silver (Reconciliação Semântica)

---

## 1️⃣ Contexto e Escopo

Este checkpoint consolida o encerramento formal do **EPIC 1 — Bronze (Ingestão Raw Governada)**, cujo objetivo foi garantir a ingestão fiel de dados operacionais derivados, com preservação de estrutura, ausência de semântica e evidência técnica sobre a natureza do dataset.

O EPIC 1 dependeu diretamente do **EPIC P — Contextos e Dicionários**, previamente concluído e validado, e não introduz qualquer transformação analítica ou reconciliação semântica.

---

## 2️⃣ Fonte de Verdade (conforme ROADMAP)

### 2.1 Fonte operacional derivada (imutável)
- **Arquivo:** `execution_log_yyyymmdd.csv`
- **Origem:** query SQL externa (fora do Lakehouse)
- **Natureza:** dataset *wide*, derivado de múltiplos joins
- **Uso:** única fonte operacional para a camada Bronze

### 2.2 Fonte semântica / contratual (normativa)
- **Arquivo:** `contexts_lrs_event_logs.xlsx`
- **Regra:** 1 aba = 1 tabela
- **Uso:** contrato semântico (não operacional), **não utilizado no Bronze**

---

## 3️⃣ EPIC 1 — Bronze (Ingestão Raw Governada)

### Objetivo do EPIC
Preservar fielmente as fontes derivadas, com evidência técnica, rastreabilidade (lineage) e ausência total de semântica ou inferência.

---

### 3.1 Item 1.1 — Ingestão Raw Governada ✅

**Notebook:** `notebook_customer_app_bronze_ingest`

#### Decisões e contratos
- Schema **100% string**
- Nenhuma inferência de tipo
- Nenhuma normalização
- Nenhuma semântica aplicada
- Lineage obrigatório

#### Implementação
- Leitura do arquivo `execution_log_yyyymmdd.csv`
- Parsing defensivo do CSV (delimiter `,`)
- Inclusão explícita de:
  - `source_file`
  - `ingested_at_utc`
- Escrita como tabela Delta:
  - **Tabela:** `bronze_execution_log`

#### Resultado
- Tabela Bronze criada e visível no Lakehouse
- Bronze definido como **única fonte** para a camada Silver

---

### 3.2 Item 1.2 — Diagnósticos do Bronze ✅

**Notebook:** `nb_bronze_diagnostics`

#### Diagnósticos executados

**A. Baseline estrutural**
- Total de linhas: **101.802**
- Total de colunas: **39**
- Schema: **100% string**
- Lineage confirmado

**B. Completude (NULL vs string vazia)**
- Ausência de dados codificada como `""` (string vazia), não como `NULL`
- Dataset caracterizado como **esparso por design**
- Padrão consistente com dataset *wide* derivado por múltiplos joins

**B.1 Validação de parsing**
- Campos estruturais (`user_id`, `registration_id`, `sco_id`) 100% preenchidos
- Hipótese de desalinhamento de colunas descartada
- Parsing do CSV confirmado como correto

**C. Duplicidade estrutural**
- Hash de linha completa aplicado
- **Nenhuma duplicidade estrutural encontrada**
- Multiplicidade ocorre por variação semântica entre tipos de evento, não por repetição de linhas

---

## 4️⃣ Conclusões Arquiteturais Congeladas

A partir das evidências coletadas no EPIC 1, ficam congeladas as seguintes decisões:

- O Bronze representa um **dataset derivado, wide e esparso**
- O Bronze é adequado como **camada raw governada**
- O Bronze é **inadequado para consumo analítico direto**
- Não existe fato analítico único no Bronze
- A ausência de dados (`""`) **não deve ser tratada no Bronze**
- Qualquer reconciliação semântica ocorre **exclusivamente no Silver**
- A criação de `event_key` é **postergada para o EPIC 2**

---

## 5️⃣ Estrutura Atual do Lakehouse (após EPIC 1)

### Tabelas
- `bronze_execution_log`
- `ctx_*` (tabelas de contexto e lookup — EPIC P)

### Arquivos
- `Files/context/raw` → Excel normativo
- `Files/context/tables` → CSVs intermediários
- `Files/bronze/raw` → CSVs operacionais

---

## 6️⃣ O que NÃO foi feito (por design)

- Nenhuma tipagem de colunas
- Nenhuma normalização de datas
- Nenhuma criação de chaves substitutas
- Nenhuma junção com tabelas de contexto
- Nenhuma lógica xAPI aplicada

Essas ações são **explicitamente reservadas ao EPIC 2**.

---

## 7️⃣ Próximo Ponto de Retomada

Ao abrir novo chat ou retomar o projeto, iniciar em:

> **EPIC 2 — Silver (Reconciliação Semântica e Modelagem Analítica)**

Com base direta nas evidências e decisões congeladas neste checkpoint.

---

## 8️⃣ Estado do ROADMAP

```text
EPIC P   ✅ DONE
EPIC 1   ✅ DONE
EPIC 2   ⏳ NOT STARTED
