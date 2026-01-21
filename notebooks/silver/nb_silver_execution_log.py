#!/usr/bin/env python
# coding: utf-8

# ## nb_silver_execution_log
# 
# null

# ###### 🟩 EPIC 2 — Silver (Reconciliação Semântica)
# 
# ###### Objetivo: tornar os dados confiáveis e semanticamente interpretáveis.
# ###### Status: ✅ DONE
# ###### Pré-requisito: EPIC 1 concluído e validado
# ###### Entrada: bronze_execution_log
# ###### Saída (sugestão): silver_execution_log (+ tabelas auxiliares de métricas)

# ### Cell 0 - Setup: imports e helpers

# In[ ]:


from notebookutils import mssparkutils
import os, time, re
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from functools import reduce


# ### Cell 1 - EPIC 2.1: Criar event_ts (event_date como timestamp)

# ###### Cell 1.1 - EPIC 2: Load Bronze (bronze_execution_log)

# In[ ]:


dfb = spark.table("bronze_execution_log")
display(dfb.limit(10))


# In[ ]:


# EPIC 2.1 — Correção semântica do tempo
# event_date na origem é TIMESTAMP completo

dfs = (
    dfb
    # timestamp canônico
    .withColumn("event_ts", F.to_timestamp(F.col("event_date")))

    # data e hora derivadas explicitamente
    .withColumn("event_date", F.to_date(F.col("event_ts")))
    .withColumn("event_time", F.date_format(F.col("event_ts"), "HH:mm:ss.SSS"))

    # rastreabilidade da decisão
    .withColumn("event_ts_source", F.lit("event_date_timestamp"))
)


# In[ ]:


display(
    dfs.select("event_date", "event_time", "event_ts").limit(20)
)


# ### Cell 2 - EPIC 2.2: Normalizar vazios e status (""->NULL, status_norm)

# In[ ]:


def empty_to_null(c):
    return F.when(F.trim(F.col(c)) == "", F.lit(None)).otherwise(F.col(c))

for c in dfs.columns:
    dfs = dfs.withColumn(c, empty_to_null(c))


# In[ ]:


dfs = dfs.withColumn("registration_status_norm", F.lower(F.trim(F.col("registration_status"))))
display(dfs.head(5))


# ### Cell 3 - EPIC 2.3: Derivar event_family (regras determinísticas)

# In[ ]:


# EPIC 2.3 — Derivar event_family (regra determinística)

dfs = dfs.withColumn(
    "event_family",
    F.when(F.col("tech_question_id").isNotNull(), F.lit("tech_question"))
     .when(F.col("meeting_id").isNotNull(), F.lit("meeting"))
     .when(F.col("reaction_survey_question_id").isNotNull(), F.lit("reaction_survey"))
     .when(F.col("stimulus_assessed_skill_id").isNotNull(), F.lit("stimulus_assessment"))
     .when(F.col("performance_evaluation_skill_id").isNotNull(), F.lit("performance_evaluation"))
     .when(F.col("assessed_risk_id").isNotNull(), F.lit("risk_assessment"))
     .when(
         (F.col("interaction_type").isNotNull()) &
         (F.col("interaction_id").isNull()),
         F.lit("interaction_message")
     )
     .when(F.col("interaction_id").isNotNull(), F.lit("interaction"))
     .otherwise(F.lit("unknown"))
)



# In[ ]:


print("=== EVENT FAMILY DISTRIBUTION (AFTER UPDATE) ===")
display(
    dfs.groupBy("event_family")
       .count()
       .orderBy(F.col("count").desc())
)

print("=== REMAINING UNKNOWN SAMPLE ===")
display(
    dfs.filter(F.col("event_family")=="unknown")
       .select("registration_id","interaction_type","event_ts")
       .limit(20)
)


# ### Cell 4 - EPIC 2.4: Deduplicação MVP por família (gate)

# In[ ]:


dfs = dfs.withColumn(
  "dedup_key",
  F.sha2(F.concat_ws("||",
      F.col("event_family"),
      F.coalesce(F.col("registration_id"), F.lit("")),
      F.coalesce(F.col("tech_question_id"), F.lit("")),
      F.coalesce(F.col("meeting_id"), F.lit("")),
      F.coalesce(F.col("interaction_id"), F.lit("")),
      F.coalesce(F.col("performance_evaluation_skill_id"), F.lit("")),
      F.coalesce(F.col("assessed_risk_id"), F.lit(""))
  ), 256)
)

# Verificar se existe colisão real de dedup_key por família
has_collisions = (
    dfs.groupBy("event_family", "dedup_key")
       .count()
       .filter(F.col("count") > 1)
       .limit(1)
       .count() > 0
)

