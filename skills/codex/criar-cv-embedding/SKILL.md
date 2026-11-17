---
name: criar-cv-embedding
description: Cria ou retoma CVs no Adaptar Vaga com API, recuperação local por text-embedding-3-large e entrega em PDF. Use quando Alex escolher criar-cv-embedding para avaliação fundamentada e seleção por ganho marginal, com as identidades do índice e a escala de pontuação vigentes.
---

# Criar CV Embedding

Projeto: `/Users/alex/Documents/Adaptar Vaga`.

## Variante de recuperação por embeddings

Esta skill usa API e substitui as chamadas `triagem_matching` e `triagem_realizacoes` por recuperação local de candidatos com `text-embedding-3-large`. O ponto de entrada é `scripts/criar_curriculo_embedding.py`; não usar o orquestrador original para iniciar esta variante.

Os parâmetros efetivos ficam em `config/recuperacao_embedding.json` e os contratos em `scripts/recuperar_embeddings.py`. A busca compara embeddings dos textos originais por requisito e acrescenta candidatos por busca lexical. Os grupos são metadados, sem filtro temático obrigatório. Preservar a fonte principal de cada realização e resolver versões adicionais por seus IDs; similaridade apenas recupera candidatos, sem confirmar fatos ou atribuir notas.

A pontuação individual mantém os pedidos, a escala e o modelo vigentes. Ela agenda até o limite de lotes simultâneos configurado, com fonte integral, todos os requisitos e ordem final preservados. Somente as chamadas de API executam nas threads; validação e checkpoint ficam na coordenadora. Em falha, não iniciar novos pedidos e salvar sucessos já em execução antes de interromper.

A deduplicação desta variante usa o conjunto exato de identidades do índice por vínculo. Sobreposição parcial em textos compostos não une famílias, e conflitos existentes permanecem bloqueados. Entre versões elegíveis da mesma identidade, usar a fonte mais completa com desempate por ID persistente, sem transferir notas entre versões. Não reconstruir famílias por IA a cada vaga nem inventar conflitos por omissão ou tradução.

A seleção cobre os requisitos pelas melhores notas disponíveis nas fontes canônicas e escolhe complementos por relevância à vaga, diversidade (MMR), novos fatos do índice e detalhes quantitativos, usando os vetores large locais. Não adicionar complementos sem novos fatos. Distinguir números por unidade, tradução e estimativa; a recompensa de detalhe quantitativo exige relação elegível com requisito central. O vetor agregado usa exclusivamente os requisitos já extraídos. Quando a concatenação ultrapassa o limite local de entrada, usar a média normalizada dos vetores dos requisitos completos, sem truncamento nem chamada adicional. Os pesos, cobertura e condição de parada ficam na configuração embedding; admissibilidade, cotas e escala vêm das regras compartilhadas. Notas determinam elegibilidade e permanecem visíveis; a ordenação editorial entre elegíveis é específica desta variante. Não preencher capacidade com complementos de baixo valor: o ganho mínimo vale também abaixo da meta editorial. Similaridade não comprova fatos nem substitui a avaliação.

A revisão da seleção integra a fundamentação na própria `cobertura_componentes`: referências elegíveis, estado único e justificativa distinguindo apoio direto, parcial, transferível e ausência. Essa mesma matriz orienta a redação. Não executar uma segunda fase de fundamentação das mesmas fontes quando a revisão integrada estiver habilitada. As notas permanecem fixas; fontes e requisitos integrais acompanham a análise. Manter ações coordenadas e alternativas com seu contexto, sem transformar cada verbo ou item separado por vírgula em uma nova unidade de análise. Não reduzir ou elevar notas para contornar validação.

As preferências editoriais de seleção passam por restrições locais: aceitar somente adições e trocas que preservem admissibilidade, cotas e a melhor nota já coberta por requisito, mantendo a seleção inicial como alternativa viável. Não pedir à IA para corrigir repetidamente essas restrições combinatórias nem alterar notas para atendê-las. A cobertura afetada por uma troca recebe correção apenas nos componentes necessários; o formato permite somente IDs selecionados e elegíveis para aquele requisito. O contador de correções semânticas persiste, com revalidação integral. Uma resposta recebida antes de uma interrupção pode ser reaproveitada sem consumir outra tentativa. Os contratos ficam em `scripts/matching_embedding.py`. Preservar os modelos e os critérios do fluxo original.

