# Object Registry — Customer App Learning Analytics (Fabric)

> **Objetivo:** registrar **todas** as tabelas e views do projeto (catálogo vivo).  
> **Regra:** qualquer novo objeto, renome, deprecação ou mudança de contrato deve atualizar este arquivo no mesmo commit/PR.

**Atualizado em:** 22/01/2026  
**Fonte:** `INFORMATION_SCHEMA.TABLES` e `INFORMATION_SCHEMA.VIEWS` (schema `dbo`) + metadados do endpoint.

---

## Convenções
- **ctx_***: tabelas de contexto (contratos, dicionários, listas)
- **bronze_***: ingestão raw governada (schema string, sem semântica)
- **silver_***: reconciliação semântica + chaves canônicas + qualidade
- **gd_***: gold (modelo analítico / fatos e dimensões)
- **vw_***: views de consumo (BI-ready)
- **DimDate**: dimensão de calendário (tempo)

---

## 1) Tabelas (schema: `dbo`)

### 1.1 Dimensões base
- **DimDate** — dimensão de calendário (tempo)

### 1.2 Bronze
- **bronze_execution_log** — raw governado (lineage explícito)

### 1.3 Silver
- **silver_execution_log** — semântica + `event_family` + `event_key` (SHA-256)

### 1.4 Contexto (ctx_)
- **ctx__column_mapping**
- **ctx_dictionary_table_event_fields**
- **ctx_global_tables_career_pathways**
- **ctx_global_tables_issues**
- **ctx_global_tables_onet_occupation_c**
- **ctx_global_tables_risks**
- **ctx_global_tables_skills**
- **ctx_lists_interaction_type**
- **ctx_local_collection_button_purpose**
- **ctx_local_collection_data_origin**
- **ctx_local_collection_quiz_purposes**
- **ctx_local_collection_reference_data**
- **ctx_local_collection_sco_categories**
- **ctx_local_collection_skill_id**
- **ctx_local_collection_user_action**
- **ctx_local_collection_user_types**
- **ctx_lookup_table_reference_data**
- **ctx_lookup_table_software_response**
- **ctx_lookup_table_user_actions**
- **ctx_lookup_table_user_goals**
- **ctx_table_event_categories** — categorias + contratos de campos por categoria

### 1.5 Gold (modelagem / consumo) — objetos presentes no endpoint
> Observação: no endpoint SQL do Fabric, alguns objetos podem aparecer tanto em `TABLES` quanto em `VIEWS`
> por conta da forma como o catálogo é exposto. A “fonte de verdade” do tipo está listada também na seção **2) Views**.
- **gd_dim_event_category**
- **gd_fact_execution_events**
- **gd_fact_execution_events_v2**
- **gd_map_meeting_group_code_category**
- **vw_execution_events**
- **vw_daily_metrics**
- **vw_registration_funnel**
- **vw_category_mapping_health**

---

## 2) Views (schema: `dbo`)

### 2.1 Gold (gd_)
- **gd_dim_event_category** — dimensão de categorias (a partir de `ctx_table_event_categories`)
- **gd_map_meeting_group_code_category** — contrato: `meeting_group_code → category_id`
- **gd_fact_execution_events_v2** — fato gold com `category_id` derivada (v2)
- **gd_fact_execution_events** — alias oficial apontando para v2

### 2.2 Consumo (vw_)
- **vw_execution_events** — fato enriquecido com dim de categoria
- **vw_daily_metrics** — métrricas diárias agregadas para BI
- **vw_registration_funnel** — funil por status/registro (BI)
- **vw_category_mapping_health** — monitoramento de coverage de `category_unknown`

### 2.3 Outras views em `dbo`
- **DimDate** — (aparece como view no endpoint; manter como dimensão de tempo)

---

## 3) Schemas de sistema/telemetria (não versionar como parte do modelo do projeto)
> Estes schemas aparecem nas queries do `INFORMATION_SCHEMA`, mas **não** são artefatos do seu modelo.
- **queryinsights**: `exec_requests_history`, `exec_sessions_history`, `frequently_run_queries`, `long_running_queries`
- **sys**: `external_delta_tables`, `managed_delta_tables`, checkpoints/logs internos, etc.

---

## 4) Deprecados / Substituídos
- *(vazio por enquanto — registrar aqui quando objetos forem substituídos; manter motivo e data)*

---

## 5) Próximas inclusões esperadas (EPIC 4)
- Expandir/automatizar a classificação para reduzir `category_unknown`
- (opcional) substituir o mapeamento manual por `ctx_meeting_group_code` (se for criada)
- (opcional) `ctx_tech_question_to_module` e/ou `ctx_sco_to_module` (se for criada)
