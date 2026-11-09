# AI Research do Apollo: Identify Competitors

Referência capturada da interface do Apollo em 18 de julho de 2026. Usar ao
avaliar alternativas e concorrentes de uma conta ou quando esse conhecimento
puder mudar segmentação, qualificação ou tese de substituição.

## Resumo executivo

O template procura até cinco concorrentes em páginas de G2, Trustpilot, CB
Insights e discussões no Reddit. Retorna somente nomes separados por vírgula,
sem fontes nem justificativa.

Na V2, tratar a saída como descoberta de candidatos, não como lista validada de
concorrentes diretos. Preservar fonte e evidência, identificar o tipo de relação
e só usar a pesquisa quando o resultado mudar uma decisão comercial concreta.

## Comportamento original

**Missão:** identificar concorrentes diretos da empresa-alvo.

**Entradas:**

- nome da conta;
- website da conta.

**Fontes orientadas:**

- seção de concorrentes da página da conta no G2;
- seção de concorrentes no Trustpilot;
- concorrentes e mapas de mercado no CB Insights;
- discussões no Reddit que mencionam a empresa e concorrentes.

**Saída original:**

- até cinco nomes;
- separados por vírgula;
- em uma única linha;
- sem citações ou notas;
- `Unable to find any competitors` quando nada for encontrado.

## Padrões úteis

- buscar fontes que explicitamente comparam empresas;
- limitar a quantidade para uso operacional;
- combinar diretórios estruturados e linguagem espontânea;
- procurar alternativas citadas por clientes e mercado;
- usar nome e website para orientar a entidade pesquisada;
- preservar um fallback explícito quando não houver resultado.

## Problemas e riscos

### Concorrente direto não é definido

Antes de classificar concorrência, comparar:

- problema ou job-to-be-done;
- produto ou serviço;
- comprador e usuário;
- segmento e porte de cliente;
- geografia;
- modelo de entrega e preço;
- momento do processo em que a solução é usada.

Duas empresas na mesma categoria podem atender públicos ou casos diferentes.

### As fontes têm vieses diferentes

- **G2:** forte para software, mas categorias e páginas de alternativas podem
  misturar concorrentes diretos, produtos adjacentes e opções populares;
- **Trustpilot:** orientado a reviews e reputação, não a taxonomia competitiva;
- **CB Insights:** útil em tecnologia e startups, mas mapas podem ser amplos,
  antigos ou limitados por acesso;
- **Reddit:** útil para linguagem de usuários, mas uma menção pode indicar
  substituto, comparação casual, integração, parceiro ou empresa homônima.

Nenhuma fonte isolada prova concorrência direta em todos os mercados.

### Nomes sem fontes não são auditáveis

A proibição de citações elimina a capacidade de verificar:

- por que a empresa foi incluída;
- qual fonte fez a associação;
- se a menção era atual;
- se a empresa está ativa;
- se houve aquisição ou mudança de marca;
- se o resultado é empresa, produto ou categoria.

A saída compacta pode existir como derivação final, mas a evidência deve ser
preservada antes dela.

### Identidade é insuficiente

Nome e website ajudam, mas o prompt não obriga a confirmar:

- domínio canônico;
- produto específico dentro de uma empresa multiproduto;
- entidade legal e marca;
- geografia e segmento;
- empresa versus produto com o mesmo nome.

### Limite de cinco pode esconder a estrutura do mercado

O ranking pode privilegiar empresas mais conhecidas, não as mais comparáveis. Em
mercados fragmentados, cinco nomes podem omitir concorrentes regionais; em
plataformas horizontais, podem misturar categorias diferentes.

### Não há janela temporal

O mercado muda por aquisições, encerramentos, reposicionamentos e lançamentos.
Registrar data da pesquisa e validar o status atual de cada candidato.

### Competidor da conta pode ser irrelevante para nossa venda

Saber quem compete com a conta não melhora automaticamente a prospecção. Pode ser
útil quando:

- vendemos substituição de uma solução concorrente;
- o ecossistema competitivo indica stack, maturidade ou categoria;
- queremos segmentar clientes, parceiros ou concorrentes de uma empresa;
- a presença de determinado concorrente muda a qualificação ou priorização.

Sem uso definido, vira enriquecimento caro e ornamental.

## Tipologia recomendada

Classificar cada candidato como:

- **Direto:** resolve o mesmo problema para o mesmo comprador e segmento com
  oferta substituível;
