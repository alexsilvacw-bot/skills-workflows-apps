# ATS-Proof CV

[Read the guide in English](README.en.md)

Adapte o currículo a cada vaga usando as experiências que você já registrou. A vaga orienta o que buscar no histórico e o que destacar no resumo. O currículo vem acompanhado dos registros que permitem conferir quais experiências sustentam cada requisito e onde ainda falta evidência.

## O que acontece em uma candidatura

Imagine uma vaga que pede **entrevistar clientes e transformar os achados em prioridades de produto**. Na base de exemplo, um relato comprova as entrevistas e outro mostra como a pesquisa orientou a priorização. A skill consegue considerar os dois juntos. A mesma base tem duas versões do relato sobre ativação de **41% para 53%**. A seleção identifica a realização em comum, preserva a fonte mais completa entre as elegíveis e evita gastar espaço repetindo o resultado. Se a vaga também pedir testes A/B, o registro de cobertura indica a lacuna. [Vaga fictícia](examples/vaga.txt) · [Base fictícia](examples/carreira.json)

1. **Busca por requisito.** A skill procura experiências por significado e por palavras específicas. A busca encontra candidatas e distingue a fonte principal das versões que podem trazer detalhes.
2. **Seleção por evidência.** Luna pontua os textos originais. A seleção protege as melhores evidências para cada requisito. Na escolha dos complementos, verifica se o relato acrescenta fatos e considera a relevância, a diversidade e o detalhe quantitativo. A revisão distingue apoio direto, parcial, transferível e ausente. Alterações propostas na seleção precisam preservar as notas e a melhor cobertura já alcançada.
3. **Revisão antes do PDF.** A vaga define o foco do resumo e a ordem de destaque das experiências. Uma segunda leitura verifica se o texto comunica esse foco e se os requisitos centrais estão ligados às fontes certas. O fluxo confere IDs, métricas e repetições e corrige os trechos afetados antes de montar o documento. Acréscimos de contexto ou responsabilidade ficam registrados para revisão factual humana.

Esta edição reaproveita os módulos de recuperação, seleção e revisão do fluxo original. O cadastro, a configuração dos vínculos e o template foram preparados para uso com o histórico de qualquer candidato. Por padrão, todos os empregadores partem da mesma prioridade. As notas, os critérios de cobertura e os pesos de seleção vêm do fluxo original.

## Instalação