A preparação do índice vetorial é separada da criação de currículo. Ela lê os textos da base e os envia à API de embeddings da OpenAI, armazenando vetores, IDs e identificadores de versão no SQLite local definido na configuração; não armazena credenciais. Preparar/atualizar somente com autorização específica, respeitando autorizações já dadas. O comando é:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/Users/alex/Documents/Adaptar Vaga/scripts/criar_curriculo_embedding.py' --preparar-embeddings
```

A preparação valida os vetores reutilizados, recalcula os inválidos mesmo quando a chave do texto permanece igual, reutiliza os demais textos inalterados e não cria candidatura. Índice ausente, incompleto, desatualizado ou com vetores inválidos impede a recuperação; não preparar automaticamente nem recorrer ao recuperador original. Usar o runtime acima para aproveitar NumPy já disponível; o recuperador também tem cálculo exato com a biblioteca padrão, sem instalar dependências.

Em testes apenas de matching, reutilizar requisitos e candidatos congelados, sem reextrair vaga nem gerar documentos. Comparar repetições independentes, separando variação de IDs, cobertura de fatos, similaridade semântica e qualidade das fontes escolhidas. Ausência de repetição lexical não garante ausência de redundância; não declarar estabilidade universal com duas rodadas. Em testes de eficiência, comparar as mesmas entradas e registrar na conversa tempo de preparação, tempo de recuperação, chamadas, tokens e cobertura das evidências esperadas. Separar consulta nova de consulta reutilizada e ganho na recuperação de ganho no CV completo. Definir evidências esperadas antes de observar o ranking e distinguir cobertura de realizações, fontes principais e detalhes. Testes e resultados temporários ficam no diretório temporário do sistema, sem relatórios no projeto. Não afirmar ausência na carreira por falha de recuperação nem garantir cobertura universal a partir de uma amostra.

Leia o `AGENTS.md` do projeto para as instruções globais. Esta skill concentra as instruções de execução. [FLUXO_CV_API.md](</Users/alex/Documents/Adaptar Vaga/FLUXO_CV_API.md>) explica este modo para consulta; não é uma segunda fonte de regras operacionais. Consultar somente a seção pertinente à etapa ou à falha atual, quando necessário. Durante a execução de um currículo, não carregar a skill ou o fluxo do outro modo.

## Fontes das regras e dos contratos

Consulte somente os blocos necessários à etapa. Os valores e contratos vigentes ficam nas configurações e nos validadores dos scripts; não mantenha cópias de escalas, limites ou schemas nesta skill.

| Fonte | Responsabilidade |
| --- | --- |
| `config/regras_matching.json` | Critérios de matching em `matching`: requisitos, evidências, escala, pontuação, deduplicação, seleção, lacunas, recuperação, saída e controles. O índice reutilizável fica em `indice_matching`. |
| `config/configuracao.json` | Regras de extração, ATS, redação, validação humana, contrato de entrada do montador, layout e dados fixos. Na execução de uma candidatura, carregar somente depois de existir `experiencias-aprovadas.json`. |
| `scripts/extrair_vaga.py` | Prompt, schema, classificação, prioridades e validações da extração, incluindo o tratamento corretivo previsto. |
| `scripts/avaliar_experiencias.py` | Recuperação, avaliação, deduplicação, seleção, validação do índice e checkpoint de retomada. |
| `config/recuperacao_embedding.json` e `scripts/recuperar_embeddings.py` | Modelo, índice vetorial local, limites de recuperação, validações e busca desta variante. |
| `scripts/matching_embedding.py` | Fundamentos com notas fixas, identidades determinísticas e seleção por relevância e diversidade, exclusivos desta variante. |
| `scripts/criar_curriculo_embedding.py` | Entrada explícita desta variante e preparação separada dos embeddings. |
| `scripts/redigir_curriculo.py` | Resposta de redação, consolidação, referências, validações e feedback de retomada. |
| `scripts/montar_curriculo.py` | Validação da entrada, resolução das fontes, preenchimento do template e exportação do PDF a partir do DOCX. |

Use os componentes existentes. Uma divergência entre instruções, configuração e implementação deve ser identificada e informada; não invente uma regra para contorná-la.

## Autorização para chamadas de API

Alex autoriza, ao invocar esta skill para criar ou continuar um currículo, as chamadas à API da OpenAI em `https://api.openai.com/v1/responses` necessárias à extração, à avaliação, à fundamentação e à redação, a `https://api.openai.com/v1/responses/input_tokens` para contar os tokens da entrada antes dessas chamadas e a `https://api.openai.com/v1/embeddings` para representar os requisitos da vaga, pelos scripts desta variante. A contagem de tokens envia a mesma entrada, instruções, schema e configuração de raciocínio preparados para a chamada de geração correspondente, incluindo os dados profissionais pertinentes à etapa. A preparação dos embeddings da base segue a autorização específica descrita acima.

