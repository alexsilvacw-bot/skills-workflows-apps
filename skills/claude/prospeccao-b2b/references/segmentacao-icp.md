# Definir ICP e traduzir em stack de filtros

Como sair de "quero vender pra empresas assim" e chegar num conjunto de filtros
do Apollo que corta lead ruim de graça. Tudo aqui é método genérico, calibro com
as respostas do intake.

## Separe sempre (padrão sabe / assume / valida)

Ao montar a segmentação, deixe explícito:

- **o que sabemos** (dado dito pelo usuário ou retornado pelo Apollo).
- **o que assumimos** (proxies e atalhos, ex.: usar porte de funcionários como
  proxy de tamanho de operação).
- **o que validar** (cobertura do Apollo no segmento, cargos ambíguos, se o
  decisor real é mesmo aquele).
- **próxima ação** (revelar faixa A, alargar geografia, criar sinal customizado).

Vender suposição como fato é o jeito mais rápido de queimar crédito.

## As duas metades do ICP

Um ICP útil tem perfil de **empresa** e perfil de **pessoa**. Filtrar só um lado
traz lixo.

### Empresa (firmografia + contexto)
- Atividade-fim: setor + SIC/NAICS (mais preciso que palavra-chave).
- Porte: faixa de funcionários e/ou faturamento compatível com o ticket.
- Geografia: onde você atende/dá suporte.
- Modelo: B2B, B2C, canal. Use segmentos de mercado quando fizer sentido.
- Maturidade/momento: ano de fundação, captação, crescimento de headcount.

### Pessoa (quem decide)
- Cargo + senioridade combinados (nunca um só).
- Área certa (a decisão pode estar em operações, técnica, compras, não no C-level).
- Localização da pessoa, se diferente da sede importa.

## Ordem de aplicação dos filtros (do mais barato/forte pro mais fino)

1. Geografia + setor/SIC-NAICS + porte. Funil grosso e gratuito.
2. Cargo + senioridade. Chega na pessoa certa.
3. Sinais de timing (vaga, intenção, crescimento). Adiciona "agora".
4. Listas/Etapa de CRM. Remove cliente atual e já-prospectado.
5. Camada de julgamento. O que o filtro não vê.
6. Portão de qualificação. Revelar só A/B.

## Template de tradução

- Localização da conta: `[geografia autorizada]`
- Porte: `[faixa compatível com ticket e operação]`
- Atividade/modelo: `[setor, código, keyword ou sinal com melhor cobertura]`
- Cargo: `[títulos ligados ao papel de compra]`
- Senioridade: `[níveis compatíveis com ticket e processo]`
- Sinal de timing: `[evento observável e janela temporal]`
- Julgamento: `[fato não coberto pelos filtros]`
- Desqualificar: `[critério explícito do contexto atual]`

Preencher o template somente com o intake e as evidências do projeto atual.

## Quando o Apollo cobre mal

Negócio pequeno, informal ou pessoa física costuma ter cobertura fraca. Nesses
casos, sugira mirar num alvo adjacente com mais pegada digital (ex.: o
distribuidor/canal em vez do usuário final, ou a associação/entidade do setor) e
avise o usuário em vez de prometer volume que não existe.
