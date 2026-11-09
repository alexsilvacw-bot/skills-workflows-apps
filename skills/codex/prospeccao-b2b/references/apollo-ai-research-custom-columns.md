# Desenhar colunas customizadas de AI Research no Apollo

Usar esta referência somente quando um fato necessário não puder ser coletado
por filtros, campos, sinais, enriquecimentos ou outra fonte adequada e, por isso,
for indispensável criar uma pesquisa por IA dentro do Apollo. As referências de
templates são uma biblioteca de padrões para construir colunas factuais; não
delegam o raciocínio comercial ao modelo do Apollo.

## Divisão de responsabilidades

- **Apollo:** filtrar, enriquecer, pesquisar e devolver fatos brutos.
- **Skill:** interpretar os fatos, comparar com o ICP e decidir fit, timing,
  papel de compra, confiança e Tier com o modelo mais potente.

Recursos pagos do Apollo podem ser usados normalmente para coleta. AI Research é
o último recurso de coleta, não porque possa consumir créditos, mas porque usa um
modelo inferior para uma tarefa que deve ser mantida estreita e verificável.

## Resultado obrigatório da skill

Nunca responder apenas `use Filtro de IA` ou `qualifique por IA`. Para cada
pesquisa recomendada, entregar uma especificação executável com:

1. nome da coluna;
2. objetivo e decisão que ela destrava;
3. objeto: conta ou pessoa;
4. momento exato do funil e universo de linhas;
5. dados e variáveis usados;
6. tipo de pesquisa/modelo necessário: dados existentes ou web;
7. prompt completo, pronto para colar;
8. formato do campo e valores permitidos;
9. estados de ausência, ambiguidade e conflito;
10. como a skill usará o resultado;
11. regra de expiração ou atualização, quando temporal.

## Princípio de desenho

A skill decide a pergunta. O Apollo executa uma pesquisa estreita por linha. A
skill recebe o resultado e calcula fit, timing, papel de compra, confiança e Tier.

Uma coluna pode coletar evidência para um critério atômico, por exemplo:

- exerce diretamente uma atividade definida no ICP;
- atende o tipo de cliente definido no ICP;
- existe vaga recente ligada à necessidade;
- houve troca de liderança em função relevante;
- a pessoa possui responsabilidade explícita sobre determinado processo.

Evitar uma coluna genérica `Qualified?`. Preferir classificações objetivas com
evidência e estado `Insufficient evidence`.

## Escolher o nível certo

### Conta

Usar para atividade, modelo comercial, ICP atendido, operação, tecnologia, vaga,
notícia, expansão, liderança ou concorrência. Deduplicar por domínio e pesquisar
uma vez por entidade, produto ou unidade relevante.

### Pessoa

Usar somente depois do gate da conta e dos filtros fixos de cargo/senioridade.
Pesquisar escopo atual, responsabilidade, função no processo de compra ou outro
fato que possa mudar a Tier da pessoa.

Nunca pesquisar a mesma empresa repetidamente em colunas de pessoas.

## Teste de necessidade antes de criar a coluna

Responder:

1. Qual dúvida específica ainda existe?
2. O resultado pode mudar uma decisão?
3. Um filtro ou campo existente já responde?
4. A skill pode calcular usando dados exportáveis?
5. Algum filtro, sinal, enriquecimento, base ou pesquisa determinística consegue
   coletar o fato sem pedir raciocínio ao modelo do Apollo?
6. A coluna pedirá somente coleta factual, sem veredito comercial?
7. Quais registros realmente precisam dessa evidência?

Se a resposta a 2 ou 6 for não, não criar. Se 3, 4 ou 5 forem sim, use essa forma
de coleta e classifique localmente. Créditos não fazem parte desse teste: o Apollo
informará o consumo ao usuário.

## Três modos de execução

### Econômico: uma coluna factual

Usar quando o resultado será enviado para a skill. Criar um campo de texto
estruturado com fato, evidência, URL e estado. A skill classifica fora do Apollo.

Vantagem: menor número de campos por linha. Limitação: pode não ser filtrável por
um único valor dentro do Apollo.

### Filtrável: uma coluna de label atômico

Usar quando os dados de entrada já são confiáveis e a classificação é simples.
Criar single-select com valores exatos, incluindo `Insufficient evidence`.

Vantagem: filtra dentro do Apollo. Limitação: reduz auditabilidade; não usar para
inferências complexas ou desqualificação irreversível.

### Auditável: evidência + label

Usar quando o usuário precisa filtrar dentro do Apollo e revisar a prova. Criar:

1. coluna factual de pesquisa;
2. coluna de classificação que lê a primeira.

Vantagem: rastreabilidade e filtro. Limitação: a segunda coluna não deve executar
um novo julgamento no Apollo; prefira trazer a evidência para a skill classificar.

## Convenção para nomes

Usar nomes curtos que indiquem objeto e resultado. Preferir o idioma da operação
do usuário. Exemplos:

