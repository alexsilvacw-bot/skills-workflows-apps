---
name: adaptar-vaga
description: Analisa uma vaga recebida por link ou descrição completa, organiza todas as exigências, cruza cada uma com as experiências verificáveis de Alex, investiga requisitos materiais com score 0 antes de redigir, escreve o currículo, simula uma triagem literal de ATS antigo com correções condicionadas à verdade, executa a avaliação completa e cria o Word somente após aprovação humana explícita. Use em candidaturas, adaptação de currículo, diagnóstico de vaga, geração de DOCX e, quando solicitado, preparação de mensagem ou entrevista, em português do Brasil ou inglês.
---

# Adaptar vaga

## Objetivo

Transformar uma vaga em um pacote de candidatura baseado em evidências. Organizar as exigências antes de escrever, pontuar a aderência de cada experiência e construir o currículo verificável com as provas de maior relevância. Separar obrigatoriamente a aprovação do conteúdo da produção do arquivo Word.

## Preparação obrigatória

1. Localizar o projeto de carreira. Usar o diretório atual quando ele contiver `00_LEIA_PRIMEIRO.md`. Caso contrário, verificar `/Volumes/alexfloriano/Documents/07_Planob`. Se não existir, pedir o caminho correto.
2. Ler `AGENTS.md` e `00_LEIA_PRIMEIRO.md`.
3. Ler completamente os arquivos canônicos exigidos em [career-source-contract.md](references/career-source-contract.md).
4. Ler [ats-bilingual-rules.md](references/ats-bilingual-rules.md).
5. Ler [ats-literal-audit-contract.md](references/ats-literal-audit-contract.md).
6. Ler [output-contract.md](references/output-contract.md).
7. Ler [docx-resume-contract.md](references/docx-resume-contract.md).
8. Ler e ativar a skill `$avaliar-curriculo` antes de qualquer criação de DOCX.

## Receber a vaga

Aceitar um link, a descrição completa ou ambos.

Quando a entrada for um link, abrir a página e adquirir a descrição integral. Não usar apenas snippet de busca. Registrar URL, data de acesso e eventual redirecionamento. Se o conteúdo estiver bloqueado, expirado ou incompleto, pedir que Alex cole a descrição.

Detectar o idioma principal da vaga. Produzir o currículo no mesmo idioma, salvo instrução explícita em contrário.

Extrair empresa, título, localidade, regime remoto, contrato, faixa publicada, missão, resultados esperados, responsabilidades, requisitos obrigatórios, requisitos desejáveis, métricas, ferramentas, escopo geográfico, time e sinais de senioridade.

Não estimar remuneração como fato. Quando não estiver publicada, registrar `não informada`.

## Regra global para perguntas a Alex

Toda pergunta factual ou de validação feita durante esta skill deve aparecer no chat acompanhada, imediatamente abaixo, por uma resposta-exemplo curta e copiável. Esta regra vale para perguntas iniciais, requisitos com score 0, lacunas parciais, conflitos entre fontes, dúvidas levantadas pela auditoria e qualquer pendência que bloqueie ou possa alterar materialmente o currículo.

Não apresentar listas de perguntas sem respostas-exemplo. Não deixar os exemplos apenas em arquivos do pacote. Mostrar no chat a pergunta e o exemplo correspondente, em rodadas de no máximo cinco perguntas.

A resposta-exemplo deve.

