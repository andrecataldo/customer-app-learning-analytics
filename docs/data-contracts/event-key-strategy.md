# Estratégia de Chaves — `event_key`
**Projeto:** Customer App – Learning Analytics  
**EPIC:** 0.2 — Definir estratégia de chaves (event_key)  
**Camada:** Silver (`sl_execution_log`)  

---

## 1. Contexto e Motivação

O dataset `execution_log_yyymmdd.csv` não contém um identificador único por evento (`event_id`).
Para garantir rastreabilidade, deduplicação e possibilidade de relacionamento no modelo analítico,
é definida uma chave técnica derivada: **`event_key`**.

A `event_key` é um **identificador técnico determinístico** (fingerprint), gerado a partir de um conjunto
de campos do evento após normalização mínima.

---

## 2. Definições

### 2.1 Chave técnica do evento
- **Nome:** `event_key`
- **Tipo:** string
- **Camada de geração:** Silver
- **Algoritmo:** hash determinístico (SHA-256)
- **Objetivo:** identificar univocamente um registro de evento *no contexto do dataset recebido*

### 2.2 Campos auxiliares de auditoria
- `event_key_version` (string): versão da estratégia de chave (ex.: `v1`)
- `event_fingerprint` (string): string concatenada (normalizada) usada como entrada do hash

---

## 3. Estratégia de Geração (v1)

### 3.1 Princípio
Gerar `event_key` como SHA-256 de um fingerprint estável:

`event_key = sha2(event_fingerprint, 256)`

### 3.2 Campos incluídos no fingerprint (v1)

#### Campos temporais (mínimos)
- `event_date`
- `event_time`

#### Identificadores (mínimos)
- `user_id`
- `organization_id`
- `registration_id`
- `sco_id`

#### Contexto de interação (quando presente)
- `interaction_id`
- `interaction_type`

> Nota: campos de texto longos (ex.: `interaction_prompt_text`) **não entram no MVP v1** por risco de variação
(whitespace, truncamento, mudanças de conteúdo) e custo. Eles podem ser incorporados em versões futuras.

### 3.3 Normalização aplicada (v1)
Antes de concatenar, cada campo passa por:

- `trim` (remoção de espaços)
- conversão para `lower` (quando aplicável)
- normalização de nulos: `NULL` e `""` viram um token estável `<null>`
- separador fixo: `|`

Exemplo de fingerprint:
`2026-01-07|10:15:03|u_123|org_9|reg_77|sco_5|int_55|attempted`

---

## 4. Riscos e Limitações

### 4.1 Colisão semântica (eventos diferentes com mesma chave)
Pode ocorrer se dois eventos compartilham exatamente os mesmos valores nos campos do fingerprint.
Mitigações:
- incluir mais campos em versões futuras (ex.: `registration_attempt`, `meeting_id`, etc.)
- monitorar duplicidade de `event_key` via checks de qualidade

### 4.2 Colisão criptográfica
Teoricamente possível, mas impraticável para SHA-256 no contexto do projeto. O risco relevante é o semântico.

---

## 5. Regras de Deduplicação

- A `event_key` é usada para detectar duplicatas no Silver/Gold.
- Política padrão (MVP):
  - manter 1 registro por `event_key`
  - em caso de duplicata: escolher o registro com maior `ingested_at`
  - registrar contagem de duplicatas em relatório/check

---

## 6. Testes e Checks (Obrigatórios)

### 6.1 Check de duplicidade
- Percentual de duplicatas:
  `dup_rate = (count(*) - count(distinct event_key)) / count(*)`

### 6.2 Check de completude
- Garantir que `event_key` não é nula.

---

## 7. Versionamento

- `event_key_version = 'v1'`
- Mudanças futuras devem:
  - atualizar a versão (v2, v3…)
  - registrar alteração no changelog
  - manter rastreabilidade e comparabilidade