A autorização abrange o anúncio da vaga, seus requisitos, os grupos e resumos do índice, as experiências recuperadas e os dados profissionais necessários à redação, respeitando o escopo de leitura de cada etapa.

Executar pelo mecanismo normal de permissões do Codex, sem solicitar nova confirmação apenas por usar a API. A autorização não abrange novos destinos, leitura ou envio integral da base fora das etapas autorizadas, nem alteração de modelo.

Executar no diretório do projeto com `PYTHONDONTWRITEBYTECODE=1`. Para autenticação, reutilizar `OPENAI_API_KEY` ou `interface_vagas.get_key()` dentro do processo existente. Não carregar a credencial no contexto do agente. Sem chave, orientar configuração no aplicativo existente, sem criar arquivos de segredo.

### Esforço de raciocínio nas etapas com Luna

Usar `high` no matching e na redação quando o modelo efetivo for `gpt-6-luna`. Isso inclui a fundamentação e a revisão da seleção, a revisão de alinhamento antes dos documentos e as correções lexicais ou técnicas. Usar `medium` na conferência final do PDF quando ela for feita com Luna e o ambiente permitir configurar o esforço dessa tarefa. A montagem e a conversão são locais e independem de esforço de raciocínio.

Configurar a variável específica de cada etapa antes de iniciar ou retomar a candidatura, conforme o modelo efetivamente resolvido pelos scripts:

- Para a redação inicial com Luna, usar `OPENAI_REASONING_EFFORT=high`.
- Para matching, fundamentação, revisão da seleção, revisão de alinhamento e correções com Luna, usar `OPENAI_MATCHING_REASONING_EFFORT=high`.
- Na extração com Luna, continuar usando `OPENAI_EXTRACTION_REASONING_EFFORT=high`.

Antes de ajustar uma variável compartilhada, conferir o esforço efetivo das etapas que usam outros modelos, inclusive o valor de fallback da extração. Preservar esses valores com as variáveis específicas quando disponíveis. Nas retomadas, reutilizar o esforço efetivo do matching e da redação para manter a compatibilidade do checkpoint.

## 1. Iniciar ou retomar

Se Alex fornecer uma nova vaga, usar o link ou o texto completo. Se a entrada estiver ausente, pedi-la. Se esta mesma candidatura já tiver sido extraída na sessão, continuar sua pasta atual.

Para uma nova vaga por link:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/Users/alex/Documents/Adaptar Vaga/scripts/criar_curriculo_embedding.py' --url '<LINK_DA_VAGA>'
```

Passar argumentos com escape seguro de shell. Para texto colado, usar um TXT UTF-8 temporário do sistema e substituir `--url` por `--arquivo`. Remover o temporário ao concluir.

O orquestrador chama o extrator, que cria `candidaturas/empresa_cargo/requisitos-vaga.json`. Usar exatamente a pasta retornada e informá-la a Alex. Colisões recebem sufixo numérico, sem sobrescrita. Ao usar diretamente o extrator, sua opção `--candidatura` cria a pasta.

Para continuar uma candidatura:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/Users/alex/Documents/Adaptar Vaga/scripts/criar_curriculo_embedding.py' --candidatura '<PASTA_ATUAL>'
```

Continuar somente na pasta informada por Alex ou retornada nesta execução. Ler seus arquivos conforme a etapa. Usar as saídas existentes e válidas; não repetir extração ou pontuação já concluídas por causa de uma falha posterior.

## 2. Extrair os requisitos

