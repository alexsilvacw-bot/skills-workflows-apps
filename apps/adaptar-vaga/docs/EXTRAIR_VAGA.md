# Extrair vaga

Abra `Adaptar Vaga.app`, cole o link de uma vaga individual ou a descrição completa e selecione Extrair vaga. Após uma extração bem-sucedida, o script salva automaticamente `requisitos-vaga.json` em uma nova pasta `candidaturas/empresa_cargo/`. A interface mostra o caminho. Baixar JSON é opcional e cria uma cópia fora do projeto, no destino escolhido pelo navegador.

O nome da pasta usa a empresa e o cargo extraídos, em minúsculas sem acentos, com underscores. Se já existir, é criada `empresa_cargo_2`, depois `_3`. A pasta anterior não é lida ou alterada. Empresa ou cargo ausente usam `empresa_nao_informada` ou `cargo_nao_informado` no nome; os dados extraídos permanecem sem alteração.

## Linha de comando

Configure `OPENAI_API_KEY` no ambiente. O extrator usa Python 3.10 ou superior, sem pacotes externos. Execute na raiz do projeto:

```bash
python3 scripts/extrair_vaga.py --url 'https://empresa.example/vagas/cargo' --candidatura
```

Para um arquivo de anúncio fornecido pelo usuário:

```bash
python3 scripts/extrair_vaga.py --arquivo /caminho/anuncio.txt --candidatura
```

`--candidatura` cria a pasta e grava o único JSON desta etapa. `--saida` é a alternativa para um destino explicitamente escolhido; não pode ser usado junto a `--candidatura`. Sem essas opções, o resultado aparece somente no terminal. Para diagnosticar a captura sem API, use `--somente-texto`, que não pode ser combinado com `--candidatura`. Não grave um anúncio auxiliar por padrão.

## Contrato da saída

O JSON contém somente oito campos:

- `nome_empresa` e `nome_vaga`, ou `null` quando ausentes.
- `requisitos_obrigatorios` e `requisitos_desejaveis`, listas no idioma original da vaga.
- `competencias`, exatamente 10 strings inferidas das atividades e contexto da vaga.
- `ferramentas`, de 5 a 10 strings, priorizando as citadas e completando por inferência contextual.
- `idioma_cv`, seguindo o idioma do anúncio, salvo instrução explícita de idioma para o currículo.
- `ats`, identificado localmente como Greenhouse, Lever, Workday, Ashby, SmartRecruiters, Gupy ou desconhecido.

Competências e ferramentas preservam o idioma original do anúncio, independentemente de uma exceção em `idioma_cv`. A extração não consulta a base nem candidaturas anteriores. Evidências são usadas internamente e não entram no JSON final.

## Execução e erros

O modelo e o esforço padrão do extrator são definidos em `scripts/extrair_vaga.py`. Com instrução humana, o modelo pode ser substituído por `--modelo` ou `OPENAI_EXTRACTION_MODEL` (com fallback para `OPENAI_MODEL`), e o esforço por `OPENAI_EXTRACTION_REASONING_EFFORT` (com fallback para `OPENAI_REASONING_EFFORT`). A interface e o orquestrador seguem os mesmos padrões de extração. Requisitos são classificados na API da OpenAI. ATS e nomes de pastas são resolvidos por código, sem chamadas adicionais.

Falha de evidência literal permite uma única chamada de correção já prevista. As demais falhas não autorizam novas chamadas por iniciativa do agente. Texto acima de 100 mil caracteres, captura acima de 5 MB, múltiplas vagas diferentes ou dados inválidos são recusados sem truncamento silencioso. Nenhuma pasta é criada antes de concluir a extração estruturada.

A chave da interface fica em `.local/openai-key`, com arquivo 600 e pasta 700. Não deve ser exposta ou compartilhada. A interface atende apenas em `127.0.0.1`, usa uma porta livre e encerra com o aplicativo. A extração pela API é cobrada; salvar o JSON não usa tokens adicionais.

Conferir tipos, evidências e quantidades não comprova completude ou precisão semântica do modelo. Revise o resultado antes de continuar o currículo.
