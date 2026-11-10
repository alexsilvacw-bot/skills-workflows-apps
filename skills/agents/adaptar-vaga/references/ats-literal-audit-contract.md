# Contrato da auditoria de ATS literal

## Propósito

Executar uma simulação deliberadamente rígida de um ATS antigo depois que `rascunho-do-curriculo.md` estiver escrito e antes da avaliação completa com `$avaliar-curriculo`.

A simulação deve agir como um filtro literal que não concede crédito por contexto implícito, títulos aproximados, experiência transferível sem explicação ou sinônimos distantes. O objetivo é revelar por que o currículo poderia ser rejeitado automaticamente e transformar cada falha em uma decisão editorial ou em uma pergunta factual concreta.

Não atribuir percentual de compatibilidade, nota universal de ATS nem probabilidade de aprovação. Não afirmar que um sistema real produzirá o mesmo resultado.

## Escopo obrigatório

Comparar o rascunho com a descrição integral da vaga e com a matriz de requisitos. Inspecionar todos os filtros eliminatórios, requisitos obrigatórios, responsabilidades centrais, ferramentas, setores, geografias, anos de experiência, tipos de parceiro, métricas e palavras exatas relevantes.

Revisar com atenção especial os requisitos com score 0, 1 ou 2. Um score 3 também deve ser marcado como fraco quando a prova existe na fonte, mas não aparece de forma literal e localizável no currículo.

Não transformar linguagem contextual da empresa em requisito do candidato. Não premiar repetição artificial de palavras nem sugerir keyword stuffing.

## Vereditos permitidos

Usar um destes vereditos para cada requisito.

1. `Cobertura literal forte` quando o termo e a prova concreta aparecem de forma clara.
2. `Correspondência literal fraca` quando existe evidência relevante, mas o termo, o escopo, a duração ou o resultado estão implícitos ou vagos.
3. `Risco de auto-rejeição` quando um filtro ou requisito material não é encontrado de forma sustentada no currículo.

Emitir também um veredito geral curto. Usar `passaria pela triagem literal`, `passaria com risco elevado` ou `auto-rejeição provável nesta simulação`. O veredito geral deve ser explicado pelos requisitos decisivos, nunca por uma porcentagem inventada.

## Registro obrigatório por requisito

Criar `auditoria-ats-literal.md`. Para cada requisito relevante, usar um identificador no formato `ATS-RXX` e registrar.

1. `Exigência exata da vaga` com o texto literal ou uma citação curta fiel.
2. `Termos literais procurados` com as palavras e variantes realmente importantes.
3. `Veredito do ATS antigo` com um dos três estados permitidos.
4. `Motivo da decisão` explicando de maneira direta por que o currículo passa, fica fraco ou seria rejeitado.
5. `Evidência atual no currículo` com a frase exata encontrada ou `Nenhuma evidência literal localizada`.
6. `O que precisaria ser verdade` com uma condição concreta, específica e verificável. Exemplo. `Ter acumulado pelo menos oito anos de atuação direta em partner, alliance ou channel marketing em fintech ou enterprise SaaS.`
7. `Frase ideal se confirmada` no idioma do currículo e pronta para uso. A frase é uma proposta condicional, não uma afirmação sobre Alex.
8. `Alteração proposta` indicando a seção e o trecho exato a substituir ou o ponto exato onde a frase seria adicionada. Preferir substituição de conteúdo fraco a crescimento automático do documento.
9. `Estado factual` usando somente `confirmado e sustentado`, `potencialmente verdadeiro, requer confirmação` ou `negado ou sem suporte confirmado`.
10. `Ação autorizada` usando somente `aplicar`, `perguntar antes de alterar` ou `não inserir`.

Mesmo quando a evidência estiver ausente, escrever a condição e a frase ideal de forma concreta. Não inserir essa frase no currículo enquanto o estado factual não for `confirmado e sustentado`.

Usar este nível de especificidade.

```markdown
O que precisaria ser verdade. Ter acumulado pelo menos oito anos de atuação direta em partner, alliance ou channel marketing em fintech ou enterprise SaaS.

Frase ideal se confirmada. "Partner marketing leader with 8+ years of experience building channel and alliance marketing programs in fintech and enterprise SaaS."

Alteração proposta. Substituir a primeira frase atual do resumo pela frase ideal. No relatório real, copiar a frase atual exata que será substituída.
```

Evitar condições vagas como `ter experiência relevante`, frases genéricas de liderança ou instruções sem uma localização editorial precisa.

## Regras para alteração do rascunho

Quando o fato já estiver confirmado e a fraqueza for apenas lexical ou editorial, substituir a frase diretamente. Usar o termo exato da vaga somente quando ele descrever com precisão a experiência confirmada.

Quando a frase ideal acrescentar duração, cargo, ownership, setor, ferramenta, tipo de parceiro, geografia, métrica ou resultado ainda não confirmado, classificar como `potencialmente verdadeiro, requer confirmação`. Adicionar uma seção `Auditoria pós-rascunho` em `confirmacao-de-requisitos.md`, apresentar a pergunta no chat com uma resposta-exemplo factual positiva e interromper antes da alteração.

A resposta-exemplo deve conter apenas a frase concreta que Alex está avaliando. Não começar com `Verdadeiro`, `Parcialmente verdadeiro`, `Falso` ou equivalentes. Solicitar a classificação fora da frase.

Quando uma negativa explícita já estiver registrada ou não houver uma âncora plausível na trajetória, usar `negado ou sem suporte confirmado` e `não inserir`. Não repetir a pergunta. Manter a lacuna real no relatório e no diagnóstico.

## Segunda passagem obrigatória

Depois de processar correções e respostas, reexecutar a auditoria sobre o rascunho atualizado e registrar a seção `Segunda passagem`.

Para cada item inicialmente fraco ou eliminatório, informar um destes resultados.

1. `Resolvido no rascunho` com a frase final aplicada.
2. `Lacuna real preservada` quando a frase condicional não foi sustentada.
3. `Bloqueado por confirmação factual` quando uma pergunta material foi apresentada e ainda não recebeu resposta.

Não avançar para `$avaliar-curriculo` enquanto existir um item `Bloqueado por confirmação factual`. Uma lacuna real já classificada pode permanecer e não autoriza inserir uma hipótese.

## Relação com a avaliação completa

A auditoria literal é um filtro adversarial de correspondência. `$avaliar-curriculo` continua obrigatório depois dela e preserva sua função de revisar aderência, seleção de provas, qualidade humana, honestidade, omissões e estratégia.

A avaliação completa deve receber `auditoria-ats-literal.md` como insumo, mas pode discordar da leitura literal quando explicar claramente a diferença. Nenhum dos dois vereditos substitui a aprovação humana para criar o Word.