1. Ser escrita em primeira pessoa, no idioma em que Alex deve responder.
2. Ser específica, completa e pronta para Alex avaliar, sem campos genéricos, colchetes ou texto para preencher.
3. Assumir uma empresa real da trajetória de Alex ou sua consultoria própria. Escolher o contexto mais plausível para o requisito com base nas fontes canônicas lidas nesta execução.
4. Usar primeiro fatos já confirmados sobre a empresa, o período, o papel pessoal, o escopo e o último marco. Quando a lacuna exigir uma hipótese adicional, escrever uma versão concreta e claramente hipotética para Alex confirmar, corrigir ou negar.
5. Escolher uma única empresa ou a consultoria própria em cada exemplo. Não misturar empregadores para fabricar uma aderência composta.
6. Delimitar o escopo com fatos positivos e específicos, sem formular a identidade profissional de Alex pela ausência de um requisito.
7. Ser curta o suficiente para Alex responder por número, mas detalhada o suficiente para revelar empresa, contexto, ação pessoal, escopo e resultado ou último marco.
8. Nunca apresentar a hipótese como fato confirmado nem reutilizá-la no currículo antes da confirmação explícita de Alex.
9. Conter somente a frase factual positiva proposta. Não iniciar a resposta-exemplo com rótulos como `Verdadeiro`, `Parcialmente verdadeiro`, `Falso`, `True`, `Partially true` ou equivalentes. A classificação deve ser solicitada fora da frase proposta.

Não usar expressões como `[empresa]`, `[período]`, `[resultado]`, `preencha aqui`, `insira um exemplo` ou equivalentes. A responsabilidade de escolher a empresa e redigir a hipótese específica é da skill, não de Alex.

## Linguagem de lacunas e limites

Nunca escrever, no chat, em respostas-exemplo, em rascunhos, em avaliação, em mensagens de candidatura, em cover letters ou no DOCX, uma frase que defina Alex pelo que ele não tem ou não fez. São proibidas formulações como `I have no experience`, `I did not do this`, `I do not have`, `não tenho experiência`, `não fiz isso`, `não possuo` e equivalentes.

Quando houver uma lacuna, usar linguagem impessoal de evidência no diagnóstico e na matriz, como `Nenhuma evidência confirmada para este requisito`, `Cobertura parcial pelo escopo confirmado` ou `Requisito fora do escopo das provas disponíveis`. No currículo verificável, omitir a lacuna. Não incluir avisos defensivos, ressalvas de ausência ou comparações negativas.

Em respostas-exemplo, mostrar apenas um caso positivo ou parcialmente positivo, ancorado em uma empresa real. Quando Alex negar ou limitar uma hipótese, registrar no pacote somente a classificação e a parte factual confirmada. Não reproduzir uma resposta negativa em primeira pessoa nem usá-la como copy de candidatura.

Usar este formato no chat.

```markdown
1. Pergunta. Você liderou pessoalmente uma iniciativa de ABM para contas enterprise?

   Exemplo de resposta para confirmar ou corrigir. "Na EAVISION, estruturei a priorização de contas agrícolas, defini abordagens específicas por empresa e coordenei o avanço comercial até conversa qualificada ou proposta. Meu escopo incluiu priorização, personalização e avanço executivo por conta."

   Responda se o exemplo é verdadeiro, parcialmente verdadeiro ou falso e corrija qualquer detalhe que não corresponda à sua experiência.
```

Quando a pergunta pedir uma escolha simples, ainda fornecer um exemplo específico e completo. Exemplo. `Resposta-exemplo. Tenho disponibilidade para rotina híbrida em São Paulo e avalio mudança internacional quando a vaga oferecer sponsorship e pacote de relocação.`

## Organizar as exigências antes do diagnóstico

Criar `matriz-de-requisitos-e-evidencias.md` antes de redigir o currículo.

1. Separar toda exigência explícita da vaga em uma linha própria e identificá-la como `R01`, `R02` e assim por diante.
2. Preservar o texto exato da vaga e acrescentar uma formulação normalizada e objetiva.
3. Classificar cada exigência como obrigatória, desejável, responsabilidade, resultado esperado, ferramenta, idioma, formação, localização ou condição de trabalho.
4. Dividir exigências compostas quando as partes puderem receber scores diferentes.
5. Não limitar a matriz a oito critérios. Cobrir todas as exigências materiais da descrição.
6. Não transformar linguagem contextual da empresa em requisito do candidato.

Para cada exigência, listar as experiências verificáveis de Alex que podem atendê-la. Registrar empresa ou projeto, período ou contexto, evidência concreta, fonte canônica e score.

