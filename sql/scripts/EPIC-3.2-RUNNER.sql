/* =========================================================
 EPIC 3.2 — GOLD / CONSUMO (RUNNER-FRIENDLY)
 Pré-requisitos:
   - EPIC 3.1 concluído
   - Views existentes:
       gd_fact_execution_events  (com category_id canônico ou category_unknown)
       gd_dim_event_category
 Observação:
   - Este EPIC NÃO cria regras de classificação. Apenas consome o Gold.
========================================================= */

------------------------------------------------------------
-- 3.2-A — View de Consumo (enriquecida): vw_execution_events
------------------------------------------------------------
CREATE OR ALTER VIEW vw_execution_events AS
SELECT
  f.*,
  d.category_name,
  d.category_description,
  d.user_types,
  d.user_actions,
  d.sco_categories
FROM gd_fact_execution_events f
LEFT JOIN gd_dim_event_category d
  ON f.category_id = d.category_id;

-- Gate V1 — vw_execution_events não duplica o fato
SELECT
  (SELECT COUNT(*) FROM gd_fact_execution_events) AS fact_rows,
  (SELECT COUNT(*) FROM vw_execution_events) AS view_rows;


------------------------------------------------------------
-- 3.2-B — View de Métricas Diárias: vw_daily_metrics
-- Objetivo: fornecer uma tabela pronta para BI com contagens e
-- dimensões principais (data, org, família, categoria, sco).
------------------------------------------------------------
CREATE OR ALTER VIEW vw_daily_metrics AS
SELECT
  event_date,
  organization_id,
  organization_group_id,
  event_family,
  category_id,
  sco_id,

  COUNT(*)                                  AS events_total,
  COUNT(DISTINCT user_id)                   AS users_distinct,
  COUNT(DISTINCT registration_id)           AS registrations_distinct,

  -- famílias específicas (úteis em dashboards)
  SUM(CASE WHEN event_family = 'meeting' THEN 1 ELSE 0 END)              AS events_meeting,
  SUM(CASE WHEN event_family = 'tech_question' THEN 1 ELSE 0 END)        AS events_tech_question,
  SUM(CASE WHEN event_family = 'interaction_message' THEN 1 ELSE 0 END)  AS events_interaction_message,
  SUM(CASE WHEN event_family = 'risk_assessment' THEN 1 ELSE 0 END)      AS events_risk_assessment,

  -- status (se houver)
  SUM(CASE WHEN registration_status_norm IS NOT NULL THEN 1 ELSE 0 END)  AS events_with_registration_status

FROM gd_fact_execution_events
GROUP BY
  event_date,
  organization_id,
  organization_group_id,
  event_family,
  category_id,
  sco_id;

-- Gate V2 — vw_daily_metrics é agregada: deve ter <= linhas que o fato
SELECT
  (SELECT COUNT(*) FROM gd_fact_execution_events) AS fact_rows,
  (SELECT COUNT(*) FROM vw_daily_metrics) AS daily_rows;


------------------------------------------------------------
-- 3.2-C — View de Funil de Registro: vw_registration_funnel
-- Objetivo: visão por dia/org/sco/status para acompanhar funil.
-- Observação: depende de registration_status_norm existir.
------------------------------------------------------------
CREATE OR ALTER VIEW vw_registration_funnel AS
SELECT
  event_date,
  organization_id,
  organization_group_id,
  sco_id,
  registration_status_norm,

  COUNT(*)                                AS events_total,
  COUNT(DISTINCT registration_id)         AS registrations_distinct,
  COUNT(DISTINCT user_id)                 AS users_distinct,

  -- tentativa (se existir)
  COUNT(DISTINCT CASE WHEN registration_attempt IS NOT NULL THEN registration_id END) AS registrations_with_attempt

FROM gd_fact_execution_events
WHERE registration_id IS NOT NULL
GROUP BY
  event_date,
  organization_id,
  organization_group_id,
  sco_id,
  registration_status_norm;

-- Gate V3 — sanity: linhas do funil <= linhas do daily_metrics (em geral)
SELECT
  (SELECT COUNT(*) FROM vw_daily_metrics) AS daily_rows,
  (SELECT COUNT(*) FROM vw_registration_funnel) AS funnel_rows;


------------------------------------------------------------
-- 3.2-D — (Opcional) View de qualidade do mapeamento de categoria
-- Objetivo: monitorar quanto ainda cai em category_unknown.
------------------------------------------------------------
CREATE OR ALTER VIEW vw_category_mapping_health AS
SELECT
  event_date,
  event_family,
  category_id,
  COUNT(*) AS rows
FROM gd_fact_execution_events
GROUP BY event_date, event_family, category_id;

-- Gate V4 — quick check: top categorias por volume
SELECT TOP 50
  category_id,
  COUNT(*) AS rows
FROM gd_fact_execution_events
GROUP BY category_id
ORDER BY rows DESC;
