---
name: criar-cv-sem-api
description: Cria ou retoma currículos de Alex Floriano pelo fluxo original do Adaptar Vaga, usando os modelos das etapas no Codex autenticado com ChatGPT, sem chave de API, até Word e PDF.
---

# Criar CV sem API

Projeto: `/Users/alex/Documents/Adaptar Vaga`.

Leia o `AGENTS.md` do projeto para as instruções globais. Esta skill concentra as instruções de execução. [FLUXO_CV_SEM_API.md](</Users/alex/Documents/Adaptar Vaga/FLUXO_CV_SEM_API.md>) explica este modo para consulta; não é uma segunda fonte de regras operacionais. Consultar somente a seção pertinente à etapa ou à falha atual, quando necessário. Durante a execução de um currículo, não carregar a skill ou o fluxo do outro modo.

## Fontes das regras e dos contratos

Consulte somente os blocos necessários à etapa. Os valores e contratos vigentes ficam nas configurações e nos validadores dos scripts; não mantenha cópias de escalas, limites ou schemas nesta skill.

| Fonte | Responsabilidade |
| --- | --- |
| `config/regras_matching.json` | Critérios de matching em `matching`: requisitos, evidências, escala, pontuação, deduplicação, seleção, lacunas, recuperação, saída e controles. O índice reutilizável fica em `indice_matching`. |
| `config/configuracao.json` | Regras de extração, ATS, redação, validação humana, contrato de entrada do montador, layout e dados fixos. Na execução de uma candidatura, carregar somente depois de existir `experiencias-aprovadas.json`. |
| `scripts/extrair_vaga.py` | Prompt, schema, classificação, prioridades e validações da extração, incluindo o tratamento corretivo previsto. |
| `scripts/avaliar_experiencias.py` | Recuperação, avaliação, deduplicação, seleção, validação do índice e checkpoint de retomada. |
| `scripts/redigir_curriculo.py` | Resposta de redação, consolidação, referências, validações e feedback de retomada. |
| `scripts/montar_curriculo.py` | Validação da entrada, resolução das fontes, preenchimento do template e exportação de Word/PDF. |

Use os componentes existentes. Uma divergência entre instruções, configuração e implementação deve ser identificada e informada; não invente uma regra para contorná-la.

## Execução pela conta ChatGPT

Ao invocar esta skill, Alex autoriza as chamadas de IA necessárias às etapas pelo cliente oficial Codex autenticado com ChatGPT, no mesmo escopo de dados do fluxo original. Usar o orquestrador com `--sem-api`, que fornece as respostas por `scripts/codex_conta.py` sem utilizar chave ou chamar a API diretamente. Não recorrer à API como alternativa.

Os modelos e esforços são os resolvidos pelos scripts originais, independentemente do modelo deste chat. Cada chamada passa explicitamente o modelo recebido da etapa ao cliente. Não trocar modelos ou alterar suas configurações automaticamente.

Cliente e login são verificados somente quando há chamada de IA pendente. Com os três JSONs válidos, a montagem local não exige cliente nem autenticação. Se uma chamada precisar de login, orientar Alex a usar `codex login`, sem ler arquivos de credenciais.

O fornecedor usa uma execução efêmera em temporário, sem ferramentas externas, com o schema original e as instruções e dados da etapa, sem instruções editoriais adicionais. O prazo por chamada é definido exclusivamente por `CALL_TIMEOUT_SECONDS` em `scripts/codex_conta.py`; consultar essa fonte, sem manter outro valor nesta skill. O fornecedor informa o prazo efetivo no terminal. O orquestrador pode executar várias chamadas consecutivas: não impor ao processo completo um limite externo menor que o necessário para concluí-las. Acompanhar execuções longas pela sessão de execução; o intervalo de espera da ferramenta não substitui o prazo da chamada de IA. Validar a conclusão da chamada e o JSON pelos validadores existentes; mensagens informativas do cliente não criam exigências de conteúdo.

