/* =========================================================
   EPIC 3.1 — GOLD / MODELAGEM (Caminho A — SQL Views)
   Projeto: Customer App Learning Analytics (Fabric)
   Observação: este script NÃO cria tabelas (policy bloqueia CREATE TABLE).
   ========================================================= */

-- 0) Pré-checks (opcional)
-- Ver amostra e schema do dicionário de categorias
SELECT TOP 10 *
FROM ctx_table_event_categories;

SELECT
  c.COLUMN_NAME,
  c.DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_NAME = 'ctx_table_event_categories'
ORDER BY c.ORDINAL_POSITION;

-- (Opcional) Ver schema do Silver
SELECT
  c.COLUMN_NAME,
  c.DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_NAME = 'silver_execution_log'
ORDER BY c.ORDINAL_POSITION;

------------------------------------------------------------
-- 3.1-A1 — Dimensão: gd_dim_event_category (VIEW)
------------------------------------------------------------
CREATE OR ALTER VIEW gd_dim_event_category AS
SELECT
    category_id,
    category_name,
    category_description,
    user_types,
    user_actions,
    sco_categories
FROM ctx_table_event_categories;

-- Gate D1 — category_id é única
SELECT
  COUNT(*) AS rows_total,
  COUNT(DISTINCT category_id) AS distinct_category_id
FROM gd_dim_event_category;

------------------------------------------------------------
-- 3.1-B1 — Fato MVP: gd_fact_execution_events (VIEW)
--         (category_id placeholder por event_family)
------------------------------------------------------------

-- (Registro de diagnóstico) category_id NÃO existe no Silver
-- (Esperado: erro "Invalid column name 'category_id'" se a coluna não existir)
SELECT TOP 5
  event_key, event_ts, event_family, category_id
FROM silver_execution_log;

CREATE OR ALTER VIEW gd_fact_execution_events AS
SELECT
  event_key,
  event_ts,
  event_date,
  event_family,

  CASE
    WHEN event_family = 'meeting' THEN 'category_meeting_mvp'
    WHEN event_family = 'tech_question' THEN 'category_question_mvp'
    WHEN event_family = 'interaction_message' THEN 'category_interaction_mvp'
    WHEN event_family = 'risk_assessment' THEN 'category_risk_mvp'
    ELSE 'category_unknown'
  END AS category_id,

  user_id,
  organization_id,
  organization_group_id,
  registration_id,
  sco_id,

  interaction_id,
  interaction_type,
  interaction_prompt_text,
  interaction_aditional_content,

  tech_question_id,
  tech_question_answer,
  tech_question_result,

  meeting_id,
  meeting_code,
  meeting_group_code,

  assessed_risk_id,
  risk_assessment_impact_answer,
  risk_assessment_probability_answer,

  reaction_survey_question_id,
  reaction_survey_answer,

  source_file,
  ingested_at_utc,
  dedup_key
FROM silver_execution_log;

-- Gate F1 — 1:1 com Silver
SELECT
  (SELECT COUNT(*) FROM silver_execution_log) AS silver_rows,
  (SELECT COUNT(*) FROM gd_fact_execution_events) AS fact_rows,
  (SELECT COUNT(DISTINCT event_key) FROM gd_fact_execution_events) AS distinct_event_key;

-- Gate F2 — distribuição do placeholder category_id
SELECT category_id, COUNT(*) AS rows
FROM gd_fact_execution_events
GROUP BY category_id
ORDER BY rows DESC;

------------------------------------------------------------
-- 3.1-C1 — Diagnósticos de discriminadores (Q1–Q4)
------------------------------------------------------------

-- Q1: meeting -> meeting_group_code
SELECT TOP 100
  meeting_group_code,
  COUNT(*) AS rows
FROM silver_execution_log
WHERE event_family = 'meeting'
GROUP BY meeting_group_code
ORDER BY rows DESC;

-- Q2a: tech_question -> sco_id
SELECT TOP 100
  sco_id,
  COUNT(*) AS rows
FROM silver_execution_log
WHERE event_family = 'tech_question'
GROUP BY sco_id
ORDER BY rows DESC;

