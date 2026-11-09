# AI Research do Apollo: Identify relevant job openings

Referência capturada da interface do Apollo em 18 de julho de 2026. Usar ao
avaliar vagas como sinal de timing ou ao decidir entre filtros/dados de vagas já
existentes, classificação local e AI Research adicional.

## Resumo executivo

O template recebe o Context Center e uma lista de títulos de vagas atribuídas à
empresa. Ele classifica liberalmente se existe qualquer relação razoável entre
essas vagas e a oferta do vendedor.

Na V2, não usar esse template como classificador. Se os títulos já estiverem
disponíveis, enviá-los à skill e calcular relevância localmente, sem AI Research.
Pesquisar no Apollo somente quando descrição, data, local ou responsabilidades
da vaga forem necessários para resolver uma ambiguidade capaz de mudar o timing.

## Comportamento original

**Missão:** determinar se as vagas abertas de uma empresa indicam necessidade
potencial pela oferta da empresa vendedora.

**Entradas:**

- `%{context}` como fonte de verdade sobre o vendedor;
- `account.name`;
- `account.job_posting_titles`, ou o marcador `<no job postings found>`.

**Critérios originais de relevância:**

- a função usaria diretamente a solução;
- a função se beneficiaria da solução;
- o departamento costuma enfrentar a dor resolvida;
- a vaga sugere iniciativa alinhada à oferta;
- a função contém processo ou workflow que a oferta poderia melhorar.

**Sobreposições funcionais sugeridas:**

- vendas como sinal de necessidade de ferramentas ou enablement;
- marketing como sinal de crescimento ou outreach;
- operações como sinal de otimização de processo;
- tecnologia como sinal de implementação de sistemas;
- gestão como sinal de eficiência ou produtividade.

**Instrução dominante:** interpretar liberalmente, aceitar conexões indiretas e
considerar relevante qualquer relação razoável.

**Saída original:**

- `Yes - Relevant jobs found`, seguido de vagas e explicação; ou
- `No relevant jobs found.`

## Padrões úteis

- relacionar vagas ao problema resolvido, não apenas ao nome do produto;
- considerar usuário direto, beneficiário, área com a dor e iniciativa associada;
- observar crescimento por departamento;
- usar vagas como sinal de prioridade ou mudança organizacional;
- analisar efeitos indiretos quando houver uma cadeia causal explícita.

## Problemas e vieses

### Relevância liberal demais

O prompt ordena pensar amplamente, aceitar benefícios indiretos e considerar
qualquer conexão razoável. Os exemplos genéricos tornam vendas, marketing,
operações, tecnologia e gestão potencialmente relevantes para quase qualquer
oferta B2B. Isso maximiza recall, mas destrói precisão e cria confirmação de fit.

### Título não comprova necessidade

O modelo recebe apenas títulos. Sem descrição, responsabilidades, senioridade,
local, data, quantidade e vínculo com uma iniciativa, não é possível distinguir:

- reposição de rotina de expansão;
- usuário direto de função adjacente;
- vaga antiga de vaga realmente aberta;
- contratação local de movimento corporativo;
- coincidência lexical de responsabilidade real.

### Estados ausentes são misturados

O resultado binário confunde:

- nenhuma vaga disponível no dado do Apollo;
- empresa sem vagas abertas;
- vagas encontradas, mas nenhuma relevante;
- vagas potencialmente relevantes sem informação suficiente;
- vaga diretamente ligada à dor.

`<no job postings found>` significa ausência no campo, não prova de que a empresa
não esteja contratando.

### Fit e timing são confundidos

Uma vaga pode indicar momento, iniciativa ou crescimento, mas não deve definir
sozinha o fit estrutural da empresa. A ausência de vaga relevante também não
desqualifica uma conta que mantém a dor de forma recorrente.

### Julgamento desnecessário no Apollo

Quando a entrada contém somente títulos já disponíveis, a skill pode executar a
mesma comparação com mais contexto e sem uma coluna adicional de AI Research.

## Decisão V2

Tratar vagas como evidência de timing e, em alguns casos, de capacidade
operacional. Não usá-las como gate obrigatório de fit.

Executar nesta ordem:

1. definir na skill quais funções, iniciativas e responsabilidades seriam sinais
   diretos, adjacentes ou irrelevantes para a oferta;
2. obter títulos, datas, locais e URLs por filtro/exportação já disponível;
3. classificar títulos na skill quando forem inequívocos;
4. marcar casos ambíguos como `Needs Job Evidence`;
5. pesquisar descrição e responsabilidades somente dos casos ambíguos;
6. recalcular o timing na skill;
7. nunca desqualificar apenas por ausência de vaga relevante.

## Classificação recomendada

Classificar cada vaga em uma destas funções:

- **Direta:** exercerá a atividade ou será usuária imediata da solução;
- **Dona do problema:** liderará a função que sofre ou compra a solução;
- **Iniciativa:** evidencia implantação, expansão ou transformação relacionada;
- **Adjacente:** pode se beneficiar, mas não prova prioridade nem necessidade;
- **Irrelevante:** não há cadeia causal concreta com a oferta;
- **Incerta:** título insuficiente; descrição pode mudar a classificação.

Separar a força do timing:

- **Forte:** vaga recente, direta ou dona do problema, com responsabilidades
  explicitamente ligadas à necessidade;
- **Moderado:** vaga de iniciativa ou conjunto coerente de contratações na área;
- **Fraco:** título adjacente sem responsabilidade ou iniciativa comprovada;
- **Ausente:** nenhuma vaga relevante encontrada nas fontes consultadas;
- **Desconhecido:** dados de vagas ausentes, incompletos ou sem data confiável.

## Dados mínimos a pedir antes de AI Research

Preferir obter, por empresa e vaga:

- título;
- departamento;
- localização;
- data de publicação ou atualização;
- URL;
- status aberto/fechado, se disponível;
- quantidade de vagas semelhantes;
- domínio canônico da empresa.

Se esses campos já resolverem a classificação, não usar AI Research.

## Contrato factual para casos ambíguos

Quando o título não bastar e a informação puder mudar a Tier, pedir ao Apollo:

```text
Job identity
- title:
- company_domain:
- posting_url:
- posted_or_updated_date:
- open_status: confirmed | uncertain | closed

Observed responsibilities
- responsibility:
- evidence_excerpt:
- source_url:

Related initiative
- initiative:
- evidence_excerpt:
- source_url:

Missing evidence
- field:
- status: not_found | unavailable | ambiguous
```

Instruir o Apollo a não decidir se a empresa precisa da oferta, não inferir
urgência pelo título e não tratar a ausência do campo como ausência de contratação.

## Regras de coleta

1. Não criar AI Research para reclassificar uma lista de títulos que já pode ser
   enviada à skill.
2. Deduplicar vagas por empresa, título, local e URL.
3. Pesquisar apenas vagas incertas com potencial de alterar o timing.
4. Pesquisar no nível da conta, não repetir para cada contato da empresa.
5. Não revelar e-mail ou telefone para analisar vagas.
6. Não calcular créditos; o Apollo informa o consumo ao usuário.

## Princípio transferível

Vaga é um sinal observável de atividade, não prova automática de necessidade. O
Apollo deve fornecer dados e descrição; a skill deve avaliar a cadeia causal
entre a contratação, a dor e a oferta.