Executar com `PYTHONDONTWRITEBYTECODE=1` pelo mecanismo normal de permissões. Os arquivos temporários de schema e resposta não ficam na candidatura. A retomada distingue os fornecedores e suas versões; não atribuir respostas da API à conta.

## 1. Iniciar ou retomar

Se Alex fornecer uma nova vaga, usar o link ou o texto completo. Se a entrada estiver ausente, pedi-la. Se esta mesma candidatura já tiver sido extraída na sessão, continuar sua pasta atual.

Para uma nova vaga por link:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 '/Users/alex/Documents/Adaptar Vaga/scripts/criar_curriculo.py' --sem-api --url '<LINK_DA_VAGA>'
```

Passar argumentos com escape seguro de shell. Para texto colado, usar um TXT UTF-8 temporário do sistema e substituir `--url` por `--arquivo`. Remover o temporário ao concluir.

O orquestrador chama o extrator, que cria `candidaturas/empresa_cargo/requisitos-vaga.json`. Usar exatamente a pasta retornada e informá-la a Alex. Colisões recebem sufixo numérico, sem sobrescrita.

Para continuar uma candidatura:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 '/Users/alex/Documents/Adaptar Vaga/scripts/criar_curriculo.py' --sem-api --candidatura '<PASTA_ATUAL>'
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

Executar `scripts/avaliar_experiencias.py` pelo orquestrador. O matching usa somente `config/regras_matching.json`; não carregar a configuração editorial antes de existir a seleção.

1. Validar os requisitos e a existência do índice. Se ausente, interromper antes de ler a base. Com índice presente, a leitura local da base é permitida para validar versão/cobertura e resolver IDs.
2. Recuperar grupos e realizações pelos fatos e componentes conforme `matching.recuperacao`. Contexto específico ainda não confirmado não bloqueia a recuperação de fatos potencialmente transferíveis. Resumos e buscas por termos servem para localizar fontes; não confirmam aderência.
3. Recuperar uma fonte principal por realização. Buscar fontes adicionais da mesma realização somente quando cobrem pistas específicas ainda não encontradas na principal. Registrar fontes, detalhes recuperados e pistas ausentes no terminal/conversa.
4. Avaliar os textos originais recuperados, deduplicar e selecionar pelas regras de pontuação e cobertura configuradas. Reutilizar as notas já calculadas nas rodadas locais de seleção, sem novas chamadas ou releituras para cada rodada.
5. Salvar `experiencias-aprovadas.json` conforme `matching.saida`. Esse nome representa a seleção do processo e não exige aprovação humana de cada experiência.

Não ampliar automaticamente a avaliação para toda a base. Preservar versões não recuperadas sem notas e não propagar avaliações entre versões. Declarar a execução exaustiva somente se toda a base tiver sido avaliada.

Requisito sem grupo, família ou realização segue o tratamento de lacunas configurado; os demais requisitos continuam. Informar a lacuna sem afirmar ausência dessa experiência na carreira. Lacunas não geram propostas nem aprovação por si só. Com seleção abaixo da meta, podem orientar as propostas limitadas ao déficit. Universo avaliado, notas, famílias, medições e pendências ficam no terminal/conversa ou no checkpoint temporário autorizado, sem matriz persistente.

## 4. Redigir e validar

Depois de existir a seleção, consultar os blocos pertinentes de `config/configuracao.json` e executar `scripts/redigir_curriculo.py` pelo orquestrador.

Resolver os IDs selecionados na base. Aplicar as regras de ATS, idioma e redação, preservando fatos, métricas, escopo e referências. Consolidar apenas relatos equivalentes do mesmo vínculo, com sustentação nas fontes. Conferir também a preservação semântica do texto produzido; validade estrutural sozinha não confirma fidelidade factual.

Gerar `dados-reescritos.json` conforme `montagem_curriculo.contrato_entrada` e os validadores. Resolver nomes de empresas, datas e demais dados fixos nas fontes durante a montagem, sem criar cópias adicionais na redação.

Aplicar `montagem_curriculo.validacao_humana` e as regras de lacunas:
- Com seleção suficiente e nenhuma proposta pendente, continuar automaticamente para Word e PDF depois da validação.
- Abaixo da meta, apresentar o rascunho com propostas separadas, ainda não aprovadas, limitadas ao déficit de experiências.
- Com a meta atingida, lacunas de quaisquer requisitos não exigem proposta nem aprovação.
- Aguardar decisão de Alex somente sobre a confirmação e inclusão das propostas. Não tratar silêncio como confirmação nem inserir hipótese como fato.
- Informar pendências de datas ou aderência no terminal/conversa; elas não criam outra etapa de aprovação.

## 5. Montar, conferir e entregar

O orquestrador chama `scripts/montar_curriculo.py` quando o conteúdo está apto. Para montagem direta de uma candidatura com redação válida, seleção suficiente e nenhuma proposta pendente, ou com complementação já aprovada e incluída validamente:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 '/Users/alex/Documents/Adaptar Vaga/scripts/montar_curriculo.py' --entrada '<PASTA_ATUAL>/dados-reescritos.json' --saida '<PASTA_ATUAL>/<NOME_RESOLVIDO_PELA_CONFIGURACAO>.docx' --pdf
```

