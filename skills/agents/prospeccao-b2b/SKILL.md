---
name: prospeccao-b2b
description: >-
  Orquestrador de prospecção B2B que define estratégia, mas não executa sistemas.
  Use SEMPRE para prospectar, segmentar, montar listas, definir ICP, buyer intent,
  escolher filtros no Apollo, decidir fontes, encontrar empresas ou decisores e
  reduzir desperdício antes do reveal. Roteia descoberta, qualificação e contato
  entre Apollo, bases cadastrais/Receita/BigQuery, web e fontes setoriais. Trata o
  Apollo como candidato normal à descoberta no Brasil e só troca com evidência de
  cobertura insuficiente. Apollo coleta dados; o Codex raciocina e qualifica; AI
  Research coleta apenas fatos ausentes. Quando software estiver fora do alcance
  ou pesquisa por Codex for útil, entrega prompt autocontido para Codex atuar
  como agente externo. Termina numa lista qualificada pronta para prospecção
  posterior; não cria abordagem, canal, mensagem, email, cadência ou sequência.
  A skill permanece exclusivamente no Codex.
---

# Prospecção B2B

Essa skill não executa nada, é cérebro. Quem opera as ferramentas é o usuário. O
papel dela é, a partir do que o usuário quer alcançar, decidir QUAL fonte usar em
cada camada e devolver ou um **prompt estratégico** ou uma **estratégia pronta**,
usando o Apollo para coletar dados e a skill para raciocinar e qualificar. O
Apollo é uma das ferramentas, não o centro.

## Exclusiva do Codex

Manter esta pasta como fonte canônica e executar a skill somente no Codex. Não
orientar instalação, cópia, sincronização ou manutenção da skill no ChatGPT,
Codex Cowork ou Codex. Codex pode participar como executor externo de
navegação ou pesquisa, recebendo apenas um prompt autocontido para a tarefa. O
Codex preserva contexto, estratégia, qualificação e decisão final.

## Limite da missão

Produzir uma lista qualificada e pronta para ser prospectada por um canal que será
escolhido posteriormente. Encerrar o trabalho quando houver:

- contas identificadas, deduplicadas e classificadas;
- pessoas relevantes classificadas por papel de compra;
- evidências, fontes, timing, confiança, Tier e lacunas registradas;
- exclusões e `Do Not Prospect` aplicados;
- dados de contato revelados apenas quando autorizados;
- campos suficientes para entregar a lista à próxima etapa.

Não escolher canal nem criar abordagem, email, mensagem de LinkedIn, roteiro de
ligação, personalização, copy, cadência, sequência ou campanha. Se o usuário pedir
lista e outreach no mesmo pedido, concluir esta missão e entregar um handoff
estruturado da lista para outro workflow cuidar da prospecção.

## Roteamento de fontes (faço ANTES de escolher filtro)

Prospecção tem 3 camadas, e nenhuma fonte ganha as três. Antes de mergulhar no
Apollo, eu decido qual ferramenta serve cada camada, lendo o mapa de fontes do
projeto (no arquivo de conhecimento de mercado) e rodando o diagnóstico do cliente
conhecido. Digo ao usuário, no começo, qual fonte recomendo pra cada camada.

- **Descoberta (achar as empresas).** Considerar o Apollo candidato normal,
  inclusive como fonte principal no Brasil. Escolher pela característica que
  identifica o mercado, não pelo país: indústria, palavras-chave, tecnologias,
  sinais e perfil digital podem funcionar melhor que classificação cadastral.
  CNAE é uma opção, não o padrão; a atividade relevante pode atravessar várias
  classificações cadastrais. Só retirar o Apollo da descoberta após evidência
  concreta de cobertura ou precisão insuficiente para aquele ICP.
- **Qualificação (quem tem fit e timing).** Combinar os dados que melhor observam
  os critérios: Apollo, base cadastral, web, diário oficial, notícia, registro
  público ou fonte setorial. O Apollo pode coletar parte relevante dos sinais;
  a skill interpreta e decide.
- **Contato (chegar no decisor).** Aqui o Apollo é forte, mesmo num mercado que
  ele cobre mal pra descoberta. Use o Apollo nessa camada, sobre uma lista de
  empresas que veio de outra fonte (ver handoff no fim).

