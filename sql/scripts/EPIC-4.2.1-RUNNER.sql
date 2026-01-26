/* =====================================================================================
   EPIC 4.2.1 — Meeting Unknown Qualification (Views-only)
   Objetivo: qualificar category_unknown em meeting sem reduzir category_id.
   Base: dbo.vw_execution_events_v2 (overlay do EPIC 4.1.1)
   ===================================================================================== */

---------------------------------------------------------------
-- 1) VIEW v3 — adiciona colunas de qualificação (SEM alterar category_id)
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_execution_events_v3;

CREATE VIEW dbo.vw_execution_events_v3 AS
SELECT
  f.*,

  /* meeting_unknown_flag: facilita filtros e métricas */
  CASE
    WHEN f.event_family = 'meeting' AND f.category_id = 'category_unknown' THEN CAST(1 AS BIT)
    ELSE CAST(0 AS BIT)
  END AS meeting_unknown_flag,

  /* meeting_unknown_type: subtipos explicáveis (sem inferência fraca) */
  CASE
    WHEN f.event_family <> 'meeting' OR f.category_id <> 'category_unknown' THEN NULL

    /* Padrão estrutural forte: placeholder */
    WHEN UPPER(LTRIM(RTRIM(f.meeting_code))) = 'CODIGO' THEN 'STRUCTURAL_CODE_PLACEHOLDER'

    /* Identificadores ausentes (caso apareça) */
    WHEN f.meeting_id IS NULL OR LTRIM(RTRIM(f.meeting_id)) = '' THEN 'MISSING_MEETING_ID'
    WHEN f.sco_id IS NULL OR LTRIM(RTRIM(f.sco_id)) = '' THEN 'MISSING_SCO_ID'

    /* Contexto semântico ausente (o que vimos no Gate C) */
    WHEN f.sco_categories IS NULL OR LTRIM(RTRIM(f.sco_categories)) = '' THEN 'NO_SCO_CATEGORIES'

    /* Fallback honesto */
    ELSE 'OTHER_UNKNOWN'
  END AS meeting_unknown_type,

  /* meeting_unknown_note: explicação curta para narrativa acadêmica */
  CASE
    WHEN f.event_family <> 'meeting' OR f.category_id <> 'category_unknown' THEN NULL
    WHEN UPPER(LTRIM(RTRIM(f.meeting_code))) = 'CODIGO'
      THEN 'meeting_code placeholder; insufficient source context'
    WHEN f.sco_categories IS NULL OR LTRIM(RTRIM(f.sco_categories)) = ''
      THEN 'missing sco_categories; no semantic dictionary available'
    ELSE 'insufficient evidence to refine unknown'
  END AS meeting_unknown_note

FROM dbo.vw_execution_events_v2 f;

---------------------------------------------------------------
-- 2) HEALTH v3 — distribuição de unknown por subtipo (meeting)
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_meeting_unknown_health_v3;

CREATE VIEW dbo.vw_meeting_unknown_health_v3 AS
SELECT
  meeting_unknown_type,
  COUNT(*) AS rows,
  CAST(COUNT(*) AS FLOAT) /
    NULLIF((SELECT COUNT(*) FROM dbo.vw_execution_events_v3
            WHERE event_family='meeting' AND category_id='category_unknown'), 0) AS share_of_meeting_unknown
FROM dbo.vw_execution_events_v3
WHERE event_family = 'meeting'
  AND category_id = 'category_unknown'
GROUP BY meeting_unknown_type;

-- Gate: health por subtipo
SELECT *
FROM dbo.vw_meeting_unknown_health_v3
ORDER BY rows DESC;

---------------------------------------------------------------
-- 3) TOP meeting_code dentro de unknown (contribuição para o total unknown)
---------------------------------------------------------------
DROP VIEW IF EXISTS dbo.vw_meeting_unknown_top_codes_v3;

CREATE VIEW dbo.vw_meeting_unknown_top_codes_v3 AS
SELECT
  meeting_code,
  COUNT(*) AS rows,
  CAST(COUNT(*) AS FLOAT) /
    NULLIF((SELECT COUNT(*) FROM dbo.vw_execution_events_v3
            WHERE event_family='meeting' AND category_id='category_unknown'), 0) AS share_of_meeting_unknown
FROM dbo.vw_execution_events_v3
WHERE event_family = 'meeting'
  AND category_id = 'category_unknown'
GROUP BY meeting_code;

SELECT TOP 20 *
FROM dbo.vw_meeting_unknown_top_codes_v3
ORDER BY rows DESC;

---------------------------------------------------------------
-- 4) Proxy de "potencial recovery" (sem prometer redução)
--    Unknown com meeting_code diferente de 'CODIGO'
---------------------------------------------------------------
SELECT
  COUNT(*) AS meeting_unknown_rows,
  SUM(CASE WHEN UPPER(LTRIM(RTRIM(meeting_code))) <> 'CODIGO' THEN 1 ELSE 0 END) AS non_placeholder_rows,
  CAST(SUM(CASE WHEN UPPER(LTRIM(RTRIM(meeting_code))) <> 'CODIGO' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS non_placeholder_ratio
FROM dbo.vw_execution_events_v3
WHERE event_family='meeting'
  AND category_id='category_unknown';

---------------------------------------------------------------
-- 5) Sample audit: 50 linhas unknown com tipo + nota
---------------------------------------------------------------
SELECT TOP 50
  meeting_group_code,
  meeting_code,
  meeting_id,
  sco_id,
  meeting_unknown_type,
  meeting_unknown_note,
  source_file,
  CAST(event_ts AS date) AS event_day
FROM dbo.vw_execution_events_v3
WHERE event_family='meeting'
  AND category_id='category_unknown'
ORDER BY event_ts DESC;
