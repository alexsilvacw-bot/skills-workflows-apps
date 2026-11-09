# Produção PDF e revisão final integradas

Implementação local de 02/11/2026. Novas sessões criadas pela aplicação recebem as ferramentas deste fluxo. Definições salvas na plataforma e sessões anteriores permanecem com suas configurações originais.

## Sequência de produção

1. O texto completo passa pela revisão de conteúdo e pela aprovação humana vinculada à versão/hash. Sem esse registro, a aplicação recusa importação visual, registro de recursos e documento final.
2. O designer prepara o inventário de recursos. Recursos utilizados precisam de arquivo importado, finalidade, origem e conferência de usabilidade; a aplicação confere os bytes e o hash. Um inventário vazio exige justificativa. A qualidade e adequação do material são conferidas pelo designer e pelo revisor.
3. O designer gera o PDF em `/workspace/outputs`, preservando o texto aprovado, e informa o SHA-256. Ele conclui seu turno. Se o arquivo ainda não estiver publicado na listagem, o orquestrador encerra o turno e continua a incorporação no seguinte, sem solicitar outra aprovação apenas por essa divisão técnica.
4. `workflow_artefatos` lista os arquivos publicados. `workflow_arquivo_importar` confere sessão, turno concluído, caminho, formato, tamanho e SHA-256, baixa os bytes e guarda uma cópia local. São aceitos PDF/PNG/JPEG, até 25 MB, produzidos em `/workspace/outputs`. O modelo não escolhe um caminho local arbitrário nem sobrescreve arquivos do operador.
5. Na importação de PDF, a aplicação extrai texto e links, conta páginas e renderiza todas as páginas em PNG. A inspeção usa o runtime PDF já instalado; não instala pacotes. Falha de leitura/renderização mantém o documento pendente. Limites desta implementação: PDF sem criptografia, de 1 a 80 páginas, dimensão máxima de 2.500 pontos; cada renderização tem lado maior de até 1.600 pixels.
6. Depois que o turno termina, o runtime envia as imagens para o mesmo ambiente em `/workspace/inputs/inspecao_workflow/`. O envio acontece entre turnos e cada confirmação é registrada. O orquestrador consulta `renderizacoes_disponiveis` no estado e delega a revisão visual no próximo turno. Upload incompleto não libera a revisão final.
7. O documento é registrado pelo ID importado e pelo mapa de páginas dos blocos `capa`, `resumo_executivo` e `preco`. A aplicação cruza o mapa com a matriz dos elementos incluídos e com o número real de páginas. Blocos incluídos precisam estar em uma única página; blocos não incluídos usam lista vazia. O revisor confere se o mapa corresponde ao conteúdo efetivo, inclusive condições comerciais que poderiam estar em outras páginas. O código não identifica sozinho os limites semânticos desses blocos.
8. O revisor abre as imagens reais, compara a exportação com o texto aprovado e confere paginação, legibilidade, recursos, links e funcionalidades aplicáveis. O relatório final vincula hash do documento, hash textual, todas as páginas, hashes das renderizações, mapa dos blocos e evidência de comparação textual. “Não verificável”, falhas ou pendências bloqueiam a conclusão. O relatório é uma revisão técnica; não registra aprovação humana.
9. Depois da revisão final sem pendências, o controle libera a entrega local ao operador. Uma aprovação humana adicional do acabamento só é exigida se a proposta tiver sido configurada com `visual_approval`. Nenhuma ferramenta envia o documento ao cliente, publica ou efetiva aceite.

A separação em turnos segue os contratos oficiais de [artefatos de sessão](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/subresources/artifacts/methods/list) e [arquivos do ambiente](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/environments/subresources/files/methods/create). A importação usa o endpoint de [conteúdo do artefato](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/subresources/artifacts/methods/content).

## Consultar a entrega

Na pasta do projeto, depois que o estado chegar a `concluida`:

```sh
python3 -m workflow.cli entrega IDENTIFICADOR
```

O comando retorna caminho local, SHA-256 e hash do documento liberado. Antes de retornar, verifica novamente documento, recursos, revisão e aprovações aplicáveis. Não altera o banco nem transmite o arquivo. Se o PDF ou uma imagem de inspeção forem modificados, a consulta recusa a entrega.

As aprovações continuam nos comandos administrativos de `WORKFLOW_LOCAL.md` e `INTEGRACAO_AGENTES.md`, fora do sandbox e das funções do modelo. Uma mudança textual retorna ao fluxo de conteúdo e invalida as aprovações afetadas; uma nova exportação invalida sua revisão final anterior.

## Verificação realizada

98 testes locais passaram: 73 anteriores e 25 novos de arquivos/documentos/sincronização. Os novos verificam bytes e hash, sessão e turno corretos, caminhos e formatos, paginação da API, bloqueio antes da aprovação, recursos inexistentes, limites comerciais, cobertura de páginas, hashes antigos, upload entre turnos e falha de sincronização, entrega local e adulteração posterior.

Um PDF fictício real de duas páginas foi criado exclusivamente para os testes. Sua leitura/renderização foi executada com Poppler/pypdf, e as duas imagens foram abertas e conferidas visualmente. Os testes de contratos utilizam relatórios e aprovações simulados em bancos temporários; não são evidência de qualidade de uma proposta real.

Nesta etapa não houve chamada à API da OpenAI, criação de sessão, aprovação real ou envio de proposta. Ainda falta a aceitação remota deste novo fluxo com designer e revisor. A geração dentro do ambiente é tarefa do designer com as ferramentas disponíveis; a aplicação faz incorporação, renderização e controle. Apresentações, documentos editáveis, páginas web, extração de documentos-fonte PDF/DOCX e validação especializada de formulários/assinaturas não foram conectados por esta implementação.

## Aceitação remota concluída

Após a implementação local acima, o teste remoto percorreu a produção/revisão PDF em Luna e chegou a `concluida`, revisão 25. Alex aprovou o texto v1 pelo hash apresentado; o designer gerou quatro páginas, com preço/condições na página 2; a aplicação importou os bytes por hash, renderizou as quatro páginas e enviou as imagens entre turnos; um revisor distinto inspecionou e comparou o arquivo, sem pendências; a entrega local passou por nova verificação. Houve exatamente duas decisões humanas no fluxo inteiro, do plano e do texto, sem aprovação adicional de acabamento. Detalhes em `verificacao_sessao/aceitacao_roi_pdf/CONCLUSAO.md`.