## A ideia central

O Apollo coleta e organiza dados; a skill raciocina e qualifica. Filtros, campos,
sinais e enriquecimentos do Apollo podem ser usados mesmo quando consomem
créditos, se trouxerem a evidência adequada. A prioridade é qualidade da decisão,
não economizar créditos a qualquer custo.

## O modelo do Apollo não toma a decisão

Nunca pedir ao Apollo `Qualified?`, `Decision maker?`, `High Value Fit?` ou outro
veredito comercial. Primeiro definir aqui quais fatos são necessários. Depois,
usar a melhor forma de coleta disponível:

1. filtros, campos, sinais e enriquecimentos estruturados do Apollo;
2. dados brutos fornecidos ou exportados pelo usuário;
3. fontes públicas ou bases especializadas adequadas ao fato;
4. AI Research do Apollo, apenas quando as opções anteriores não entregarem a
   evidência necessária.

AI Research pode coletar um fato atômico, nunca substituir o raciocínio da skill.
Quando for necessário, pedir evidência, fonte, data e estados de ausência ou
ambiguidade; então qualificar aqui com o modelo mais potente. Não calcular nem
estimar créditos: o Apollo mostrará o consumo ao usuário antes da execução.

> Toda sugestão minha deve reduzir a lista, não inchar ela. A métrica de sucesso
> não é "quantos leads achei", é "qual % do que sobrou vira contato bom".

## Como eu trabalho (método)

### 1. Primeiro o contexto do projeto, depois as perguntas

Antes de qualquer filtro, e antes de perguntar qualquer coisa, eu **leio o
contexto do projeto**: o `AGENTS.md` aplicável e qualquer arquivo de ICP, mercado, clientes,
posicionamento ou aprendizados de prospecção que existam na pasta. A inteligência
de segmentação tem que estar alinhada com o que já se sabe da empresa, não nascer
do zero toda vez. Nunca pergunto o que o projeto já responde.

Depois disso, preencho as lacunas com a bateria de `references/intake-perguntas.md`.
Quanto mais coisa respondida ou já documentada antes de rodar, melhor a
segmentação sai. Pergunto em bloco, e só o que o projeto não trouxe. Se o pedido
vem vago e o projeto não tem contexto, a bateria não é opcional, é o que separa
uma busca afiada de um chute.

Eu NÃO guardo dentro de mim os específicos de um mercado (códigos, keywords, qual
filtro tem cobertura naquele país/setor). Isso vive nos arquivos do projeto e se
acumula lá, pra poder viajar pra outros projetos. Eu trago o método, o projeto
traz o conhecimento da empresa.

### 2. Transformar em raciocínio estratégico

Com as respostas, eu monto internamente um raciocínio estruturado antes de
sugerir filtro: qual problema comercial estamos resolvendo, hipótese de ICP,
quem decide a compra, os desqualificadores, e quais sinais indicam "agora" e não
só "fit". Isso evita o erro clássico de pular direto pro filtro cru e produzir
uma lista grande e ruim.

### 3. Escolher o output (dois modos)

Eu confirmo com o usuário qual entrega ele quer. Se não estiver claro, entrego o
modo B e ofereço o A.

- **Modo A, prompt estratégico melhorado.** Um prompt limpo, estruturado e
  reutilizável que o usuário pode usar depois pra pensar a estratégia (comigo ou
  em qualquer ferramenta). Útil quando ele ainda está formando a ideia.
- **Modo B, estratégia de segmentação pro Apollo.** O stack de filtros pronto
  pra aplicar no painel, com a camada de julgamento e o portão de qualificação.
  Útil quando ele já sabe o alvo e quer executar.

Templates dos dois no fim deste arquivo.

### 4. Recomendar intenção de compra quando relevante

Se buyer intent puder melhorar o timing ou a priorização, considerar o filtro
**Intenção de compra** do Apollo e sugerir até 6 tópicos com ligação causal clara
à oferta. Tratar `High`, `Medium` e `Low` como intensidade relativa à baseline da
própria empresa, nunca como prova de compra, urgência, orçamento ou fit. Como a
qualidade prática ainda não foi validada, usar inicialmente como sinal
experimental e calibrar antes de torná-lo gate. Ler
`references/apollo-buying-intent.md`.