Usar somente esta escala.

| Score | Interpretação |
|---|---|
| 0 | Não atende. Não existe evidência confirmada nem experiência transferível relevante. |
| 1 | Atende pouco. Há experiência adjacente ou parcial, mas falta parte material da exigência. |
| 2 | Atende bem. Há experiência direta e sólida, embora o escopo, a duração, a ferramenta ou o resultado não cubra integralmente a exigência. |
| 3 | Atende perfeitamente. A evidência confirmada cobre diretamente a exigência, o contexto e o nível pedidos. |

Pontuar aderência da evidência, não prestígio do cargo. Não elevar o score por plausibilidade, título semelhante ou palavra-chave isolada. Quando não houver experiência aplicável, registrar `Nenhuma evidência confirmada` com score 0. Não inventar uma experiência para preencher a linha.

Depois da análise por requisito, criar um ranking agregado por experiência com.

1. Soma dos scores.
2. Quantidade de requisitos cobertos com score 3.
3. Quantidade de requisitos cobertos com score 2.
4. Requisitos obrigatórios cobertos.
5. Lacunas obrigatórias remanescentes.
6. Fontes usadas.

Ordenar primeiro pela cobertura dos requisitos obrigatórios com score 3 ou 2, depois pela soma. Não somar duas vezes a mesma evidência apenas porque a vaga repetiu a exigência com outras palavras.

## Confirmar requisitos com score 0 antes de escrever

Não assumir que a fonte canônica contém toda a experiência possível ou está integralmente atualizada. Todo requisito material com score 0 deve ativar descoberta e confirmação antes da redação do currículo.

1. Identificar todos os requisitos materiais com score 0, incluindo experiência, conhecimento, ferramenta, setor, resultado, formação, idioma ou condição relevante.
2. Para cada requisito, criar uma hipótese plausível de experiência que Alex possa ter realizado, mesmo quando essa hipótese ainda não aparece na fonte canônica. Ancorar a hipótese na trajetória conhecida sempre que houver uma âncora útil, mas não deixar de perguntar apenas porque a fonte não oferece uma âncora suficiente.
3. Apresentar uma pergunta objetiva sobre a experiência requerida e, imediatamente abaixo, uma resposta-exemplo específica conforme a regra global de perguntas. Escolher uma empresa real da trajetória de Alex ou a consultoria própria e escrever uma hipótese completa, sem colchetes ou campos para preenchimento.
4. Rotular a resposta-exemplo como `Exemplo hipotético, não confirmado e proibido no currículo até confirmação de Alex`. O exemplo serve para mostrar o nível de detalhe e aderência procurado, não para sugerir que Alex o confirme sem correspondência factual.
5. Perguntar explicitamente se a resposta-exemplo é verdadeira, parcialmente verdadeira ou falsa no histórico de Alex e pedir que ele corrija o exemplo com o fato real.
6. Solicitar somente os detalhes necessários sobre papel pessoal, escopo, período, contexto, escala, resultado, métrica e possibilidade de divulgação.
7. Fazer no máximo cinco perguntas por rodada. Interromper a redação do currículo até processar todas as respostas materiais e continuar em novas rodadas quando necessário.
8. Exibir no chat o conteúdo integral de cada rodada, incluindo a pergunta e a resposta-exemplo correspondente. Registrar o mesmo conteúdo e depois as respostas de Alex em `confirmacao-de-requisitos.md` e atualizar a matriz com o resultado.

Usar este formato para cada requisito.

```markdown
### RXX

Exigência da vaga. [texto exato ou formulação fiel]

Hipótese a confirmar. [experiência plausível que poderia atender ao requisito]

Exemplo de resposta para confirmar ou corrigir. [resposta específica e completa em primeira pessoa, ancorada em uma empresa real da trajetória de Alex ou na consultoria própria, mostrando papel, escopo, contexto e resultado ou último marco, sem colchetes ou campos para preenchimento]

Aviso. Exemplo hipotético, não confirmado e proibido no currículo até confirmação de Alex.

Pergunta. Isso é verdadeiro, parcialmente verdadeiro ou falso na sua experiência? Se houver experiência relacionada, corrija o exemplo com o que você realmente fez.

Detalhes necessários. [papel pessoal, período, escopo, resultado e possibilidade de divulgação]
```