Nesta etapa, ler o anúncio atual e o extrator; não consultar a base. Captura e classificação são feitas por `scripts/extrair_vaga.py`, não por requisitos escritos manualmente pelo agente.

Conferir se a extração cobre tanto responsabilidades e entregas profissionais quanto qualificações explícitas. As responsabilidades entram como obrigatórias salvo preferência explícita, preservando ações, objetos, contexto, resultados e condições, sem inventar exigência de experiência anterior ou pesos. Competências e ferramentas não substituem requisitos.

Manter as exclusões profissionais previstas pelo projeto: idioma/proficiência, viagens e formação acadêmica. Em requisitos mistos, preservar a parte profissional restante. A escolha do idioma do currículo é independente dessas exclusões.

As prioridades vêm somente do anúncio, segundo a classificação implementada no extrator; são independentes de obrigatório/desejável. Ao continuar uma candidatura sem prioridades, classificar somente os requisitos existentes pelo mecanismo do extrator, sem reextrair seus textos.

Não repetir a extração nem suas chamadas fora do tratamento corretivo previsto. Depois de salvar `requisitos-vaga.json`, continuar automaticamente com matching e redação.

### Acesso à vaga e à rede

Executar com acesso à rede pelo mecanismo normal de permissões. Se o ambiente estiver restrito, solicitar a execução com `sandbox_permissions="require_escalated"` e justificativa para o acesso autorizado. Não contornar uma rejeição.

Falha de DNS ou conexão não demonstra bloqueio do site nem necessidade de Chrome. Conferir a causa e as permissões antes de recorrer ao navegador ou pedir o anúncio a Alex. Se a falha ocorreu apenas na leitura da URL, antes da extração por IA e da criação da candidatura, retomar com a permissão apropriada. Em caso de dúvida, conferir a saída e somente o código necessário para identificar a etapa alcançada.

Tratar erros HTTP, conteúdo insuficiente, login e JavaScript conforme a causa. Usar `--arquivo` quando necessário, preservando o texto completo em temporário do sistema.

## 3. Executar o matching

Executar pelo orquestrador desta variante, que usa `EmbeddingCaller.retrieve()` em `scripts/recuperar_embeddings.py`. Consultar `config/regras_matching.json` e `config/recuperacao_embedding.json`; não carregar a configuração editorial antes da seleção.

1. Validar o índice existente de grupos e realizações, sua cobertura e versão, e o índice vetorial. Com índice presente, a leitura local da base é permitida para validar fontes e resolver IDs.
2. Representar cada requisito completo por embedding e buscar candidatos nos textos originais. Reunir realizações recuperadas semanticamente e lexicalmente conforme a configuração. Não executar as duas triagens por LLM nem restringir a busca a grupos escolhidos previamente.
3. Recuperar a fonte principal e as versões adicionais selecionadas por requisito, mantendo IDs e textos. As pistas sem confirmação factual continuam sujeitas à avaliação original. Os diagnósticos da recuperação não comprovam atendimento de detalhes.
4. Pontuar os textos originais com os pedidos e o modelo do avaliador vigente. Deduplicar pelas identidades exatas do índice e selecionar por cobertura e MMR, mantendo admissibilidade, cotas e escala. Reutilizar notas já calculadas nas rodadas locais de seleção.
5. Antes de finalizar a seleção, definir o posicionamento em uma chamada que recebe somente os requisitos: problema da contratação, entrega central, foco do resumo e requisitos centrais. Revisar o conjunto inicial contra todas as fontes canônicas elegíveis já avaliadas, combinando várias experiências por componente de requisito, sem alterar notas, cotas, melhor cobertura inicial, IDs ou vínculos. O contrato fica em `scripts/matching_embedding.py`; não exigir que uma única experiência cubra um requisito composto. Fundamentar as referências na mesma matriz, com estado e limites de cada apoio. Ordenar as fontes pela contribuição à entrega central dentro de cada vínculo.
6. Salvar `experiencias-aprovadas.json` conforme `matching.saida`, incluindo `posicionamento_vaga` e `cobertura_componentes` no mesmo arquivo. O nome representa a seleção do processo e não exige aprovação humana de cada experiência.

