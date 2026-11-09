# Intenção de compra do Apollo

Referência fornecida pelo usuário em 18 de julho de 2026. Usar para decidir se o
filtro agrega timing ou priorização. A eficácia prática da feature ainda não foi
validada nesta operação; manter confiança `não calibrada` até teste real.

## Conteúdo

- O que a feature informa
- Interpretação correta
- Quando sugerir
- Como escolher até 6 tópicos
- Uso recomendado dos níveis
- Saída obrigatória
- Calibração da confiabilidade

## O que a feature informa

O usuário pode selecionar até 6 tópicos entre mais de 200 temas. O Apollo mede,
no nível da empresa, o volume e a frequência com que pessoas daquela organização
consomem conteúdo relacionado ao tópico e compara o comportamento com a baseline
histórica da própria empresa.

- **High:** consumo muito acima da baseline histórica;
- **Medium:** consumo moderadamente acima da baseline;
- **Low:** consumo levemente acima da baseline.

O score considera:

- quantidade de páginas consumidas sobre o tema;
- frequência das visitas;
- diversidade de fontes consultadas;
- comparação com o histórico da própria empresa.

Os dados são atualizados semanalmente e pertencem à conta, não a uma pessoa. O
período exato de observação deve ser confirmado na interface quando relevante;
não inventar uma janela.

## Interpretação correta

O nível mede uma **mudança relativa de consumo**, não propensão absoluta de compra.
Portanto:

- `High` pode reforçar timing, mas não prova projeto, orçamento ou urgência;
- `Medium` pode indicar interesse crescente, sem confirmar necessidade;
- `Low` pode representar exploração inicial ou monitoramento;
- ausência de sinal pode significar falta de atividade, cobertura insuficiente ou
  tópico mal escolhido;
- o sinal não identifica qual pessoa pesquisou nem confirma o decisor;
- empresas com baseline historicamente baixa podem se comportar de modo diferente
  de empresas que pesquisam o tema continuamente.

Não usar intenção como baseline de ICP nem como desqualificador isolado. Primeiro
confirmar fit estrutural; depois usar intenção para ordenar contas semelhantes.

## Quando sugerir

Sugerir quando:

- existir tópico do Apollo causalmente próximo à dor, solução, tecnologia ou
  iniciativa que antecede a compra;
- a rodada precisar separar `fit` de `fit + possível timing`;
- houver volume suficiente de contas para comparar níveis;
- o usuário puder acompanhar resultados por nível e tópico;
- o sinal puder mudar prioridade, Tier de timing ou ordem da lista.

Não sugerir quando:

- os tópicos disponíveis forem amplos ou apenas tangenciais;
- o mercado quase não produz consumo digital observável sobre o tema;
- a rodada for pequena e já possuir sinais diretos mais fortes;
- o resultado não mudar nenhuma decisão;
- a intenção estiver sendo usada para substituir fit estrutural.

## Como escolher até 6 tópicos

Partir do mecanismo de compra, não apenas do nome do produto:

1. listar dores e iniciativas que fazem a empresa buscar uma solução;
2. mapear tecnologias, processos, regulações ou eventos causalmente próximos;
3. localizar os tópicos equivalentes disponíveis no Apollo;
4. priorizar tópicos específicos com linguagem usada pelo comprador;
5. evitar sinônimos redundantes que medem praticamente o mesmo comportamento;
6. limitar aos tópicos cuja presença mudaria uma ação comercial.

Classificar cada tópico proposto:

- **Direto:** descreve a solução ou categoria comprada;
- **Problema:** descreve a dor que leva à compra;
- **Iniciativa:** descreve projeto que cria necessidade;
- **Tecnologia:** indica stack ou mudança associada;
- **Adjacente:** relação plausível, mas fraca; usar apenas para teste.

Não preencher seis vagas artificialmente. Um ou dois tópicos fortes são melhores
que seis temas vagos.

## Uso recomendado dos níveis

Até a calibração:

- `High`: aumentar prioridade de timing e pedir validação por outro sinal;
- `Medium`: manter no grupo ativo e procurar confirmação;
- `Low`: monitorar ou manter em prioridade inferior;
- sem sinal: preservar a classificação de fit e marcar timing desconhecido.

O nível não altera sozinho `Disqualified`, `Possible Fit` ou `High Value Fit`.
A skill combina intenção com fit estrutural, vaga, expansão, liderança,
tecnologia, notícia e demais evidências.

## Saída obrigatória quando recomendar o filtro

```text
INTENÇÃO DE COMPRA DO APOLLO

Por que usar:
Decisão que o sinal pode mudar:
Confiança atual: não calibrada | baixa | média | alta

Tópicos sugeridos, até 6:
1. [tópico] — [direto | problema | iniciativa | tecnologia | adjacente]
   Relação causal: [explicação curta]

Níveis a incluir:
- [High | Medium | Low]

Uso na qualificação:
- [como altera timing ou prioridade]

Não usar para:
- [fit, desqualificação, decisor, orçamento ou urgência sem confirmação]

Plano de validação:
- [amostra, comparação e métrica]
```

Se os nomes exatos dos tópicos disponíveis não forem conhecidos, não inventar.
Entregar conceitos de tópicos para localizar na interface. Se o Codex não puder
operar a interface, gerar o prompt de Claude navegador conforme
`browser-handoff.md`.

## Calibração da confiabilidade

Começar como experimento:

1. selecionar contas conhecidas com e sem pesquisa ativa real;
2. verificar cobertura e níveis nos tópicos escolhidos;
3. revisar uma amostra de `High`, `Medium`, `Low` e sem sinal;
4. comparar com sinais externos observáveis;
5. acompanhar por tópico e nível: resposta positiva, reunião, oportunidade e
   falso positivo;
6. promover o sinal de experimental para confiável somente após padrão consistente.

Não exigir cálculo de créditos. O Apollo informará o consumo ou requisito de plano.

## Princípio transferível

Intenção de compra é um termômetro relativo de pesquisa da conta. Apollo coleta o
nível; o Codex avalia validade, combina com outras evidências e decide prioridade.
