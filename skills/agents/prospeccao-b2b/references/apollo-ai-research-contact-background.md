# AI Research do Apollo: Summarize contact's professional background

Referência capturada da interface do Apollo em 18 de julho de 2026. Usar ao
avaliar resumo de perfil profissional, selecionar campos de pessoa para
qualificação ou decidir se uma síntese deve acontecer no Apollo ou na skill.

## Resumo executivo

O template recebe campos que o Apollo já possui — cargo, headline, resumo e
formação — e os comprime em uma frase e um parágrafo. Só tenta acessar LinkedIn
quando todos os dados estiverem ausentes.

Na V2, não incluir esse resumo no output padrão. Enviar os campos brutos à skill,
classificar diretamente e preservar apenas os fatos e o papel de compra
necessários à lista qualificada. Qualquer síntese para uso comercial posterior
pertence a outro workflow.

## Comportamento original

**Missão:** resumir o histórico profissional de uma pessoa que trabalha na conta.

**Entradas:**

- nome e sobrenome;
- empresa e domínio;
- `%{context}` do vendedor;
- cargo atual;
- headline;
- resumo profissional;
- instituição de ensino;
- área de estudo.

**Fallback:** se não houver informação, visitar o LinkedIn informado. Se o perfil
não trouxer conteúdo relevante, retornar literalmente `No information available
for the contact.`

**Saída original:**

- uma frase concisa;
- um parágrafo curto sobre experiência;
- sem preâmbulo, cabeçalho ou explicação do método.

## Padrões úteis

- reunir campos dispersos de pessoa em uma leitura rápida;
- preservar uma resposta explícita quando não houver informação;
- não expor processo interno na saída;
- usar nome, empresa e domínio para contextualizar identidade;
- limitar a síntese para evitar biografias longas.

## Problemas e riscos

### Não é pesquisa quando os campos já existem

Cargo, headline, resumo e formação já são entradas. Pedir a uma coluna de AI
Research que apenas os reescreva não cria evidência nova. Se os
campos puderem ser exportados ou enviados, a skill pode sintetizá-los localmente.

### Resumo perde informação antes da decisão

Uma síntese pode apagar:

- diferença entre responsabilidade atual e experiência anterior;
- linguagem exata que prova escopo funcional;
- incertezas e campos ausentes;
- contradições entre cargo e headline;
- diferença entre formação e responsabilidade profissional;
- sinais de mudança recente de função.

Classificar a pessoa a partir do resumo gerado cria uma cadeia de inferência mais
frágil do que usar os campos brutos.

### O nome promete mais do que a entrada oferece

O template chama o resultado de `professional background`, mas não recebe:

- histórico de cargos;
- empresas anteriores;
- datas e duração;
- tempo no cargo atual;
- responsabilidades verificáveis;
- resultados ou áreas sob gestão.

Formação acadêmica não substitui histórico profissional.

### Context Center pode enviesar uma síntese neutra

O contexto do vendedor não é necessário para resumir fatos profissionais. Sua
presença pode induzir o modelo a destacar somente experiências convenientes à
oferta ou interpretar o perfil como comprador. Usar o contexto apenas na etapa
separada de classificação do papel de compra.

### LinkedIn como fallback é frágil

O template não exige:

- confirmação de que a URL pertence à pessoa correta;
- tratamento de perfil privado, bloqueado ou desatualizado;
- distinção entre ausência de acesso e ausência de informação;
- URL e data para cada fato coletado.

`No information available` pode significar falta de dados, falha de acesso ou
identidade não confirmada. Esses estados não devem ser fundidos.

### Saída redundante

Uma frase seguida de um parágrafo sobre os mesmos poucos campos pode repetir
conteúdo. O formato é adequado para leitura humana, mas não para cálculo,
auditoria ou classificação em lote.

### Execução multiplica por pessoa

Ao contrário da pesquisa de empresa, este template roda por contato. Aplicá-lo
antes do gate da conta ou sobre todos os cargos amplia rapidamente o consumo sem
melhorar a descoberta de empresas.

## Decisão V2

Executar nesta ordem:

