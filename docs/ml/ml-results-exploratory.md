# EPIC 6 — Resultados exploratórios (Clusterização não supervisionada)

## Resumo executivo
A segmentação foi realizada por aluno (`user_id`) usando indicadores agregados de **participação** e **desempenho**. Um caso extremo de participação (≈90k eventos) dominou a solução inicial (k=2 → **392 vs 1**), caracterizando detecção de outlier; por isso, esse caso foi tratado separadamente e a clusterização foi recalculada no conjunto remanescente. No subconjunto combinado (participação × desempenho), a PCA indicou forte estrutura latente no desempenho (**2 componentes explicam ~92,5% da variância**). A escolha de k considerou *silhouette* e dendrograma (Ward): k=5 maximizou *silhouette*, porém gerou cluster unitário; k=4 foi adotado como solução principal por maior **interpretabilidade pedagógica**. Foram identificados quatro perfis: (1) participante regular com desempenho em desenvolvimento, (2) alto desempenho com participação enxuta, (3) engajado intensivo com alto desempenho e (4) alta participação com baixa competência socioargumentativa.

---

## 1. Base analítica e pré-processamento
A base analítica foi agregada por aluno (`user_id`) a partir do snapshot `vw_user_features_v1.csv` (393 linhas × 13 colunas), contendo:
- **Participação:** `total_events`, `days_active`, `events_per_day`, contagens por família (`total_meetings`, `total_interactions`, `total_tech_questions`, `total_risk_assessments`), e `pct_unknown_category`.
- **Desempenho:** médias das dimensões `technicalAbility`, `attitude`, `argumentation`, `articulation`, `negotiation`.

Tratamentos aplicados:
- **Assimetria em participação:** *winsorization* (cap p99) + transformação `log1p(total_events_cap_p99)`.
- **Ausência de avaliação codificada como 0:** valores 0 nas dimensões socioargumentativas foram tratados como ausentes (NaN).
- **Imputação para PCA/KMeans:** imputação por **mediana** (robusta), seguida de padronização (*StandardScaler*).

---

## 2. Caso extremo e ajuste do procedimento
Na clusterização inicial da participação (A), k=2 obteve *silhouette* muito alto, mas a distribuição dos clusters foi **392 vs 1**, indicando que o agrupamento estava capturando essencialmente um **caso extremo isolado**, e não perfis pedagógicos. Por esse motivo, o caso extremo foi tratado separadamente e a clusterização foi recalculada sem esse ponto (A_no/C_no).

---

## 3. PCA no desempenho (B)
A PCA aplicada às dimensões de desempenho (após imputação e padronização) mostrou que as duas primeiras componentes explicam **~92,5% da variância** (PC1 ≈ 0,81; PC2 ≈ 0,12), sugerindo forte colinearidade entre as dimensões avaliativas e boa adequação de visualização em 2D.

---

## 4. Escolha do número de clusters (C_no): k e validação
No conjunto combinado (participação × desempenho), o melhor *silhouette* foi observado em **k=5**, porém essa solução gerou **cluster unitário** (1 observação), o que reduz utilidade interpretativa como “perfil pedagógico”. A inspeção do **dendrograma hierárquico (Ward)** indicou estrutura consistente também com **k=4**, que foi adotado como solução principal para interpretação pedagógica.

- **k=4:** silhouette = **0,3541**
- **k=5:** silhouette = **0,3673** (referência técnica, porém com cluster unitário)

---

## 5. Distribuição por perfil (k=4)
| perfil | n |
|---|---:|
| Participante regular / Desempenho em desenvolvimento | 43 |
| Alto desempenho / Participação enxuta | 21 |
| Engajado intensivo / Alto desempenho | 7 |
| Alta participação / Baixa competência socioargumentativa | 5 |

---

## 6. Centroides por perfil (k=4) — escala original
> Observação: os valores abaixo correspondem aos centroides do KMeans em k=4 no conjunto C_no (sem o caso extremo).

