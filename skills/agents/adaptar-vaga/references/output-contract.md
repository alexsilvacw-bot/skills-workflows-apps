# Contrato de saída

## Diretório

Criar um diretório dentro de `candidaturas` no projeto de carreira.

Usar o padrão.

`AAAA-MM-DD_empresa_cargo`

Normalizar o nome sem perder a identificação humana. Não sobrescrever uma candidatura existente. Acrescentar sufixo de versão quando necessário.

## Fase 1. Arquivos obrigatórios antes da aprovação

### `matriz-de-requisitos-e-evidencias.md`

Criar antes do currículo e incluir.

1. Fonte e data de acesso da descrição.
2. Inventário completo das exigências com identificadores `R01`, `R02` e assim por diante.
3. Texto exato, formulação normalizada, categoria e prioridade de cada exigência.
4. Uma seção para cada requisito com todas as experiências verificáveis relevantes.
5. Empresa ou projeto, período ou contexto, evidência concreta, fonte canônica, score de 0 a 3 e justificativa do score.
6. Uma linha `Nenhuma evidência confirmada` com score 0 quando não houver experiência aplicável.
7. Ranking agregado por experiência com soma, quantidade de scores 3 e 2, requisitos obrigatórios cobertos, lacunas obrigatórias e fontes.
8. Registro de exigências repetidas que não foram somadas duas vezes.

### `confirmacao-de-requisitos.md`

Criar antes do rascunho e incluir.

1. Todos os requisitos materiais que receberam score 0 na primeira análise.
2. Para cada requisito, a hipótese plausível criada, a pergunta objetiva e uma resposta-exemplo que atenderia perfeitamente à vaga.
3. O rótulo explícito `Exemplo hipotético, não confirmado e proibido no currículo até confirmação de Alex` antes de cada resposta-exemplo.
4. A classificação da resposta de Alex como `confirmado`, `parcialmente confirmado`, `negado` ou `ainda incerto` e somente a parte factual positiva confirmada. Não reproduzir respostas negativas em primeira pessoa.
5. Os detalhes factuais confirmados, o score revisado e a justificativa da mudança ou manutenção do score.
6. Quando não houver requisito material com score 0, registrar isso explicitamente.
7. Uma seção `Auditoria pós-rascunho` com toda pergunta factual nova gerada pela auditoria literal, a resposta de Alex, a classificação e a consequência editorial.

Não criar `rascunho-do-curriculo.md` enquanto uma resposta pendente puder mudar materialmente o score, o diagnóstico, a arquitetura ou a seleção de provas.

### `diagnostico-da-vaga.md`

Incluir.

1. Fonte e data de acesso.
2. O que sabemos.
3. O que assumimos.
4. O que precisa ser validado.
5. Ação recomendada.
6. Problema central da contratação.
7. Síntese dos requisitos decisivos, melhores scores e lacunas.
8. Arquitetura e narrativa escolhidas.
9. Remuneração publicada ou `não informada`.

### `rascunho-do-curriculo.md`

Criar o currículo verificável completo em texto e incluir somente conteúdo seguro para candidatura. Priorizar as experiências com maior cobertura de requisitos obrigatórios e scores 3 e 2.

Estrutura recomendada.

1. Nome e contato.
2. Título funcional.
3. Resumo executivo.
4. Competências centrais.
5. Experiência profissional.
6. Formação.
7. Idiomas.

Mostrar o texto integral no chat. Não criar currículo aspiracional, artefatos contrafactuais ou qualquer DOCX nesta fase.

### `auditoria-ats-literal.md`

Criar imediatamente depois do primeiro rascunho e antes da avaliação completa com `$avaliar-curriculo`. Incluir.

1. Veredito geral da simulação de ATS antigo.
2. Uma seção `ATS-RXX` para cada requisito material, com os termos literais procurados e o motivo da decisão.
3. O que precisaria ser verdade em linguagem concreta e verificável.
4. A frase ideal se confirmada, escrita no idioma do currículo.
5. A alteração proposta com a seção e o trecho exato a substituir ou o ponto exato de adição.
6. Estado factual e ação autorizada para cada frase.
7. Uma segunda passagem depois das correções, com cada item classificado como resolvido, lacuna real preservada ou bloqueado por confirmação factual.