Não avaliar toda a base nem aumentar automaticamente os limites de recuperação para preencher a meta editorial. Uma recuperação integral interrompe a etapa para revisão. Lacunas da avaliação não demonstram ausência na carreira e não geram propostas por si só. Complementação continua condicionada à seleção abaixo da meta mínima. Medições e rastros ficam na conversa, no terminal ou no checkpoint temporário autorizado.

## 4. Redigir e gerar para revisão posterior

Depois de existir a seleção, executar a redação pelo orquestrador desta variante. A política `redacao` de `config/recuperacao_embedding.json` prevalece sobre as restrições editoriais compartilhadas de comprovação anterior; os modos originais permanecem inalterados.

A vaga define foco, hierarquia e linguagem; o histórico generalista fornece provas e limites factuais. Usar o posicionamento da seleção para abrir o resumo pela capacidade que responde à entrega central, seguir com experiências pertinentes e usar a amplitude como apoio. Não fixar a identidade na área ou no cargo mais recente. Preservar os cargos históricos e distribuir requisitos compostos entre várias experiências, mantendo os vínculos. Priorizar experiências concretas antes de ampliar escopo com hipóteses.

Com `redacao.revisar_alinhamento_antes_documentos` habilitado, revisar o texto final em chamada separada ao mesmo modelo: foco das primeiras frases do resumo, provas pertinentes, distribuição de componentes, prioridade dos bullets e uso de experiências concretas antes de hipóteses. A revisão recebe os textos finais, fontes, orientação e acréscimos uma vez, sem recópias dos mesmos bullets em cada requisito. Falhas semânticas indicam resumo, IDs específicos ou somente ordenação dentro do vínculo e recebem correção localizada antes de salvar e montar, dentro do orçamento técnico persistente. Ampliação de responsabilidade ou contexto autorizada não reprova apenas por não constar na fonte; números, duração, clientes, cargos e vínculos continuam protegidos. Não exigir aprovação humana prévia nem bloquear por lacunas factuais; a revisão factual continua posterior. Registrar o parecer em `revisao_editorial.revisao_alinhamento` no JSON existente, vinculado à versão do conteúdo e à orientação da seleção. O orquestrador e a montagem direta validam esse registro. Rascunhos antigos sem revisão ou com conteúdo alterado não são montados silenciosamente; não sobrescrever candidaturas concluídas.

Abrir cada experiência pelo requisito mais relevante e usar expressões exatas da vaga e equivalências úteis. Integrar ações, objetos, contexto, decisões e resultados, sem copiar o anúncio inteiro, repetir frases ou reiterar a mesma ideia. Desenvolver contexto somente quando acrescenta informação; não aumentar texto apenas para perseguir similaridade. O limite de palavras fica na configuração da variante. Não acrescentar medição automática de embeddings nem promessa de notas finais. A revisão semântica de alinhamento anterior aos documentos é parte desta variante.

Pode ampliar responsabilidades e contexto mesmo sem evidência, para conferência humana posterior. Não pedir evidências nem interromper a redação ou os documentos por lacunas de aderência ou seleção abaixo da meta. Preservar nomes próprios, clientes, números, unidades, datas, cargos históricos, IDs e vínculo de origem. Não inventar métricas, clientes ou tempo de experiência. Não alterar a base nem as notas do matching. Cada ID continua em seu vínculo; consolidar somente relatos equivalentes com as referências verificáveis vigentes, sem gerar novas experiências para preencher a meta.

Se todos os critérios da revisão semântica estiverem aprovados, sugestões adicionais são não bloqueantes e permanecem em `revisao_alinhamento.sugestoes_nao_bloqueantes`, sem iniciar outra correção. Uma ordem explícita e completa de IDs exatos do mesmo vínculo pode ser aplicada localmente, uma vez, sem reescrita; a revisão posterior usa o conteúdo reordenado. Uma sugestão de ordem parcial ou ambígua não autoriza inferir IDs nem deslocar textos entre vínculos.

No pedido de redação desta variante, transmitir somente a formatação ATS, não as antigas restrições de conteúdo que impedem ampliação sem evidência. A redação deve efetivamente mudar o foco dos textos, não apenas traduzir ou trocar sinônimos. Mapear todos os requisitos em `revisao_editorial.alinhamento_requisitos`, com ID de origem, trecho final literal e cobertura (inclusive parcial). Quando faltar contexto, aplicar a ampliação autorizada e registrar a hipótese.