- **Parcial:** sobrepõe parte relevante do caso de uso ou segmento;
- **Indireto:** resolve a mesma necessidade por abordagem diferente;
- **Substituto:** processo manual, serviço, solução interna ou categoria distinta
  que compete pelo mesmo resultado ou orçamento;
- **Adjacente:** aparece na mesma jornada, mas não substitui a oferta principal;
- **Parceiro/integração:** coopera com a conta, não compete necessariamente;
- **Menção apenas:** citado junto sem evidência de relação competitiva;
- **Incerto:** informação insuficiente ou conflitante.

Somente `Direto` deve entrar automaticamente em uma lista chamada concorrentes
diretos.

## Decisão V2

Antes de pesquisar, responder:

> O que mudará se identificarmos os concorrentes desta conta?

Usos válidos incluem:

- encontrar empresas que usam ou substituem determinada categoria;
- construir tese de displacement;
- decidir exclusões ou adjacências do ICP;
- avaliar maturidade de mercado;
- registrar contexto competitivo necessário à classificação da lista.

Se o resultado servir apenas como curiosidade ou uso posterior de outreach, não
gastar AI Research durante qualificação.

Executar:

1. confirmar identidade, produto e segmento da conta;
2. definir concorrência direta para a tese em questão;
3. coletar candidatos e fontes;
4. deduplicar empresas, produtos e marcas;
5. validar relação competitiva na skill;
6. atribuir tipo, confiança, geografia e segmento;
7. só então produzir a lista curta de nomes.

## Hierarquia e uso das fontes

Preferir:

1. páginas oficiais de comparação ou migração, com cautela comercial;
2. avaliações e categorias estruturadas com explicação de similaridade;
3. relatórios e mapas de mercado datados;
4. casos de clientes que documentem substituição;
5. discussões de usuários como evidência de percepção ou alternativa;
6. agregadores como pistas que exigem confirmação.

Uma fonte independente que descreva a substituição vale mais que múltiplas listas
sem contexto.

## Contrato factual recomendado

```text
Research context
- researched_at:
- target_company:
- target_domain:
- target_product_or_category:
- target_segment:
- target_geography:
- identity_status: confirmed | ambiguous | not_confirmed

Competitor candidate
- candidate_name:
- candidate_domain:
- candidate_product:
- relationship_claimed: direct | partial | indirect | substitute | adjacent | partner | mention | uncertain
- overlapping_problem:
- overlapping_buyer:
- overlapping_segment:
- source_url:
- source_type: official | review_platform | market_map | customer_case | community | aggregator
- source_date:
- evidence_excerpt:

Validation
- relationship_validated:
- confidence: low | medium | high
- conflicting_evidence:
```

Instruir o Apollo a não retornar somente nomes, não assumir que `alternative`
significa concorrente direto e não fundir marca, produto e empresa.

## Classificação fora do Apollo

A skill deve produzir:

1. candidatos encontrados;
2. tipo de relação competitiva;
3. evidência e confiança;
4. relevância para a tese de prospecção;
5. lista curta final, quando solicitada.

Classificar a relevância comercial como:

- **Direta:** altera qualificação, exclusão ou tese de substituição;
- **Secundária:** altera priorização ou caso de uso;
- **Contextual:** informa a lista, sem afetar o gate;
- **Irrelevante:** não muda nenhuma decisão;
- **Incerta:** falta ligação causal com a prospecção.

## Quando usar AI Research do Apollo

Usar o template ou uma versão factual somente quando filtros, dados já
disponíveis, bases e pesquisa adequada não conseguirem coletar os candidatos e a
evidência necessários. Nesse caso:

- pedir candidatos, tipo de relação alegado, fonte, data e trecho de evidência;
- não pedir ao modelo do Apollo que decida quais são concorrentes diretos finais;
- validar e classificar a relação na skill.

Volume, automação ou necessidade de um campo no workflow não justificam delegar
o raciocínio ao Apollo. Recursos estruturados podem ser usados mesmo se pagos.

## Regras de execução e atualização

1. Rodar uma vez por domínio, produto e segmento, não por contato.
2. Não pesquisar antes de explicar qual decisão será afetada.
3. Não usar AI Research para recomprimir candidatos já disponíveis em fontes do projeto.
4. Guardar fontes e data para evitar regeneração desnecessária.
5. Revalidar após aquisição, rebranding ou mudança relevante de produto.
6. Não revelar contatos para pesquisar concorrentes.
7. Não calcular créditos; o Apollo informa o consumo ao usuário.

## Princípio transferível

Uma lista de nomes é o produto final, não a evidência. Apollo encontra candidatos;
a skill valida identidade, tipo de concorrência, confiança e utilidade comercial.
