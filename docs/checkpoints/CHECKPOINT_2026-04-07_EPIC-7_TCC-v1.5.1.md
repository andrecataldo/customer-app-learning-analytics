# CHECKPOINT_2026-04-07_EPIC-7_TCC-v1.5.1

## Metadados
- **Data:** 2026-04-07
- **Responsável:** Andre Cataldo
- **Projeto:** customer-app-learning-analytics
- **Epic:** EPIC 7 - TCC / Consolidação do texto final
- **Estado:** Em andamento
- **Versão de referência do TCC:** v1.5 / v1.5.1
- **Origem:** consolidação dos avanços realizados após múltiplas rodadas de revisão do TCC e feedbacks sucessivos da orientadora

---

## Objetivo deste checkpoint
Registrar o estado consolidado do trabalho após a evolução do texto do TCC até a versão v1.5 / v1.5.1, preservando:
- decisões metodológicas já congeladas;
- principais mudanças estruturais e conceituais realizadas;
- feedbacks centrais da orientadora;
- pendências para a próxima iteração (v1.5.2).

Este checkpoint tem como finalidade permitir retomada segura do trabalho sem perda de contexto, mantendo alinhamento entre repositório analítico, notebook de ML e texto acadêmico final.

---

## Contexto consolidado
O trabalho evoluiu de uma fase inicialmente mais orientada à construção e validação do pipeline analítico para uma fase de consolidação acadêmica do TCC, com foco em tornar o texto:
- mais defensável em banca;
- mais explícito metodologicamente;
- mais coerente na relação entre objetivo, método, resultados e conclusões.

Ao longo desta iteração, o TCC passou por revisões sucessivas com a orientadora, especialmente em torno dos seguintes temas:
- clareza do objetivo;
- definição da unidade de análise;
- explicitação da metodologia de clusterização;
- relação entre K-Means e agrupamento hierárquico;
- papel da participação na interpretação dos perfis;
- nomenclatura dos clusters;
- eliminação de trechos excessivamente técnicos ou irrelevantes ao argumento final.

---

## Decisões metodológicas congeladas
As seguintes decisões devem ser consideradas **congeladas** para continuidade do trabalho, salvo nova orientação explícita da professora:

### 1. Unidade de análise
A unidade de análise do estudo é o **aluno**.

O texto não deve mais reabrir a discussão sobre a passagem do grão do evento para o grão do aluno como se isso fosse uma decisão ainda em aberto. Essa escolha decorre diretamente do objetivo do estudo.

### 2. Variáveis usadas na clusterização
A análise de agrupamento final foi conduzida **exclusivamente com as cinco dimensões de desempenho**:
- `technicalAbility`
- `attitude`
- `argumentation`
- `articulation`
- `negotiation`

### 3. Papel da participação
Os indicadores de participação:
- **não entraram diretamente no K-Means**;
- foram utilizados **posteriormente**, como apoio descritivo complementar à interpretação dos perfis.

Consequência:
- a participação não pode ser apresentada como critério de formação do cluster;
- ela pode ser usada como leitura posterior e complementar dos grupos.

### 4. Papel do agrupamento hierárquico
O agrupamento hierárquico com critério de Ward:
- foi utilizado como **apoio complementar** à escolha do número de grupos;
- não gerou a solução final interpretada.

### 5. Papel do K-Means
A solução final interpretada foi a do **K-Means**, com:
- `k = 4`
- perfis descritos a partir da posição relativa dos centróides nas cinco variáveis de desempenho.

### 6. Base final de modelagem
A base final de modelagem foi conduzida com:
- **78 alunos com desempenho válido**
- **77 alunos após exclusão de um único caso extremo de participação**

### 7. Outlier extremo
Foi identificado um único caso extremo de participação, correspondente a aproximadamente **90 mil eventos concentrados em um único dia**.

Esse caso:
- foi retirado da modelagem final;
- não deve ser dramatizado no texto ou na defesa;
- deve ser tratado como exclusão pontual de um outlier, sem transformar isso em foco central do argumento.

---

## Principais mudanças realizadas no TCC até a v1.5 / v1.5.1

### Resumo / Abstract
- revisão completa para alinhar a redação à lógica final do estudo;
- remoção da ambiguidade entre desempenho e participação;
- explicitação de que os perfis foram identificados por análise de agrupamento não supervisionada a partir das cinco dimensões de desempenho;
- participação reposicionada como apoio descritivo complementar.

### Palavras-chave / Keywords
- revisão para evitar repetição de termos do título;
- adoção de termos mais aderentes ao método e ao resultado:
  - análise de agrupamento;
  - perfil discente;
  - desempenho discente;
  - participação observada;
  - análise não supervisionada.

### Introdução
- objetivo incorporado diretamente à introdução;
- reforço da conexão entre Learning Analytics, xAPI, LRS e o problema do estudo;
- explicitação de que a modelagem dos perfis foi baseada em desempenho, com participação usada para leitura complementar.

### Material e Métodos
- fortalecimento teórico dos métodos;
- explicitação de:
  - PCA;
  - K-Means;
  - centróides;
  - silhouette;
  - Ward;
- inserção de tabela com as cinco variáveis de desempenho utilizadas no agrupamento;
- explicitação de que a participação não entrou diretamente na clusterização;
- definição clara da base final (78 → 77 alunos);
- inclusão de parágrafo sobre ambiente computacional, linguagem, pacotes e referência ao Apêndice A.

