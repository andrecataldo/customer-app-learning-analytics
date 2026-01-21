# 📌 CHECKPOINT - EPIC 2 concluído | Silver (Reconciliação Semântica)

**Projeto:** Customer App Learning Analytics (Fabric + Lakehouse)  
**Data:** 21/01/2026  
**Estado:** Silver criado, validado semanticamente e persistido  

---

## 1️⃣ Fonte de Verdade (conforme ROADMAP)

### Fonte operacional reconciliada (Silver)

- **Origem:** `bronze_execution_log`
- **Natureza:** dataset derivado e *wide*, reconciliado semanticamente
- **Uso:** base confiável para análises, métricas educacionais e modelagem Gold
- **Persistência:** tabela Delta `silver_execution_log`

📌 O Silver **não substitui o Bronze** — preserva lineage e adiciona semântica controlada.

---

## 2️⃣ EPIC 2 - Silver (Reconciliação Semântica) ✅ CONCLUÍDO

### Status

- **EPIC:** 🟩 EPIC 2 - Silver  
- **Estado:** ✅ Finalizado e validado  

### Objetivo do EPIC

Tornar os dados **confiáveis, consistentes e semanticamente interpretáveis**, sem perda de informação e com evidência técnica explícita.

---

## 3️⃣ Etapas Executadas (ROADMAP)

### 2.1 Criação de `event_ts`

- Conversão explícita e controlada de data/hora
- Garantia de campo temporal único para ordenação, deduplicação e chave canônica

---

### 2.2 Normalização de vazios, strings e status

- Padronização de `NULL` vs `""`
- Preparação para regras determinísticas de classificação e deduplicação

---

### 2.3 Derivação de `event_family` (usando `ctx_*`)

- Classificação semântica baseada em presença de IDs e contratos de contexto
- Eliminação completa de `event_family = unknown`

📌 **Resultado:** 100% dos eventos classificados semanticamente.

---

### 2.4 Política MVP de deduplicação por família

- Geração de `dedup_key` determinística por família
- Implementação de política conservadora (keep latest by `event_ts`)
- **Evidência técnica:** nenhuma colisão detectada

```text
has_collisions = False
rows_dropped  = 0
```
📌 Deduplicação caracterizada como no-op justificada (dataset já consistente).

---

### 2.5 Métricas antes/depois (impacto do tratamento)

- Comparação de contagem total de linhas
- Distribuição por event_family
- Verificação de impacto zero na cardinalidade

📌 Nenhuma linha perdida ou alterada indevidamente.

---

### 2.6 Ativação de event_key (chave canônica)

#### Gate mínimo (2.6.1)

Critérios avaliados antes da ativação:
- event_ts sem valores nulos
- event_family sem unknown
- dedup_key sem valores nulos

```
rows              = 101802
event_ts_nulls    = 0
unknown_family    = 0
dedup_key_nulls   = 0
gate_ok           = True
```

#### Geração de `event_key` (2.6.2)

- Hash SHA-256 determinístico
- Baseado em:
    - event_family
    - dedup_key
    - event_ts normalizado

```
rows_total           = 101802
distinct_event_key   = 101802
collisions           = 0
collision_pct        = 0.0%
```

📌 `event_key` validada como **única, estável e auditável.**


---

## 4️⃣ Persistência Oficial

- **Tabela criada:** `silver_execution_log`
- **Formato:** Delta
- **Modo:** `overwrite` (MVP controlado)
- **Origem:** `dfs_final`

📌 Silver passa a ser a **fonte oficial para o Gold.**

---

## 5️⃣ Evidências Técnicas Registradas

- Gate explícito para ativação de `event_key`
- Evidência formal de:
    - ausência de colisões
    - deduplicação no-op justificada
    - unicidade total da chave canônica
- Amostras visuais com `event_key`, `event_family` e `event_ts`

---

## 6️⃣ Decisões Arquiteturais Congeladas

- Silver **aplica semântica**, Bronze não
- `event_key` só existe a partir do Silver
- Deduplicação segue política **conservadora por família**
- Nenhuma inferência implícita ou heurística oculta
- Pipeline segue rigor **xAPI-inspired** / **Learning Analytics**

---

## 7️⃣ ROADMAP - Estado Atual

```
EPIC P   ✅ concluído
EPIC 1   ✅ concluído
EPIC 2   ✅ concluído
EPIC 3   ⏳ não iniciado (Gold / Star Schema)
```

