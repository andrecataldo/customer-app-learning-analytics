# Estratégia de Chaves — `event_key`
**Projeto:** Customer App – Learning Analytics  
**EPIC:** 0.2 — Definir estratégia de chaves (event_key)  
**Status:** 🟡 **Proposta (pré-EPIC 1.1)**  
**Camada alvo:** Silver (`sl_execution_log`)  

---

## 1. Contexto e Motivação

O dataset de origem `execution_log_yyymmdd.csv` **não contém um identificador único por evento**
(`event_id`). Para garantir rastreabilidade, deduplicação e possibilidade de relacionamento no
modelo analítico (Star Schema, ML, métricas), define-se uma **chave técnica derivada** denominada
`event_key`.

Esta estratégia estabelece **o contrato conceitual** da chave, **antes da implementação**,
que ocorrerá somente após a refatoração do pipeline de ingestão e normalização
(**EPIC 1.1 e EPIC 2.1**).

---

## 2. Natureza da `event_key`

- **Tipo:** identificador técnico derivado (fingerprint)
- **Determinística:** mesmo evento → mesma chave
- **Escopo:** unicidade *no contexto do dataset recebido*
- **Finalidade:**
  - deduplicação técnica
  - relacionamento analítico
  - base para métricas e ML

> ⚠️ Importante: `event_key` **não é um identificador de negócio**, e sim um identificador técnico
derivado, conforme boas práticas em Learning Analytics e Data Engineering.

---

## 3. Pré-requisitos para Implementação

A implementação da `event_key` **NÃO deve ocorrer** enquanto os itens abaixo não forem concluídos:

- **EPIC 1.1** — Refatoração do Bronze para leitura de `execution_log_yyymmdd.csv`
- **EPIC 2.1** — Silver com:
  - schema real estabilizado
  - campos tipados
  - criação de `event_ts` (timestamp unificado)
- Disponibilidade dos campos reais definidos neste contrato

Somente após esses pontos a implementação passa de *proposta* para *ativa*.

---

## 4. Estratégia Proposta (v1)

### 4.1 Princípio Geral

Gerar a `event_key` a partir de um **fingerprint estável do evento**, composto por um subconjunto
mínimo de campos **estruturais e temporais**, normalizados e concatenados, e então transformados
via hash determinístico.

---

### 4.2 Campos Propostos para o Fingerprint (v1)

#### Campos temporais
- `event_date`
- `event_time`

#### Identificadores principais
- `user_id`
- `organization_id`
- `registration_id`
- `sco_id`

#### Contexto de interação (quando existente)
- `interaction_id`
- `interaction_type`

> 📌 Campos de texto longo (ex.: `interaction_prompt_text`) **não entram na versão v1**
por risco de variação semântica, custo computacional e instabilidade.

---

### 4.3 Normalização Proposta

Antes da geração do fingerprint, cada campo deverá:

- ser convertido para string
- aplicar `trim`
- aplicar `lower` (quando aplicável)
- normalizar nulos e vazios para um token estável: `<null>`
- utilizar separador fixo: `|`

**Exemplo de fingerprint lógico (ilustrativo):**

`2026-01-07|10:15:03|u_123|org_9|reg_77|sco_5|int_55|attempted`


---

## 5. Algoritmo Proposto

- **Hash:** SHA-256
- **Campo final:** `event_key`
- **Versão:** `event_key_version = 'v1'`

A geração da chave deve ocorrer **exclusivamente na camada Silver**.

---

## 6. Campos Técnicos Associados

Para garantir auditabilidade e evolução controlada, a estratégia prevê:

| Campo | Tipo | Descrição |
|-----|-----|----------|
| `event_key` | string | Hash do fingerprint |
| `event_key_version` | string | Versão da estratégia |
| `event_fingerprint` | string | String normalizada usada no hash |

---

## 7. Riscos Conhecidos e Mitigações

### 7.1 Colisão Semântica
Eventos distintos podem gerar a mesma chave se todos os campos do fingerprint coincidirem.

**Mitigações previstas:**
- monitorar taxa de duplicidade
- evoluir fingerprint em versões futuras (v2, v3…)
- documentar mudanças no contrato

### 7.2 Colisão Criptográfica
Improvável no contexto do projeto (SHA-256). O risco relevante é o **semântico**, não o criptográfico.

---

## 8. Critérios de Validação (para ativação futura)

A estratégia só será considerada **ativa** quando:

- `event_key` não for nula
- taxa de duplicidade (`dup_rate`) for medida e registrada
- resultados forem documentados (log ou métrica)
- versão (`v1`) estiver explícita no dataset

---

## 9. Versionamento e Evolução

- Esta especificação define a **versão v1 (proposta)**.
- Mudanças futuras devem:
  - criar nova versão (`v2`, `v3`, …)
  - manter rastreabilidade
  - registrar impacto em métricas e ML

---

## 10. Status Atual

🟡 **Proposta aprovada conceitualmente**  
⏳ **Implementação adiada até conclusão do EPIC 1.1**