1. Baixe ou clone o repositório e copie a pasta inteira `skills/public/ats-proof-cv` para sua área de trabalho.
2. Use Python 3.10 ou superior e LibreOffice no macOS ou Linux. Disponibilize `soffice` ou `libreoffice` no terminal. No Windows, use um ambiente Linux como WSL com as dependências instaladas nele.
3. Na pasta da skill, execute `python -m pip install -r requirements.txt` no seu ambiente Python. Se o seu sistema usa `python3`, substitua `python` nos comandos.
4. Configure `OPENAI_API_KEY` no ambiente que executará o script. A chave precisa ter acesso a `gpt-6.1-sol` para extração, `gpt-6-luna` para pontuação, revisão e redação, e `text-embedding-3-large` para os vetores. As chamadas são cobradas conforme o uso. [Autenticação da API](https://developers.openai.com/api/reference/overview#authentication)
5. Para usar pelo Codex, copie a pasta da skill para `.agents/skills/` no seu projeto e invoque `$ats-proof-cv`. Para usar pelo terminal, execute os comandos abaixo a partir da pasta da skill. [Skills no Codex](https://developers.openai.com/codex/skills)

## Cadastrar e indexar suas experiências

- **No Codex.** Anexe seu currículo ou cole suas realizações e envie este pedido. «Use `$ats-proof-cv` para cadastrar minhas experiências em `dados/carreira.json`. Preserve os cargos, as datas e as métricas que forneci. Mostre a base para eu revisar antes de indexar.»
- **Manualmente.** Copie [a base fictícia](examples/carreira.json) para `dados/carreira.json` e preencha com os seus dados. O campo `contato` é opcional. Use um vínculo por combinação de empresa, cargo e período. Dentro de `experiencia`, inclua um item por relato. Mantenha os IDs de vínculos e relatos estáveis e distintos.

| Campo | Como preencher |
| --- | --- |
| `experiencias` | Lista de vínculos. Cada vínculo tem `id`, `empresa`, `cargo`, `periodo` e a lista `experiencia` |
| `periodo` | Use `AAAA-MM` para `entrada` e `saida`. Use `null` para mês desconhecido. Em um vínculo atual, marque `atual` como `true` e deixe a saída como `null` |
| `experiencia` | Cada relato tem `id` e `texto`. Descreva a ação, o contexto e o resultado, se conhecido. Preserve as unidades e os qualificadores dos números |

Revise o JSON e prepare a base. Guarde a base e os resultados na sua área de trabalho privada.

```bash
python scripts/cv.py index --base dados/carreira.json
```

Na preparação, a API da OpenAI recebe os relatos para organizar as realizações e criar os vetores. O índice e os dados operacionais ficam em `.ats-proof-cv/`. Ao acrescentar uma experiência, crie um novo ID. Ao corrigir um relato, mantenha seu ID. Execute `index` novamente após editar o arquivo. Os vetores de textos idênticos com o mesmo ID são reutilizados, e a organização das realizações é atualizada para a versão da base. Use `--workspace` com o mesmo caminho nos comandos se preferir outra pasta.

## Criar e retomar uma candidatura

Forneça o anúncio em TXT UTF-8 ou passe a URL pública com `--url`.

```bash
python scripts/cv.py create --vaga dados/vaga.txt
```

O caminho da candidatura aparece no terminal. Para retomar uma execução interrompida, passe esse mesmo caminho. O fluxo retoma a etapa pendente e pode reaproveitar respostas compatíveis do checkpoint temporário.

```bash
python scripts/cv.py resume --candidatura .ats-proof-cv/candidaturas/empresa_cargo
```

A seleção normalmente trabalha com um recorte da base. Se a busca já retornar todos os textos de uma base pequena, `--permitir-base-integral` autoriza a avaliação desse conjunto. Use a opção de forma explícita, pois nesse caso todos os relatos recuperados podem ser enviados à API para pontuação.

### Testar com os dados fictícios

Os dois comandos fazem chamadas à API e usam uma área de trabalho própria para o exemplo.

```bash
python scripts/cv.py index --base examples/carreira.json --workspace dados/demo
python scripts/cv.py create --vaga examples/vaga.txt --workspace dados/demo --permitir-base-integral
```

## Conferir o resultado

O fluxo gera o PDF em português ou inglês, conforme a vaga. O DOCX é o intermediário usado para a conversão. Os JSONs na pasta da candidatura registram o percurso.

- `requisitos-vaga.json` contém os requisitos extraídos e suas prioridades.
- `experiencias-aprovadas.json` contém a seleção e o mapa de cobertura por componente. O nome do arquivo identifica a seleção do processo. A aprovação factual é humana.
- `dados-reescritos.json` contém a redação, o parecer de alinhamento e os acréscimos pendentes de revisão.
- `origens-recuperacao.json` mostra de onde vieram as experiências recuperadas.

Abra o PDF e revise o conteúdo com os JSONs, especialmente as métricas, a atribuição dos resultados e os acréscimos pendentes. As listas de habilidades e ferramentas vêm da extração do anúncio e também precisam de conferência. A conversão e a validação de texto do PDF são locais. Durante a candidatura, o anúncio, os requisitos e as evidências pertinentes são enviados à OpenAI para as etapas de extração, embeddings, contagem de entrada, avaliação e redação. Nome e contato do cabeçalho são preenchidos localmente.

[Instruções operacionais da skill](SKILL.md)

[Licença MIT da edição pública](LICENSE)
