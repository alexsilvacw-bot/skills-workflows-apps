# Paleta de filtros do Apollo (base de conhecimento do cérebro)

O que cada filtro faz e qual evidência ele coleta. Uso isso pra montar a
segmentação que o usuário vai aplicar no painel. A regra que orienta tudo: o
Apollo fornece características; a skill raciocina e qualifica. Um recurso pago
pode ser recomendado quando for a melhor fonte. A skill não calcula créditos;
o Apollo mostra o consumo ao usuário.

## Disponibilidade no plano

- **Grátis**: aplicar qualquer filtro de busca, ver firmographics, cargo, perfil.
  Busca de pessoas não revela email/telefone.
- **Custa crédito**: revelar/enriquecer contato (email, telefone verificado) e a
  busca de empresas (org search). É o clique do fim, não o do meio.
- **Pode exigir upgrade de plano**: tópicos de intenção extras, lookalike,
  scores, sinais avançados, campos de IA. Isso não torna o recurso inadequado;
  o Apollo mostrará disponibilidade e consumo antes da execução.

## Filtros de empresa (firmografia e contexto)

- **Localização da conta** (grátis). HQ da empresa. Incluir região, excluir
  região, ou raio de CEP. Corta: fora da área de atuação/suporte técnico.
  Cuidado: é o HQ, não a filial. Grupo com sede numa cidade e operação em outra
  aparece sob a sede.
- **Nº de funcionários** (grátis). Faixa pronta ou Min/Max, e opção "desconhecido".
  Corta: pequeno demais pra ter operação ou grande demais pro ticket. Proxy
  imperfeito do porte da operação, ver camada de julgamento.
- **Setor e palavras-chave** (grátis). Palavra-chave + escolha de ONDE procurar
  (nome da empresa, tags, etc.) e "Incluir TODOS". Corta: empresa que tem o termo
  mas não é do ramo. Palavra-chave deixa a busca mais lenta.
- **SIC e NAICS** (grátis). Código de classificação econômica, potencialmente
  mais preciso que palavra-chave para isolar uma atividade bem classificada.
  Corta: ruído de nome. Dá pra incluir e excluir códigos.
- **Segmentos de mercado** (grátis). Categorias prontas (B2B, B2C, SaaS, etc.).
  Mais útil pra empresas de tecnologia/serviços do que pra negócios tradicionais.
- **Receita** (grátis ver, faixa). Está entre / é conhecida / desconhecida, +
  Private/Public. Corta: porte financeiro incompatível com o ticket.
- **Financiamento** (grátis ver). Rodada (Seed, Series A/B/C, PE, M&A), valor
  total e última data/valor. Corta ou prioriza: empresa que acabou de captar tem
  budget. Mais útil pra empresas que captam investimento (tech/startups).
- **Tecnologias** (grátis). Tech stack da empresa (1.500+ techs), incluir e
  excluir. Serve mais pra empresas de software/tecnologia.
- **Ano de fundação** e **crescimento de headcount** (% num período). Sinais de
  momento. Empresa crescendo rápido tende a estar montando operação nova.
- **Headcount por departamento**. Tamanho de áreas específicas (ex.: operações,
  vendas). Bom pra confirmar que a operação relevante existe de fato.

## Sinais de intenção e timing (os mais valiosos)

- **Intenção de compra** (pode depender do plano). Seleciona até 6 tópicos entre
  mais de 200 e retorna High/Medium/Low no nível da conta. O nível compara volume
  e frequência de consumo com a baseline histórica da própria empresa; não mede
  propensão absoluta e não identifica a pessoa. Usar como timing/priorização
  experimental, nunca como prova de compra ou desqualificador. Dados informados
  como atualizados semanalmente. Ver `apollo-buying-intent.md`.
- **Vagas de emprego** (grátis). Cargos sendo contratados, local da vaga, data.
  Empresa contratando um cargo ligado ao que você vende está montando ou
  expandindo operação agora. Sinal de timing barato e poderoso.
- **Visitantes do site** (PAGO, de-anonimização). Empresas que visitaram o seu
  site. Quando existir, é lead quente, priorizar.
- **Sinais** (pode ser pago). Gatilhos como prêmios, reconhecimentos, mudanças.
- **Pontuações** (Apollo score, pode ser pago). Score do próprio Apollo. Trato
  como segunda opinião, não como verdade.