if has_collisions:
    w = Window.partitionBy("event_family", "dedup_key") \
              .orderBy(F.col("event_ts").desc_nulls_last())

    dfs_dedup = (
        dfs.withColumn("rn", F.row_number().over(w))
           .filter(F.col("rn") == 1)
           .drop("rn")
    )
else:
    dfs_dedup = dfs



# In[ ]:


print("=== DEDUP GATE ===")
display({"has_collisions": has_collisions})


# ### Cell 5 - EPIC 2.5: Métricas antes/depois (impacto)

# In[ ]:


before = dfs.count()
after = dfs_dedup.count()

metrics = {
  "rows_before": before,
  "rows_after": after,
  "rows_dropped": before - after
}
display(metrics)

display(
  dfs.groupBy("event_family").count().withColumnRenamed("count","before")
  .join(dfs_dedup.groupBy("event_family").count().withColumnRenamed("count","after"), "event_family", "left")
  .fillna(0, ["after"])
  .withColumn("dropped", F.col("before") - F.col("after"))
  .orderBy(F.col("dropped").desc())
)


# ### Cell 6 - EPIC 2.6: Ativar event_key (se gate passar)

# In[ ]:


# EPIC 2.6 — Ativar event_key (se gate passar)

# 2.6.1 Gate mínimo
gate = (
    dfs_dedup
    .agg(
        F.count("*").alias("rows"),
        F.sum(F.when(F.col("event_ts").isNull(), 1).otherwise(0)).alias("event_ts_nulls"),
        F.sum(F.when(F.col("event_family") == "unknown", 1).otherwise(0)).alias("unknown_family"),
        F.sum(F.when(F.col("dedup_key").isNull(), 1).otherwise(0)).alias("dedup_key_nulls"),
    )
    .collect()[0]
)

gate_ok = (
    gate["event_ts_nulls"] == 0 and
    gate["unknown_family"] == 0 and
    gate["dedup_key_nulls"] == 0
)

print("=== EVENT_KEY GATE (EPIC 2.6) ===")
display({
    "rows": gate["rows"],
    "event_ts_nulls": gate["event_ts_nulls"],
    "unknown_family": gate["unknown_family"],
    "dedup_key_nulls": gate["dedup_key_nulls"],
    "gate_ok": gate_ok
})

if not gate_ok:
    raise ValueError("Gate do EPIC 2.6 não passou. Corrija as nulidades antes de ativar event_key.")

# 2.6.2 Gerar event_key (hash determinístico)
dfs_final = (
    dfs_dedup
    .withColumn(
        "event_key",
        F.sha2(
            F.concat_ws(
                "||",
                F.col("event_family"),
                F.col("dedup_key"),
                F.date_format(F.col("event_ts"), "yyyy-MM-dd'T'HH:mm:ss.SSS")
            ),
            256
        )
    )
)

# 2.6.3 Evidência de unicidade
print("=== EVENT_KEY UNIQUENESS CHECK ===")
total = dfs_final.count()
distinct_keys = dfs_final.select("event_key").distinct().count()

display({
    "rows_total": total,
    "distinct_event_key": distinct_keys,
    "collisions": total - distinct_keys,
    "collision_pct": round(((total - distinct_keys) / total) * 100, 6)
})

display(dfs_final.select("event_key","event_family","event_ts","registration_id","user_id","sco_id").limit(20))


# ### Cell  7- Persistência oficial do Silver.

# In[ ]:


(
    dfs_final
    .write
    .mode("overwrite")
    .format("delta")
    .saveAsTable("silver_execution_log")
)

print("✅ Written: silver_execution_log")


# ==================================================================

# ## 🧾 Evidências (EPIC 2 - Auditoria)
# #### EPIC 2 - Silver (Reconciliação Semântica)
# #### Evidências visuais: baseline -> normalização -> family -> dedup -> métricas -> event_key
# 

# ### Evidence 1 - EPIC 2.0: Baseline Bronze (entrada)

# In[ ]:


dfb = spark.table("bronze_execution_log")

print("=== BRONZE BASELINE ===")
print("rows:", dfb.count())
print("cols:", len(dfb.columns))
print("schema sample:", [(f.name, f.dataType.simpleString()) for f in dfb.schema][:10])
display(dfb.select("registration_id","user_id","sco_id","meeting_id","tech_question_id","assessed_risk_id").limit(10))


# ### Evidence 2 - EPIC 2.1: event_ts e fonte

# In[ ]:


