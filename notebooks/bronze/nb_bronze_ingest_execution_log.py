#!/usr/bin/env python
# coding: utf-8

# ## notebook_customer_app_bronze_ingest
# 
# New notebook

# ### Cell 1 — Parâmetros

# In[ ]:


# ===== Parâmetros =====
FILE_PATH = "Files/log-register-2025nov11.csv"   # caminho do CSV no OneLake
BRONZE_TABLE = "log_register_bronze"             # nome da tabela Bronze
HAS_HEADER = False                               # mude para False se o CSV não tiver cabeçalho



# ### Cell 2 — Leitura (CSV → DataFrame)

# In[ ]:


from pyspark.sql import Row

# 1) Ler RDD
rdd = spark.sparkContext.textFile(FILE_PATH)

# 2) Extrair o header original
header = rdd.first()

# 3) Remover header
data_rdd = rdd.filter(lambda x: x != header)

# 4) Função de limpeza das aspas
def clean_line(line):
    # Remove aspas no começo e no final
    line = line.strip('"')
    line = line.strip()
    
    # Se ainda houver aspas duplicadas ou triplas, remover
    line = line.replace('"""', '"').replace('""', '"')
    
    # Split normal por vírgula
    parts = line.split(",")
    
    # Garantir exatamente 10 colunas
    if len(parts) != 10:
        print("Linha inválida:", line)
    
    return parts

# 5) Aplicar limpeza
parsed_rdd = data_rdd.map(clean_line)

# 6) Criar DataFrame com schema explícito
cols = ["id","org","name","type","first_name","last_name",
        "email","createdAt","createdDate","createdTime"]

df = spark.createDataFrame(parsed_rdd, cols)

display(df.limit(20))


# ### Cell 3 — Gravação como Tabela Delta

# In[ ]:


# ===== Gravar Bronze como tabela Delta gerenciada =====
(
    df.write
      .format("delta")
      .mode("overwrite")
      .saveAsTable(BRONZE_TABLE)
)

print(f"Tabela Bronze criada/atualizada: {BRONZE_TABLE}")