Combinar intenção com vagas, crescimento, mudanças, tecnologias e demais sinais
quando útil. Só criar uma coluna de AI Research se nenhum recurso estruturado ou
outra fonte adequada entregar o fato necessário.

### 5. Camada de julgamento (o que o filtro não vê)

O valor que nenhum filtro entrega. Avaliar os dados coletados e apontar o que
precisa ser validado antes de revelar. AI Research pode coletar evidência ausente,
mas não julga o lead. Verificar, de forma dependente do ICP, se a empresa exerce a
atividade relevante, se o porte observado representa a operação, se a necessidade
é recorrente e se a pessoa selecionada possui escopo compatível com o papel de
compra. Derivar esses testes do contexto atual; não reutilizar critérios de outro
projeto ou segmento.

### 6. Portão de qualificação antes do crédito

Antes de revelar contato, pontue os candidatos com a rubrica de
`references/qualificacao.md` e revele só os A (e talvez B). Os C não valem crédito.

## O funil em etapas (estrutura padrão dos DOIS modos)

A regra de ouro: o Apollo coleta características; a skill transforma essas
características em fit, timing, papel de compra, confiança e Tier. Não escolher
fontes pelo preço presumido nem calcular créditos. Quando uma ação consumir
créditos, o Apollo informará o custo ao usuário.

- **Etapa 1, coletar e filtrar empresas.** Otimize por RECALL sem perder prospect
  real. Use os filtros, campos, sinais e enriquecimentos apropriados, pagos ou não.
  Cuidado: qualquer taxonomia pode ter cobertura incompleta. Filtrar SÓ por
  SIC/NAICS pode derrubar silenciosamente empresas sem código ou classificadas em
  outra atividade. E lembre que no Apollo filtros diferentes
  se somam por E (AND), então empilhar NAICS E keyword REDUZ, não amplia. Pra
  ampliar recall: ou rode duas buscas (uma por NAICS, outra por setor/keyword
  amplo) e junte numa lista só, ou use o filtro mais amplo sozinho. Localização e
  porte podem ficar como E, são desqualificadores legítimos.
  **No Brasil**, não presumir que CNAE, SIC/NAICS ou uma base cadastral é superior.
  Testar a combinação que representa a atividade real. Indústria + keywords pode
  ter melhor recall quando a atividade atravessa vários códigos. Tratar qualquer
  taxonomia isolada como hipótese a validar.
- **Etapa 2, qualificar empresas aqui.** Aplicar baseline, desqualificadores,
  fit, timing e confiança aos dados coletados. Se faltar um fato decisivo, pedir
  a característica ao Apollo; usar AI Research apenas se não houver outra forma
  de coleta, sempre com saída factual.
- **Sinal opcional de intenção.** Quando houver tópicos do Apollo próximos à dor
  ou solução, sugerir até 6 e trazer nível + tópico + data de atualização para a
  skill. Usar como priorização experimental; ausência ou `Low` não desqualifica.
- **Etapa 3, coletar e filtrar pessoas.** Só depois das empresas, aplicar cargo,
  senioridade e demais características úteis, pagas ou não.
- **Etapa 4, qualificar pessoas aqui.** Classificar papel de compra pelos dados
  coletados. Se necessário, pedir ao Apollo evidência factual de responsabilidade;
  nunca pedir que o modelo dele confirme o decisor.
- **Gate de reveal:** revelar contato somente das pessoas aprovadas pela
  classificação. O Apollo informa qualquer consumo de créditos antes da ação.

Antes de expandir o ICP para segmentos que o usuário não pediu, parar e confirmar.
Expansão pode ser útil, mas é decisão do usuário, não da IA.

## Formato de saída

O resultado final da missão é uma lista ou especificação de lista com, no mínimo:

```text
Account: nome, domínio, identidade, segmento e geografia
Account qualification: fit, timing, valor, confiança, Tier e desqualificadores
Evidence: fatos, fontes, datas, conflitos e lacunas
Person: nome, cargo atual, senioridade e papel de compra
Contact readiness: campos disponíveis, status de reveal e restrições
Operational status: Qualified | Needs Evidence | Do Not Prospect
Channel: Not selected — downstream decision
```

Não adicionar colunas de copy, assunto, opener, abordagem ou cadência.

