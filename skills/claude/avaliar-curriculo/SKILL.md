---
name: avaliar-curriculo
description: Audita um rascunho textual ou currículo verificável contra a descrição integral de uma vaga e contra as justificativas usadas para construí-lo. Consulta o histórico canônico de carreira de Alex, identifica requisitos bem atendidos, provas relevantes omitidas, formulações fracas e exageros. Para toda exigência material sem prova direta suficiente, procura ativamente histórias, conquistas e experiências ainda não registradas, formula perguntas objetivas ancoradas no histórico e somente depois classifica a lacuna. Corrige o texto após a confirmação explícita de Alex. Use automaticamente antes de transformar um rascunho em DOCX e também para revisar, criticar, validar ou melhorar um currículo já adaptado antes de candidatura ou entrevista, em português ou inglês.
---

# Avaliar currículo

## Objetivo

Verificar se o currículo apresenta a melhor evidência verdadeira para o problema da vaga. Tratar palavras-chave como consequência da aderência, não como objetivo isolado.

Trabalhar em duas fases.

1. Auditar e perguntar.
2. Corrigir somente depois da resposta de Alex e emitir um novo veredito.

Nunca inserir no currículo verificável algo apenas provável, desejável, inferido ou presente no currículo aspiracional.

Sempre tentar descobrir se Alex possui histórias, conquistas, decisões, projetos ou resultados que atendam às exigências materiais da vaga e ainda não estejam registrados nas fontes. Não confundir ausência na fonte canônica com ausência na carreira.

## Preparação obrigatória

1. Localizar o projeto de carreira. Usar o diretório atual quando ele contiver `AGENTS.md` e `09_ESTADO_ATUAL_E_PENDENCIAS.md`. Caso contrário, verificar `/Volumes/alexfloriano/Documents/07_Planob`. Se não existir, pedir o caminho correto.
2. Ler completamente o `AGENTS.md` aplicável ao projeto.
3. Ler, nesta ordem, `09_ESTADO_ATUAL_E_PENDENCIAS.md`, `03_BANCO_DE_PROVAS_E_METRICAS.md` e `02_FONTE_DA_VERDADE_CARREIRA.md`.
4. Ler `00_LEIA_PRIMEIRO.md`, `01_POSICIONAMENTO_E_OBJETIVOS.md`, `04_ARQUITETURA_DE_CURRICULOS.md`, `05_PROCESSO_DE_ADAPTACAO_E_ATS.md`, `06_ESTILO_DE_ESCRITA_E_REGRAS.md` e `08_TEMPLATES_DE_TRABALHO.md` quando existirem.
5. Localizar a descrição integral da vaga, o currículo verificável em texto ou DOCX e a justificativa de construção. Quando existirem, usar `matriz-de-requisitos-e-evidencias.md` como mapa de aderência e `diagnostico-da-vaga.md` como justificativa de arquitetura e narrativa.
6. Ler `qa-word.json`, `validacao-do-pacote.json` e o script de geração do currículo quando existirem. Tratar esses arquivos como evidência de processo, não como prova de verdade factual ou qualidade semântica.
7. Se o currículo estiver apenas em `rascunho-do-curriculo.md` ou no chat, não carregar a skill `documents` e não criar DOCX. Se já estiver em DOCX, carregar `documents` antes de ler, alterar, renderizar ou verificar o arquivo.

Não usar o currículo aspiracional como fonte factual. Consultá-lo apenas para encontrar hipóteses de perguntas, sempre vinculadas a uma âncora real nas fontes canônicas.

## Confirmar os insumos

Exigir a descrição integral da vaga. Um título, snippet, resumo de busca ou página incompleta não basta. Quando houver somente um link, adquirir o texto integral. Se o acesso estiver bloqueado, pedir que Alex cole a descrição.

Identificar sem adivinhação.

1. Qual texto ou arquivo é o currículo verificável.
2. Qual arquivo explica as escolhas feitas.
3. Qual idioma e qual versão devem ser avaliados.
4. Qual arquivo editável e qual script geram a versão final.

Se a justificativa não existir, reconstruir a lógica provável a partir do diagnóstico e do currículo. Marcar essa parte como `racional reconstruído`, nunca como justificativa original.

Se houver somente um rascunho textual, tratá-lo como a versão em avaliação e não exigir DOCX ou arquivos de QA. Se houver mais de um DOCX com nomes diferentes, comparar conteúdo e datas antes de escolher. Não alterar um alias e deixar outra cópia de entrega divergente.

## Integrar com adaptar-vaga antes do Word

