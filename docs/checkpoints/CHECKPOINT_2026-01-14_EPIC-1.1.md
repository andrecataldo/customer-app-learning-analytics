# 📌 CHECKPOINT — EPIC 1.1 concluído | EPIC 1.2 em andamento

**Projeto:** Customer App Learning Analytics (Fabric + Lakehouse)  
**Data:** 14/01/2026  
**Estado:** Bronze criado e validado estruturalmente; diagnósticos em execução  

---

## 1️⃣ Fonte de Verdade (conforme ROADMAP)

### 1. Fonte operacional derivada (imutável)
- **Arquivo:** `execution_log_yyyymmdd.csv`
- **Origem:** query SQL externa (fora do Lakehouse)
- **Natureza:** dataset *wide*, derivado de múltiplos joins
- **Uso:** única fonte de dados operacionais (Bronze)

### 2. Fonte semântica / contratual (normativa)
- **Arquivo:** `contexts_lrs_event_logs.xlsx`
- **Regra:** 1 aba = 1 tabela
- **Uso:** contrato semântico (não operacional)

---

## 2️⃣ EPIC P — Contextos e Dicionários ✅ CONCLUÍDO

### Status
- **EPIC:** 🟪 EPIC P — Contextos e Dicionários  
- **Estado:** ✅ Finalizado e versionado  

### Artefatos gerados
- CSVs em `Files/context/tables/*.csv`
- Tabelas Delta `ctx_*`
- Manifest oficial:
  - `Files/context/manifest/manifest_ctx_v1.yml`

### Validações realizadas
- PK sanity check v3 (heurística + overrides)
- Todas as tabelas com PK única e não nula
- Coleções locais normalizadas com `id`
- `global_tables_onet_occupation_c` com PK explícita (`onet_occupation_code`)

### Notebook
- `nb_context_ingest_dictionaries`
  - Header com contrato explícito
  - EPIC P fechado

---

## 3️⃣ EPIC 1 — Bronze (Ingestão Raw Governada)

### 1.1 Ingestão Bronze — ✅ CONCLUÍDA

**Notebook:** `notebook_customer_app_bronze_ingest`

#### Contrato do Bronze
- Schema **100% string**
- Nenhuma inferência
- Nenhuma semântica
- Lineage obrigatório

#### Execução
- Leitura do `execution_log_yyyymmdd.csv`
- Cópia defensiva para `/tmp`
- Inclusão de:
  - `source_file`
  - `ingested_at_utc`
- Escrita Delta:
  - **Tabela:** `bronze_execution_log`

#### Resultado
- Tabela Bronze criada e visível no Lakehouse
- Bronze é a **única fonte** para o Silver

📌 **EPIC 1.1 pode ser marcado como DONE no ROADMAP**

---

### 1.2 Diagnósticos do Bronze — 🟡 EM ANDAMENTO

**Objetivo:** produzir evidência técnica e metodológica da qualidade e das limitações do dado derivado.

#### Executado até agora
- Snapshot inicial do Bronze (rows, cols, schema)
- Confirmação de schema string-only

#### Planejado / em execução
- Perfil de completude (null + vazio)
- Distribuição por IDs (`user_id`, `registration_id`, etc.)
- Duplicidade por hash de linha
- Proxy de “explosão por join”

---

## 4️⃣ Estrutura atual do Lakehouse (alto nível)

### Tables
- `bronze_execution_log`
- `ctx_*` (todas as tabelas de contexto e lookup)

### Files
- `Files/context/raw` → Excel normativo
- `Files/context/tables` → CSVs intermediários
- `Files/bronze/raw` → CSVs operacionais

---

## 5️⃣ Decisões Arquiteturais Congeladas

- Bronze **não aplica semântica**
- Contextos **não se misturam ao Bronze**
- Reconciliação semântica ocorre **somente no Silver**
- `event_key` **ainda não ativada** (depende do EPIC 2)
- Pipeline segue rigor **xAPI-inspired / Learning Analytics**

---

## 6️⃣ Próximo ponto de retomada

Ao abrir novo chat, retomar em:

> **EPIC 1.2 — Diagnósticos obrigatórios do Bronze**

Nada do EPIC P ou do EPIC 1.1 deve ser refeito.

---

## 7️⃣ ROADMAP — Estado Atual

```text
EPIC P   ✅ concluído
EPIC 1.1 ✅ concluído
EPIC 1.2 🟡 em andamento
EPIC 2   ⏳ não iniciado
