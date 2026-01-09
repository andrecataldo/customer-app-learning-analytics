#!/usr/bin/env python
# coding: utf-8

# ## notebook_customer_app_silver_to_gold
# 
# null

# ### Cell 1 – Imports e parâmetros

# In[5]:


from pyspark.sql import functions as F

SILVER_TABLE = "log_register_silver"
GOLD_TABLE_EVENTS = "log_register_gold_events"


# ### Cell 2 – Ler Silver

# In[6]:


df_silver = spark.read.table(SILVER_TABLE)

print("Schema Silver:")
df_silver.printSchema()

display(df_silver.limit(10))


# ### Cell 3 – Montar Gold “evento a evento”

# In[7]:


df_gold_events = (
    df_silver
    # Deriva data e hora
    .withColumn("event_date", F.to_date("event_time"))
    .withColumn("event_hour", F.date_format("event_time", "HH:mm:ss"))

    # Nome completo do usuário
    .withColumn("user_full_name", F.concat_ws(" ", "first_name", "last_name"))

    # Renomeia colunas para termos mais semânticos
    .withColumnRenamed("id",   "event_id")
    .withColumnRenamed("name", "session_name")
    .withColumnRenamed("type", "role")
)

df_gold_events = df_gold_events.withColumn(
    "is_instructor",
    F.when(F.upper(F.col("role")) == "INSTRUTOR", F.lit(1)).otherwise(F.lit(0))
)


display(df_gold_events.count())
display(df_gold_events.limit(20))



# ### Cell 4 – Gravar Gold como Delta

# In[8]:


(
    df_gold_events
      .write
      .format("delta")
      .mode("overwrite")
      .saveAsTable(GOLD_TABLE_EVENTS)
)

print(f"Tabela Gold Daily criada/atualizada: {GOLD_TABLE_EVENTS}")


# ### Cell 5 – Checks rápidos

# In[9]:


display(spark.sql(f"""
SELECT 
    COUNT(*) AS rows_gold,
    MIN(event_date) AS first_day,
    MAX(event_date) AS last_day,
    COUNT(DISTINCT email) AS distinct_users
FROM {GOLD_TABLE_EVENTS}
"""))

display(spark.sql(f"""
SELECT event_date, org, role, COUNT(*) AS events
FROM {GOLD_TABLE_EVENTS}
GROUP BY event_date, org, role
ORDER BY event_date DESC, org, role
LIMIT 50
"""))



# ### Cell 6 – View para Power BI / SQL

# In[10]:


CREATE OR ALTER VIEW vw_customer_app_events AS
SELECT
    event_id                AS IdEvento,
    event_time              AS DataHoraEvento,
    event_date              AS DataEvento,
    event_hour              AS HoraEvento,
    org                     AS Organizacao,
    session_name            AS TurmaOuSessao,
    role                    AS Papel,
    is_instructor           AS EhInstrutor,
    user_full_name          AS NomeParticipante,
    first_name              AS PrimeiroNome,
    last_name               AS Sobrenome,
    email                   AS Email
FROM log_register_gold_events;



# In[ ]:


CREATE OR ALTER VIEW vw_customer_app_daily_metrics AS
SELECT
    event_date      AS DataEvento,
    org             AS Organizacao,
    role            AS Papel,
    COUNT(*)              AS QtdeEventos,
    COUNT(DISTINCT email) AS QtdeUsuarios
FROM log_register_gold_events
GROUP BY event_date, org, role;