Quando `$adaptar-vaga` acionar esta skill antes da criação do DOCX.

1. Auditar o texto integral de `rascunho-do-curriculo.md` contra a descrição, a matriz com scores e as fontes canônicas.
2. Verificar se as experiências com maior score realmente orientaram o título, o resumo, as competências e os bullets.
3. Registrar a auditoria em `avaliacao-do-curriculo.md`.
4. Classificar o resultado como `pronto para aprovação humana`, `requer correções` ou `bloqueado por confirmação factual`.
5. Não considerar esse veredito uma aprovação humana.
6. Não criar, editar, renderizar ou validar DOCX.
7. Depois das correções materiais, reavaliar o rascunho completo.
8. Devolver o texto avaliado para que `$adaptar-vaga` o mostre integralmente no chat e espere uma aprovação humana explícita.
9. Quando qualquer exigência material não tiver prova direta suficiente, executar a descoberta obrigatória, fazer as perguntas e classificar o resultado como `bloqueado por confirmação factual` até Alex responder.
10. Não declarar `pronto para aprovação humana` apenas porque o rascunho está conservador e enviável. Primeiro testar as possíveis histórias e conquistas que possam melhorar materialmente a aderência.

## Decompor a vaga

Extrair cada exigência relevante e classificá-la como uma destas categorias.

1. Filtro eliminatório explícito.
2. Responsabilidade central.
3. Resultado esperado.
4. Experiência ou conhecimento preferencial.
5. Ferramenta, idioma, setor ou contexto operacional.
6. Sinal de senioridade, influência ou escala.

Separar exigências compostas. Por exemplo, `liderar estratégia regional de CRM e orientar product managers` contém pelo menos três exigências diferentes.

Não tratar toda frase da vaga com o mesmo peso. Priorizar filtros, problema central da contratação, resultados esperados e responsabilidades repetidas.

## Auditar o racional

Verificar se a justificativa explica de forma coerente.

1. Qual problema a empresa quer resolver.
2. Qual narrativa dominante foi escolhida.
3. Por que determinadas experiências e métricas entraram.
4. Por que provas aparentemente relevantes ficaram de fora.
5. Quais lacunas foram assumidas conscientemente.
6. Onde a estratégia depende de uma hipótese não confirmada.

Apontar quando o racional não aparece no currículo, quando o currículo contradiz o racional ou quando a narrativa escolhida reduz aderência sem uma boa razão.

## Construir a matriz de cobertura

Comparar cada exigência decisiva com cinco superfícies quando a matriz de scores existir.

1. Texto explícito do currículo.
2. Justificativa de construção.
3. Matriz de requisitos, evidências e scores.
4. Fontes canônicas da carreira.
5. Hipóteses plausíveis ainda não confirmadas.

Usar uma linha por exigência e estas colunas.

| Exigência da vaga | Importância | Evidência no currículo | Evidência canônica omitida | Diagnóstico | Ação recomendada |
|---|---|---|---|---|---|

Classificar `Diagnóstico` com apenas um destes estados.

1. `Atende com prova direta`.
2. `Atende por experiência transferível`.
3. `Atende, mas está mal apresentado`.
4. `Há prova canônica relevante omitida`.
5. `Pode existir, precisa confirmar`.
6. `Lacuna real`.
7. `Currículo exagera ou não sustenta`.

Não inventar uma nota universal de ATS. Entregar um veredito fundamentado entre `atende bem`, `atende com ressalvas` e `não atende suficientemente`, acompanhado das exigências decisivas que sustentam a conclusão.

Quando a matriz usar scores de 0 a 3, conferir a coerência de cada score com a evidência. Não recalcular um percentual geral de fit. Apontar score inflado, score subestimado, evidência sem fonte e experiência de alto score omitida do currículo.

## Descoberta obrigatória de histórias e conquistas

Executar esta etapa em toda avaliação, antes de declarar uma lacuna real ou emitir o veredito final.