1. aprovar a empresa no gate de conta;
2. aplicar cargo, senioridade, área e demais filtros fixos;
3. obter campos brutos dos candidatos;
4. classificar papel de compra e força da evidência na skill;
5. pedir evidência adicional somente para pessoas ambíguas cuja classificação
   possa mudar;
6. encerrar com os campos factuais e a classificação necessários à lista pronta
   para handoff.

Nunca usar o resumo produzido pelo Apollo como substituto dos campos originais.

## Dados brutos recomendados

Para qualificação de pessoa, preferir:

- nome;
- empresa e domínio canônico;
- cargo atual;
- departamento;
- senioridade;
- headline;
- resumo original;
- histórico de cargos, quando disponível;
- tempo no cargo atual;
- localização;
- LinkedIn URL;
- fonte e data de atualização de cada campo, quando disponíveis.

Formação acadêmica é contextual. Só deve influenciar qualificação quando houver
relação explícita com um papel técnico, regulado ou especializado.

## Estados de informação

Manter separados:

- **Available:** dados suficientes nos campos existentes;
- **Partial:** há dados, mas falta informação capaz de mudar a classificação;
- **Unavailable:** campos não fornecidos;
- **Access blocked:** fonte indicada existe, mas não pôde ser acessada;
- **Identity ambiguous:** não foi possível confirmar que o perfil pertence à
  pessoa certa;
- **Conflicting:** campos ou fontes divergem;
- **Stale:** a informação parece antiga ou não corresponde ao cargo atual.

Não converter esses estados em uma única mensagem de ausência.

## Classificação com dados brutos

A skill deve mapear a pessoa para um papel de compra:

- decisor econômico;
- dono funcional do problema;
- avaliador técnico;
- champion ou influenciador;
- compras/procurement;
- usuário;
- sem relação;
- incerto.

Avaliar separadamente:

- relevância funcional;
- autoridade explicitamente observada;
- senioridade compatível com o ticket;
- proximidade da dor;
- confiança da evidência.

Não inferir orçamento ou poder de compra somente pelo título.

## Contrato factual para pesquisa adicional

Se os campos brutos não bastarem e a informação puder mudar a Tier, pedir uma
pesquisa estreita, não um resumo genérico:

```text
Contact identity
- full_name:
- current_company:
- profile_url:
- identity_status: confirmed | ambiguous | not_confirmed

Current role
- title:
- department:
- start_date:
- evidence_excerpt:
- source_url:

Observed scope
- responsibility:
- scope_type: team | budget | process | technology | vendor | unknown
- evidence_excerpt:
- source_url:

Career evidence
- prior_role:
- prior_company:
- dates:
- evidence_excerpt:
- source_url:

Missing or conflicting evidence
- field:
- status: not_found | blocked | stale | conflicting
```

Instruir o Apollo a reportar fatos, não classificar decision maker, não inferir
autoridade pelo título e não preencher histórico ausente.

## Fora do escopo da skill

Um workflow posterior pode decidir criar um resumo para operação comercial,
CRM, preparação ou personalização. A Prospecção B2B não produz esse artefato:
seu handoff contém os fatos brutos relevantes, a classificação do papel de compra,
a confiança, as lacunas e a prontidão do contato. A etapa seguinte escolhe canal
e transforma esses dados em material de prospecção.

## Regras de coleta

1. Não usar AI Research para reescrever campos exportáveis.
2. Não rodar antes do gate de empresa.
3. Não rodar em cargos claramente irrelevantes.
4. Pesquisar somente pessoas ambíguas quando o novo dado puder mudar a Tier.
5. Recursos pagos de coleta podem ser usados; o modelo do Apollo não deve julgar
   o papel de compra.
6. Não revelar e-mail ou telefone apenas para obter um resumo profissional.
7. Não gerar resumo profissional como coluna da lista qualificada.
8. Não calcular créditos; o Apollo informa o consumo ao usuário.

## Princípio transferível

Dados brutos servem para decidir e compor a lista qualificada. Resumos e materiais
de comunicação pertencem ao workflow posterior. Preservar as fontes originais até
terminar a classificação. Apollo deve adicionar fatos, não comprimir evidência
antes do gate.
