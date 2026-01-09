# Naming Convention e Estrutura de Tabelas  
**Projeto:** Customer App – Learning Analytics  
**EPIC:** 0.1 — Preparação e Convenções  

Este documento define os padrões oficiais de nomenclatura e organização dos
artefatos de dados do projeto, garantindo consistência técnica, escalabilidade
e reprodutibilidade acadêmica.

---

## 1. Princípios Gerais

- Utilizar **snake_case** em todos os nomes.
- Não usar acentos, espaços ou caracteres especiais.
- Separar claramente **camada**, **tipo de objeto** e **domínio**.
- Priorizar nomes curtos, explícitos e semanticamente claros.
- Manter compatibilidade com **Spark, SQL Analytics e Power BI**.
- O GitHub é a **fonte da verdade conceitual**; o Fabric é o ambiente de execução.

---

## 2. Convenção de Camadas e Objetos

### 2.1 Prefixos por camada

| Camada | Prefixo | Descrição |
|------|--------|----------|
| Bronze | `br_` | Dados brutos governados, fiéis à fonte |
| Silver | `sl_` | Dados limpos, tipados e normalizados |
| Gold – Fato | `gd_fact_` | Tabelas fato para consumo analítico |
| Gold – Dimensão | `gd_dim_` | Tabelas dimensão (Star Schema) |
| Contexto / Dicionário | `ctx_` | Tabelas periféricas e contratos semânticos |
| Bridge (N:N) | `gd_bridge_` | Tabelas de relacionamento (quando necessário) |
| Views SQL | `vw_` | Views de consumo e métricas |

---

### 2.2 Tabelas principais (canônicas)

| Camada | Nome |
|------|-----|
| Bronze | `br_execution_log` |
| Silver | `sl_execution_log` |
| Gold (Fato) | `gd_fact_execution_events` |

---

## 3. Convenção de Colunas

### 3.1 Chaves e Identificadores

- Todos os identificadores terminam com `_id`.
- Identificadores são armazenados como **string**.

Exemplos:
- `user_id`
- `organization_id`
- `registration_id`
- `interaction_id`
- `meeting_id`
- `sco_id`

### 3.2 Chave Técnica do Evento

Como o arquivo de origem **não possui um ID único de evento**, é definida uma
chave técnica:

- **`event_key`**  
  - Tipo: string  
  - Gerada via **hash determinístico**  
  - Criada na camada **Silver**

A estratégia de geração é detalhada em: `docs/data-contracts/event-key-strategy.md`


---

### 3.3 Datas e Tempo

| Coluna | Tipo | Descrição |
|------|-----|----------|
| `event_date` | date | Data original do evento |
| `event_time` | string | Hora original do evento |
| `event_ts` | timestamp | Timestamp unificado (Silver+) |
| `event_day` | date | Data derivada (uso analítico) |
| `event_hour` | int | Hora derivada (uso analítico) |

---

### 3.4 Colunas Técnicas (Lineage / Auditoria)

Padronizadas principalmente na camada Bronze:

| Coluna | Tipo | Descrição |
|------|-----|----------|
| `source_file` | string | Nome do arquivo de origem |
| `ingested_at` | timestamp | Data/hora da ingestão |
| `row_number` | long | Posição do registro no arquivo (opcional) |
| `row_hash` | string | Hash do registro bruto (opcional) |

---

### 3.5 Valores Categóricos

- Campos categóricos utilizam sufixos explícitos:
  - `*_status`
  - `*_type`
- Exemplos:
  - `registration_status`
  - `interaction_type`

---

## 4. Regras por Camada

### 4.1 Bronze (`br_*`)
✔ Pode:
- adicionar colunas técnicas
- preservar registros inválidos (se necessário)

✖ Não pode:
- tipar semanticamente
- remover colunas da fonte

**Objetivo:** preservar o dado bruto com governança.

---

### 4.2 Silver (`sl_*`)
✔ Pode:
- tipar campos
- normalizar strings e vazios
- gerar `event_ts`, `event_key`

✖ Não pode:
- agregar dados
- aplicar métricas de negócio

**Objetivo:** dados limpos e consistentes.

---

### 4.3 Gold (`gd_*`, `vw_*`)
✔ Pode:
- estruturar fatos e dimensões
- criar métricas e agregações
- expor views para BI

**Objetivo:** consumo analítico e modelagem dimensional.

---

## 5. Notebooks (GitHub)

Os notebooks versionados no GitHub seguem o padrão: `nb_<camada><ação><dataset>.py`


### Exemplos oficiais:

| Camada | Notebook |
|-----|--------|
| Bronze | `nb_bronze_ingest_execution_log.py` |
| Silver | `nb_silver_transform_execution_log.py` |
| Gold | `nb_gold_build_execution_events.py` |
| Dimensions | `nb_dimensions_build.py` |
| Context | `nb_context_ingest_dictionaries.py` |

📌 No **Fabric**, os notebooks podem manter nomes históricos temporariamente.

---

## 6. Mapeamento Histórico (Antigo → Novo)

### 6.1 Fonte

| Antigo | Novo |
|-----|-----|
| `log-register-2025nov11.csv` | `execution_log_yyymmdd.csv` |

---

### 6.2 Tabelas

| Antigo | Novo |
|-----|-----|
| `log_register_bronze` | `br_execution_log` |
| `log_register_silver` | `sl_execution_log` |
| `log_register_gold_events` | `gd_fact_execution_events` |

---

### 6.3 Views

| Antigo | Novo |
|-----|-----|
| `vw_customer_app_events` | `vw_execution_events` |
| `vw_customer_app_daily_metrics` | `vw_daily_metrics` |

---

## 7. Decisões Registradas

- Dataset canônico: **execution_log**
- Chave técnica de evento: **event_key**
- Arquitetura em camadas: **Bronze → Silver → Gold**
- Modelagem analítica: **Star Schema**
- ML (quando aplicado): **exploratório, não supervisionado**

---

## 8. Status

✔ Naming convention definida  
✔ Estrutura de tabelas validada  
✔ EPIC 0.1 concluído