Frases condicionais deste relatório são privadas e não podem entrar no rascunho ou no Word sem suporte factual confirmado. Seguir [ats-literal-audit-contract.md](ats-literal-audit-contract.md).

### `avaliacao-do-curriculo.md`

Gerar com a skill `$avaliar-curriculo` depois de concluir a segunda passagem da auditoria literal. Comparar o rascunho com a descrição integral, a matriz, `auditoria-ats-literal.md` e as fontes canônicas. Registrar veredito, provas omitidas, formulações fracas, exageros, lacunas reais, perguntas materiais e correções necessárias.

Depois de corrigir o rascunho, reavaliar toda alteração material. Uma avaliação positiva não substitui aprovação humana.

### `validacao-do-pacote.json`

Executar o validador com `--stage draft --require-ats-audit`. O estágio deve falhar se a auditoria literal estiver ausente ou se encontrar DOCX, `qa-word.json` ou `aprovacao-humana.md` antes da aprovação.

## Gate de aprovação humana

Apresentar no chat o rascunho integral avaliado e interromper a execução. Criar o Word somente depois de Alex aprovar explicitamente o texto ou autorizar sua conversão em Word.

Silêncio, ausência de objeção, autorização genérica anterior ou veredito da skill `$avaliar-curriculo` não contam como aprovação humana.

## Fase 2. Arquivos obrigatórios depois da aprovação

### `aprovacao-humana.md`

Registrar.

1. Data da aprovação.
2. Texto exato da confirmação humana.
3. Identificação da versão aprovada de `rascunho-do-curriculo.md`.

### `Alex_Floriano_Cargo_Empresa_Idioma.docx`

Criar em Word a partir do rascunho aprovado. Não fazer mudança editorial material sem retornar à Fase 1, reavaliar o texto e obter nova aprovação.

Usar o padrão exato `Alex_Floriano_Cargo_Empresa_Idioma.docx`, com `PTBR` para português do Brasil e `EN` para inglês. Exemplo. `Alex_Floriano_Gerente_de_Marketing_Oxiquimica_Agrociencia_PTBR.docx`.

### `qa-word.json`

Registrar a verificação visual do currículo verificável com.

1. Caminho do arquivo.
2. Quantidade de páginas renderizadas.
3. Confirmação de inspeção de todas as páginas.
4. Ausência de clipping, sobreposição, fontes ausentes e quebras inadequadas.
5. Estado `passed` somente depois da última renderização revisada.

### `validacao-do-pacote.json`

Gerar com o script de validação usando `--stage final --require-ats-audit`. Não editar manualmente para esconder falhas.

## Entregáveis opcionais somente quando solicitados

### `mensagem-de-candidatura.md`

Criar somente quando Alex solicitar. Usar somente fatos do currículo verificável e adaptar ao idioma da vaga. Não criar quando a recomendação for `não priorizar`, salvo pedido explícito.

### `preparacao-de-entrevista.md`

Criar somente quando Alex solicitar. Incluir tese de fit, três provas, lacunas, perguntas prováveis, perguntas para a empresa e red flags. Usar somente fatos verificáveis nas respostas sugeridas.

## Entrega em chat

Informar.

1. Recomendação de candidatura.
2. Posicionamento escolhido.
3. Experiências com maior score e requisitos que elas cobrem.
4. Três lacunas principais.
5. Idioma e formato recomendados.
6. Na Fase 1, texto integral e caminho do rascunho, da matriz, da auditoria literal e da avaliação.
7. Pedido explícito de aprovação humana antes do Word.
8. Na Fase 2, caminhos do currículo Word e dos documentos finais.

Não atualizar a fonte de verdade como efeito automático da candidatura.
