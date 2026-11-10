# AI Research do Apollo: Research and evaluate a company for fit

Referência capturada da interface do Apollo em 18 de julho de 2026. Usar ao
avaliar esse template, desenhar pesquisa factual de contas ou evoluir a V2 da
skill. Não tratar o template como autoridade sobre qualificação; tratá-lo como
fonte de padrões de coleta e como exemplo de custo evitável.

## Resumo executivo

O template cria um pipeline de três campos dependentes:

1. transformar o Context Center do vendedor em critérios de pesquisa;
2. pesquisar uma empresa e registrar fatos relevantes;
3. classificar a empresa com base nos critérios e fatos anteriores.

Na arquitetura recomendada para a V2, executar as etapas 1 e 3 na própria skill.
Usar a etapa 2 no Apollo somente quando faltar evidência que possa mudar a
classificação. Pesquisar uma vez por domínio, nunca uma vez por contato.

## Pipeline original reconstruído

Os trechos fornecidos vieram intercalados. A dependência entre variáveis permite
reconstruir a ordem funcional abaixo.

### Etapa 1: Determine research guidelines

**Missão original:** extrair e resumir critérios de qualificação a partir apenas
do Context Center. Não pesquisar na web nem inventar critérios além do que estiver
declarado ou claramente implícito.

**Entrada:**

- `%{context}` como fonte de verdade sobre a empresa vendedora.

**Saída original:**

- `ICP Fit Criteria`: requisitos mínimos observáveis, sem estreitar demais;
- `High-Value Fit Criteria`: sinais de fit excepcional ou urgência;
- `Disqualification Criteria`: motivos explícitos ou claramente implícitos;
- `Research Signals to Look For`: sinais públicos realistas e escaláveis.

**Padrão útil:** compilar o contexto comercial em critérios observáveis antes de
pesquisar qualquer conta.

**Problema operacional:** os critérios do vendedor são estáveis durante a rodada.
Calculá-los como campo por conta ou contato repete trabalho e pode repetir consumo.

**Decisão V2:** executar uma vez na skill, depois do intake e da leitura do
projeto. Reutilizar o mesmo contrato de critérios em todas as contas da rodada.

### Etapa 2: Research target company

**Missão original:** pesquisar uma empresa e reportar todas as informações
relevantes para qualificá-la ou desqualificá-la. Reportar fatos, sem avaliar fit.

**Entradas:**

- `%{context}`;
- critérios gerados na etapa 1;
- nome, domínio e descrição da empresa;
- vagas encontradas pelo Apollo;
- tecnologias encontradas pelo Apollo.

**Controles de identidade originais:**

- confirmar que o domínio visitado coincide com o domínio da conta;
- conferir nome, marca, logotipo ou página institucional;
- rejeitar conteúdo de domínio externo em caso de ambiguidade;
- registrar discrepâncias e usar somente o que puder ser confirmado.

**Escopo original da pesquisa:**

- usar o site oficial como fonte primária;
- visitar até 20 páginas do mesmo domínio;
- não seguir links externos;
- procurar os sinais definidos na etapa 1;
- reportar fatos, sem decidir fit.

**Saída original:**

- confirmação de identidade;
- log detalhado da pesquisa;
- descrição do negócio e modelo comercial;
- indicadores observados de fit;
- indicadores observados de desqualificação;
- notícias ou atualizações relevantes;
- tecnologias relevantes;
- vagas e necessidades de contratação.

**Padrões úteis:**

- separar coleta de julgamento;
- confirmar a identidade antes da pesquisa;
- orientar a busca por critérios predefinidos;
- combinar site, vagas e tecnologia;
- explicitar evidência ausente.

**Limitações:**

- restrição ao domínio oficial favorece fontes primárias, mas pode não encontrar
  notícias, registros públicos, LinkedIn, licitações ou mudanças externas;
- o log detalhado pode consumir texto sem melhorar a decisão;
- o formato não exige URL junto a cada afirmação;
- "até 20 páginas" pode virar uma meta desnecessária;
- rodar em registros de pessoas pode repetir a mesma pesquisa para vários
  contatos da mesma empresa.