- **Semelhantes / lookalike** (Apollo AI, pode ser pago). A partir de clientes
  bons, acha parecidos. Ótimo depois que houver uma base de clientes que deram
  certo. Cedo demais sem amostra boa.

## Montar os dados necessários para medir buyer intent

Combine gatilhos concretos coletados pelo Apollo ou por outra fonte. O fato de um
recurso consumir créditos não é motivo para descartá-lo:

- Vaga aberta de um cargo específico ligado ao produto (sinal forte de timing).
- Captação recente ou crescimento de headcount numa área relevante (budget novo).
- Adoção (ou ausência) de uma tecnologia específica no stack.
- Visita ao site, quando disponível.
- Notícia/gatilho de expansão, nova unidade, troca de fornecedor.

A lógica: nenhum gatilho isolado prova intenção. O Apollo coleta os gatilhos; a
skill combina e interpreta `fit + timing`. Uma coluna de AI Research só é criada
se o fato necessário não existir em filtro, campo, sinal, enriquecimento ou outra
fonte adequada. Ela retorna evidência, nunca o veredito de intenção.

## Pessoas (quem é o alvo dentro da empresa)

- **Cargo/Título** (grátis). Casa 1 título já entra; traz títulos similares por
  padrão (desligar pra match estrito). Combinar com senioridade.
- **Senioridade** (grátis). owner, founder, c_suite, partner, vp, head, director,
  manager, senior, entry, intern. Só conta o cargo ATUAL.
- **Localização da pessoa** (grátis). Onde a pessoa mora (diferente do HQ).
- **Tempo no cargo atual** e **anos de carreira**. Quem assumiu cargo há pouco é
  gatilho de abertura (revisando fornecedores/processos).
- **Status do email** (verified, likely to engage, etc.). Pra priorizar quem tem
  contato mais provável de funcionar, antes de revelar.

## Filtros de CRM/conta (organização do trabalho, não descoberta)

- **Listas** (suas listas salvas), **Proprietário** (responsável da conta na
  equipe), **Etapa** (estágio no CRM: Cold, Current Client, Do Not Prospect),
  **Campos personalizados**. Servem pra não reprospectar quem já está na base ou
  é cliente. Corta retrabalho e contato indevido.

## Como eu combino isso (heurística)

1. Recall primeiro. NÃO empilhe automaticamente NAICS E keyword: filtros
   diferentes se somam por E e isso reduz o universo. Testar qual dimensão
   representa a atividade real. No Brasil, o Apollo pode ser a principal fonte;
   CNAE, SIC/NAICS, indústria e keywords são hipóteses de busca, não uma hierarquia
   fixa. Uma atividade pode atravessar vários CNAEs, favorecendo indústria,
   keywords, sinais operacionais ou buscas combinadas. Validar cobertura com
   contas conhecidas, amostra de precisão e referência externa plausível.
2. Cargo + senioridade = chega na pessoa certa.
3. Intenção/vaga/crescimento = adiciona "agora", não só "fit".
4. Listas/Etapa = remove cliente atual e já-prospectado.
5. Camada de julgamento na skill = o que os dados coletados significam.
6. AI Research = última forma de coletar um fato ausente, nunca de julgar fit.
7. Gate de reveal: revelar contato só da Tier autorizada.

## AI Research: coleta factual de último recurso

Os Filtros de IA podem pesquisar um fato por empresa ou pessoa quando filtros,
campos, sinais, enriquecimentos e fontes adequadas não o entregam. O prompt deve
perguntar algo observável: "Há evidência de que esta empresa exerce [atividade
definida no ICP]? Retorne fato, URL, data e estado da evidência." Não pedir que o
modelo do Apollo decida se a empresa é boa, qualificada ou Tier A.

Ordem certa:
- Defina aqui os critérios e os fatos necessários.
- Colete esses fatos com filtros e recursos estruturados do Apollo, pagos ou não.
- Traga os dados brutos para a skill qualificar com o modelo mais potente.
- Se um fato decisivo continuar indisponível, crie uma coluna factual de AI
  Research e traga o resultado para interpretação aqui.
- Revele contato apenas depois da classificação.

Não perguntar como o plano cobra, não calcular custo e não rejeitar um recurso
somente porque usa créditos. O Apollo apresentará o consumo ao usuário.
