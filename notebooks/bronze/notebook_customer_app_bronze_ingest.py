#!/usr/bin/env python
# coding: utf-8

# ## notebook_customer_app_bronze_ingest
# 
# New notebook

# ###### Notebook: notebook_customer_app_bronze_ingest
# ###### EPIC: EPIC 1 - Bronze (Ingestão Raw Governada)
# ###### Fonte de verdade: execution_log_yyyymmdd.csv (derivado, imutável)
# ###### Contrato: schema string-only + lineage v1
# 

# ###### Status atual:
# - Última execução válida: 2026-01-14
# - Estado: consistente com contrato
# - Observações: 
# 

# ### Cell 0 - Imports

# In[2]:


from notebookutils import mssparkutils
import pandas as pd
from datetime import datetime, timezone
from pyspark.sql import Row


# ### Cell 1 — Parâmetros

# In[3]:


# ===== Parâmetros =====

EXEC_FILE = "execution_log_20260107.csv"  # caminho do CSV no OneLake
BRONZE_DIR = "Files/bronze/execution_log"
BRONZE_TABLE = "bronze_execution_log"  # nome da tabela Bronze
SRC_PATH = f"{BRONZE_DIR}/{EXEC_FILE}"
LOCAL_PATH = f"/tmp/{EXEC_FILE}"
HAS_HEADER = False  # mudar para False se o CSV não tiver cabeçalho


# ### Cell 2 — Leitura (CSV → DataFrame)

# In[5]:


# sanity: listar arquivos
files = mssparkutils.fs.ls(BRONZE_DIR)
print("Arquivos em", BRONZE_DIR)
for f in files:
    print("-", f.name)

# copiar para /tmp
mssparkutils.fs.cp(SRC_PATH, f"file:{LOCAL_PATH}", True)

# ler como string-only
df = pd.read_csv(
    LOCAL_PATH,
    sep=",",
    dtype=str,
    keep_default_na=False
)

# lineage
df["source_file"] = EXEC_FILE
df["ingested_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print("shape:", df.shape)
display(df.head(20))


# ### Cell 3 — Gravação como Tabela Delta

# In[6]:


# ===== Gravar Bronze como tabela Delta gerenciada =====

spark_df = spark.createDataFrame(df)

spark_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(BRONZE_TABLE)

print(f"Tabela Bronze criada/atualizada: {BRONZE_TABLE}")
print("OK: ", spark_df.count())