O validador deve preservar os valores numéricos e percentuais das fontes selecionadas ao menos uma vez em IDs elegíveis do mesmo vínculo. Deduplicar mantém a métrica em um relato e remove só as repetições; omissão de todas as ocorrências gera feedback técnico automático antes de salvar e montar. O controle normaliza separadores, escalas abreviadas, multiplicadores e cardinais ingleses, mas não comprova unidade contextual, causalidade ou atribuição, que continuam na revisão humana. Distinguir a abreviação financeira `M` e o `m` associado explicitamente a moeda da unidade física `m`; não converter metros em milhões. Sem contexto financeiro, `1.5m` preserva o valor 1.5. Preservar razões como `1:1` na redação e nos documentos; somente nesta variante, os dois-pontos entre dígitos são exceção à limpeza de pontuação.

A normalização numérica serve à comparação interna, não à apresentação. Exibir milhões por extenso conforme o idioma: `R$ 6,8 milhões` em português e `BRL 6.8 million` em inglês. Preservar valor exato, moeda e qualificadores, sem arredondamento ou sequências extensas de zeros. O formatador local atua antes da validação final e da revisão semântica; não altera trechos originais usados como fonte.

Gerar `dados-reescritos.json` com `revisao_editorial.status=pendente`, referências e trechos dos acréscimos para revisão, sem artefato adicional. Acréscimos no resumo usam `id_fonte=null` com citação literal do resumo final; não substituir essa citação pelo texto de uma experiência. Os IDs comprovam a origem do relato, não a veracidade dos acréscimos. Pendências são informadas na entrega e não geram perguntas ou aprovação anterior. A revisão factual final será manual, após a geração do PDF. Não marcar `aprovado_por_usuario` como verdadeiro sem decisão humana.

## 5. Montar, conferir e entregar

O PDF é o único documento final do currículo. Gerar DOCX somente quando for necessário para a conversão. O montador atual cria esse intermediário a partir do template do projeto e exporta o PDF na mesma pasta.

Quando o conteúdo está apto, o orquestrador chama `scripts/montar_curriculo.py` e grava ambos os arquivos na pasta da candidatura. Após conferir o PDF, apagar somente o DOCX identificado como intermediário dessa conversão. Na retomada, preservar DOCX preexistentes cuja origem como intermediário da mesma execução não esteja registrada.