Classificar cada resposta como `confirmado`, `parcialmente confirmado`, `negado` ou `ainda incerto`.

1. Quando confirmado, incorporar somente o fato confirmado, atualizar a fonte e a justificativa e recalcular o score.
2. Quando parcialmente confirmado, usar apenas a parte confirmada e atribuir o score compatível com o escopo real.
3. Quando negado ou ainda incerto, manter score 0, registrar a lacuna em linguagem impessoal de evidência e excluir a hipótese do currículo.
4. Não escrever `rascunho-do-curriculo.md` enquanto uma resposta pendente puder mudar materialmente o score, o diagnóstico, a arquitetura ou a seleção de provas.

## Diagnosticar antes de escrever

Produzir sempre estes quatro blocos.

1. O que sabemos.
2. O que estamos assumindo.
3. O que precisa ser validado.
4. Qual ação deve acontecer agora.

Responder qual problema a empresa tenta resolver com a contratação.

Usar a matriz para resumir os critérios decisivos, as melhores provas, a distribuição dos scores e as lacunas reais. Não criar nota universal de ATS nem converter a soma em percentual de fit.

Recomendar `aplicar`, `aplicar com ressalvas` ou `não priorizar`. Explicar a razão.

## Escolher a arquitetura

Escolher pelo problema dominante, não apenas pelo título.

1. CMO e Growth.
2. Commercial e GTM.
3. Híbrido Revenue e Marketing.
4. Content Strategy.
5. Country Manager e Market Entry.
6. Business Development e Strategic Partnerships.

Usar apenas uma narrativa dominante. Tratar as demais como suporte.

## Selecionar conteúdo pelo score

Usar o ranking da matriz como base da seleção editorial.

1. Priorizar experiências e bullets com score 3 e 2 nos requisitos obrigatórios e no problema central da contratação.
2. Usar evidências com score 1 apenas para demonstrar experiência transferível relevante e sem apresentá-la como aderência direta.
3. Antes da seleção editorial, investigar todo requisito material com score 0 conforme o gate de confirmação. Se a resposta confirmar uma experiência, atualizar a matriz e usar apenas o fato confirmado. Se a resposta for negativa ou incerta, manter score 0 e não sugerir atendimento.
4. Manter cronologia e contexto suficientes para o currículo continuar fiel à carreira, mesmo quando uma experiência tiver score agregado menor.
5. Resolver empates por relevância ao problema da vaga, força da evidência, recência e clareza do papel pessoal.
6. Não omitir lacuna material do diagnóstico apenas porque ela enfraquece a candidatura.

## Criar o currículo verificável

Trabalhar em duas fases e não avançar automaticamente da primeira para a segunda.

### Fase 1. Redigir, avaliar e pedir aprovação