- `Evidence — Performs Target Activity`
- `Account Type — Target Business Model`
- `Signal — Relevant Hiring`
- `Signal — Executive Change`
- `Market — Customer Segment`
- `Role Scope — Owns Target Process`
- `Evidence — Uses Competitor`

Evitar nomes vagos como `AI Research`, `Qualified` ou `Good Lead`.

## Anatomia do prompt

Montar o prompt nesta ordem:

```text
## Mission
[Uma tarefa atômica e observável.]

## Commercial context
[Somente o contexto necessário para interpretar o critério.]

## Target record
[Nome, domínio ou campos de pessoa e empresa necessários.]

## Identity verification
[Como confirmar empresa, pessoa, produto ou unidade.]

## Research question
[A pergunta específica que a coluna deve responder.]

## Source scope
[Dados do Apollo, site oficial, fontes externas autorizadas e prioridade.]

## Evidence rules
- Report facts, not sales fit.
- Do not infer missing facts from plausibility.
- Preserve dates and source URLs.
- Distinguish not found, unavailable, ambiguous and conflicting.

## Allowed output
[Valores exatos ou esquema estruturado.]

## Fallback
[Saída literal para evidência insuficiente.]
```

Não incluir o Context Center inteiro quando bastar uma definição curta do critério.
Contexto excessivo aumenta viés e custo.

## Formato padrão de especificação entregue ao usuário

```text
COLUNA CUSTOMIZADA DE AI RESEARCH

Nome:
Executar em: Accounts | People
Objetivo:
Decisão que destrava:
Rodar quando:
Não rodar quando:
Universo estimado:
Dados/variáveis:
Pesquisa: dados do Apollo | web | híbrida
Tipo de campo: single-select | single-line | multi-line
Valores permitidos:

Prompt para colar:
"""
[prompt completo]
"""

Uso do resultado pela skill:
Aviso: o Apollo informará os créditos antes da execução; não calcular aqui.
Expiração/atualização:
```

Se houver mais de uma coluna, numerar e mostrar a dependência entre elas.

## Saída factual recomendada

Para o modo econômico ou a primeira coluna do modo auditável:

```text
Identity
- status: confirmed | ambiguous | not_confirmed

Finding
- criterion:
- observed_value:
- evidence_excerpt:
- source_url:
- source_date:

Coverage
- sources_checked:
- missing_or_blocked:
- result_state: found | not_found | unavailable | ambiguous | conflicting
```

Adaptar os campos ao objeto pesquisado usando as referências específicas.

## Labels atômicos

Quando uma label for necessária, definir valores mutuamente exclusivos. Exemplo:

```text
Operator
Installer only
Seller/distributor
Both operator and installer
Insufficient evidence
Identity mismatch
```

Evitar `Yes/No` quando há estados operacionais diferentes. Nunca transformar
ausência de informação em `No`.

## Biblioteca de padrões

- `apollo-ai-research-company-fit.md`: compilar critérios uma vez; pesquisar
  fatos de conta; classificar fora do Apollo.
- `apollo-ai-research-job-openings.md`: vagas como timing; descrição só para
  casos ambíguos.
- `apollo-ai-research-target-customer.md`: mercado atendido, buyer/user/canal e
  hierarquia de evidência.
- `apollo-ai-research-contact-background.md`: preservar campos brutos; pesquisar
  escopo de função, não gerar resumo antes da decisão.
- `apollo-ai-research-executive-changes.md`: sinais temporais, janela, datas,
  fontes e expiração.
- `apollo-ai-research-competitors.md`: candidatos, tipo de relação e validação
  antes de gerar lista curta.

Combinar padrões somente quando a pergunta exigir. Não criar uma coluna omnibus
com vários objetivos independentes.

## Escopo e calibração

Antes de recomendar execução:

1. confirmar que nenhum recurso estruturado ou outra fonte adequada coleta o fato;
2. aplicar os filtros, sinais e enriquecimentos úteis, pagos ou não;
3. usar as prévias disponíveis para calibrar exemplos positivos,
   negativos e ambíguos;
4. rodar inicialmente nos registros que ainda dependem da evidência;
5. revisar falsos positivos, falsos negativos e `Insufficient evidence`;
6. só então ampliar se mais registros ainda exigirem o mesmo fato.

Não calcular, estimar ou perguntar sobre créditos. O Apollo mostrará o consumo e
o usuário decidirá se executa.

## Critérios de qualidade da coluna

Uma coluna está pronta quando:

- responde uma pergunta única;
- identifica corretamente o objeto;
- usa fontes adequadas;
- retorna evidência ou estado de ausência;
- não mistura fit e timing sem necessidade;
- não repete pesquisa no nível errado;
- possui labels mutuamente exclusivos, quando aplicável;
- explica como o resultado muda a decisão;
- tem universo de execução explícito;
- foi calibrada com casos positivos, negativos e ambíguos.

## Princípio transferível

As referências ensinam padrões de coleta. Quando AI Research for realmente
necessário, a entrega da skill é uma coluna factual pronta para o Apollo executar,
não uma recomendação abstrata de usar IA. Apollo preenche o campo; a skill
interpreta e decide o funil.
