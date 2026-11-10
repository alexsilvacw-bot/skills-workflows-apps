# Skills, workflows e aplicativos

Repositório privado para acompanhar versões de skills e código de ferramentas pessoais.

## Conteúdo

- `skills/codex` e `skills/claude`: cópias das skills próprias ou com sinais fortes de adaptação, preservadas por ambiente para comparar versões.
- `workflows/agente-propostas`: instruções gerais do agente de propostas comerciais.
- `apps/buscador-influenciadores`: código do buscador, sem banco, resultados ou validações.
- `apps/studio-imagens`: código do Studio, sem imagens geradas nem materiais de campanhas.
- `apps/revisor-de-telas`: HTML e bundle local do aplicativo.
- `apps/voice-studio`: registro da versão instalada do Voice Studio; o pacote de 814 MB e suas dependências não foram copiados.
- `apps/adaptar-vaga`: scripts, interface e documentação; currículos, candidaturas e credenciais ficam fora.

## Fontes ainda pendentes

- Workflow “Debatedor Claude vs. ChatGPT”. O arquivo-fonte ainda não foi localizado neste computador.

O site Ag.Geo já está versionado em [alexsilvacw-bot/aggeo-site](https://github.com/alexsilvacw-bot/aggeo-site) e não foi duplicado aqui. Skills de bibliotecas genéricas instaladas não foram copiadas como criações próprias.

## Fluxo de atualização

As skills selecionadas em `~/.agents/skills`, `~/.codex/skills` e `~/.claude/skills` usam links para este checkout local, mantendo as diferenças por ambiente. Para atualizações em agentes e aplicativos, sincronize apenas os arquivos-fonte aprovados para `workflows/` ou `apps/`. Após aprovação, revise o diff, faça commit e envie `main` pelo GitHub Desktop. Dados pessoais, segredos, bancos locais, logs e saídas de execução permanecem fora.
