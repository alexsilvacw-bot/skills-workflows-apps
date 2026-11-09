# AI Research do Apollo: Identify who your target company sells to

Referência capturada da interface do Apollo em 18 de julho de 2026. Usar ao
avaliar o mercado atendido por uma conta, seu modelo comercial ou quando o ICP
dos clientes da conta for relevante para canal, parceria, concorrência ou fit.

## Resumo executivo

O template recebe descrição da empresa e texto raspado do site. A partir disso,
produz uma hipótese de ICP com setor, porte, geografia, funções, cargos e dores.

Na V2, tratar esse resultado como pesquisa sobre o mercado atendido pela conta,
não como verdade cadastral nem como qualificação automática. Se descrição e
texto raspado puderem ser fornecidos à skill, fazer a síntese localmente. Usar
AI Research apenas quando o Apollo possuir conteúdo útil que o usuário não
consegue disponibilizar de outra forma.

## Comportamento original

**Missão:** avaliar uma empresa e determinar seu perfil de cliente ideal.

**Entradas:**

- `account.description`, ou `<account description unavailable>`;
- `company_scraped_info`, ou `<company scraped info unavailable>`.

**Requisitos originais:**

- sintetizar critérios claros de ICP;
- incluir critérios de empresa e de pessoa;
- evitar suposições sem fundamento;
- permitir inferências consideradas conexões lógicas fortes.

**Saída original:**

- visão geral das empresas atendidas;
- um a três setores-alvo;
- porte: pequeno, médio ou grande;
- geografia;
- funções atendidas;
- até cinco cargos decisores;
- dores das empresas atendidas;
- `Not enough information` quando não houver base suficiente.

## Padrões úteis

- separar atributos de empresa e pessoa no mercado atendido;
- procurar setor, porte, geografia, função, cargo e dor;
- preservar `None identified` quando um campo específico não puder ser derivado;
- reconhecer oferta agnóstica de indústria;
- usar descrição e conteúdo do site como evidência primária;
- permitir conclusão `Not enough information` em vez de preencher tudo.

## Problemas e riscos

### Três ICPs podem ser confundidos

Manter separados:

1. **ICP do vendedor:** empresas que nós queremos prospectar;
2. **ICP da conta:** clientes para quem a empresa-alvo vende;
3. **Buyer map da conta:** pessoas dentro da empresa-alvo que comprariam nossa
   oferta.

O template calcula o segundo, mas sua saída de funções e cargos pode parecer o
terceiro. Um cargo que compra da empresa-alvo não é automaticamente o cargo que
compra da empresa vendedora.

### Contradição entre não inferir e poder inferir

O prompt proíbe suposição sem fundamento, mas autoriza inferir setor, função,
cargo e dor a partir da oferta. Sem indicar o grau de evidência, uma associação
plausível pode ser apresentada como fato.

### Texto raspado é ruidoso

`company_scraped_info` pode misturar navegação, blog, vagas, páginas antigas,
conteúdo de parceiros ou mensagens para vários públicos. O prompt não exige:

- domínio confirmado;
- URL de origem de cada trecho;
- data;
- distinção entre página de produto, caso de cliente e conteúdo editorial;
- separação entre usuário, comprador, beneficiário, parceiro e público geral.

### Porte é difícil de provar

Classificar clientes como pequenos, médios ou grandes exige evidência de planos,
casos, linguagem de segmento, ticket, requisitos ou logos representativos. A
descrição geral raramente basta.

### Títulos são especialmente frágeis

Inferir até cinco decisores com base apenas na oferta da conta pode produzir uma
lista genérica de C-level e managers. Procurar primeiro títulos explicitamente
citados em páginas de persona, casos, depoimentos, integrações ou materiais de
produto.

### Regra de insuficiência é inconsistente

O prompt permite `None identified` por campo, mas também manda retornar somente
`Not enough information` quando não houver contexto suficiente e, em outro ponto,
quando qualquer campo não tiver saída confiável. A skill deve permitir evidência
parcial sem apagar campos confirmados.

### Utilidade depende da tese comercial

Quem a conta atende pode ser:

- critério direto em venda para canais, agências, distribuidores, marketplaces
  ou parceiros;
- sinal secundário quando a oferta depende do modelo operacional ou dos clientes
  da conta;
- informação irrelevante em muitas vendas funcionais internas.

Não gastar pesquisa antes de explicar como o ICP da conta altera nossa decisão.

## Decisão V2

Antes de pesquisar, formular a pergunta causal:

> Se descobrirmos para quem esta empresa vende, qual decisão de segmentação ou
> qualificação da lista poderá mudar?

