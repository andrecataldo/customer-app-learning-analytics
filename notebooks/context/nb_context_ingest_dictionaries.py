#!/usr/bin/env python
# coding: utf-8

# ## nb_context_ingest_dictionaries
# 
# null

# ###### Notebook: nb_context_ingest_dictionaries
# ###### EPIC: EPIC P — Contextos e Dicionários
# ###### Fonte de verdade: Excel editor (1 aba = 1 tabela)
# ###### Contrato: ctx_manifest v1
# 

# ###### Status atual:
# - Última execução válida: 2026-01-14
# - Estado: consistente com contrato
# - Observações: 
# 

# ### Cell 0 - Imports

# In[1]:


from notebookutils import mssparkutils
import os, time, re
import pandas as pd
import yaml


# ### Cell 0.1 - Descobrir o arquivo .xlsx no path

# In[2]:


def ls(path):
    try:
        return mssparkutils.fs.ls(path)
    except Exception as e:
        print(f"ERR ls({path}): {type(e).__name__}: {str(e)[:160]}")
        return []

# 1) O que existe na raiz Files/
root = "Files"
print("Listing:", root)
items = ls(root)
for it in items:
    print(it.name, "=>", it.path)

# 2) Procurar recursivamente (até 4 níveis) por xlsx
def find_xlsx(start="Files", max_depth=4):
    found = []
    queue = [(start, 0)]
    while queue:
        p, d = queue.pop(0)
        if d > max_depth:
            continue
        for it in ls(p):
            if it.name.lower().endswith(".xlsx"):
                found.append(it.path)
            # desce em diretórios (heurística: path termina com "/")
            # no Fabric, pastas aparecem como item; vamos tentar ls nelas
            if not it.name.lower().endswith(".xlsx"):
                # tenta descer, mas evita arquivos
                if "." not in it.name:  # heurística simples p/ folder
                    queue.append((it.path, d+1))
    return found

xlsx_paths = find_xlsx("Files", max_depth=6)
print("\nXLSX encontrados:")
for p in xlsx_paths:
    print(" -", p)


# ### Cell 1 - copiar XLSX do OneLake para /tmp

# In[3]:


XLSX_ABFSS_PATH = "abfss://2cbaa9e1-98cf-42dd-a24e-10fa9f320b27@onelake.dfs.fabric.microsoft.com/7e814e70-a45d-4e26-b424-424df8549780/Files/context/raw/contexts_lrs_event_logs.xlsx"
LOCAL_XLSX_PATH = "/tmp/contexts_lrs_event_logs.xlsx"

t0 = time.time()
mssparkutils.fs.cp(XLSX_ABFSS_PATH, f"file:{LOCAL_XLSX_PATH}", True)
print(f"OK: copied to {LOCAL_XLSX_PATH} in {time.time()-t0:.2f}s")


# ### Cell 2 - abrir workbook e listar abas

# In[4]:


t0 = time.time()
xls = pd.ExcelFile(LOCAL_XLSX_PATH, engine="openpyxl")
print(f"OK: opened in {time.time()-t0:.2f}s")
print("Sheets:", len(xls.sheet_names))
print(xls.sheet_names)


# ### Cell 3 - export 1 CSV por aba para Files/context/tables/

# In[5]:


OUT_DIR = "Files/context/tables"

def to_table_key(sheet_name: str) -> str:
    s = sheet_name.strip().lower()
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

# cria pasta de saída
try:
    mssparkutils.fs.mkdirs(OUT_DIR)
except Exception:
    pass

exports = []

for s in xls.sheet_names:
    df = xls.parse(s)

    # remove colunas "Unnamed" e colunas 100% vazias
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed")]
    df = df.dropna(axis=1, how="all")

    # pula abas vazias
    if df.shape[0] == 0 and df.shape[1] == 0:
        print("SKIP empty:", s)
        continue

    table_key = to_table_key(s)
    tmp_csv = f"/tmp/{table_key}.csv"
    out_csv = f"{OUT_DIR}/{table_key}.csv"

    df.to_csv(tmp_csv, index=False, encoding="utf-8")
    mssparkutils.fs.cp(f"file:{tmp_csv}", out_csv, True)

    exports.append((s, table_key, out_csv, df.shape))
    print(f"OK: {s} -> {out_csv} shape={df.shape}")