Para montagem direta com redação válida e `revisao_editorial.modo=embedding`, criar um diretório temporário do sistema e executar:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/Users/alex/Documents/Adaptar Vaga/scripts/montar_curriculo.py' --entrada '<PASTA_ATUAL>/dados-reescritos.json' --saida '<DIRETORIO_TEMPORARIO>/<NOME_RESOLVIDO_PELA_CONFIGURACAO>.docx' --pdf --revisao-posterior
```

Usar `--aprovado` somente para registrar uma decisão humana efetivamente dada. Após conferir o PDF, mover o arquivo para a pasta da candidatura e remover o diretório temporário. Não sobrescrever documentos sem autorização.

Resolver o nome pelo bloco `montagem_curriculo.nome_arquivo` de `config/configuracao.json`, com empresa e cargo de `requisitos-vaga.json`, usando a função `document_stem` do orquestrador. Nome solicitado por Alex ou pelo formulário substitui o padrão, sem cópia adicional. Na montagem, consultar o JSON de redação, as fontes para resolver dados, a configuração e o template. Copiar os blocos fixos; não reescrever, traduzir, chamar a API ou recalcular o matching nessa etapa.

Conferir versões da base e da vaga, referências, texto extraível e todas as páginas. Manter temporários de revisão fora do projeto. Se a exportação falhar, informar a falha e manter o intermediário apenas enquanto necessário para retomar a conversão. O orquestrador compara todas as partes do DOCX existente com a montagem esperada e conclui a exportação quando forem idênticas. Na montagem direta, usar o mesmo caminho temporário e adicionar `--retomar` para esse caso; diferenças permanecem bloqueadas, sem sobrescrita.

Entregar o link do PDF, a pasta atual e as pendências reais, indicando revisão factual humana pendente e onde os acréscimos estão registrados no JSON. Distinguir validação estrutural, conferência semântica, revisão visual e execução real.

## Falhas e retomada

Identificar a etapa e a causa antes de repetir uma execução. Usar o mecanismo existente de retomada e feedback de validação. Uma falha técnica não exige aprovação humana do currículo; corrigir dentro do escopo autorizado, respeitando os contratos.

Respostas de API já recebidas e lacunas podem permanecer no checkpoint SQLite temporário do sistema, sem credenciais e com permissões restritas. Reutilizar somente entradas idênticas e contratos compatíveis de base, vaga, regras, modelo, raciocínio e configuração editorial pertinente. Nesta variante, a compatibilidade é conferida por etapa e por pedido; uma edição sem relação com a etapa não renova o orçamento nem descarta respostas. Revalidar as respostas com os controles atuais. Não copiar checkpoints antigos para outra identidade sem verificar compatibilidade. Excluir o checkpoint de cada etapa após salvar sua seleção ou redação pelo mecanismo existente.

O sistema pode apagar temporários. Quando isso impedir a retomada, informar a necessidade de reconstrução. Não criar matriz ou checkpoint persistente no projeto.

Se o processo retornar erro, verificar o que foi salvo e o que precisa ser refeito. Não prometer que a retomada corrigirá o erro. Falhas não autorizam trocar modelo, alterar limites, relaxar contratos ou cortar conteúdo silenciosamente.

## Preparação do índice — tarefa separada

A criação de um currículo não autoriza preparar ou atualizar o índice automaticamente. Índice ausente ou desatualizado exige a preparação apropriada antes de continuar o matching. Verificar se Alex já autorizou especificamente o método e a leitura integral necessária; não pedir a mesma autorização novamente.

Com autorização específica, os comandos existentes são:
- `scripts/avaliar_experiencias.py --indexar-base` ou `scripts/criar_curriculo.py --indexar-base`: preparar o índice. A opção do orquestrador não extrai vaga, não cria candidatura e não aceita `--aprovado` ou `--pdf`.
- `scripts/avaliar_experiencias.py --organizar-realizacoes`: organizar realizações preservando grupos, base e IDs.
- `scripts/avaliar_experiencias.py --consolidar-realizacoes`: revisar equivalências entre famílias organizadas.

Usar `matching.recuperacao` e armazenar o resultado no próprio `indice_matching`, sem JSON adicional. Conferir as fontes antes de usar agrupamentos consolidados. Separar fatos distintos e preservar os IDs; traduções, omissões e recortes compatíveis não são automaticamente contradições.

Divergências factuais materiais aguardam decisão de Alex e impedem a consolidação correspondente. Manter somente conflitos ainda pendentes em `indice_matching.revisao_conflitos`, com referências; não guardar relatos de revisão ou pendências resolvidas no JSON operacional.

## Monitoramento da origem da recuperação

Nas próximas execuções, o matching embedding salva `origens-recuperacao.json` na pasta da candidatura, autorizado especificamente para acompanhar a contribuição das buscas. O registro contém, por experiência recuperada, requisito, realização, papel da fonte e posição nos cortes semântico, lexical e por componentes. Inclui contagens das recuperadas e selecionadas: exclusivas de cada caminho, sobrepostas e fora do top K semântico em todos os requisitos. Versões adicionais herdam os caminhos da realização que as trouxe; não interpretar essa origem como ranking individual da versão.

Se houver interrupção após gravar o registro e antes de salvar a seleção, reutilizar o registro somente quando seu conteúdo operacional for idêntico, desconsiderando apenas o tempo de montagem. Registro incompatível permanece bloqueado, sem sobrescrita. Apresentar na entrega o resumo das selecionadas e o link do registro. Não enviar o registro aos modelos, alterar seleção, limites, notas ou executar buscas/chamadas adicionais para produzi-lo. A ausência de contribuições exclusivas das buscas extras é observacional: não prova equivalência de uma seleção executada sem elas. As buscas extras são locais; qualquer economia de avaliação por API depende dos candidatos evitados e dos lotes. O tempo registrado mede a montagem do relatório, não todo o custo de instrumentação. Candidaturas já concluídas não ganham registro retroativo automaticamente. Este registro é a exceção autorizada aos artefatos adicionais; não criar outros relatórios.


### Controle de reformulação editorial

Redigir primeiro os textos integrados por experiência, seguindo `plano_por_experiencia`, as fontes e a matriz de apoio. Distribuir os requisitos pertinentes, resolver sobreposições preservando detalhes e métricas e buscar a cobertura lexical configurada já na primeira redação. Depois mapear citações literais do texto efetivamente produzido, sem criar aberturas concorrentes apenas nos metadados.

Preservar a meta lexical escolhida por Alex. A configuração `redacao.correcoes_focais_maximas` permite uma única tentativa de correção lexical por candidatura, inclusive retomadas. Corrigir somente os textos afetados, fornecendo os termos usados pelo validador. Depois dessa tentativa, recalcular a cobertura e registrar eventuais requisitos abaixo da meta em `revisao_editorial.controle_lexical` e `pendencias`; seguir com os controles factuais, a revisão semântica e os documentos. Não reiniciar a tentativa lexical por uma retomada, por falha de salvamento ou usando uma correção técnica como pretexto. A pendência lexical não equivale a aprovação factual ou garantia de desempenho em ATS.

A comparação literal aplica-se somente a requisitos e currículo em inglês; a identificação local exclui domínios e abreviações ambíguas. Em idiomas diferentes, traduzir o sentido sem exigir coincidência de palavras. Ausência de condição quantitativa não autoriza inventar números, anos de experiência ou clientes.

Resolver apontamentos contra o texto final do ID indicado. Uma referência parafraseada pode ser corrigida localmente para o bullet efetivo, sem reescrever o currículo ou fazer outra chamada apenas para recópia. Requisitos compostos podem reunir as fontes complementares planejadas na matriz; não somar indiscriminadamente textos sem relação com o requisito. Citações e cobertura lexical não comprovam fatos.

A remoção local de redundância continua restrita a sentenças literais comprovadas pelas fontes, integralmente contidas em um relato mais completo do mesmo vínculo, sem esvaziar textos. Reaplicar os controles de métricas e referências. Outros erros de redundância, consolidação, extensão ou alinhamento recebem patches apenas nos campos afetados, preservando os demais textos. O limite técnico de `redacao.correcoes_tecnicas_maximas` vale para toda a candidatura e persiste nas retomadas; esgotamento não autoriza novas chamadas automáticas ou omissão dos controles factuais.

Uma consolidação explicitamente declarada pode ter seu formato normalizado localmente: exigir grupo simétrico, mesmo vínculo, declaração comum consistente e citações literais inequívocas por fonte; integrar os textos únicos completos, sem cortar detalhes, e repetir o resultado em cada ID do grupo. Não inferir novos grupos, ocultar sobreposição parcial ou exceder o limite de palavras. Revalidar todos os contratos e registrar a normalização nos metadados existentes. A identidade da declaração não comprova semanticamente o mesmo fato; a revisão factual continua humana.

Persistir os contadores antes das chamadas e preservar respostas, falhas e patches recebidos no checkpoint temporário. Um patch já recebido pode ser aplicado após interrupção sem nova chamada. Se o pedido lexical recebido se tornar incompatível, registrar a não aplicação e seguir com a tentativa consumida. Uma geração inicial interrompida sem resposta pode ser repetida na retomada consumindo o orçamento técnico, sem renovar a correção lexical. Nunca regenerar uma redação já recebida para corrigir um erro localizado. Antes de salvar, revalidar o conteúdo integral; se a revisão semântica do mesmo conteúdo já foi concluída, reutilizá-la. Falha apenas de salvamento não deve gerar outro currículo. Não sobrescrever candidaturas concluídas.

Os scripts conferem os limites do formato antes de enviar pedidos à API, incluindo campos que aceitam texto ou vazio, e informam etapa, duração, tokens e reaproveitamento no terminal. Diagnósticos de HTTP expõem apenas identificadores sanitizados, nunca credenciais ou conteúdo ecoado. Medições ficam na conversa e nos temporários autorizados, sem relatórios adicionais.

Falha comprovadamente anterior ao envio da geração, como indisponibilidade na contagem prévia de tokens, não consome geração nem correção. Interrupção ou timeout depois do envio permanece contabilizado, mesmo sem resposta recebida.

Limitações de comprovação e instruções de revisão ficam somente em `revisao_editorial.pendencias`, nunca nos bullets ou no resumo. A revisão factual continua posterior e `aprovado_por_usuario` permanece falso até decisão humana.
