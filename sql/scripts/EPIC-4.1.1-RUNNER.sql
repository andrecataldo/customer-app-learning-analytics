/* ============================================================
   EPIC-4.1.1-RUNNER.sql  (NO TABLE CREATE; VIEWS ONLY)
   ============================================================ */

-- =====================================================================================
-- EPIC 4.1.1 — Gold Hardening: Explicit Meeting Classification (Views-only Runner)
--
-- Contexto:
-- Este runner implementa o hardening da classificação de eventos do tipo "meeting"
-- por meio de regras explícitas e auditáveis, sem alterar o grão nem reprocessar dados.
--
-- Restrição de ambiente:
-- O SQL Endpoint do Microsoft Fabric não permite CREATE TABLE / PRIMARY KEY neste contexto.
-- Por isso, a implementação é deliberadamente "views-only", utilizando CTEs e VALUES
-- para simular ctx_ (contexto semântico) de forma reprodutível.
--
-- Escopo:
-- - Tornar explícitas regras já existentes no Gold v1
-- - Adicionar auditoria por evento (applied_rule_id)
-- - NÃO reduzir category_unknown (hardening, não coverage)
--
-- Evidência e narrativa acadêmica:
-- Ver checkpoint canônico:
-- docs/checkpoints/CHECKPOINT_2026-01-24_EPIC-4.1.1.md
--
-- =====================================================================================


---------------------------------------------------------------
-- 0) BASELINE (v1): meeting unknown ratio
---------------------------------------------------------------
SELECT
  COUNT(*) AS meeting_rows,
  SUM(CASE WHEN category_id = 'category_unknown' THEN 1 ELSE 0 END) AS unknown_rows,
  CAST(SUM(CASE WHEN category_id = 'category_unknown' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS unknown_ratio
FROM vw_execution_events
WHERE event_family = 'meeting';

---------------------------------------------------------------
-- 1) VIEW BASE (ALL meetings)
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_epic4_meeting_base;

CREATE VIEW dbo.vw_epic4_meeting_base AS
SELECT
  meeting_group_code,
  meeting_code,
  meeting_id,
  category_id,
  sco_categories,
  CAST(event_ts AS date) AS event_day
FROM vw_execution_events
WHERE event_family = 'meeting';

---------------------------------------------------------------
-- 2) CONTEXTO como VIEW (em vez de TABLE) — regras explícitas
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_ctx_meeting_group_mapping;

CREATE VIEW dbo.vw_ctx_meeting_group_mapping AS
SELECT *
FROM (VALUES
  ('0FJVC20','category_18','MG_001',
   'Deterministic mapping: meeting_group_code consistently associated with ENCONTRO_FACILITADOR',
   'EPIC 4.1.1 — evidence: category_id + sco_categories consistency',
   CAST(1 AS BIT)),
  ('QFE7HQN','category_19','MG_002',
   'Deterministic mapping: meeting_group_code consistently associated with ENCONTRO_APRESENTACAO',
   'EPIC 4.1.1 — evidence: category_id + sco_categories consistency',
   CAST(1 AS BIT)),
  ('EM53C1V','category_20','MG_003',
   'Deterministic mapping: meeting_group_code consistently associated with ENCONTRO',
   'EPIC 4.1.1 — evidence: category_id + sco_categories consistency',
   CAST(1 AS BIT))
) AS v(meeting_group_code_norm, target_category_id, rule_id, rule_rationale, rule_source, is_active);

-- Gate: ver regras
SELECT *
FROM dbo.vw_ctx_meeting_group_mapping
WHERE is_active = 1
ORDER BY rule_id;

---------------------------------------------------------------
-- 3) OVERLAY — vw_execution_events_v2 (category_id_v2 + auditoria)
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_execution_events_v2;

CREATE VIEW dbo.vw_execution_events_v2 AS
SELECT
  f.*,

  CASE
    WHEN f.event_family = 'meeting'
     AND m.target_category_id IS NOT NULL
    THEN m.target_category_id
    ELSE f.category_id
  END AS category_id_v2,

  m.rule_id     AS applied_rule_id,
  m.rule_source AS applied_rule_source

FROM vw_execution_events f
LEFT JOIN dbo.vw_ctx_meeting_group_mapping m
  ON UPPER(LTRIM(RTRIM(f.meeting_group_code))) = m.meeting_group_code_norm
 AND m.is_active = 1;