### Resultados e Discussão
- simplificação do encadeamento da seção;
- remoção de blocos excessivamente técnicos e metodológicos que antes estavam deslocados em Resultados;
- redução drástica da ênfase em `unknown` e subclassificações semânticas que não impactavam diretamente o resultado final;
- manutenção da distribuição por famílias de eventos;
- reorganização do trecho de clusterização;
- atualização dos nomes dos perfis para versões metodologicamente mais defensáveis;
- reposicionamento da participação como leitura posterior;
- revisão do parágrafo final da seção para evitar a ideia de que participação formou diretamente os clusters.

### Perfis identificados
Nomes mais recentes trabalhados:
- **Desempenho intermediário com participação regular**
- **Alto desempenho com menor participação observada**
- **Alto desempenho com maior participação observada**
- **Desempenho mais baixo em argumentação e comunicação**

Observação:
- ainda pendente inserir estatísticas descritivas concretas por cluster para sustentar melhor “participação regular”, “menor” e “maior participação observada”.

### Conclusões
- remoção de conclusões sobre escolhas metodológicas que já estavam dadas pelo objetivo;
- reforço da ideia de que os perfis foram diferenciados pela configuração relativa das cinco dimensões de desempenho;
- participação tratada como apoio interpretativo posterior;
- limitações reformuladas para destacar:
  - subconjunto de alunos com desempenho válido;
  - participação como medida absoluta registrada;
  - caráter exploratório da técnica.

### Apêndice
- decisão de incluir **Apêndice A** com:
  - descrição dos artefatos computacionais utilizados;
  - linguagem e pacotes;
  - link para o código desenvolvido.
- decisão de não incluir, por ora, código-fonte completo no corpo do TCC.

---

## Principais feedbacks da orientadora que pautaram esta versão
Os comentários mais relevantes da orientadora, consolidados até aqui, podem ser sintetizados assim:

1. **O trabalho está ficando muito bom**, mas precisa reforçar alguns pontos.
2. A banca vai cobrar:
   - clareza metodológica;
   - teoria dos métodos;
   - explicação do que foi usado no cluster;
   - coerência entre método e interpretação.
3. O texto deve deixar explícito que:
   - o agrupamento hierárquico ajudou a definir o número de grupos;
   - o K-Means gerou os grupos finais interpretados.
4. A participação não pode ser tratada como variável formadora do cluster se ela não entrou no K-Means.
5. Os nomes dos perfis devem refletir principalmente as variáveis que participaram da clusterização.
6. O trabalho precisa ficar mais forte em estatística descritiva e menos apoiado em adjetivos genéricos.
7. O texto deve evitar rediscutir decisões metodológicas já assumidas, especialmente a escolha do aluno como unidade de análise.
8. É necessário incluir apêndice com referência ao código desenvolvido.

---

## Pendências abertas para a v1.6

### Pacote 1 - Material e Métodos
- reforçar ainda mais a explicação teórica de:
  - K-Means;
  - centróides;
  - Ward;
  - silhouette;
- inserir ou revisar o parágrafo sobre linguagem, pacotes e Apêndice A;
- revisar justificativa explícita da não inclusão da participação na clusterização.

### Pacote 2 - Resultados e Discussão: encadeamento da análise
- recolocar ou ajustar o parágrafo com:
  - ~92,5% da variabilidade explicada;
  - silhouette ~0,367 para `k=5`;
  - silhouette ~0,354 para `k=4`;
  - escolha final de `k = 4`;
- melhorar a transição antes da Figura 1;
- deixar clara a sequência:
  - base por aluno → inspeção hierárquica → K-Means final.

### Pacote 3 - Perfis
- extrair do notebook estatísticas descritivas por cluster:
  - média de `days_active`
  - média de `events_per_day`
  - média de `total_meetings`
  - opcionalmente `total_interactions` e `total_tech_questions`
- inserir esses valores no texto dos perfis e, se necessário, na tabela resumo.

### Pacote 4 - Interpretação final dos resultados
- inserir um parágrafo interpretativo sobre a predominância de `meeting` como principal forma de uso da plataforma;
- reforçar a leitura aplicada/pedagógica dos achados.

### Pacote 5 - Apêndice A
- criar formalmente:
  - `Apêndice A. Artefatos computacionais utilizados na análise`
- inserir:
  - linguagem utilizada;
  - principais pacotes;
  - finalidade dos scripts/notebooks;
  - link para o repositório ou pasta versionada do código.

---

## Artefatos correlatos importantes
### Repositório analítico
- `docs/ml/ml-results-exploratory.md`
- `ml/notebooks/ml_feature_engineering.ipynb`

### Documento do TCC
- versão base atual: **v1.5 / v1.5.1**
- próxima iteração prevista: **v1.6**

---

## Próximos passos recomendados
1. Atualizar o repositório com:
   - notebook de feature engineering;
   - documentação exploratória de ML;
   - este checkpoint.
2. Executar a v1.6 por pacotes:
   - Material e Métodos
   - encadeamento da análise
   - perfis com estatística descritiva
   - interpretação final dos resultados
   - Apêndice A
3. Revisar o texto final comentário por comentário, apenas após os pacotes estarem fechados.
4. Submeter nova versão à professora.

---

## Estado ao final deste checkpoint
O TCC saiu da fase de “reestruturação” e entrou na fase de **reforço acadêmico e acabamento fino**.

A direção metodológica está estabilizada.
As próximas iterações devem priorizar:
- robustez explicativa;
- concretude numérica;
- clareza para banca;
- reprodutibilidade documental.