**Decisão V2:** preservar essa etapa como pesquisa opcional e factual. Executar
por conta deduplicada pelo domínio, somente quando a evidência existente não
bastar. Tratar 20 páginas como teto, encerrar assim que cada critério estiver
confirmado, refutado ou marcado como não encontrado.

### Etapa 3: Final analysis of qualification

**Missão original:** combinar os critérios da etapa 1 com os achados da etapa 2
e retornar exatamente um status:

- `Disqualified`;
- `Possible Fit`;
- `High Value Fit`;
- `Not Enough Information`.

**Heurísticas originais:**

- usar `Possible Fit` como categoria padrão quando não houver desqualificador e
  existir alinhamento geral;
- usar `Disqualified` quando a conta falhar no baseline, permitindo inclusive
  decidir por intuição em casos aparentemente irrelevantes;
- usar `High Value Fit` para característica, evento, dor ou urgência especial;
- reservar `Not Enough Information` para ausência quase total de informação;
- produzir justificativa de 10 a 20 frases com citações no campo de reasoning.

**Problemas:**

- "go with your gut" autoriza desqualificação sem evidência;
- `Possible Fit` como padrão pode inflar a lista;
- `High Value Fit` mistura fit estrutural, timing e valor potencial;
- `Not Enough Information` é restrito demais e força decisões prematuras;
- a etapa pode racionalizar depois de escolher uma classe;
- 10 a 20 frases aumentam custo e ruído;
- as citações são exigidas depois de uma pesquisa que não liga obrigatoriamente
  cada fato à sua URL.

**Decisão V2:** remover essa etapa do Apollo. Classificar na skill, separando fit
estrutural, timing, valor potencial e confiança da evidência antes de derivar uma
Tier operacional.

## Contrato recomendado para pesquisa factual no Apollo

Quando faltar uma evidência capaz de mudar a decisão e filtros, campos, sinais,
enriquecimentos ou outra fonte adequada não conseguirem coletá-la, pedir um único
campo factual com estrutura semelhante a esta:

```text
Identity
- status: confirmed | ambiguous | not_confirmed
- confirmed_domain:
- evidence_url:

Business model evidence
- criterion:
- fact:
- source_url:
- source_date:

Fit evidence
- criterion:
- fact:
- source_url:
- source_date:

Disqualification evidence
- criterion:
- fact:
- source_url:
- source_date:

Timing evidence
- signal_type:
- fact:
- source_url:
- source_date:

Missing evidence
- criterion:
- searches_or_pages_checked:
```

Instruir o Apollo a não classificar, não inferir orçamento, não preencher lacunas
por plausibilidade e escrever `not found` quando não houver evidência.

## Regras de coleta e deduplicação

1. Compilar os critérios uma vez na skill, não por registro no Apollo.
2. Coletar com filtros, campos, sinais, enriquecimentos e fontes adequadas antes
   de recorrer a AI Research; esses recursos podem ser pagos.
3. Separar contas em evidência suficiente, ambíguas e incompatíveis.
4. Rodar pesquisa apenas nas contas ambíguas quando o resultado puder mudar a
   decisão.
5. Deduplicar por domínio canônico antes de pesquisar.
6. Nunca repetir pesquisa de empresa para cada contato da mesma conta.
7. Preferir um campo factual estreito a vários campos de julgamento.
8. Classificar fora do Apollo e revelar contato somente depois do gate.
9. Não calcular créditos; o Apollo informa o consumo ao usuário.

## Classificação recomendada fora do Apollo

Avaliar separadamente:

- **Fit estrutural:** baixo, médio ou alto;
- **Timing:** ausente, fraco ou forte;
- **Valor potencial:** baixo, médio ou alto;
- **Confiança:** baixa, média ou alta;
- **Desqualificador:** confirmado, ausente ou incerto.

Derivar a Tier somente depois desses eixos. Ausência de prova não equivale a
desqualificação. Uma conta sem evidência suficiente deve ir para `Needs Evidence`,
não para um fit presumido nem para descarte intuitivo.

## Princípio transferível

Usar o Apollo para adquirir fatos aos quais ele tem acesso. Usar a skill para
compilar critérios, comparar evidências, lidar com incerteza e decidir o gate.