-- Q2b: tech_question -> tech_question_id
SELECT TOP 100
  tech_question_id,
  COUNT(*) AS rows
FROM silver_execution_log
WHERE event_family = 'tech_question'
GROUP BY tech_question_id
ORDER BY rows DESC;

-- Q3a: interaction_message -> sco_id
SELECT TOP 100
  sco_id,
  COUNT(*) AS rows
FROM silver_execution_log
WHERE event_family = 'interaction_message'
GROUP BY sco_id
ORDER BY rows DESC;

-- Q3b: interaction_message -> interaction_prompt_text
SELECT TOP 100
  interaction_prompt_text,
  COUNT(*) AS rows
FROM silver_execution_log
WHERE event_family = 'interaction_message'
GROUP BY interaction_prompt_text
ORDER BY rows DESC;

-- Q4: risk_assessment -> assessed_risk_id
SELECT TOP 100
  assessed_risk_id,
  COUNT(*) AS rows
FROM silver_execution_log
WHERE event_family = 'risk_assessment'
GROUP BY assessed_risk_id
ORDER BY rows DESC;

------------------------------------------------------------
-- 3.1-D1 — Mapa explícito (contrato): meeting_group_code -> category_id
--          (preencher iterativamente com categorias reais category_XX)
------------------------------------------------------------
CREATE OR ALTER VIEW gd_map_meeting_group_code_category AS
SELECT * FROM (VALUES
  -- Preencha aos poucos: (meeting_group_code, category_id)
  ('0fjvc20', 'category_unknown'),
  ('qfe7hqn', 'category_unknown'),
  ('em53c1v', 'category_unknown')
) AS m(meeting_group_code, category_id);

SELECT TOP 10 *
FROM gd_map_meeting_group_code_category;


------------------------------------------------------------
-- 3.1-D2/D3 — Fato V2 (classificação real quando possível)
------------------------------------------------------------
CREATE OR ALTER VIEW gd_fact_execution_events_v2 AS
SELECT
  s.*,

  CASE
    WHEN s.event_family = 'meeting'
      THEN COALESCE(m.category_id, 'category_unknown')

    WHEN s.event_family = 'tech_question'
      THEN COALESCE(tc.category_id, 'category_unknown')

    WHEN s.event_family = 'interaction_message'
      THEN COALESCE(ic.category_id, 'category_unknown')

    WHEN s.event_family = 'risk_assessment'
      THEN 'category_unknown'

    ELSE 'category_unknown'
  END AS category_id

FROM silver_execution_log s
LEFT JOIN gd_map_meeting_group_code_category m
  ON s.meeting_group_code = m.meeting_group_code

OUTER APPLY (
  SELECT TOP 1 d.category_id
  FROM gd_dim_event_category d
  WHERE d.category_name LIKE 'Resposta questão%'
    AND d.sco_categories IS NOT NULL
    AND CHARINDEX(s.sco_id, d.sco_categories) > 0
  ORDER BY d.category_id
) tc

OUTER APPLY (
  SELECT TOP 1 d.category_id
  FROM gd_dim_event_category d
  WHERE d.category_name LIKE 'Prompt de interação%'
    AND d.sco_categories IS NOT NULL
    AND CHARINDEX(s.sco_id, d.sco_categories) > 0
  ORDER BY d.category_id
) ic;


------------------------------------------------------------
-- 3.1-D4 — Promoção do Fato Oficial
------------------------------------------------------------
CREATE OR ALTER VIEW gd_fact_execution_events AS
SELECT * FROM gd_fact_execution_events_v2;


------------------------------------------------------------
-- 3.1-D5 — Gates finais
------------------------------------------------------------
-- Distribuição final
SELECT category_id, COUNT(*) AS rows
FROM gd_fact_execution_events
GROUP BY category_id
ORDER BY rows DESC;

-- Gate F3 (ignora category_unknown)
SELECT COUNT(*) AS not_mapped
FROM gd_fact_execution_events f
LEFT JOIN gd_dim_event_category d
  ON f.category_id = d.category_id
WHERE f.category_id <> 'category_unknown'
  AND d.category_id IS NULL;


