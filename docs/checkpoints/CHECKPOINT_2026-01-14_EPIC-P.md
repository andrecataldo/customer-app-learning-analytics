# CHECKPOINT — EPIC P (Contextos e Dicionários)
Data: 2026-01-14

## Objetivo do checkpoint
Congelar o estado do contrato semântico (contextos e dicionários)
antes do início da ingestão Bronze do execution_log.

---

## Fonte de verdade
- Excel normativo: contexts_lrs_event_logs.xlsx
- Regra: 1 aba = 1 tabela
- Local: Files/context/raw

---

## Artefatos gerados

### CSVs (OneLake)
Files/context/tables/*.csv

Principais:
- dictionary_table_event_fields.csv
- table_event_categories.csv
- local_collection_*.csv
- lookup_table_*.csv
- global_tables_*.csv

### Delta Tables
Todas gravadas com prefixo `ctx_`

Exemplos:
- ctx_dictionary_table_event_fields
- ctx_table_event_categories
- ctx_global_tables_skills
- ctx_global_tables_onet_occupation_c

---

## Chaves Primárias (PK)
Validadas via:
- heurística (*_id)
- overrides explícitos

Resultado:
✅ Todas as tabelas possuem PK única e não-nula

---

## Manifest
- Arquivo: Files/context/manifest/manifest_ctx_v1.yml
- Função: contrato semântico oficial do pipeline

---

## Notebooks envolvidos
- nb_context_ingest_dictionaries → FINALIZADO (EPIC P)
- notebook_customer_app_bronze_ingest → LIMPO, pronto para EPIC 1

---

## Próximo passo planejado
Iniciar EPIC 1 — Bronze:
- Ingestão raw do execution_log_yyyymmdd.csv
- Schema 100% string
- Lineage: source_file, ingested_at

Nenhuma transformação semântica antes do Silver.