-- Gate: sem duplicação de linhas
SELECT
  (SELECT COUNT(*) FROM vw_execution_events)        AS v1_rows,
  (SELECT COUNT(*) FROM dbo.vw_execution_events_v2) AS v2_rows;

---------------------------------------------------------------
-- 4) HEALTH VIEW — before/after por família
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_category_mapping_health_v2;

CREATE VIEW dbo.vw_category_mapping_health_v2 AS
SELECT
  event_family,
  COUNT(*) AS rows,
  SUM(CASE WHEN category_id = 'category_unknown' THEN 1 ELSE 0 END)    AS unknown_v1,
  SUM(CASE WHEN category_id_v2 = 'category_unknown' THEN 1 ELSE 0 END) AS unknown_v2
FROM dbo.vw_execution_events_v2
GROUP BY event_family;

SELECT *
FROM dbo.vw_category_mapping_health_v2
ORDER BY rows DESC;

---------------------------------------------------------------
-- 5) IMPACTO: meeting before/after
---------------------------------------------------------------
SELECT
  COUNT(*) AS meeting_rows,
  SUM(CASE WHEN category_id = 'category_unknown' THEN 1 ELSE 0 END) AS unknown_rows_v1,
  CAST(SUM(CASE WHEN category_id = 'category_unknown' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS unknown_ratio_v1
FROM dbo.vw_execution_events_v2
WHERE event_family = 'meeting';

SELECT
  COUNT(*) AS meeting_rows,
  SUM(CASE WHEN category_id_v2 = 'category_unknown' THEN 1 ELSE 0 END) AS unknown_rows_v2,
  CAST(SUM(CASE WHEN category_id_v2 = 'category_unknown' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS unknown_ratio_v2
FROM dbo.vw_execution_events_v2
WHERE event_family = 'meeting';

---------------------------------------------------------------
-- 6) AUDITORIA: impacto por regra
---------------------------------------------------------------
SELECT
  applied_rule_id,
  COUNT(*) AS impacted_rows
FROM dbo.vw_execution_events_v2
WHERE event_family = 'meeting'
  AND applied_rule_id IS NOT NULL
GROUP BY applied_rule_id
ORDER BY impacted_rows DESC;

---------------------------------------------------------------
-- 7) SPOT CHECK: amostra reclassificada
---------------------------------------------------------------
SELECT TOP 50
  meeting_group_code,
  category_id AS category_v1,
  category_id_v2 AS category_v2,
  applied_rule_id,
  sco_categories,
  CAST(event_ts AS date) AS event_day
FROM dbo.vw_execution_events_v2
WHERE event_family = 'meeting'
  AND applied_rule_id IS NOT NULL
ORDER BY meeting_group_code, event_day;



-- Gate A — As linhas com regra aplicada eram unknown no v1?
SELECT
  applied_rule_id,
  category_id AS category_v1,
  category_id_v2 AS category_v2,
  COUNT(*) AS rows
FROM dbo.vw_execution_events_v2
WHERE event_family = 'meeting'
  AND applied_rule_id IS NOT NULL
GROUP BY applied_rule_id, category_id, category_id_v2
ORDER BY applied_rule_id, rows DESC;

-- Gate B — Quantos unknown existem dentro dos 3 códigos no v1?
SELECT
  meeting_group_code,
  SUM(CASE WHEN category_id = 'category_unknown' THEN 1 ELSE 0 END) AS unknown_v1_rows,
  COUNT(*) AS total_rows
FROM vw_execution_events
WHERE event_family = 'meeting'
  AND meeting_group_code IN ('0fjvc20','qfe7hqn','em53c1v')
GROUP BY meeting_group_code
ORDER BY total_rows DESC;

-- Gate C — A view vw_execution_events já traz category_* populado via join com dim?
SELECT TOP 50
  meeting_group_code,
  category_id,
  category_name,
  category_description,
  sco_categories
FROM vw_execution_events
WHERE event_family = 'meeting'
  AND category_id = 'category_unknown';


-- o que distingue unknown meeting?
SELECT TOP 50
  meeting_group_code,
  meeting_code,
  meeting_id,
  sco_id,
  category_id,
  source_file,
  CAST(event_ts AS date) AS event_day
FROM vw_execution_events
WHERE event_family = 'meeting'
  AND category_id = 'category_unknown'
ORDER BY event_ts DESC;


SELECT
  meeting_code,
  COUNT(*) AS rows
FROM vw_execution_events
WHERE event_family = 'meeting'
  AND category_id = 'category_unknown'
GROUP BY meeting_code
ORDER BY rows DESC;

