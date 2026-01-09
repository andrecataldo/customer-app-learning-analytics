#!/usr/bin/env python
# coding: utf-8

# ## notebook_customer_app_dimensions
# 
# null

# ### Cell 1 - Conferir o schema

# In[4]:


from pyspark.sql import functions as F


df_events = spark.read.table("log_register_gold_events")
df_events.printSchema()
df_events.select("event_date").show(5)



# ### Cell 2 - Criar a dim_date a partir de event_date

# In[7]:


from pyspark.sql import functions as F
from datetime import timedelta

# 1) Ler a tabela de eventos Gold
df_events = spark.read.table("log_register_gold_events")

# 2) Garantir que event_date esteja em formato date
#    Ajuste o formato se for diferente de 'yyyy-MM-dd'
df_dates = df_events.withColumn(
    "event_date_d",
    F.to_date("event_date", "yyyy-MM-dd")
)

# 3) Calcular data mínima e máxima
min_max = (
    df_dates
        .agg(
            F.min("event_date_d").alias("min_date"),
            F.max("event_date_d").alias("max_date")
        )
        .collect()[0]
)

start = min_max["min_date"]
end   = min_max["max_date"]

print("Período de eventos:", start, "→", end)

# 4) Gerar o range de datas usando sequence + explode (ajustado)
df_dim_date = (
    spark
        .createDataFrame([(start, end)], ["start_date", "end_date"])
        .select(F.sequence("start_date", "end_date").alias("DateSeq"))
        .select(F.explode("DateSeq").alias("Date"))
        .withColumn("Ano", F.year("Date"))
        .withColumn("MesNumero", F.month("Date"))
        .withColumn("MesNome", F.date_format("Date", "MMM"))
        .withColumn("AnoMes", F.date_format("Date", "yyyy-MM"))
        # Aqui usamos dayofweek em vez de 'u'
        .withColumn("DiaSemanaNumero", F.dayofweek("Date"))   # 1 = domingo, 7 = sábado
        .withColumn("DiaSemanaNome", F.date_format("Date", "EEE"))
)

display(df_dim_date.limit(10))



# ### Cell 3 - Gravar como tabela Delta dim_date

# In[8]:


(
    df_dim_date
        .write
        .mode("overwrite")
        .saveAsTable("dim_date")
)

spark.read.table("dim_date").show(5)