| cluster | perfil | log_total_events_cap_p99 | days_active | events_per_day | total_meetings | total_interactions | total_tech_questions | total_risk_assessments | pct_unknown_category | technicalAbility_avg | attitude_avg | argumentation_avg | articulation_avg | negotiation_avg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | Participante regular / Desempenho em desenvolvimento | 3.813111 | 1.883721 | 29.773256 | 38.093023 | 5.790698 | 2.558140 | 0.000000 | 1.0 | 1.839147 | 1.800388 | 1.860465 | 1.852713 | 1.823643 |
| 1 | Engajado intensivo / Alto desempenho | 4.894135 | 3.428571 | 45.247619 | 71.428571 | 15.857143 | 53.285714 | 1.428571 | 1.0 | 2.326531 | 2.387755 | 2.367347 | 2.326531 | 2.326531 |
| 2 | Alto desempenho / Participação enxuta | 3.805602 | 1.380952 | 36.269841 | 36.047619 | 5.142857 | 3.952381 | 0.000000 | 1.0 | 2.404762 | 2.369048 | 2.444444 | 2.444444 | 2.412698 |
| 3 | Alta participação / Baixa competência socioargumentativa | 4.867977 | 7.666667 | 33.253831 | 65.833333 | 26.166667 | 35.166667 | 5.833333 | 1.0 | 2.273810 | 1.264881 | 1.264881 | 1.264881 | 1.264881 |

---

## 7. Assinatura resumida por perfil (k=4)
| perfil | intensidade (log_total_events) | regularidade (days_active) | desempenho técnico (technicalAbility_avg) | socioargumentativo (médias) |
|---|---:|---:|---:|---|
| Participante regular / Desempenho em desenvolvimento | 3.81 | 1.88 | 1.84 | baixo (≈1.80–1.86) |
| Alto desempenho / Participação enxuta | 3.81 | 1.38 | 2.40 | alto (≈2.37–2.44) |
| Engajado intensivo / Alto desempenho | 4.89 | 3.43 | 2.33 | alto (≈2.33–2.39) |
| Alta participação / Baixa competência socioargumentativa | 4.87 | 7.67 | 2.27 | baixo (≈1.26) |

---

## 8. Interpretação pedagógica e implicações por perfil (fase D)

### Perfil 1 — Participante regular / Desempenho em desenvolvimento
**Leitura:** participação moderada, baixa evidência de interação/consulta e desempenho inferior nas dimensões avaliativas.  
**Implicações (ações):**
- *scaffolding* + microfeedback (rubricas, exemplos guiados, checkpoints curtos);
- estímulo à verbalização do raciocínio (orientar uso de perguntas técnicas e interações para explicitar dúvidas).

### Perfil 2 — Alto desempenho / Participação enxuta
**Leitura:** alto desempenho com baixa necessidade de interação; perfil autônomo/objetivo.  
**Implicações (ações):**
- oferecer trilhas avançadas e desafios de maior complexidade;
- convidar para contribuição em *peer learning* (respostas, exemplos, revisões).

### Perfil 3 — Engajado intensivo / Alto desempenho
**Leitura:** alta intensidade de participação e alto uso de perguntas técnicas, com desempenho elevado.  
**Implicações (ações):**
- incentivar papel de apoio ao grupo (aluno âncora/mentor leve);
- monitorar sobrecarga/ruído (alto volume de eventos pode indicar repetição/ansiedade).

### Perfil 4 — Alta participação / Baixa competência socioargumentativa
**Leitura:** alta participação e regularidade, desempenho técnico razoável, mas baixo desempenho persistente em argumentação/articulação/negociação.  
**Implicações (ações):**
- intervenção focada em comunicação (templates de argumentação, prática guiada, rubricas);
- aprendizagem em pares (duplas com perfis de alto socioargumentativo, com tarefas de explicação/negociação).

---

## 9. Observação sobre qualidade semântica (pct_unknown_category)
O `pct_unknown_category` permaneceu elevado (≈1,0) em todos os clusters, sugerindo limitações de mapeamento semântico de categorias. Essa restrição reduz interpretações “por conteúdo”, mas não inviabiliza a segmentação baseada em intensidade de participação e desempenho. Como trabalho futuro, recomenda-se ampliar a cobertura de categorização e reavaliar perfis incluindo indicadores semânticos mais ricos.