1. Executar o gate de confirmação de todos os requisitos materiais com score 0.
2. Avaliar as respostas, registrar o resultado em `confirmacao-de-requisitos.md`, atualizar a matriz e os scores e então produzir ou atualizar o diagnóstico e a arquitetura.
3. Interromper sem criar o rascunho enquanto houver confirmação material pendente.
4. Escrever o currículo verificável completo em `rascunho-do-curriculo.md` somente depois de processar as respostas.
5. Executar a auditoria de ATS antigo definida em [ats-literal-audit-contract.md](references/ats-literal-audit-contract.md) e registrá-la em `auditoria-ats-literal.md`.
6. Para cada falha literal, declarar o que precisaria ser verdade, escrever a frase ideal condicionada a essa verdade e indicar exatamente qual trecho do currículo seria substituído ou onde a frase seria adicionada.
7. Corrigir diretamente apenas termos e formulações cuja evidência já esteja confirmada e cujo novo texto preserve exatamente o mesmo escopo factual.
8. Para fatos potencialmente verdadeiros, mas ainda não confirmados, registrar a pergunta em `confirmacao-de-requisitos.md`, apresentá-la no chat conforme a regra global e interromper antes de alterar o rascunho. Não repetir perguntas já respondidas nem reabrir lacunas explicitamente negadas.
9. Processar as respostas, incorporar somente os fatos confirmados, atualizar a matriz quando o score mudar e reexecutar a auditoria literal. Lacunas reais podem permanecer no relatório, mas toda ação deve estar resolvida como aplicada, descartada por falta de suporte ou dependente de uma pergunta apresentada a Alex.
10. Ativar automaticamente `$avaliar-curriculo` para auditar o rascunho contra a descrição integral, a matriz de requisitos, as confirmações registradas, `auditoria-ats-literal.md` e as fontes canônicas.
11. Registrar a avaliação completa em `avaliacao-do-curriculo.md`.
12. Corrigir no texto os problemas factuais ou editoriais encontrados. Se a avaliação levantar novas perguntas materiais, interromper e esperar as respostas de Alex antes de corrigir.
13. Reexecutar a avaliação e a auditoria literal quando houver alteração material no texto.
14. Mostrar no chat o texto integral do currículo final avaliado, não apenas bullets selecionados ou um resumo.
15. Apresentar junto do rascunho o veredito do ATS antigo, as lacunas reais remanescentes e as alterações aplicadas ou descartadas.
16. Pedir aprovação humana explícita para transformar o rascunho em Word.
17. Interromper a execução. Silêncio, ausência de objeção, avaliação positiva da skill ou autorização genérica anterior não contam como aprovação humana.

Executar `scripts/validate_application_package.py --package <diretorio> --language <pt|en> --stage draft --require-ats-audit` antes de pedir a aprovação. O estágio `draft` deve falhar se a auditoria literal estiver ausente ou se um DOCX já tiver sido criado.

### Fase 2. Produzir o Word depois da aprovação

Retomar somente depois de uma mensagem humana explícita aprovando o rascunho avaliado ou autorizando sua conversão em Word.

1. Registrar em `aprovacao-humana.md` a data, o texto exato da confirmação e a versão do rascunho aprovada.
2. Não fazer mudanças editoriais materiais depois da aprovação. Se uma mudança material for necessária, voltar à Fase 1, mostrar o novo texto, reavaliar e pedir nova aprovação.
3. Gerar o DOCX a partir do texto aprovado.

Nomear o arquivo enviável no padrão `Alex_Floriano_Cargo_Empresa_Idioma.docx`. Usar `PTBR` para português do Brasil e `EN` para inglês. Normalizar espaços e caracteres incompatíveis com nomes de arquivo sem perder a identificação humana. Exemplo. `Alex_Floriano_Gerente_de_Marketing_Oxiquimica_Agrociencia_PTBR.docx`.

Usar somente fatos sustentados pela fonte de verdade. Nunca inventar experiência, ferramenta, idioma, cargo, responsabilidade formal, orçamento ou resultado.

Nunca inserir no currículo verificável, em título, resumo, competência, experiência, nota, rodapé ou mensagem de candidatura qualquer frase sobre requisito ausente, experiência não realizada ou limitação declarada. O currículo mostra somente fatos confirmados, escopo comprovado e linguagem positiva compatível com a vaga.

Aplicar estas regras.

1. Uma coluna e fluxo linear.
2. Duas páginas como ponto de partida, sem tratar o número como regra universal.
3. Texto pesquisável e seções convencionais.
4. Datas consistentes em mês e ano quando disponíveis.
5. Informações essenciais fora de imagens e elementos decorativos.
6. Título, resumo e competências adaptados ao idioma e ao problema da vaga.
7. Palavras-chave exatas somente quando verdadeiras.
8. Competências demonstradas dentro das experiências.
9. Bullets no formato decisão ou ação, escopo, mecanismo e impacto.
10. Distinção explícita entre participação, influência e ownership.
11. Conteúdo priorizado conforme a matriz de requisitos e o ranking por experiência.