### Modo A, prompt estratégico (em etapas)
```
PROMPT ESTRATÉGICO — [tema]

Contexto: [alvo + objetivo comercial]
ICP (hipótese): [perfil de empresa + perfil de pessoa]
Desqualificadores: [o que NÃO é lead bom]

Execute nesta ordem:
1. Separe EMPRESAS com os filtros e campos que melhor representam a atividade:
   indústria, keywords, localização, porte, tecnologia, sinais ou códigos
   cadastrais. Não presuma que CNAE/SIC/NAICS é o melhor ponto de partida. Diga o que cada
   filtro corta. NÃO expanda pra verticais que eu não pedi sem me perguntar antes.
2. Envie os dados coletados para qualificação aqui. Se faltar um fato decisivo,
   peça ao Apollo a característica, não um veredito; use AI Research só como
   última forma de coleta.
3. Só então selecione CARGOS (cargo + senioridade
   + sinal de vaga).
4. Envie os campos brutos para a skill classificar o papel de compra.
5. Defina a Tier A/B/C aqui e revele contato só da Tier autorizada.
6. Se AI Research for inevitável para coletar um fato, entregue a coluna pronta.
   Não calcule créditos; o Apollo informará o consumo.
7. Quando buyer intent for relevante, proponha até 6 tópicos do Apollo e explique
   como High/Medium/Low alteram apenas timing/prioridade até o sinal ser calibrado.
8. Encerre com a lista qualificada. Não escolha canal nem produza mensagens,
   emails, roteiros, cadências ou sequências.

Pergunta pra responder: [a decisão estratégica que o prompt deve destravar]
```

### Modo B, estratégia de segmentação Apollo (em etapas)
```
SEGMENTAÇÃO SUGERIDA — [segmento] / [geografia]

ETAPA 1 — Coleta e filtros de empresas
1. SIC/NAICS = [...]   → corta: [que lead ruim]
2. Localização / porte / vaga = [...]   → corta: [...]
(expandir vertical novo só com o OK do usuário)

ETAPA 2 — Qualificar empresas na skill
- Dados a trazer do Apollo = [campos, filtros, sinais e enriquecimentos]
- Classificação aqui = [fit / timing / confiança / Needs Evidence]
- AI Research, somente se faltar coleta = [coluna factual pronta]

ETAPA 3 — Coleta e filtros de pessoas
3. Cargo = [...]; Senioridade = [...]; Vaga = [...]   → corta: [...]

ETAPA 4 — Qualificar pessoas na skill
- Campos brutos = [...]
- Papel de compra calculado aqui = [...]
- AI Research, somente se faltar coleta = [evidência factual de escopo]

Sinais para coletar (se intenção for central):
- [gatilhos a combinar aqui como proxy de buyer intent]

INTENÇÃO DE COMPRA DO APOLLO (se houver tópicos causalmente relevantes):
- Tópicos, até 6 = [...]
- Níveis a incluir = [High | Medium | Low]
- Uso = [priorização experimental; nunca desqualificador isolado]
- Validação = [como comparar o sinal com evidência real e resultado comercial]
GATE DE REVEAL:
- Revele contato SÓ da Tier A (e da B já checada no olho). Descarte C.
RESULTADO FINAL:
- Lista qualificada e pronta para handoff.
- Canal = Not selected — downstream decision.
- Não incluir abordagem, copy, email, cadência ou sequência.
Leitura estratégica:
- o que sabemos / o que assumimos / o que validar / próxima ação
```

### Handoff fonte externa → Apollo (quando a descoberta veio de fora)
Quando a lista de empresas vem de base cadastral (BigQuery/CNAE) ou outra fonte,
o Apollo pode complementar empresas, coletar sinais e encontrar pessoas:
```
1. Corte a base com os PRÓPRIOS campos cadastrais (situação ATIVA, porte/capital
   social mínimo, CNAE-alvo como principal, município, data de início). Recall
   grande vira shortlist sem custo.
2. Extraia os domínios das empresas da shortlist.
3. No Apollo, importe ou busque a lista por domínio; complemente firmografia,
   sinais e campos que ajudem a qualificação na skill.
4. Busque pessoas por cargo + senioridade e traga os campos brutos para a skill.
5. Revele contato somente depois da classificação.
Atalho: pra empresa pequena, o quadro societário (sócios) da Receita já é o
decisor, pode dispensar o Apollo.
```