print("=== EVENT_TS SOURCE DISTRIBUTION ===")
display(
  dfs.groupBy("event_ts_source").count()
     .withColumn("pct", F.round(F.col("count")/F.sum("count").over(Window.partitionBy())*100,2))
     .orderBy(F.col("count").desc())
)

print("=== SAMPLE EVENT_TS ===")
display(dfs.select("event_ts_source","event_ts","event_date","event_time","ingested_at_utc").limit(20))


# ### Evidence 3 - EPIC 2.2: Missingness antes/depois

# In[ ]:


cols_check = ["event_time","organization_id","meeting_id","tech_question_id","registration_status"]

def missing_stats(df, cols):
    exprs = []
    for c in cols:
        exprs += [
            F.lit(c).alias("col"),
            F.count(F.when(F.col(c).isNull(), 1)).alias("nulls"),
            F.count(F.when(F.col(c) == "", 1)).alias("empties"),
            F.count(F.when((F.col(c).isNotNull()) & (F.col(c) != ""), 1)).alias("filled")
        ]
    # mais simples: retorna um DF por coluna
    out = []
    for c in cols:
        out.append(df.select(
            F.lit(c).alias("col"),
            F.count(F.when(F.col(c).isNull(), 1)).alias("nulls"),
            F.count(F.when(F.col(c) == "", 1)).alias("empties"),
            F.count(F.when((F.col(c).isNotNull()) & (F.col(c) != ""), 1)).alias("filled"),
        ))
    return reduce(lambda a,b: a.unionByName(b), out)

print("=== MISSINGNESS (BRONZE) ===")
display(missing_stats(dfb, cols_check))

print("=== MISSINGNESS (SILVER-STAGE) ===")
display(missing_stats(dfs, cols_check))


# ### Evidence 4 - EPIC 2.3: Distribuição + amostras por família

# In[ ]:


print("=== EVENT FAMILY DISTRIBUTION ===")
display(
  dfs.groupBy("event_family").count()
     .orderBy(F.col("count").desc())
)

families = [r["event_family"] for r in dfs.select("event_family").distinct().collect()]

for fam in sorted(families):
    print(f"\n=== SAMPLE: {fam} ===")
    display(
      dfs.filter(F.col("event_family")==fam)
         .select("event_family","registration_id","user_id","sco_id",
                 "meeting_id","tech_question_id","assessed_risk_id",
                 "interaction_id","event_ts","event_ts_source")
         .limit(10)
    )


# ### Evidence 5 - EPIC 2.4: Impacto do dedup (total e por família)

# In[ ]:


print("=== DEDUP IMPACT (TOTAL) ===")
before = dfs.count()
after  = dfs_dedup.count()
display({"rows_before": before, "rows_after": after, "rows_dropped": before-after,
         "dropped_pct": round((before-after)/before*100, 4)})

print("=== DEDUP IMPACT BY FAMILY ===")
byfam = (
  dfs.groupBy("event_family").count().withColumnRenamed("count","before")
  .join(dfs_dedup.groupBy("event_family").count().withColumnRenamed("count","after"), "event_family", "left")
  .fillna(0, ["after"])
  .withColumn("dropped", F.col("before") - F.col("after"))
  .withColumn("dropped_pct", F.round(F.col("dropped")/F.col("before")*100, 3))
  .orderBy(F.col("dropped").desc())
)
display(byfam)


# ### Evidence 6 - EPIC 2.4: Checagem de colisões (por que dedup é no-op)

# In[ ]:


print("=== DEDUP KEY COLLISION CHECK ===")
collisions = (
  dfs.groupBy("event_family","dedup_key").count()
     .filter(F.col("count") > 1)
     .groupBy("event_family")
     .agg(F.count("*").alias("keys_with_collisions"),
          F.sum("count").alias("rows_in_collisions"),
          F.max("count").alias("max_collision"))
     .orderBy(F.col("rows_in_collisions").desc())
)
display(collisions)


# In[ ]:


display(dfs.select("event_date","event_ts_source","event_ts","event_date","event_time","ingested_at_utc").limit(20))


# ### Evidence 7 - EPIC 2.3: Controle de unknown (esperado = 0 linhas)

# In[ ]:


print("=== UNKNOWN SAMPLE ===")
display(
  dfs_dedup.filter(F.col("event_family")=="unknown")
           .select("registration_id","user_id","sco_id",
                   "interaction_id","interaction_type",
                   "reaction_survey_question_id","stimulus_assessed_skill_id",
                   "performance_evaluation_skill_id","assessed_risk_id",
                   "event_ts")
           .limit(30)
)

