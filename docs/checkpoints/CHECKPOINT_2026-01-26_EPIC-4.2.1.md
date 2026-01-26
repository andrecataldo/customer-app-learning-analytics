# CHECKPOINT — EPIC 4.2.1  
## Meeting Unknown Qualification (Semantic Coverage orientado a evidência)

**Projeto:** Customer App Learning Analytics (Microsoft Fabric + Lakehouse)  
**Data:** 26/01/2026  
**EPIC:** 4 — Gold Hardening & Semantic Coverage  
**Sub-tarefa:** 4.2.1 — Qualificação estrutural de *meeting unknown* (sem redução)  
**Status:** ✅ Concluído  

---

## 1. Contexto

Após o hardening do Gold Layer realizado no EPIC 4.1.1, permaneceu uma parcela
significativa de eventos classificados como `category_unknown`, especialmente
na família de eventos *meeting*.

O EPIC 4.2.1 foi concebido para **qualificar** esses eventos, isto é, explicar
**por que** permanecem como unknown, **sem alterar a classificação semântica**
(`category_id`) e **sem introduzir inferência não suportada por evidência**.

Este passo é fundamental tanto para:
- rigor acadêmico (explanação de limites do dado), quanto para
- decisões técnicas futuras sobre viabilidade de *semantic recovery*.

---

## 2. Objetivo do EPIC 4.2.1

> Qualificar eventos `meeting` classificados como `category_unknown`,
> identificando causas estruturais e semânticas de ausência de classificação,
> sem reduzir `category_unknown`.

---

## 3. Abordagem Metodológica

### 3.1 Princípios adotados

- Nenhuma alteração em `category_id`
- Nenhuma inferência heurística
- Qualificação baseada apenas em evidência observável no dado
- Implementação **views-only**, compatível com restrições do SQL Endpoint

### 3.2 Estratégia técnica

1. Utilização da view `vw_execution_events_v2` (overlay auditável do EPIC 4.1.1)
2. Criação de um novo overlay analítico (`vw_execution_events_v3`) contendo:
   - `meeting_unknown_flag`
   - `meeting_unknown_type`
   - `meeting_unknown_note`
3. Classificação determinística dos eventos unknown em subtipos explicativos
4. Construção de métricas de *health* e diagnósticos de contribuição

---

## 4. Subtipos de *meeting unknown*

Os eventos `meeting` com `category_unknown` foram classificados nos seguintes
subtipos:

| Subtipo | Descrição |
|------|-----------|
| `STRUCTURAL_CODE_PLACEHOLDER` | `meeting_code = 'CODIGO'`, indicando placeholder ou ausência estrutural de informação |
| `NO_SCO_CATEGORIES` | Ausência de `sco_categories`, indicando falta de dicionário semântico |
| `OTHER_UNKNOWN` | Casos residuais sem evidência suficiente para classificação |

---

## 5. Resultados Empíricos

### 5.1 Distribuição por subtipo (Health v3)

| meeting_unknown_type | rows | share |
|----------------------|------:|------:|
| STRUCTURAL_CODE_PLACEHOLDER | 36.580 | 66,6% |
| NO_SCO_CATEGORIES | 18.359 | 33,4% |

**Interpretação:**  
A maioria dos eventos unknown decorre de **ausência estrutural de informação
no dado de origem**, e não de ambiguidade semântica.

---

### 5.2 Contribuição por `meeting_code`

O código genérico `meeting_code = 'CODIGO'` responde isoladamente por
**66,6%** dos eventos unknown.  
Os demais códigos apresentam uma distribuição em cauda longa, nenhum deles
superando 8% individualmente.

---

### 5.3 Potencial máximo de *semantic recovery*

| Métrica | Valor |
|------|------:|
| meeting_unknown_rows | 54.939 |
| non_placeholder_rows | 18.359 |
| non_placeholder_ratio | 33,4% |

**Conclusão importante:**  
Mesmo em um cenário hipotético ideal, no qual todos os eventos non-placeholder
fossem semanticamente recuperáveis, o limite superior teórico de redução de
`category_unknown` para eventos *meeting* seria **~33%**.

---

## 6. Interpretação e Implicações

Os resultados do EPIC 4.2.1 demonstram que:

- `category_unknown` não é um erro do modelo, mas um **reflexo fiel das
  limitações do dado de origem**
- A maior parte do unknown é **irredutível sem enriquecimento externo**
- Qualquer tentativa de redução sem contexto adicional violaria o rigor
  metodológico do estudo

Dessa forma, a redução adicional de `category_unknown` depende exclusivamente
da existência de **dicionários externos confiáveis** que atribuam significado
semântico explícito aos `meeting_code` não genéricos.

---

## 7. Critérios de Aceite — Avaliação Final

| Critério | Status |
|--------|--------|
| Qualificação explícita de `meeting unknown` | ✅ |
| Subtipos explicáveis e auditáveis | ✅ |
| Nenhuma alteração em `category_id` | ✅ |
| Evidência empírica do limite de recovery | ✅ |
| Base objetiva para decisão futura (EPIC 4.2.2) | ✅ |

**EPIC 4.2.1: APROVADO**

---

## 8. Próximos Passos

- **EPIC 4.2.2 — Semantic Recovery via Contexto Externo (Stand by)**
  - Execução condicionada à obtenção de dicionário externo confiável
  - Sem compromisso prévio de redução percentual
- Consolidação deste checkpoint como insumo direto para:
  - seção de *Resultados Preliminares* do TCC
  - discussão de limitações do dado

---

📌 *Checkpoint fechado com base em evidência empírica, reforçando rigor
metodológico e transparência científica.*