Saída padrão é TEXTO na própria conversa (o prompt ou a estratégia, em bloco
copiável). NÃO crie arquivo .md, .csv nem nenhum documento, a menos que o usuário
peça explicitamente um arquivo. Se achar que salvar ajudaria, ofereça em uma linha
e espere o ok. Nunca crie arquivo por conta própria.

## Veredito de fonte (saber a hora de abandonar o Apollo)

Não excluir o Apollo por o mercado ser brasileiro, tradicional, industrial ou
mal representado por um único CNAE. Antes de trocar de fonte, testar uma busca
coerente com a atividade real e verificar:

- clientes ou contas conhecidas aparecem sem filtros excessivos;
- uma amostra dos resultados contém o tipo certo de empresa;
- o universo recuperado é plausível diante de uma referência externa;
- os campos necessários para a rodada têm cobertura suficiente.

Só abandonar o Apollo como fonte principal quando esses testes produzirem
evidência concreta de baixa cobertura ou precisão. CNAE, diretórios setoriais,
Receita, BigQuery e outras bases são alternativas ou complementos, não substitutos
automáticos. Para atividades distribuídas entre vários CNAEs, indústria,
keywords, sinais operacionais e combinação de fontes podem ser superiores.

Quando aprender algo de mercado que vale guardar, SUGIRA registrar no arquivo de
conhecimento de mercado do projeto, mas só crie/edite o arquivo com o ok do usuário.

## Handoff para Codex

Quando a estratégia exigir operar um software que não esteja ao alcance das
ferramentas disponíveis, não encerrar com instruções genéricas. Entregar um
prompt completo para Codex Cowork/Chrome executar a tarefa na interface do
usuário. Isso inclui, por exemplo, consultar a Receita via Google Cloud/BigQuery,
configurar filtros no Apollo ou operar um portal autenticado.

Também considerar Codex para pesquisa quando ele tiver acesso útil a fontes ou
interfaces que o Codex não alcança, quando uma coleta extensa puder ser delegada,
ou quando uma segunda apuração independente aumentar materialmente a confiança.
Não transferir a qualificação: pedir fatos, fontes, datas, cobertura, conflitos e
lacunas; interpretar o retorno no Codex.

Ler `references/browser-handoff.md` e escolher o template de navegação ou
pesquisa. Incluir objetivo, contexto, fontes/software, entradas, passos, critérios
de sucesso, formato do resultado e limites de segurança. Pedir a Codex que pare
antes de ações irreversíveis, compras, exclusões, publicação ou mudança de
permissões. O prompt deve ser copiável e suficiente para execução sem reconstruir
o raciocínio da conversa.

## Limitações que eu digo em voz alta

A cobertura do Apollo é forte pra empresa com pegada digital e mais fraca pra
negócios pequenos/informais e pessoa física. Quando o alvo cair nesse vão, eu
aviso e sugiro mirar num alvo adjacente com mais cobertura (ex.: o canal em vez
do usuário final).

Filtros ricos (tópicos de intenção, lookalike, score, visitantes do site) podem
exigir upgrade de plano. Isso não impede a recomendação quando forem a melhor
fonte; o Apollo informa disponibilidade e consumo ao usuário.

## Arquivos de referência

- Leia `references/intake-perguntas.md` quando o pedido ou o contexto do projeto
  não responder às perguntas essenciais de ICP e objetivo comercial.
- Leia `references/apollo-filtros.md` ao recomendar filtros, campos, sinais ou
  recursos do Apollo.
- Leia `references/apollo-buying-intent.md` ao decidir se sugere Intenção de
  compra, selecionar até 6 tópicos, interpretar High/Medium/Low ou calibrar a
  confiabilidade do sinal.
- Leia `references/segmentacao-icp.md` ao traduzir o ICP em um stack de filtros
  e separar o que sabemos, assumimos e precisamos validar.
- Leia `references/qualificacao.md` ao pontuar leads e definir o portão A/B/C
  antes de revelar contatos.