Se não houver resposta concreta, não usar o template.

Quando houver utilidade:

1. obter descrição, domínio e conteúdo de páginas relevantes;
2. confirmar identidade e separar tipos de página;
3. extrair afirmações explícitas sobre clientes, casos e personas;
4. marcar inferências separadamente;
5. sintetizar o ICP da conta na skill;
6. ligar o resultado ao nosso critério comercial;
7. nunca substituir o buyer map da conta pelo buyer map dos clientes dela.

## Hierarquia de evidência

Classificar cada campo como:

- **Explícito:** declarado diretamente em página de produto, solução, segmento,
  caso de cliente ou depoimento;
- **Corroborado:** sustentado por duas ou mais evidências coerentes, como casos,
  logos, linguagem de produto ou planos;
- **Inferência forte:** conclusão plausível com cadeia lógica registrada, mas sem
  declaração direta;
- **Desconhecido:** não há base suficiente;
- **Conflitante:** fontes da própria empresa apontam públicos diferentes.

Não promover inferência forte a fato.

## Ontologia recomendada do mercado atendido

Separar:

- modelo: B2B, B2C, B2B2C, marketplace, canal ou misto;
- cliente pagante;
- usuário final;
- beneficiário;
- parceiro ou canal;
- setor;
- porte;
- geografia;
- função usuária;
- comprador econômico;
- influenciadores;
- caso de uso;
- dor declarada;
- evidência e confiança.

Essa separação é especialmente importante para marketplaces, consultorias,
plataformas horizontais e empresas com vários produtos.

## Dados mínimos a pedir antes de AI Research

- nome e domínio canônico;
- descrição da conta;
- texto ou URLs de páginas de produto e soluções;
- páginas de setores/personas;
- casos de clientes e depoimentos;
- página de preços ou planos, quando existir;
- geografia explicitamente mencionada;
- exemplos de clientes.

Se esses dados puderem ser enviados à skill, não usar uma coluna do Apollo apenas
para sintetizá-los.

## Contrato factual para pesquisa no Apollo

Quando o Apollo detiver conteúdo necessário que não esteja disponível fora dele,
pedir fatos rastreáveis:

```text
Company identity
- company_name:
- confirmed_domain:
- identity_status: confirmed | ambiguous | not_confirmed

Audience evidence
- audience_type: paying_customer | user | beneficiary | partner | unknown
- explicit_claim:
- evidence_excerpt:
- source_url:

Segment evidence
- dimension: industry | company_size | geography | function | title | use_case
- observed_value:
- evidence_level: explicit | corroborated | strong_inference | unknown
- evidence_excerpt:
- source_url:

Customer examples
- customer_name:
- customer_type:
- source_url:

Missing or conflicting evidence
- field:
- status: not_found | conflicting | unavailable
```

Instruir o Apollo a não produzir ICP completo quando houver somente evidência
parcial, não inventar títulos e não transformar audiência editorial em cliente.

## Classificação fora do Apollo

A skill deve produzir dois resultados separados:

1. **ICP observado da conta:** para quem a empresa-alvo parece vender;
2. **Relevância para nossa prospecção:** por que isso aumenta, reduz ou não altera
   o fit da conta com a oferta do vendedor.

Para a relevância, usar:

- **Direta:** o mercado atendido é requisito explícito da tese comercial;
- **Secundária:** altera valor ou caso de uso, mas não o baseline;
- **Contextual:** informa a lista sem afetar qualificação;
- **Irrelevante:** não muda nenhuma decisão;
- **Incerta:** relação causal ainda não definida.

## Regras de coleta

1. Não rodar por contato; pesquisar uma vez por domínio.
2. Não usar AI Research se descrição e texto raspado puderem ser analisados na
   skill.
3. Não pesquisar ICP da conta sem explicar qual decisão o resultado mudará.
4. Preferir campos faltantes específicos a uma síntese ampla de sete dimensões.
5. Não revelar contatos para identificar o mercado atendido.
6. Não repetir pesquisa já coberta por casos, páginas de segmentos ou contexto do
   projeto.
7. Filtros, campos, enriquecimentos e outras fontes podem ser usados mesmo se
   pagos; AI Research fica reservado ao fato que eles não conseguem coletar.
8. Não calcular créditos; o Apollo informa o consumo ao usuário.

## Princípio transferível

O mercado atendido pela conta é evidência contextual. Só vira critério de
qualificação quando existir uma relação causal explícita com a oferta e a tese de
prospecção. Apollo coleta afirmações; a skill separa públicos, estima confiança e
decide relevância.