print("\nTOTAL exports:", len(exports))


# ### Cell 4 - gravar como Delta (ctx_*)

# In[6]:


def normalize_colname(c: str) -> str:
    c = str(c).strip().lower()
    c = re.sub(r"\s+", "_", c)              # espaços -> _
    c = re.sub(r"[^\w]", "_", c)            # tudo não-alfanum -> _
    c = re.sub(r"_+", "_", c).strip("_")    # colapsa ___ e tira _ das pontas
    return c or "col"

def dedupe_cols(cols):
    seen = {}
    out = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            out.append(c)
        else:
            seen[c] += 1
            out.append(f"{c}_{seen[c]+1}")
    return out

for sheet_name, table_key, out_csv, shape in exports:
    df = pd.read_csv(f"/tmp/{table_key}.csv")

    # normaliza nomes de coluna
    new_cols = [normalize_colname(c) for c in df.columns]
    new_cols = dedupe_cols(new_cols)
    df.columns = new_cols

    spark_df = spark.createDataFrame(df)

    delta_table = f"ctx_{table_key}"
    spark_df.write.format("delta").mode("overwrite").saveAsTable(delta_table)

    print(f"OK: saved Delta {delta_table} ({shape})")


# ### Cell 4.1 - gerar “column_mapping” e salvar em Delta

# In[7]:


def normalize_colname(c: str) -> str:
    c = str(c).strip().lower()
    c = re.sub(r"\s+", "_", c)
    c = re.sub(r"[^\w]", "_", c)
    c = re.sub(r"_+", "_", c).strip("_")
    return c or "col"

def dedupe_cols(cols):
    seen = {}
    out = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            out.append(c)
        else:
            seen[c] += 1
            out.append(f"{c}_{seen[c]+1}")
    return out

rows = []
for sheet_name, table_key, out_csv, shape in exports:
    df0 = xls.parse(sheet_name)  # pega headers originais direto do Excel
    orig_cols = [str(c).strip() for c in df0.columns]
    norm_cols = dedupe_cols([normalize_colname(c) for c in orig_cols])

    ctx_table = f"ctx_{table_key}"
    for o, n in zip(orig_cols, norm_cols):
        rows.append({
            "sheet_name": sheet_name,
            "table_key": table_key,
            "ctx_table": ctx_table,
            "original_column": o,
            "normalized_column": n
        })

df_map = pd.DataFrame(rows)
spark.createDataFrame(df_map).write.format("delta").mode("overwrite").saveAsTable("ctx__column_mapping")

print("OK: saved ctx__column_mapping", df_map.shape)


# ### Cell 5 - Validação leve de PK (onde fizer sentido)

# In[8]:


def infer_pk(cols):
    # heurística simples: qualquer coluna terminando em _id
    id_cols = [c for c in cols if c.endswith("_id")]
    return id_cols[0] if id_cols else None

print("=== PK SANITY CHECK (heurístico) ===")

for sheet_name, table_key, out_csv, shape in exports:
    df = pd.read_csv(f"/tmp/{table_key}.csv")
    pk = infer_pk(list(df.columns))

    if not pk:
        print(f"INFO: {table_key} → sem coluna *_id (PK não inferida)")
        continue

    nulls = int(df[pk].isna().sum())
    dups = int(df[pk].duplicated().sum())

    if nulls == 0 and dups == 0:
        print(f"OK:   {table_key} → PK={pk} (unique, non-null)")
    else:
        print(f"ATTN: {table_key} → PK={pk} nulls={nulls} dups={dups}")


# ### Cell Extra 1 - Excel disponível localmente

# In[4]:


XLSX_ABFSS_PATH = "abfss://2cbaa9e1-98cf-42dd-a24e-10fa9f320b27@onelake.dfs.fabric.microsoft.com/7e814e70-a45d-4e26-b424-424df8549780/Files/context/raw/contexts_lrs_event_logs.xlsx"
LOCAL_XLSX_PATH = "/tmp/contexts_lrs_event_logs.xlsx"

mssparkutils.fs.cp(XLSX_ABFSS_PATH, f"file:{LOCAL_XLSX_PATH}", True)
print("OK: XLSX disponível em /tmp")


# ### Cell Extra 2 - Criar o objeto .xls

# In[5]:


xls = pd.ExcelFile(LOCAL_XLSX_PATH, engine="openpyxl")
print("OK: xls carregado")
print("Sheets:", xls.sheet_names)


# ### Cell Extra 3 - Reconstruir exports (em memória)

# In[6]:


OUT_DIR = "Files/context/tables"

def to_table_key(sheet_name: str) -> str:
    s = sheet_name.strip().lower()
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

exports = []

for s in xls.sheet_names:
    df = xls.parse(s)

    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed")]
    df = df.dropna(axis=1, how="all")

    if df.shape[0] == 0 and df.shape[1] == 0:
        continue

    table_key = to_table_key(s)
    exports.append((s, table_key, f"{OUT_DIR}/{table_key}.csv", df.shape))

print("OK: exports rebuilt =", len(exports))


# ### Cell Extra 4 - PK SANITY CHECK

# In[7]:


PK_OVERRIDES = {
    "global_tables_onet_occupation_c": "onet_occupation_code",
}

def infer_pk(cols):
    id_cols = [c for c in cols if c.endswith("_id")]
    return id_cols[0] if id_cols else None

print("=== PK SANITY CHECK v2 (override + heurística) — lendo via cp ===")

for sheet_name, table_key, out_csv, shape in exports:
    tmp = f"/tmp/{table_key}.csv"
    mssparkutils.fs.cp(out_csv, f"file:{tmp}", True)   # copia do OneLake p/ /tmp
    df = pd.read_csv(tmp)

    cols = list(df.columns)
    pk = PK_OVERRIDES.get(table_key) or infer_pk(cols)

    if not pk or pk not in cols:
        print(f"INFO: {table_key} → PK não definida")
        continue

    nulls = int(df[pk].isna().sum())
    dups  = int(df[pk].duplicated().sum())

    if nulls == 0 and dups == 0:
        print(f"OK:   {table_key} → PK={pk} (unique, non-null)")
    else:
        print(f"ATTN: {table_key} → PK={pk} nulls={nulls} dups={dups}")


# ### Cell Extra 5 - PK não definida

# In[8]:


no_pk = [x for x in exports if x[1].startswith("local_collection_") or x[1].startswith("lists_")]

for sheet_name, table_key, out_csv, shape in no_pk:
    tmp = f"/tmp/{table_key}.csv"
    mssparkutils.fs.cp(out_csv, f"file:{tmp}", True)
    df = pd.read_csv(tmp)
    print(f"\n{table_key} cols=", df.columns.tolist(), "shape=", df.shape)
    display(df.head(5))


# ### Cell Extra 6 - Inspecionar e sugerir PK natural 

# In[9]:


CANDIDATES_PRIORITY = ["id", "code", "value", "key", "name", "label"]

def suggest_pk(cols):
    cols_l = [c.lower().strip() for c in cols]
    # match exato primeiro
    for cand in CANDIDATES_PRIORITY:
        if cand in cols_l:
            return cols[cols_l.index(cand)]
    # depois match por sufixo/prefixo
    for cand in CANDIDATES_PRIORITY:
        for i, c in enumerate(cols_l):
            if c.endswith(f"_{cand}") or c.startswith(f"{cand}_"):
                return cols[i]
    return None

print("=== PK NATURAL SUGGEST (local_collection_* + lists_*) ===")

pk_suggestions = {}

targets = [x for x in exports if x[1].startswith("local_collection_") or x[1].startswith("lists_")]

