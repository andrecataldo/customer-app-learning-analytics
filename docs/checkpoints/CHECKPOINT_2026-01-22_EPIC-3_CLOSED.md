# ✅ CHECKPOINT — EPIC 3 FECHADO (Gold v1)

**Projeto:** Customer App Learning Analytics (Microsoft Fabric + Lakehouse)  
**Data:** 22/01/2026  
**Status:** ✅ EPIC 3 concluído (v1) — *classificação parcial e controlada*  

---

## 1) Escopo do EPIC 3

### EPIC 3.1 — Gold / Modelagem (✅)
- Dimensão de categorias a partir de `ctx_table_event_categories`
- Fato Gold canônico **1:1 com Silver** (grão = `event_key`)
- Derivação de `category_id` (v1):
  - **meeting**: mapeamento explícito via `meeting_group_code → category_18/19/20`
  - **tech_question / interaction_message / risk_assessment**: permanecem `category_unknown`
- Gates de integridade e não-duplicação aplicados

### EPIC 3.2 — Gold / Consumo (✅)
- Views de consumo e métricas:
  - `vw_execution_events`
  - `vw_daily_metrics`
  - `vw_registration_funnel`
  - `vw_category_mapping_health`

---

## 2) Evidências (Gates) — Resultado final

### 2.1 Gates do Fato (Gold)
- **Fato 1:1 com Silver**  
  `fact_rows = 101.802` e `distinct_event_key = 101.802`

- **Distribuição por categoria (top)**  
  - `category_unknown`: 61.776  
  - `category_18`: 14.220  
  - `category_19`: 13.510  
  - `category_20`: 12.296  

### 2.2 Cobertura de classificação por família
| event_family | rows | unknown_rows | observação |
|---|---:|---:|---|
| meeting | 94.965 | 54.939 | mapeado parcialmente |
| tech_question | 4.124 | 4.124 | 100% unknown |
| interaction_message | 2.491 | 2.491 | 100% unknown |
| risk_assessment | 222 | 222 | 100% unknown |

### 2.3 Gates do Consumo (Views)
- **Gate V2**: `vw_daily_metrics` agregada corretamente  
  `fact_rows = 101.802`, `daily_rows = 473` ✅
- **Gate V3**: `vw_registration_funnel` é subconjunto esperado  
  `daily_rows = 473`, `funnel_rows = 439` ✅

---

## 3) Decisões arquiteturais consolidadas

- Gold não distorce grão (fato em `event_key`)
- Classificação **explícita e auditável**
- `category_unknown` é **permitido e monitorado**
- EPIC 3 fechado como **Gold v1**, pronto para BI

---

## 4) Inventário oficial de objetos (fonte de verdade)

> A lista **completa e atualizada** de tabelas e views do projeto está registrada em:
>
> **`docs/catalog/OBJECT_REGISTRY.md`**
>
> Este arquivo é o **catálogo vivo** do modelo e deve ser atualizado a cada EPIC/PR.
> O checkpoint referencia esse catálogo em vez de duplicar a listagem.

---

## 5) Pendências registradas para EPIC 4 (Gold Hardening)
- Expandir mapeamento de `meeting_group_code`
- Classificar `tech_question`, `interaction_message` e `risk_assessment`
- Meta sugerida: reduzir `category_unknown` global para **< 30%**

---

## 6) Artefatos gerados
- `EPIC-3.1-RUNNER.sql`
- `EPIC-3.2-RUNNER.sql`

---

### ✅ Encerramento
EPIC 3 (Gold v1) concluído com gates aprovados, consumo estável e inventário oficial separado em catálogo próprio.
