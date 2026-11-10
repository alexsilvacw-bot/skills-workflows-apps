# Rubrica de qualificação A/B/C

Objetivo: separar os resultados da busca (de graça) ANTES de gastar crédito de
enrich. A busca já devolve cargo, empresa, setor, tamanho e local, que bastam
pra pontuar.

Pontue cada lead em 4 critérios. Cada um vale 0, 1 ou 2.

1. **Fit de cargo/decisão** — a pessoa decide ou influencia a compra do produto?
   - 2: decisor direto (dono, diretor, gerente da área que compra).
   - 1: influenciador (técnico, usuário, quem recomenda).
   - 0: cargo sem relação com a compra.

2. **Fit de segmento** — a empresa é de um segmento priorizado do ICP?
   - 2: segmento alvo da rodada.
   - 1: segmento adjacente (compra possível, não óbvia).
   - 0: fora do ICP.

3. **Fit de porte/geografia** — tamanho e local batem com a estratégia?
   - 2: bate nos dois.
   - 1: bate em um.
   - 0: não bate.

4. **Sinal de timing** — há indício de momento de compra (vaga aberta ligada ao
   produto, captação recente, expansão, troca de fornecedor)?
   - 2: sinal claro e recente.
   - 1: sinal fraco/indireto.
   - 0: nenhum sinal.

## Faixas

- **A (6 a 8 pontos)** — enriquecer. Melhor uso do crédito.
- **B (4 a 5 pontos)** — enriquecer se sobrar crédito/orçamento da rodada.
- **C (0 a 3 pontos)** — descartar. Não gastar crédito.

## Como entregar

Devolva ao usuário a contagem por faixa, uma amostra dos A com o motivo do score
e quais Tiers estão prontas para o gate. Não calcular custo: o Apollo informa o
consumo antes da execução. Nunca enriqueça C. Deixe o usuário decidir sobre os B.

Se quase tudo cair em C, o problema é o filtro, não os leads. Refaça a pontaria
do stack de filtros (ver segmentacao-icp.md) em vez de baixar a régua.