Usar `--aprovado` somente para registrar uma decisão humana efetivamente dada. Não sobrescrever documentos sem autorização.

Gerar sempre Word e PDF. Resolver o nome pelo bloco `montagem_curriculo.nome_arquivo` de `config/configuracao.json`, com empresa e cargo de `requisitos-vaga.json`, usando a função `document_stem` do orquestrador. O PDF usa o mesmo nome do Word. Nome solicitado por Alex ou pelo formulário substitui o padrão, sem cópia adicional. Na montagem, consultar o JSON de redação, as fontes para resolver dados, a configuração e o template. Copiar os blocos fixos; não reescrever, traduzir, chamar a API ou recalcular o matching nessa etapa.

Conferir versões da base e da vaga, referências, texto extraível e todas as páginas. Manter temporários de revisão fora do projeto. Se a exportação de PDF falhar, preservar o DOCX.

Entregar os links dos documentos, a pasta atual e as pendências reais. Distinguir validação estrutural, conferência semântica, revisão visual e execução real.

## Falhas e retomada

Identificar a etapa e a causa antes de repetir uma execução. Usar o mecanismo existente de retomada e feedback de validação. Uma falha técnica não exige aprovação humana do currículo; corrigir dentro do escopo autorizado, respeitando os contratos.

Respostas de IA já recebidas e lacunas podem permanecer no checkpoint SQLite temporário do sistema, sem credenciais e com permissões restritas. Reutilizar somente entradas idênticas e versões compatíveis de base, vaga, regras, código, modelo e configuração editorial pertinente. Excluir o checkpoint após salvar a redação pelo mecanismo existente.

O sistema pode apagar temporários. Quando isso impedir a retomada, informar a necessidade de reconstrução. Não criar matriz ou checkpoint persistente no projeto.

Se o processo retornar erro, verificar o que foi salvo e o que precisa ser refeito. Não prometer que a retomada corrigirá o erro. Falhas não autorizam trocar modelo, alterar limites, relaxar contratos ou cortar conteúdo silenciosamente.

## Preparação do índice — tarefa separada

A criação de um currículo não autoriza preparar ou atualizar o índice automaticamente. Índice ausente ou desatualizado exige a preparação apropriada antes de continuar o matching. Verificar se Alex já autorizou especificamente o método e a leitura integral necessária; não pedir a mesma autorização novamente.

A preparação, organização e consolidação do índice pela conta não estão implementadas neste fornecedor. `--sem-api --indexar-base` é rejeitado. Não executar os comandos com API como alternativa dentro desta skill. Com índice ausente ou desatualizado, informar a necessidade da tarefa separada antes de continuar o matching.
