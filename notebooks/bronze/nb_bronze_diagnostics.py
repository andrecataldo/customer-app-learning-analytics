#!/usr/bin/env python
# coding: utf-8

# ## nb_bronze_diagnostics
# 
# null

# ###### Notebook: nb_bronze_diagnostics
# ###### EPIC: 1.2 — Diagnósticos do Bronze
# ###### Fonte analisada: bronze_execution_log
# ###### Regra: nenhuma escrita, nenhuma semântica, nenhuma inferência

# ### Cell 0 - Imports

# In[1]:


from notebookutils import mssparkutils
import pandas as pd
from datetime import datetime, timezone
from pyspark.sql import Row
from pyspark.sql import functions as F
from functools import reduce


# ### Cell 1 - Carga controlada da tabela

# In[2]:


df = spark.table("bronze_execution_log")
display(df.head(20))



# ### Cell 2 - Diagnóstico A: Perfil estrutural do Bronze (baseline)

# In[3]:


rows = df.count()
cols = len(df.columns)
schema = [(f.name, f.dataType.simpleString()) for f in df.schema]

display({
    "rows": rows,
    "columns": cols,
    "schema": schema
})


# ### Cell 3 - Diagnóstico B: Completude (null vs vazio)

# In[4]:


df = spark.table("bronze_execution_log")
total = df.count()

def col_completeness(c: str):
    return (
        df.select(
            F.lit(c).alias("column"),
            F.count(F.when(F.col(c).isNull(), 1)).alias("null_count"),
            F.count(F.when(F.col(c) == "", 1)).alias("empty_count"),
            F.count(F.when(F.col(c).isNotNull() & (F.col(c) != ""), 1)).alias("filled_count"),
            F.lit(total).alias("total_rows"),
        )
        .withColumn("null_pct", F.round(F.col("null_count") / F.col("total_rows") * 100, 2))
        .withColumn("empty_pct", F.round(F.col("empty_count") / F.col("total_rows") * 100, 2))
        .withColumn("filled_pct", F.round(F.col("filled_count") / F.col("total_rows") * 100, 2))
    )

rows = [col_completeness(c) for c in df.columns]
df_completeness = reduce(lambda a,b: a.unionByName(b), rows)

display(df_completeness.orderBy(F.col("filled_pct").asc(), F.col("empty_pct").desc()))


# ### Cell 3 - Diagnóstico B.1: : “sample de linhas” + checagem de colunas-chave

# In[7]:


# inspecionar 20 linhas com foco nas colunas suspeitas
sus = [
  "event_date","event_time","user_id","registration_id","sco_id",
  "organization_id","interaction_id","source_file","ingested_at_utc"
]

display(df.select(*sus).limit(20))



# In[9]:


keys = ["user_id", "registration_id", "sco_id", "event_time", "organization_id"]

exprs = [
    F.count(F.when((F.col(c).isNotNull()) & (F.col(c) != ""), 1)).alias(f"{c}_filled")
    for c in keys
]

display(df.select(*exprs))



# In[11]:


from pyspark.sql import functions as F

df = spark.table("bronze_execution_log")

# criar hash da linha inteira (diagnóstico puro)
df_h = df.withColumn(
    "row_hash",
    F.sha2(
        F.concat_ws(
            "||",
            *[F.coalesce(F.col(c), F.lit("<<NULL>>")) for c in df.columns]
        ),
        256
    )
)

# grupos duplicados
dupes = (
    df_h
    .groupBy("row_hash")
    .count()
    .filter(F.col("count") > 1)
)

# resumo final (isso cria dup_summary)
dup_summary = (
    dupes.agg(
        F.count("*").alias("distinct_duplicate_hashes"),
        F.sum("count").alias("rows_in_duplicate_groups"),
        F.max("count").alias("max_repetition")
    )
)

display(dup_summary)


# In[12]:


display(
    dupes.orderBy(F.col("count").desc()).limit(20)
)

