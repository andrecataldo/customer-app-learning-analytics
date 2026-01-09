#!/usr/bin/env python
# coding: utf-8

# ## notebook_customer_app_bronze_to_silver
# 
# null

# ### Cell 1 — Parâmetros

# In[ ]:


from pyspark.sql import functions as F

# nomes das tabelas
BRONZE_TABLE = "log_register_bronze"
SILVER_TABLE = "log_register_silver"


# ### Cell 2 – Ler Bronze

# In[ ]:


df_raw = spark.read.table(BRONZE_TABLE)

print("Schema Bronze:")
df_raw.printSchema()

display(df_raw.limit(10))


# ### Cell 3 – Limpeza de texto (strings)

# In[ ]:


df_clean = (
    df_raw
    # ORG: maiúsculo, sem aspas, sem espaços extras
    .withColumn("org",
        F.upper(
            F.trim(
                F.regexp_replace("org", '"', "")
            )
        )
    )
    
    # Nomes: capitaliza, remove aspas e espaços
    .withColumn("first_name",
        F.initcap(
            F.trim(
                F.regexp_replace("first_name", '"', "")
            )
        )
    )
    .withColumn("last_name",
        F.initcap(
            F.trim(
                F.regexp_replace("last_name", '"', "")
            )
        )
    )
    
    # E-mail: minúsculo, sem aspas, sem espaços
    .withColumn("email",
        F.lower(
            F.trim(
                F.regexp_replace("email", '"', "")
            )
        )
    )
    
    # Datas/horas: apenas tirar aspas e espaços (tipagem vem depois)
    .withColumn("createdAt",
        F.trim(
            F.regexp_replace("createdAt", '"', "")
        )
    )
    .withColumn("createdDate",
        F.trim(
            F.regexp_replace("createdDate", '"', "")
        )
    )
    .withColumn("createdTime",
        F.trim(
            F.regexp_replace("createdTime", '"', "")
        )
    )
)

display(df_clean.count())
display(df_clean.limit(10))


# ### Cell 4 – Criar event_time (timestamp)

# In[ ]:


# string base para data/hora
event_str = F.when(
    (F.col("createdAt").isNotNull()) & (F.col("createdAt") != ""),
    F.col("createdAt")
).otherwise(
    F.concat_ws(" ", F.col("createdDate"), F.col("createdTime"))
)

# tenta dois formatos: com e sem milissegundos
ts1 = F.to_timestamp(event_str, "yyyy-MM-dd HH:mm:ss.SSS")
ts2 = F.to_timestamp(event_str, "yyyy-MM-dd HH:mm:ss")

df_ts = df_clean.withColumn("event_time", F.coalesce(ts1, ts2))
display(df_ts.count())
display(
    df_ts.select("createdAt", "createdDate", "createdTime", "event_time")
         .limit(20)
)


# ### Cell 5 – Filtrar ruídos e remover duplicados

# In[ ]:


"""
df_silver = (
    df_ts
    # garante que só entram linhas com timestamp válido
    .filter(F.col("event_time").isNotNull())
    # remove duplicados por id + event_time
    .dropDuplicates(["id", "event_time"])
)
"""

df_silver = df_ts

display(df_silver.count())
display(df_silver.limit(20))



# ### Cell 6 – Gravar tabela Silver (Delta)

# In[ ]:


(
    df_silver
      .write
      .format("delta")
      .mode("overwrite")
      .saveAsTable(SILVER_TABLE)
)

print(f"Tabela Silver criada/atualizada: {SILVER_TABLE}")


# ### Cell 7 – Checks rápidos de qualidade

# In[ ]:


# Resumo geral
display(spark.sql(f"""
SELECT 
    COUNT(*)                      AS rows_silver,
    COUNT(DISTINCT email)         AS distinct_emails,
    MIN(event_time)               AS first_event,
    MAX(event_time)               AS last_event
FROM {SILVER_TABLE}
"""))

# Distribuição por org e type
display(spark.sql(f"""
SELECT org, type, COUNT(*) AS events
FROM {SILVER_TABLE}
GROUP BY org, type
ORDER BY events DESC
"""))

# E-mails suspeitos
display(spark.sql(f"""
SELECT *
FROM {SILVER_TABLE}
WHERE email IS NULL OR email NOT LIKE '%@%'
LIMIT 50
"""))