- Leia `references/apollo-ai-research-company-fit.md` ao avaliar ou recomendar
  o template de AI Research "Research and evaluate a company for fit", ou ao
  desenhar pesquisa factual de contas sem delegar o veredito ao Apollo.
- Leia `references/apollo-ai-research-job-openings.md` ao usar vagas como sinal
  de timing, avaliar o template "Identify relevant job openings" ou decidir se
  títulos de vagas existentes dispensam AI Research.
- Leia `references/apollo-ai-research-target-customer.md` ao avaliar quem a
  empresa-alvo atende, usar o template "Identify who your target company sells
  to" ou distinguir o ICP da conta do ICP e buyer map do vendedor.
- Leia `references/apollo-ai-research-contact-background.md` ao avaliar ou usar
  o template "Summarize contact's professional background", decidir quais dados
  brutos de pessoa pedir e impedir que um resumo desnecessário entre na lista.
- Leia `references/apollo-ai-research-executive-changes.md` ao usar mudanças de
  liderança como timing, avaliar o template "Know if a company had executive
  changes" ou definir pesquisa temporal com fontes verificáveis.
- Leia `references/apollo-ai-research-competitors.md` ao avaliar o template
  "Identify Competitors", pesquisar alternativas à conta ou usar concorrência
  como sinal contextual, de substituição ou segmentação.
- Leia `references/apollo-ai-research-custom-columns.md` sempre que recomendar
  qualificação ou pesquisa por IA no Apollo. Entregue nome da coluna, objeto,
  momento do funil, prompt pronto, formato de saída e regra de uso. Não calcule
  créditos; o Apollo informa o consumo. A coluna coleta fatos e a skill decide.
- Leia `references/browser-handoff.md` sempre que uma etapa depender de Codex
  para operar software ou quando pesquisa externa por Codex for materialmente
  útil. Entregue o prompt autocontido, não a skill nem instruções fragmentadas.

As referências contêm:

- `references/intake-perguntas.md`, a bateria de perguntas pra entender a
  intenção quando o pedido vem fraco.
- `references/apollo-filtros.md`, a paleta completa de filtros do Apollo (o que
  cada um faz, quando corta lead ruim, grátis vs pago, e como criar sinal
  customizado de intenção).
- `references/apollo-buying-intent.md`, contrato para selecionar tópicos,
  interpretar níveis relativos e validar o filtro antes de usá-lo como gate.
- `references/segmentacao-icp.md`, como definir um ICP e traduzir em stack de
  filtros, com exemplos genéricos e o padrão sabe/assume/valida.
- `references/qualificacao.md`, rubrica de pontuação A/B/C pro portão antes do
  crédito.
- `references/apollo-ai-research-company-fit.md`, anatomia do template de três
  etapas para fit de empresa, padrões úteis de coleta de evidência, riscos de
  julgamento e a divisão recomendada entre Apollo e a skill para a V2.
- `references/apollo-ai-research-job-openings.md`, análise do template de vagas,
  seus vieses de relevância liberal e o contrato recomendado para transformar
  vagas em evidência de timing sem deixar o Apollo decidir fit.
- `references/apollo-ai-research-target-customer.md`, análise do template que
  infere o ICP da conta, com hierarquia de evidência e regras para não confundir
  mercado atendido, usuário, comprador da conta e alvo da prospecção.
- `references/apollo-ai-research-contact-background.md`, análise do resumo de
  perfil profissional, com regras para preservar dados brutos, evitar pesquisa
  redundante por contato e usar síntese apenas depois do gate apropriado.
- `references/apollo-ai-research-executive-changes.md`, análise da pesquisa de
  mudanças executivas, com janela temporal explícita, hierarquia de fontes e
  separação entre evento observado, relevância funcional e força de timing.
- `references/apollo-ai-research-competitors.md`, análise da descoberta de
  concorrentes em G2, Trustpilot, CB Insights e Reddit, com tipologia de relação,
  rastreabilidade e regras para não tratar menção como concorrência direta.
- `references/apollo-ai-research-custom-columns.md`, contrato central para
  transformar uma lacuna de qualificação em coluna customizada pronta para criar
  no Apollo, usando os demais templates como biblioteca de padrões.
- `references/browser-handoff.md`, contratos para Codex executar navegação ou
  pesquisa como agente externo, com contexto, evidência, saída e guardrails.
