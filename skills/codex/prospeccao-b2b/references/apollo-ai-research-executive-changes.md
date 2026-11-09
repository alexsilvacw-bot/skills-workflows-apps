# AI Research do Apollo: Know if a company had executive changes

Referência capturada da interface do Apollo em 18 de julho de 2026. Usar ao
avaliar mudanças de liderança como sinal de timing, desenhar pesquisas temporais
ou decidir se essa investigação deve acontecer no Apollo ou fora dele.

## Resumo executivo

O template pesquisa site oficial e fontes externas para encontrar mudanças de
executivos ou conselheiros nos três meses anteriores. Ele exige verificação da
identidade e pede cargo, pessoa, ação, data e links.

Este é um bom padrão de aquisição factual. Na V2, preservá-lo como opção de
pesquisa, mas não transformar qualquer mudança executiva em fit ou intenção.
Registrar a janela exata, distinguir anúncio de data efetiva e calcular na skill
se a função e o tipo de mudança têm relação causal com a oferta.

## Comportamento original

**Missão:** determinar se uma empresa teve mudanças executivas nos últimos três
meses.

**Entradas:**

- nome da conta;
- website da conta.

**Fontes originais:**

- blog, imprensa, notícias e atualizações no site da empresa;
- grandes publicações e fontes de notícias consideradas reputáveis.

**Eventos procurados:**

- nomeações;
- renúncias;
- promoções;
- desligamentos;
- mudanças em CEO, CFO, COO, CMO, CTO ou President;
- Chief People Officer, Head of Strategy, VP of Operations;
- outros C-levels e membros do conselho.

**Verificação:** confirmar identidade usando simultaneamente nome e website.

**Saída original:**

- declaração positiva ou negativa sobre mudanças nos últimos três meses;
- quando positivas: cargo, pessoa, ação, data e links;
- quando negativas: `No executive changes identified in the last 3 months` e
  nota breve sobre as fontes consultadas.

## Padrões úteis

- pesquisar fonte primária e confirmação externa;
- verificar identidade antes de associar um evento;
- usar janela temporal delimitada;
- procurar vários tipos de transição, não apenas nomeações;
- exigir campos objetivos e links;
- registrar fontes consultadas mesmo quando nada for encontrado;
- produzir uma constatação factual, sem depender do Context Center.

## Problemas e riscos

### Janela relativa sem data de corte

`Last 3 months` muda diariamente. Sem `as_of_date`, a mesma execução não é
reproduzível e o resultado fica obsoleto rapidamente. Registrar:

- data de corte da pesquisa;
- início e fim da janela;
- data de execução;
- validade ou próxima data de atualização.

### Data de anúncio e data efetiva são diferentes

Uma nomeação pode ser anunciada dentro da janela e começar depois; ou começar
dentro da janela e ter sido anunciada antes. Preservar:

- `announcement_date`;
- `effective_date`;
- qual delas fez o evento entrar na janela;
- evento futuro, vigente ou concluído.

### Escopo de liderança é inconsistente

O texto inclui C-suite, board, Head of Strategy e VP of Operations, mas a saída
resume o universo como `CXO/board`. Definir antes da execução:

- C-suite e presidentes;
- conselho;
- heads e VPs materialmente relevantes;
- subsidiária, região ou unidade versus grupo inteiro.

Não tratar todo VP ou board member como equivalente a CEO/CFO.

### Ausência de resultado não prova ausência de evento

`No executive changes identified` deve significar que nada foi encontrado nas
fontes e janela consultadas, não que a empresa comprovadamente não teve mudança.
Registrar cobertura, bloqueios, fontes inacessíveis e nível de confiança.

### Identidade exige mais que nome e URL

Além de nome e domínio, verificar:

- entidade legal, marca e grupo econômico;
- controladora e subsidiárias;
- país ou região;
- executivo da empresa versus executivo de unidade ou parceiro;
- domínio canônico da fonte oficial.

### Duplicação e eventos relacionados

Várias notícias podem descrever o mesmo evento. Uma saída e uma entrada também
podem ser lados da mesma sucessão. Deduplicar por empresa, cargo, pessoa, ação e
data, mantendo múltiplas fontes como corroboração.

### Mudança não é automaticamente sinal positivo

Uma troca pode indicar revisão de fornecedores, orçamento novo ou iniciativa;
mas também instabilidade, congelamento ou nenhuma relação com a oferta. A função
mudada importa:

- CPO tende a ser mais relevante para oferta de People/HR;
- CFO para finanças, risco ou eficiência financeira;
- CTO/CIO para tecnologia e infraestrutura;
- COO/Operations para processos e operação;
- board pode ter baixa influência operacional imediata.

Calcular relevância depois, usando a tese comercial.

## Decisão V2

Usar mudanças executivas como sinal factual de timing, nunca como baseline de
fit. Antes de pesquisar, definir:

1. quais funções de liderança são relevantes para a oferta;
2. quais ações representam abertura, risco ou neutralidade;
3. qual janela temporal e data de corte usar;
4. se a pesquisa mudará Tier, timing ou ordem da lista;
5. se filtros, sinais, enriquecimentos ou fontes adequadas já conseguem coletar
   o evento sem AI Research.

Pesquisar somente contas que passaram pelo baseline ou contas ambíguas em que o
evento possa resolver uma decisão.

## Hierarquia recomendada de fontes

Priorizar:

1. comunicado oficial, newsroom, relações com investidores ou filing regulatório;
2. perfil oficial da liderança ou página institucional atualizada;
3. publicação jornalística reputável com data e autoria;
4. veículo setorial reconhecido;
5. bases agregadoras como pista, não como única confirmação.

Para evento positivo, preferir uma fonte primária ou duas fontes independentes.
Para achado negativo, listar quais classes de fontes foram consultadas.

## Contrato factual recomendado

```text
Research window
- as_of_date:
- window_start:
- window_end:
- researched_at:

Company identity
- company_name:
- canonical_domain:
- entity_scope: group | subsidiary | business_unit | uncertain
- identity_status: confirmed | ambiguous | not_confirmed

Executive event
- person:
- role:
- organizational_scope:
- action: appointment | resignation | promotion | termination | board_change | other
- announcement_date:
- effective_date:
- window_basis: announcement | effective | both
- event_status: announced | effective | completed | uncertain
- source_url:
- source_type: primary | filing | reputable_news | trade_press | aggregator
- evidence_excerpt:

Coverage when no event is found
- sources_checked:
- blocked_or_unavailable_sources:
- result: no_change_identified | insufficient_coverage
- confidence: low | medium | high
```

Instruir o Apollo a não estimar impacto comercial, não inventar datas, não fundir
empresas homônimas e não converter `não encontrado` em prova de inexistência.

## Classificação fora do Apollo

Depois da coleta, a skill avalia:

- **Relevância funcional:** direta, adjacente, irrelevante ou incerta;
- **Tipo de abertura:** provável abertura, provável risco, neutra ou incerta;
- **Recência:** dentro da janela, fora da janela ou data desconhecida;
- **Confiança:** baixa, média ou alta;
- **Força de timing:** forte, moderada, fraca, ausente ou desconhecida.

Exemplos de timing forte exigem função relevante, evento recente confirmado e
uma cadeia causal plausível com revisão de processo, equipe ou fornecedor. Uma
mudança de board sem relação funcional pode permanecer apenas contextual.

## Quando usar AI Research do Apollo

Usar AI Research somente quando filtros, sinais, enriquecimentos, dados
disponíveis e outras fontes adequadas não conseguirem coletar o evento necessário.
Nesse caso:

- pedir evento, função, pessoa, ação, data, URL e cobertura das fontes;
- não pedir ao modelo que avalie fit, urgência ou Tier;
- trazer o resultado para a skill calcular a relevância e o timing.

Volume, automação ou necessidade de um campo no workflow não bastam para delegar
o raciocínio ao modelo. Recursos estruturados do Apollo podem ser usados mesmo
quando consomem créditos.

## Regras de execução e atualização

1. Rodar uma vez por domínio e entidade, não por contato.
2. Não pesquisar contas já desqualificadas estruturalmente.
3. Não pesquisar todas as funções se somente algumas forem relevantes.
4. Registrar `as_of_date` e expiração do sinal.
5. Reutilizar o resultado até expirar; não regenerar em cada lista ou pessoa.
6. Não calcular créditos; o Apollo informa o consumo ao usuário.
7. Não revelar contatos para investigar liderança.
8. Atualizar somente quando a janela avançar ou surgir novo gatilho.

## Princípio transferível

Pesquisa temporal deve produzir eventos verificáveis e datados. A mudança é um
fato; seu impacto comercial é uma inferência separada. Apollo encontra o evento,
a skill calcula relevância, direção e força do timing.