Gerar o currículo final em DOCX conforme [docx-resume-contract.md](references/docx-resume-contract.md). Não entregar o currículo apenas em Markdown.

Não afirmar P&L formal a partir de decisões sobre preço, margem, orçamento ou viabilidade. Não afirmar mandarim fluente. Não elevar domínio de ferramentas sem evidência.

Não criar currículo aspiracional, currículo contrafactual, aviso de não envio ou plano de evidências simulado. `auditoria-ats-literal.md` pode conter frases ideais condicionais somente como mapa privado de remediação. Essas frases não são um currículo alternativo e são proibidas no rascunho e no Word enquanto não estiverem sustentadas por fatos confirmados.

## Trabalhar em português e inglês

Não traduzir literalmente. Preservar fatos e métricas, mas adaptar títulos, palavras-chave e linguagem de senioridade ao idioma da vaga.

Quando um título não tiver equivalente seguro, preservar o título formal e acrescentar uma descrição funcional conservadora. Nunca converter automaticamente Diretor em VP, Diretor de Marketing em CMO ou CEO Brasil em Country Manager.

## Auditar a candidatura

Executar revisão ATS, humana e de honestidade.

Na auditoria de ATS antigo, simular uma triagem deliberadamente literal e registrar o resultado em `auditoria-ats-literal.md` conforme [ats-literal-audit-contract.md](references/ats-literal-audit-contract.md). Essa simulação serve para localizar falhas de correspondência e não prevê o comportamento de um ATS real.

Na revisão ATS da avaliação completa, verificar idioma, seções, datas, parsing provável, termos exatos verdadeiros, campos estruturados e nome do arquivo.

Na revisão humana, verificar tese executiva, clareza, densidade de provas, escopo, resultados, trabalho remoto e linguagem genérica.

Na revisão de honestidade, verificar ownership, métricas conflitantes, pipeline versus receita, orçamento versus P&L, ferramentas, idiomas e clientes não confirmados.

Na revisão da matriz, verificar cobertura de todas as exigências, consistência da escala, fontes de cada evidência, ranking agregado e correspondência entre os maiores scores e o conteúdo escolhido para o currículo.

Na Fase 1, revisar a matriz, o rascunho e a avaliação. Não carregar a skill de DOCX nem criar Word.

Na Fase 2, executar para o DOCX o ciclo obrigatório de criação, renderização, inspeção de todas as páginas e correção definido em [docx-resume-contract.md](references/docx-resume-contract.md). Registrar o resultado em `qa-word.json`.

Executar `scripts/validate_application_package.py --package <diretorio> --language <pt|en> --stage final --require-ats-audit` depois de criar os arquivos finais. Corrigir falhas antes da entrega.

## Entregar

Criar o pacote em duas fases conforme [output-contract.md](references/output-contract.md). A invocação desta skill autoriza criar os arquivos de análise e o rascunho dentro do projeto. Não autoriza criar o DOCX antes da aprovação humana nem alterar fontes canônicas.

Na Fase 1, apresentar o diagnóstico, o mapa de exigências, a recomendação, a auditoria de ATS antigo, a avaliação completa e o texto integral do currículo. Explicar quais experiências tiveram maior score, quais mudanças literais foram aplicadas e quais lacunas reais permaneceram. Encerrar pedindo aprovação humana explícita para gerar o Word.

Na Fase 2, entregar o Word final corretamente nomeado e os resultados de QA e validação. Criar mensagem de candidatura e preparação de entrevista somente quando Alex solicitar explicitamente cada entregável.

Quando Alex confirmar um novo fato, propor a evidência, a origem e o destino canônico. Atualizar o banco de provas antes do estado atual e registrar conflitos no `CHANGELOG.md`. Não atualizar silenciosamente.