for sheet_name, table_key, out_csv, shape in targets:
    tmp = f"/tmp/{table_key}.csv"
    mssparkutils.fs.cp(out_csv, f"file:{tmp}", True)
    df = pd.read_csv(tmp)

    pk = suggest_pk(df.columns.tolist())
    if not pk:
        print(f"INFO: {table_key} → sem candidato óbvio (cols={df.columns.tolist()})")
        continue

    nulls = int(df[pk].isna().sum())
    dups = int(df[pk].duplicated().sum())

    status = "OK" if (nulls == 0 and dups == 0) else "ATTN"
    print(f"{status}: {table_key} → PK_natural={pk} nulls={nulls} dups={dups}")

    pk_suggestions[table_key] = pk

print("\nSUGESTÕES (para PK_OVERRIDES):")
print(pk_suggestions)


# ### Cell Extra 7 - Aplicar overrides

# In[10]:


import pandas as pd
from notebookutils import mssparkutils

# começa com o que já é verdade do domínio
PK_OVERRIDES = {
    "global_tables_onet_occupation_c": "onet_occupation_code",
}

# adiciona sugestões automáticas (Opção A)
PK_OVERRIDES.update(pk_suggestions)

def infer_pk(cols):
    id_cols = [c for c in cols if c.endswith("_id")]
    return id_cols[0] if id_cols else None

print("=== PK SANITY CHECK v3 (overrides completos + heurística) ===")

for sheet_name, table_key, out_csv, shape in exports:
    tmp = f"/tmp/{table_key}.csv"
    mssparkutils.fs.cp(out_csv, f"file:{tmp}", True)
    df = pd.read_csv(tmp)
    cols = list(df.columns)

    pk = PK_OVERRIDES.get(table_key) or infer_pk(cols)

    if not pk or pk not in cols:
        print(f"INFO: {table_key} → PK não definida")
        continue

    nulls = int(df[pk].isna().sum())
    dups  = int(df[pk].duplicated().sum())

    if nulls == 0 and dups == 0:
        print(f"OK:   {table_key} → PK={pk} (unique, non-null)")
    else:
        print(f"ATTN: {table_key} → PK={pk} nulls={nulls} dups={dups}")


# ### Cell 6 - Gerar manifest.yml v1 no OneLake

# In[11]:


MANIFEST_DIR = "Files/context/manifest"
MANIFEST_PATH = f"{MANIFEST_DIR}/manifest_ctx_v1.yml"

# usa o PK_OVERRIDES que você já tem no notebook (v3)
# e ainda garante fallback na heurística caso apareça tabela nova
def infer_pk(cols):
    id_cols = [c for c in cols if c.endswith("_id")]
    return id_cols[0] if id_cols else None

entries = []
for sheet_name, table_key, out_csv, shape in exports:
    # ler csv via cp para obter colunas (sem depender de /tmp prévio)
    tmp = f"/tmp/{table_key}.csv"
    mssparkutils.fs.cp(out_csv, f"file:{tmp}", True)
    df = pd.read_csv(tmp)

    cols = df.columns.tolist()
    pk = PK_OVERRIDES.get(table_key) or infer_pk(cols)

    entries.append({
        "table_key": table_key,
        "sheet_name": sheet_name,
        "primary_key": pk,
        "csv_path": out_csv,
        "delta_table": f"ctx_{table_key}",
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": cols
    })

manifest = {
    "manifest_name": "ctx_tables",
    "version": "v1",
    "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "source_excel": "Files/context/raw/contexts_lrs_event_logs.xlsx",
    "tables": entries
}

# garantir diretório
try:
    mssparkutils.fs.mkdirs(MANIFEST_DIR)
except Exception:
    pass

# escrever YAML local e copiar para OneLake
local_yaml = "/tmp/manifest_ctx_v1.yml"
with open(local_yaml, "w", encoding="utf-8") as f:
    yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True)

mssparkutils.fs.cp(f"file:{local_yaml}", MANIFEST_PATH, True)
print("OK: manifest salvo em:", MANIFEST_PATH)