1. Percorrer todas as exigências materiais, não apenas as palavras-chave ou os filtros eliminatórios.
2. Para cada exigência, verificar se a fonte canônica já contém a melhor prova direta disponível.
3. Quando a prova for transferível, parcial, mal contextualizada, ausente ou mais fraca que a exigência, procurar âncoras em empresas, projetos, contas, canais, equipes, ferramentas e resultados adjacentes da carreira de Alex.
4. A partir de cada âncora, tentar descobrir uma história, conquista, decisão, conflito resolvido, processo criado, resultado medido ou responsabilidade real que possa atender à exigência.
5. Agrupar exigências relacionadas em uma única pergunta quando a mesma história puder responder a várias delas.
6. Fazer no máximo cinco perguntas por rodada e continuar em novas rodadas até que todas as exigências materiais fracas tenham sido testadas ou já possuam resposta explícita anterior de Alex.
7. Registrar quais requisitos cada pergunta tenta resolver e quais âncoras tornaram a hipótese plausível.
8. Não aceitar `não está na fonte`, `o currículo já está seguro` ou `a experiência parece transferível` como motivo para deixar de perguntar.
9. Não repetir uma pergunta já respondida explicitamente por Alex. Reutilizar a resposta confirmada, parcial, negativa ou incerta.
10. Classificar como `lacuna real` somente depois de uma busca canônica e de uma tentativa explícita de descoberta com Alex, salvo quando a própria fonte já registrar uma negativa explícita aplicável à exigência.
11. Enquanto uma resposta puder mudar materialmente o score, o diagnóstico, a seleção de provas ou a redação, usar o status `bloqueado por confirmação factual` e interromper antes da aprovação humana ou do Word.

Mesmo quando todas as exigências já tiverem prova direta, fazer uma verificação final para descobrir se existe uma conquista mais forte, mais recente ou mais comparável ao contexto da vaga. Perguntar somente quando a possível melhoria for material.

## Procurar melhorias verdadeiras

Para cada requisito fraco ou ausente, seguir esta ordem.

1. Procurar uma prova direta já confirmada no histórico.
2. Procurar uma experiência transferível que resolva o mesmo problema.
3. Verificar se a prova existe no currículo com linguagem fraca, vaga ou pouco visível.
4. Procurar um fato plausível, mas ainda não confirmado, somente quando houver uma âncora concreta no histórico.
5. Formular uma pergunta ancorada para tentar descobrir uma história ou conquista ainda não registrada.
6. Classificar como lacuna real somente depois da resposta de Alex ou de uma negativa explícita já registrada na fonte canônica.

Uma hipótese plausível precisa nascer de algo concreto. Exemplos válidos incluem um escopo adjacente documentado, uma ferramenta citada sem nível de domínio, um projeto com participação confirmada mas ownership incerto, uma métrica sem recorte definido, relacionamento com distribuidores que possa ter incluído QBRs ou regras de canal e gestão de contas que possa ter produzido expansão ou retenção mensurável.

Não criar hipóteses apenas porque a vaga pede algo. Não perguntar se Alex fez uma atividade sem indicar por que isso parece possível no histórico. Essa restrição melhora a qualidade das perguntas, mas nunca autoriza pular a busca obrigatória por âncoras e histórias.

## Perguntar antes de alterar

Fazer todas as perguntas ancoradas que possam mudar materialmente a aderência, o score, o diagnóstico, a seleção de provas ou a redação. Agrupar no máximo cinco por rodada. Quando existirem mais de cinco, continuar em rodadas posteriores depois das respostas.

Para cada pergunta, mostrar.

1. A exigência que ela pode resolver.
2. A âncora real que tornou a hipótese plausível.
3. O fato exato que precisa ser confirmado.
4. A formulação proposta para o currículo se a resposta for positiva.
5. O detalhe mínimo necessário sobre escopo, papel pessoal, período, resultado e possibilidade de divulgação.

Usar este formato.

```markdown
### Pergunta 1

Exigência da vaga. [texto curto]

Por que estou perguntando. [âncora real no histórico]

Confirmação necessária. [pergunta objetiva]

Se for verdade, proponho escrever. [bullet ou frase]

Detalhes necessários. [somente o que altera a redação]
```

Depois de apresentar as perguntas, interromper a edição e esperar a resposta de Alex. Não criar uma versão provisória com as hipóteses.

Só registrar `Nenhuma pergunta material` quando todas as exigências materiais já tiverem prova direta suficiente ou resposta explícita anterior de Alex. Explicar no arquivo de avaliação por que nenhuma descoberta adicional é necessária.

## Processar as respostas

Classificar cada resposta como `confirmado`, `parcialmente confirmado`, `negado` ou `ainda incerto`.

Uma confirmação direta de Alex é fonte válida. Mesmo assim, escrever de forma conservadora e limitada ao escopo confirmado.

Quando a resposta for parcial, usar apenas a parte confirmada. Quando for negativa ou incerta, excluir a hipótese do currículo verificável e registrar a lacuna sem insistir.

Se a confirmação revelar um novo fato reutilizável da carreira.

