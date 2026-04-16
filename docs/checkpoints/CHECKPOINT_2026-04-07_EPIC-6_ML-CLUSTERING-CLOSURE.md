# 📌 CHECKPOINT - EPIC 6: Machine Learning Não Supervisionado (Fechamento)

**Data:** 2026-04-07  
**Status:** ✅ CONCLUÍDO  
**Responsável:** Andre Cataldo  

---

## 🎯 Objetivo do EPIC

Realizar análise exploratória não supervisionada para identificação de perfis de alunos com base em dimensões de desempenho, utilizando dados derivados de registros xAPI/LRS.

---

## 🧠 Decisões metodológicas consolidadas

- Unidade de análise: **aluno (`user_id`)**
- Base analítica: agregação de **101.802 eventos → 77 alunos válidos**
- Variáveis de clusterização: **5 dimensões de desempenho**
  - `technicalAbility`
  - `attitude`
  - `argumentation`
  - `articulation`
  - `negotiation`
- Variáveis de participação:
  - utilizadas **apenas como apoio descritivo complementar**
  - não incluídas na clusterização

📌 Racional:
- evitar viés por volume de atividade
- preservar foco analítico em desempenho

---

## 🔄 Pipeline analítico executado

### 1. Preparação da base
- transformação do nível de evento → nível do aluno
- construção de indicadores agregados

### 2. Elegibilidade analítica
- filtro de dados válidos de desempenho
- aplicação de critérios mínimos
- remoção de outlier extremo (~90k eventos em 1 dia)
- base final: **77 alunos**

### 3. Análise exploratória (PCA)
- aplicação de Análise de Componentes Principais
- resultado:
  - **~92,5% da variabilidade explicada pelos 2 primeiros componentes**

📌 Uso:
- inspeção da estrutura dos dados
- não utilizado diretamente na clusterização

---

### 4. Clusterização

#### Método principal:
- **K-Means**

#### Avaliação de soluções:
- métrica: **silhouette**

| k | silhouette | observação |
|---|-----------|-----------|
| 5 | ~0,367 | presença de cluster unitário |
| 4 | ~0,354 | melhor interpretabilidade |

📌 Decisão:
- escolha de **k = 4**

#### Método complementar:
- análise hierárquica (Ward)
- uso:
  - apoio visual (dendrograma)
  - não utilizado como solução final

---

## 📊 Resultado final

Identificação de **4 perfis de alunos**, com base nas dimensões de desempenho:

1. Desempenho intermediário com participação regular  
2. Alto desempenho com menor participação observada  
3. Alto desempenho com maior participação observada  
4. Desempenho mais baixo em argumentação e comunicação  

📌 Interpretação:
- clusters definidos exclusivamente por desempenho
- participação utilizada posteriormente para enriquecimento descritivo

---

## ⚠️ Limitações reconhecidas

- base reduzida após critérios de elegibilidade
- forte assimetria estrutural dos eventos (`meeting` predominante)
- natureza exploratória da técnica
- ausência de inferência causal

---

## ✅ Critério de aceite

- [x] pipeline reprodutível
- [x] decisão de `k` justificada
- [x] perfis interpretáveis
- [x] coerência com objetivo do estudo
- [x] integração com narrativa do TCC

---

## 📦 Entregáveis do EPIC

- dataset analítico final (nível aluno)
- definição dos clusters (`k = 4`)
- centróides dos grupos
- estatísticas descritivas por perfil
- base para seção de Resultados e Discussão do TCC

---

## 🔐 Status final

EPIC 6 concluído com sucesso, com resultados consolidados e integrados à versão v1.6 do TCC.