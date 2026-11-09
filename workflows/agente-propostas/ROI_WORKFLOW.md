# ROI integrado ao controle local

Implementado em 02/11/2026. As novas sessões criadas por `workflow.agent_runtime` recebem as ferramentas de fontes e cálculo. A definição salva na plataforma e as sessões anteriores não são atualizadas automaticamente. Para testar esse ramo, use um identificador novo de proposta; não reutilize o teste sem ROI como se fosse uma proposta real.

## Sequência

1. O analista lê os dados e pesquisa somente as variáveis que precisam de referência externa. O orquestrador registra os extratos e as entradas com suas origens.
2. O analista entrega plano completo: método, alternativa sem projeto, moeda/base, tributos, calendário, hipóteses, entradas, cenários e fórmulas. O gateway valida as fórmulas sem executá-las e incorpora cópias das fontes vinculadas antes de calcular o hash do plano.
3. O orquestrador apresenta o plano integral, versão e hash e aguarda o humano. Nenhuma ferramenta de aprovação está disponível ao agente.
4. O operador registra a decisão pelo comando local `workflow.cli decisao-humana`, com objeto `plano_roi`, revisão e hash apresentados. Escrever “aprovado” no chat não registra essa decisão.
5. Depois de uma aprovação humana válida e avanço à produção, `workflow_calcular_roi` executa o plano. A chamada só aceita a revisão atual: não recebe novos números ou fórmulas. A memória registra plano/hash, ID da aprovação, fontes, entradas, hash do executor, precisão, fluxos e resultados por cenário.
6. O revisor confere a memória e as fontes. No ramo numérico, o relatório precisa incluir `verificacao_roi`, com hashes atuais do plano/cálculo, evidência de reprodução e conferência de cada fonte utilizada. O critério ROI não pode ser “Não se aplica”. O código valida a cobertura e os vínculos; a conferência semântica e a leitura da fonte original continuam sendo trabalho do revisor.
7. O texto integrado segue para revisão e aprovação humana textual. Mudança do plano invalida cálculo e resultados dependentes, além da aprovação afetada.

## Fontes

Mensagens humanas já têm IDs registrados pela aplicação. Para importar documentos textuais do cliente:

```sh
python3 -m workflow.sources --db dados/workflow.sqlite3 --proposta IDENTIFICADOR --arquivo /caminho/cliente.md --titulo 'Informações do cliente'
```

São aceitos `.txt`, `.md`, `.csv` e `.json` em UTF-8, até 2 MB. O conteúdo fica congelado no banco, com SHA-256; mudar ou remover o arquivo original não muda a fonte cadastrada. O agente consulta os IDs em `workflow_estado` e lê o conteúdo por `workflow_fonte_ler` com paginação de 12.000 caracteres. A importação de PDF/DOCX e sua extração ainda não estão conectadas.

Para pesquisa web, `workflow_fonte_web` recebe título, URL direta, entidade, datas de publicação/dados/acesso, localização, contexto/limitações, dado original e extrato consultado. Não faz uma nova requisição HTTP nem certifica que a página foi lida: preserva a declaração e o extrato do analista como `declarada_pelo_agente_pendente_revisor`. O revisor precisa abrir a fonte original e conferir sua aplicação. O ID do registro é derivado do conteúdo, e as fontes são isoladas por proposta. Nenhum conteúdo de fonte registra autorização humana.

Cada entrada do plano exige `id`, `valor` decimal em string, `unidade`, `natureza`, `fonte_id`, `localizacao` e `justificativa`. Naturezas: `dado_cliente`, `benchmark_adaptado` ou `hipotese_simulacao`. A justificativa descreve a adaptação e o vínculo entre operação e caixa; não transforma uma hipótese em dado confirmado. O plano congela todas as fontes referidas nas entradas.

## Motor disponível

`fluxo_caixa_mensal_v1` implementa o ROI simples de caixa incremental do guia: I0 no mês zero, benefícios e demais custos nos meses 1..H; ROI acumulado sem desconto, sem anualização. Usa `Decimal`, com 34 dígitos de precisão, e não arredonda os valores da memória para apresentação.

Suporta 1 a 120 meses, 1 a 12 cenários explícitos e até 100 variáveis. Cada cenário declara I0 e todos os meses, com fórmulas de benefícios/custos e justificativa do calendário. As fórmulas aceitam variáveis cadastradas, literais decimais, parênteses e operações `+ - * /`; não aceitam chamadas, atributos, índices, potências ou código livre. Variáveis e literais têm módulo entre 1e-18 e 1e18, ou zero; resultados intermediários têm limite de 1e30. Valores de custo e benefício calculados precisam ser não negativos.

Com investimento total zero, ROI percentual é `null`; os valores absolutos continuam disponíveis. Payback informa o primeiro mês de recuperação após saldo negativo, sinaliza recaída e distingue ausência de saldo negativo de falta de recuperação. Não usa fração de mês sem um modelo adicional.

Valor presente, análise de equilíbrio específica e outros métodos ainda não são executores disponíveis. Diante de método incompatível, lacuna ou fórmula inválida, o agente registra pendência e pede ajuste, sem substituir o método por conta própria. A revisão deve verificar unidades, ausência de dupla contagem e efeitos reais de caixa; a validação de sintaxe não prova essas propriedades econômicas.

## Reproduzir uma memória já calculada

Exporte o estado local depois de um cálculo aprovado e execute a conferência:

```sh
python3 -m workflow.cli ver IDENTIFICADOR > /tmp/estado_roi.json
python3 -m workflow.roi --estado /tmp/estado_roi.json
```

Esse comando verifica a aprovação registrada, recalcula a partir do plano exportado e compara cada campo de resultado com a memória. Não registra aprovação, não altera o banco e não substitui a conferência independente do revisor.

## Validação realizada

73 testes locais passaram: 51 anteriores e 22 novos. Os novos cobrem cálculo decimal, fluxo mensal, investimento zero, ROI negativo, payback e recaída, calendário completo, fórmulas proibidas, fonte desconhecida, ausência de aprovação, etapa correta, mudança de plano, tentativa de trocar números na chamada, divisão por zero sem alteração do estado, cobertura de revisão e fontes imutáveis.

As aprovações usadas pelos testes são simulações em bancos temporários, removidos ao final. Nenhuma aprovação real foi registrada nesta etapa. Não houve novo teste remoto nem pesquisa de benchmarks de um cliente; os dois testes remotos anteriores continuam documentados em `verificacao_sessao/integracao_workflow/`.
