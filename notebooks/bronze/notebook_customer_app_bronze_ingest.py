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

# In[3]:


from notebookutils import mssparkutils
import pandas as pd
from datetime import datetime, timezone
from pyspark.sql import Row
from pyspark.sql import functions as F


# ### Cell 1 - Parâmetros

# In[4]:


# ===== Parâmetros =====

EXEC_FILE = "execution_log_20260107.csv"  # caminho do CSV no OneLake
BRONZE_DIR = "Files/bronze/execution_log"
BRONZE_TABLE = "bronze_execution_log"  # nome da tabela Bronze
SRC_PATH = f"{BRONZE_DIR}/{EXEC_FILE}"
LOCAL_PATH = f"/tmp/{EXEC_FILE}"
HAS_HEADER = False  # mudar para False se o CSV não tiver cabeçalho


# ### Cell 2 - Leitura (CSV → DataFrame)

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


# ### Cell 3 - Gravação como Tabela Delta

# In[6]:


# ===== Gravar Bronze como tabela Delta gerenciada =====

spark_df = spark.createDataFrame(df)

spark_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(BRONZE_TABLE)

print(f"Tabela Bronze criada/atualizada: {BRONZE_TABLE}")
print("OK: ", spark_df.count())



# ### Cell Epic 1.2-A - Snapshot do schema + contagens básicas

# In[5]:


t = spark.table(BRONZE_TABLE)

print("=== BRONZE SNAPSHOT ===")
print("rows =", t.count())
print("cols =", len(t.columns))
print("first 25 cols =", t.columns[:25])

# schema (prova de string-only)
t.printSchema()

# contagem por source_file (se já tiver mais de um arquivo)
if "source_file" in t.columns:
    (t.groupBy("source_file").count()
      .orderBy(F.desc("count"))
      .show(50, truncate=False))
else:
    print("WARN: source_file não existe (lineage incompleto).")


# ### Cell Epic 1.2-B - Perfil de completude (null/empty) para colunas-chave

# In[6]:


KEY_COLS_CANDIDATES = [
    "event_date", "event_time", "event_ts",
    "user_id", "registration_id", "sco_id",
    "interaction_id", "meeting_id",
    "event_name", "event_type"
]

cols = [c for c in KEY_COLS_CANDIDATES if c in t.columns]
print("Cols avaliadas:", cols)

def is_empty(c):
    return (F.col(c).isNull()) | (F.trim(F.col(c)) == "")

metrics = []
total = t.count()

for c in cols:
    null_or_empty = t.filter(is_empty(c)).count()
    metrics.append((c, null_or_empty, total, round(null_or_empty/total, 4)))

df_metrics = spark.createDataFrame(metrics, ["col", "null_or_empty", "total", "pct"])
display(df_metrics.orderBy(F.desc("pct")))


# ### Cell Epic 1.2-C - Distribuições úteis (cardinalidade e top values)

# In[7]:


def show_top(col, n=20):
    if col in t.columns:
        print(f"\n=== TOP {n} — {col} ===")
        (t.groupBy(col).count()
          .orderBy(F.desc("count"))
          .show(n, truncate=False))
    else:
        print(f"INFO: coluna {col} não existe.")

for c in ["user_id", "registration_id", "sco_id", "interaction_id", "meeting_id"]:
    show_top(c, 20)


# ### Cell Epic 1.2-D - Checar duplicidade “bruta” (linha inteira)

# In[8]:


# hash da linha toda (exceto campos de lineage, se existirem)
exclude = set([c for c in ["source_file", "ingested_at_utc"] if c in t.columns])
cols_for_hash = [c for c in t.columns if c not in exclude]

t_hash = t.withColumn("row_hash", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c), F.lit("")) for c in cols_for_hash]), 256))

dup = (t_hash.groupBy("row_hash").count()
       .filter(F.col("count") > 1)
       .orderBy(F.desc("count")))

print("rows com hash duplicado =", dup.count())
dup.show(20, truncate=False)


# - ### Cell Epic 1.2-E - Evidência de “explosão por join” (proxy)
# Preocupação com “wide derivado de join SQL”. 
# 
# Busco por:
# - muitos registros por registration_id
# - muitos registros por user_id+event_date
# - valores repetidos em blocos

# In[9]:


if "registration_id" in t.columns:
    print("\n=== Distribuição por registration_id ===")
    reg = t.groupBy("registration_id").count()
    reg.describe("count").show()

    reg.orderBy(F.desc("count")).show(20, truncate=False)
else:
    print("INFO: sem registration_id para analisar explosão.")

if "user_id" in t.columns and "event_date" in t.columns:
    print("\n=== Linhas por user_id + event_date (top) ===")
    (t.groupBy("user_id", "event_date").count()
      .orderBy(F.desc("count"))
      .show(30, truncate=False))

