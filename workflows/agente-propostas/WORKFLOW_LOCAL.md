# Controle local do workflow — primeira implementação

Implementado em 02/11/2026. Este núcleo persiste registros e aplica condições de avanço. A conexão de conteúdo com a Agents API está em `workflow/gateway.py` e `workflow/agent_runtime.py`, descrita em `INTEGRACAO_AGENTES.md`. O módulo core isoladamente não chama a API nem gera documentos.

## O que funciona

- SQLite com estado atual e histórico de cada alteração, em transação. Uma operação recusada não altera a revisão persistida.
- Controle de concorrência por revisão esperada: um resultado de agente baseado em revisão antiga não pode substituir o estado atual.
- Resultados com conteúdo, versão, hash, dependências e validade; versões anteriores ficam no histórico. Alteração invalida os resultados dependentes e retorna à etapa correspondente.
- Briefing com dados/fontes e matriz dos 14 elementos; bloqueio de decisões não resolvidas. Estrutura com seções, ordem relativa e numeração verificadas, sem aprovação humana obrigatória.
- Decisão separada de uso de ROI. Ramo numérico exige aprovação do plano antes da produção/cálculo; retirada explícita reabre estrutura e dependências. Fórmulas/cálculo e validação semântica do método ainda não foram implementados.
- Revisão de conteúdo e final separadas, com cobertura mínima de dimensões, evidências e situações permitidas. Resultados parciais, não verificáveis e falhas bloqueiam o avanço. A revisão especializada ainda precisa conferir os critérios completos dos guias e fornecer evidências reais.
- Aprovação humana vinculada ao hash da versão, preservada quando só muda o layout; alteração do texto exige nova revisão e aprovação.
- Inventário de recursos: arquivo real, hash e registro de verificação; opção de não usar recursos com justificativa. Documento verificado novamente antes da entrega para detectar alteração posterior à revisão.
- Pendências por etapa: insumo de etapa futura não bloqueia por si só o briefing. Resolução exige registro de informação/decisão/evidência.
- Limite de tentativas obrigatório antes de ciclos automáticos; nenhum valor padrão foi escolhido. Aprovação visual adicional somente se configurada.

## Como executar

Use Python 3.12 ou posterior, sem instalar dependências. Execute os comandos na pasta `/Users/alex/Documents/11_IA/agente_proposta_comercial`.

```sh
python3 -m workflow.cli criar --id proposta-teste
python3 -m workflow.cli ver proposta-teste
python3 -m workflow.cli historico proposta-teste
```

O banco padrão é `dados/workflow.sqlite3`. Para usar outro destino, passe `--db /caminho/banco.sqlite3` antes do subcomando. Não inclua o banco comercial no pacote de referências.

Para registrar um resultado, use um JSON com seu conteúdo e a revisão corrente do estado:

```sh
python3 -m workflow.cli registrar proposta-teste --revision 0 --tipo briefing --json /caminho/briefing.json
python3 -m workflow.cli avancar proposta-teste --revision 1
```

Cada operação bem-sucedida incrementa `revision`. O comando `ver` mostra a revisão atual, a etapa, pendências, versões e hashes. `avancar` só muda a etapa quando os requisitos do código são atendidos. Não use estes exemplos com números de revisão antigos.

Os tipos aceitos e os formatos iniciais estão em `workflow/core.py`. Briefing usa `dados`, `fontes` e `matriz` (elemento, decisão, justificativa, fontes). Estrutura usa `secoes` (número, título, elementos, pergunta, fontes, mensagens). As revisões usam `escopo`, `criterios` (ID, situação, evidência) e `pendencias`. Os IDs mínimos de revisão estão em `REVIEW_CRITERIA`. Listas mínimas não substituem os critérios completos dos guias.

Para decisões humanas existe um comando separado:

```sh
python3 -m workflow.cli decisao-humana proposta-teste --revision REVISAO_ATUAL --objeto texto --hash HASH_ATUAL --decisao aprovar --manifestacao 'Manifestação humana original ou referência ao evento da interface'
```

Este comando é uma entrada administrativa local. O hash impede aprovar outra versão, mas não autentica por si só quem o executou. O runtime não expõe essa operação como ferramenta e não fornece o banco ou esse código ao sandbox. O operador local registra a manifestação explicitamente; o modelo não aprova em nome do usuário. Uma futura interface multiusuário precisará autenticar a identidade do aprovador.

## Validação

```sh
python3 -m unittest discover -s tests -v
```

Os testes usam base temporária, dados fictícios, aprovações simuladas e um arquivo textual de teste. Percorrer o estado de entrega nesse teste não significa ter produzido ou revisado visualmente um PDF. Nenhuma conta, agente remoto ou proposta real é alterado pelos testes.

## Onde estamos

Núcleo local integrado ao fluxo de conteúdo pela Agents API, com 51 testes locais e dois testes reais (briefing incompleto bloqueado e fluxo sem ROI até espera de aprovação textual). A aplicação usa sessão própria para atender funções locais; a sessão original da plataforma permanece separada. Aprovação é uma operação exclusiva do operador local, fora das ferramentas do modelo. ROI executável, fontes documentais do cliente, produção de documentos e revisão visual continuam sendo etapas posteriores.

O guia original acompanha o progresso. A cópia em `referencias/` permanece como a versão funcional 1.0 enviada e conferida na sessão; o acompanhamento do desenvolvimento não altera seus hashes.
