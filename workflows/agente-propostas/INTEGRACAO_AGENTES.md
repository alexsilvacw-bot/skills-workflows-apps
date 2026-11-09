# Integração entre Agents API e workflow local

Implementação de conteúdo, ROI mensal e fluxo PDF, 02/11/2026. Referências oficiais: [Functions](https://developers.openai.com/api/docs/guides/agents-api/tools/functions), [sessões](https://developers.openai.com/api/docs/guides/agents-api/sessions) e [criação de sessão](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/methods/create).

## Separação de responsabilidades

O orquestrador roda em uma sessão OpenAI-hosted, com os guias e instruções dos especialistas. A aplicação chamadora mantém o banco SQLite e a chave da API no computador local. Somente as ferramentas explicitamente listadas em `workflow/gateway.py` são atendidas pela aplicação. O ambiente remoto não recebe o banco, a chave, o código administrativo de aprovação ou uma ferramenta de aprovação.

O modelo pode consultar o estado e fontes, registrar extratos web e briefing/estrutura/plano/texto/revisão, executar o cálculo mensal aprovado, indicar pendências, propor resolução com referência e solicitar avanço. O código verifica revisão esperada, campos permitidos, fontes humanas registradas, etapa e dependências. As funções são executadas localmente e seus resultados voltam à sessão com os IDs do turno e da chamada. Chamadas repetidas usam um recibo transacional para não duplicar alterações.

O orquestrador pode delegar aos subagentes nativos, que compartilham arquivos do ambiente e recebem suas instruções completas. As ferramentas function da aplicação são usadas pelo coordenador; especialistas devolvem resultados para incorporação. A responsabilidade semântica pela revisão permanece com o revisor; o gateway valida estrutura, condições e versões, mas não substitui avaliação de conteúdo por um especialista.

## Aprovações exclusivamente humanas

Não existe função de aprovação na lista de ferramentas do modelo. Chamar nome inexistente, incluir campos de aprovação no resultado, mencionar “aprovado” em uma resposta ou registrar uma mensagem humana de chat não cria aprovação. O gateway também não permite ao modelo retirar silenciosamente um ramo numérico já selecionado.

A decisão é registrada por uma operação local explícita do operador, após apresentação do objeto, versão e hash. O comando humano fica fora do dispatcher da API e fora do sandbox. Esta versão é uma interface administrativa local em um computador de um único operador; não implementa autenticação multiusuário ou um portal público.

## Executar uma conversa integrada

Na pasta do projeto, usando Python e a chave já configurada em `.env.local`:

```sh
python3 -m workflow.agent_runtime --proposta IDENTIFICADOR --mensagem-arquivo /caminho/mensagem.txt
```

A primeira chamada cria uma sessão pela aplicação com a credencial local, reutiliza a definição salva do orquestrador e o template, e fornece referências/instruções no ambiente. As ferramentas locais são aplicadas à sessão, sem alterar a definição salva. Modelo, esforço e configurações não sobrescritas vêm do agente salvo. As funções antigas eventualmente salvas são substituídas pela lista explícita da aplicação; outras ferramentas configuradas são preservadas.

Próximas mensagens usam o mesmo comando e identificador. IDs de sessão/turno, eventos e resultados são salvos em `dados/integracao/`. O runtime observa eventos antes de enviar follow-ups, atende chamadas pendentes e confere o status do turno específico; sessão idle não basta para declarar sucesso. Desconexão do observador não equivale a cancelar a execução.

Para retomar observação sem enviar outra mensagem:

```sh
python3 -m workflow.agent_runtime --proposta IDENTIFICADOR --retomar
```

Não reinicie uma criação cuja resposta se perdeu sem reconciliar o ID pela plataforma. O marcador `creation_pending` impede criar outra sessão automaticamente. A sessão original criada por Alex na plataforma permanece preservada e separada; a restrição de credencial observada nela não se aplica à sessão criada pela própria aplicação.

## Apresentar e registrar uma decisão humana

Quando o workflow aguardar aprovação, o orquestrador apresenta o conteúdo completo. O operador também pode consultar diretamente o objeto no banco:

```sh
python3 -m workflow.cli apresentar IDENTIFICADOR --objeto texto
```

Após ler o conteúdo, o operador executa a decisão com a revisão e o hash exatos apresentados:

```sh
python3 -m workflow.cli decisao-humana IDENTIFICADOR --revision REVISAO --objeto texto --hash HASH --decisao aprovar --manifestacao 'Manifestação humana referente a esta versão'
```

Use `ajustar` ou `reprovar` conforme a decisão real, e `plano_roi` como objeto quando aplicável. Alterar o conteúdo invalida as aprovações afetadas. Após a decisão, uma nova mensagem ao orquestrador o faz consultar o estado atualizado; não basta dizer no chat que foi aprovado. O runtime nunca executa o comando administrativo a partir de texto de modelo.

## Escopo atual

Conectados: entrevista/briefing, matriz, estrutura, fontes textuais/web, decisão inicial de ROI, plano, cálculo mensal após aprovação humana, redação, integração e revisão de conteúdo. O uso e os limites do ramo numérico estão em `ROI_WORKFLOW.md`. O fluxo PDF, a incorporação de recursos, as renderizações e o contrato da revisão final estão em `DOCUMENTO_WORKFLOW.md`. O avanço para a preparação visual continua dependente de aprovação humana válida.

PDF e recursos PNG/JPEG/PDF têm importação de artefatos publicados, renderização local, disponibilização de páginas entre turnos, revisão final por hashes e entrega local. Outros formatos finais e validação especializada de formulários/assinaturas ainda não estão conectados. Documentos-fonte UTF-8 têm importação própria; extração de PDF/DOCX permanece pendente. As novas ferramentas/instruções são fornecidas na criação de novas sessões; uma sessão anterior mantém sua configuração original.

Limites de correções automáticas continuam sem valor padrão escolhido. O gateway não expõe alteração desse limite ao modelo. Uma segunda versão de um mesmo tipo de resultado no mesmo turno exige limite de tentativas configurado; sem ele, o código recusa a correção automática. Uma mensagem humana posterior inicia outro turno e permite incorporar as novas informações. Retransmissões de chamada não repetem mutações. Resultados recusados por revisão antiga ou esquema inválido exigem revalidação, sem repetição cega.

## Testes

`python3 -m unittest discover -s tests -q` verifica núcleo, gateway e runtime com APIs simuladas. Os testes de integração reais usam mensagens explicitamente fictícias em `tests/mensagem_integracao_ficticia.txt` e `tests/mensagem_fluxo_sem_roi_ficticio.txt` e um banco separado `dados/teste_integracao.sqlite3`. Nenhuma aprovação humana é registrada pelo teste real.
