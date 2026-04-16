/* EPIC 6.0 — USER FEATURES (Snapshot base analítica por aluno)
   Fonte: dbo.vw_execution_events_v3
   Unidade de análise: user_id
*/

CREATE OR ALTER VIEW dbo.vw_user_features_v1 AS
SELECT
    user_id,

    /* participação */
    COUNT(*) AS total_events,
    COUNT(DISTINCT CAST(event_ts AS date)) AS days_active,

    SUM(CASE WHEN event_family = 'meeting' THEN 1 ELSE 0 END) AS total_meetings,
    SUM(CASE WHEN event_family = 'interaction_message' THEN 1 ELSE 0 END) AS total_interactions,
    SUM(CASE WHEN event_family = 'tech_question' THEN 1 ELSE 0 END) AS total_tech_questions,
    SUM(CASE WHEN event_family = 'risk_assessment' THEN 1 ELSE 0 END) AS total_risk_assessments,

    /* cobertura semântica (útil para diagnosticar “unknown”) */
    SUM(CASE WHEN category_id IS NULL OR category_id = 'category_unknown' THEN 1 ELSE 0 END) AS total_unknown_category,
    CAST(
        1.0 * SUM(CASE WHEN category_id IS NULL OR category_id = 'category_unknown' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0)
        AS decimal(10,4)
    ) AS pct_unknown_category,

    /* desempenho — conversão robusta (caso venha como varchar em alguns casos) */
    AVG(TRY_CONVERT(float, REPLACE(CAST(technicalAbility AS varchar(50)), ',', '.'))) AS technicalAbility_avg,
    AVG(TRY_CONVERT(float, REPLACE(CAST(attitude         AS varchar(50)), ',', '.'))) AS attitude_avg,
    AVG(TRY_CONVERT(float, REPLACE(CAST(argumentation    AS varchar(50)), ',', '.'))) AS argumentation_avg,
    AVG(TRY_CONVERT(float, REPLACE(CAST(articulation     AS varchar(50)), ',', '.'))) AS articulation_avg,
    AVG(TRY_CONVERT(float, REPLACE(CAST(negotiation      AS varchar(50)), ',', '.'))) AS negotiation_avg,

    /* opcional: variabilidade (ajuda na interpretação do perfil) */
    STDEV(TRY_CONVERT(float, REPLACE(CAST(technicalAbility AS varchar(50)), ',', '.'))) AS technicalAbility_sd,
    STDEV(TRY_CONVERT(float, REPLACE(CAST(attitude         AS varchar(50)), ',', '.'))) AS attitude_sd,
    STDEV(TRY_CONVERT(float, REPLACE(CAST(argumentation    AS varchar(50)), ',', '.'))) AS argumentation_sd,
    STDEV(TRY_CONVERT(float, REPLACE(CAST(articulation     AS varchar(50)), ',', '.'))) AS articulation_sd,
    STDEV(TRY_CONVERT(float, REPLACE(CAST(negotiation      AS varchar(50)), ',', '.'))) AS negotiation_sd

FROM dbo.vw_execution_events_v3
GROUP BY user_id;
GO

/* sanity check */
SELECT TOP 10 *
FROM dbo.vw_user_features_v1
ORDER BY total_events DESC;
GO


SELECT * FROM dbo.vw_user_features_v1;