1. Atualizar primeiro `03_BANCO_DE_PROVAS_E_METRICAS.md`.
2. Atualizar depois `09_ESTADO_ATUAL_E_PENDENCIAS.md` quando o fato alterar o estado atual ou resolver uma pendência.
3. Registrar a resolução no `CHANGELOG.md` quando houver versão histórica diferente, conflito ou mudança material.
4. Preservar versões antigas e explicar por que a confirmação mais recente prevalece.

Não atualizar fontes canônicas para uma simples escolha editorial que não cria um novo fato.

## Corrigir o currículo

A resposta positiva de Alex às perguntas autoriza incorporar somente os fatos confirmados e concluir a correção textual em escopo. Não pedir uma segunda autorização genérica para incorporar o fato. Quando a avaliação ocorrer antes do Word, ainda exigir a aprovação humana explícita do rascunho final para autorizar o DOCX.

Aplicar a menor mudança que resolva a exigência. Preferir substituir conteúdo menos relevante em vez de apenas aumentar o documento.

Revisar, nesta ordem.

1. Título funcional e resumo.
2. Competências essenciais.
3. Ordem e seleção das experiências.
4. Bullets, métricas e palavras-chave verdadeiras.
5. Consistência entre currículo, justificativa e fontes canônicas.

Preservar a diferença entre participação, influência e ownership. Não converter pipeline em receita, proposta em venda, decisão sobre preço ou margem em P&L formal, estudo de mandarim em fluência ou familiaridade com ferramenta em domínio avançado.

Quando a entrada for um rascunho textual anterior ao Word, corrigir primeiro `rascunho-do-curriculo.md`, registrar a nova avaliação e parar. Quando a entrada já for DOCX, atualizar primeiro o script de geração quando ele for a fonte editável. Regenerar todos os arquivos verificáveis equivalentes usados para entrega. Não editar nem copiar conteúdo para `aspiracional_privado_nao_enviar`.

Preservar o padrão visual vigente no `AGENTS.md` e no pacote. Quando houver conflito entre uma regra genérica de DOCX e a instrução permanente do projeto, seguir a instrução do projeto.

## Refazer o QA

Executar esta seção somente quando já existir um DOCX aprovado para edição. Depois de cada alteração material no DOCX.

1. Renderizar todas as páginas com o fluxo da skill `documents`.
2. Inspecionar todas as páginas em tamanho legível.
3. Corrigir clipping, sobreposição, espaços irregulares, bullets desalinhados, quebras ruins, linhas órfãs e páginas excessivamente vazias.
4. Verificar que o texto é pesquisável e que as informações essenciais não dependem de elementos decorativos.
5. Atualizar `qa-word.json` com o caminho exato e a quantidade real de páginas.
6. Executar o validador do pacote quando existir.
7. Confirmar que nenhuma hipótese negada, incerta ou aspiracional entrou no currículo verificável.

Um `status: passed` estrutural não prova aderência, honestidade, qualidade visual ou envio da candidatura.

## Entregar

Na fase de auditoria, apresentar nesta ordem.

1. Veredito de aderência.
2. O que o currículo resolve bem.
3. Exigências mal resolvidas ou não resolvidas.
4. Crítica das justificativas de construção.
5. Provas canônicas omitidas que já podem entrar.
6. Perguntas de confirmação sobre fatos plausíveis.
7. Mudanças que dependem das respostas.

Quando a descoberta obrigatória gerar perguntas, encerrar com `bloqueado por confirmação factual`. Não pedir aprovação do rascunho e não autorizar a criação do Word até processar todas as respostas materiais e reavaliar o currículo.

Quando houver um diretório de candidatura, registrar a auditoria em `avaliacao-do-curriculo.md`. Antes da confirmação, não alterar o currículo.

Na fase de correção textual anterior ao Word, entregar.

1. Respostas incorporadas e limites preservados.
2. Exigências que passaram a ser atendidas.
3. Lacunas que permanecem reais.
4. Caminhos de `rascunho-do-curriculo.md` e `avaliacao-do-curriculo.md`.
5. Veredito entre `pronto para aprovação humana`, `requer correções` e `bloqueado por confirmação factual`.
6. Aviso de que o veredito não substitui a aprovação humana e não autoriza criar o Word.

Na fase de correção de um DOCX já existente, entregar.

1. Respostas incorporadas e limites preservados.
2. Exigências que passaram a ser atendidas.
3. Lacunas que permanecem reais.
4. Arquivos atualizados.
5. Resultado da renderização, inspeção visual e validação estrutural.

Não afirmar que a candidatura foi enviada. Não usar o currículo aspiracional em candidatura, LinkedIn, entrevista ou formulário.
