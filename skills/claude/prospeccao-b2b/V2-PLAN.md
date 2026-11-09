# Plano da V2 — Prospecção B2B

## Objetivo

Evoluir a skill de um orquestrador que delega parte da qualificação à IA do
Apollo para um sistema em que o Apollo filtra e coleta evidências, enquanto a
skill canônica no Codex interpreta e classifica com o modelo mais potente.

Este arquivo acompanha a construção incremental da V2. As decisões centrais de
coleta no Apollo e raciocínio na skill já foram aplicadas ao comportamento ativo;
as demais frentes continuam em evolução.

## Decisões já fechadas

1. Tratar o Apollo como fonte de dados e pesquisa, não como árbitro de fit.
2. Compilar ICP, alto valor, desqualificadores e sinais observáveis uma vez por
   rodada dentro da skill.
3. Qualificar empresas antes de procurar pessoas.
4. Deduplicar pesquisa de empresa por domínio canônico.
5. Usar filtros, campos, sinais e enriquecimentos do Apollo como coleta de dados,
   mesmo quando consumirem créditos.
6. Usar AI Research somente para preencher uma lacuna factual capaz de mudar a
   decisão e que não possa ser coletada por recursos estruturados ou outra fonte
   adequada.
7. Pedir fatos, evidências, URLs e datas; não pedir `Qualified/Disqualified`.
8. Separar fit estrutural, timing, valor potencial e confiança.
9. Tratar ausência de evidência como incerteza, não como desqualificação.
10. Não calcular nem perguntar sobre créditos; o Apollo informa o consumo e o
    usuário decide antes da execução.
11. Revelar contato somente depois da classificação externa e do gate.
12. Distinguir o ICP do vendedor, o ICP atendido pela conta e o buyer map dentro
    da conta antes de usar qualquer um deles na qualificação.
13. Preservar campos brutos de empresa e pessoa até concluir a classificação;
    não substituir evidência por resumo profissional no output padrão.
14. Registrar data de corte, janela, data do evento e validade em todo sinal
    temporal; separar fato observado de impacto comercial inferido.
15. Tratar listas compactas geradas por IA como derivações, nunca como evidência;
    preservar fontes e classificar o tipo de relação antes de usar o resultado.
16. Sempre que recomendar AI Research, entregar uma coluna customizada pronta
    para criar: nome, objeto, momento, prompt, output e regra de uso.
17. Manter todo raciocínio comercial, qualificação e decisão na skill; o Apollo
    apenas coleta e estrutura as informações solicitadas.
18. Tratar o Apollo como candidato normal — inclusive principal — para descoberta
    no Brasil. Não preferir CNAE ou base cadastral sem testar qual dimensão
    representa melhor a atividade e sem evidência de cobertura.
19. Quando uma etapa exigir operar software fora do alcance disponível, entregar
    um prompt completo para Claude executar a interface, coletar os dados e
    devolver o resultado ao Codex.
20. Manter a skill exclusivamente no Codex; não instalar, sincronizar ou manter
    cópias no ChatGPT, Claude Cowork ou Claude Code.
21. Usar Claude como agente externo para navegação e, quando materialmente útil,
    pesquisa delimitada. Enviar prompt autocontido; receber fatos e fontes; manter
    estratégia, integração das evidências e qualificação no Codex.
22. Permitir sugerir o filtro Intenção de compra do Apollo com até 6 tópicos
    causalmente relevantes. Tratar High/Medium/Low como sinal relativo de timing,
    não como prova de fit, compra, urgência, orçamento ou decisor; manter confiança
    não calibrada até validação empírica.
23. Encerrar a missão na lista qualificada e pronta para handoff. Não escolher
    canal nem criar abordagem, mensagem, e-mail, copy, cadência, sequência ou
    campanha; esses artefatos pertencem ao workflow posterior.

## Referências incorporadas

- [x] `references/apollo-ai-research-custom-columns.md` — contrato central para
  desenhar colunas customizadas a partir das referências.
- [x] `references/apollo-ai-research-company-fit.md` — template de três etapas
  `Research and evaluate a company for fit`.
- [x] `references/apollo-ai-research-job-openings.md` — template
  `Identify relevant job openings`.
- [x] `references/apollo-ai-research-target-customer.md` — template
  `Identify who your target company sells to`.
- [x] `references/apollo-ai-research-contact-background.md` — template
  `Summarize contact's professional background`.
- [x] `references/apollo-ai-research-executive-changes.md` — template
  `Know if a company had executive changes`.
- [x] `references/apollo-ai-research-competitors.md` — template
  `Identify Competitors`.
- [x] `references/browser-handoff.md` — contratos para Claude navegar ou pesquisar
  como agente externo sem receber a skill.
- [x] `references/apollo-buying-intent.md` — interpretação, seleção de tópicos e
  calibração do filtro Intenção de compra.
- [x] Catálogo de referências fornecidas pelo usuário encerrado.

## Arquitetura-alvo

```text
Contexto do projeto + intake
→ critérios observáveis compilados pela skill
→ escolha da fonte de descoberta
→ filtros e dados existentes
→ classificação preliminar por empresa
→ intenção de compra como sinal opcional de timing/priorização
→ pesquisa factual apenas nas contas ambíguas
→ classificação final da empresa pela skill
→ busca de pessoas apenas nas contas aprovadas
→ classificação do papel de compra pela skill
→ prompt autocontido para Claude quando navegação ou pesquisa externa for útil
→ retorno de fatos e fontes ao Codex
→ gate de crédito
→ reveal da Tier autorizada
→ lista qualificada pronta para handoff
→ fim da skill; canal e execução ficam para o workflow posterior
```

## Frentes de trabalho

### 1. Catálogo de AI Research

- [x] Definir formato de referência por template.
- [x] Definir contrato obrigatório de coluna customizada.
- [x] Definir modos econômico, filtrável e auditável.
- [x] Registrar o primeiro template de fit de empresa.
- [x] Registrar o template de vagas como sinal factual de timing.
- [x] Registrar o template de mercado atendido e separar os três ICPs.
- [x] Registrar o template de resumo profissional como referência de campos
  brutos e anti-padrão para o output desta skill.
- [x] Registrar mudanças executivas como pesquisa factual temporal.
- [x] Registrar descoberta de concorrentes como candidatos a validar.
- [ ] Registrar templates factuais relevantes.
- [ ] Registrar templates de decisão que devem ser evitados.
- [ ] Mapear objeto de execução: conta ou pessoa.
- [ ] Mapear quantidade de campos e dependências entre eles.
- [ ] Mapear fonte usada: dados internos, site oficial ou web externa.
- [ ] Definir alternativa estruturada ou externa para cada template.

### 2. Aquisição de dados

- [x] Corrigir a premissa da V1 de que a IA do Apollo deve qualificar.
- [x] Permitir recursos pagos do Apollo quando forem úteis para coletar dados.
- [x] Proibir cálculo ou estimativa de créditos; o Apollo informa o consumo.
- [x] Remover a preferência automática por CNAE/base cadastral no Brasil.
- [x] Exigir evidência de cobertura ou precisão antes de tirar o Apollo da
  descoberta principal.
- [x] Incorporar Intenção de compra como filtro estruturado opcional, separado de
  AI Research.
- [ ] Calibrar cobertura e poder preditivo de High/Medium/Low por tópico.
- [ ] Criar uma árvore de decisão: filtro/campo/sinal/enriquecimento, outra fonte,
  AI Research factual ou reveal.
- [ ] Definir calibração por preview e casos ambíguos antes de ampliar AI Research.

### 3. Contrato de evidência

- [ ] Definir esquema mínimo para fatos, URL, data, identidade e ausência de
  evidência.
- [ ] Distinguir fonte primária, fonte pública externa e campo do Apollo.
- [ ] Proibir inferência de autoridade, orçamento ou dor sem evidência.
- [ ] Definir quando encerrar pesquisa e quando pedir uma segunda fonte.
- [ ] Incluir data de corte, início/fim da janela, anúncio, vigência e expiração
  para sinais temporais.
- [ ] Definir hierarquia de fontes e cobertura mínima para achados negativos.
- [ ] Preservar evidência anterior a outputs compactos como listas e labels.

### 4. Qualificação de empresas

- [ ] Substituir o julgamento do Filtro de IA por classificação na skill.
- [ ] Separar baseline, desqualificadores, alto valor, timing e confiança.
- [ ] Criar estado `Needs Evidence` para casos ambíguos.
- [ ] Rever a rubrica A/B/C atual para não misturar empresa e pessoa cedo demais.
- [ ] Definir deduplicação por domínio e tratamento de grupos, filiais e marcas.
- [ ] Incorporar vagas como timing separado de fit estrutural.
- [ ] Distinguir sem vaga relevante, sem vaga encontrada e dados insuficientes.
- [ ] Definir quando o ICP atendido pela conta é critério direto, secundário,
  contextual ou irrelevante para nossa tese comercial.
- [ ] Separar cliente pagante, usuário, beneficiário, parceiro e canal.
- [ ] Incorporar mudança de liderança como timing dependente da função e da
  tese, nunca como fit automático.
- [x] Incorporar Intenção de compra como timing experimental, nunca como
  desqualificador isolado.
- [ ] Definir quando concorrência é critério direto, secundário, contextual ou
  irrelevante para a tese de prospecção.
- [ ] Separar concorrente direto, parcial, indireto, substituto, adjacente,
  parceiro, menção e caso incerto.

### 5. Qualificação de pessoas

- [ ] Trocar `Confirm decision-maker` por coleta de evidência de escopo da função.
- [ ] Mapear decisor econômico, dono funcional, avaliador técnico, champion,
  compras, usuário e função irrelevante.
- [ ] Tornar regras de senioridade dependentes do ticket e do processo de compra.
- [ ] Classificar pessoas fora do Apollo.
- [ ] Definir os campos brutos mínimos de pessoa e preservar rastreabilidade.
- [ ] Separar dados ausentes, acesso bloqueado, identidade ambígua, conflito e
  informação desatualizada.
- [x] Excluir resumo profissional, preparação, CRM e personalização do output
  padrão; manter apenas campos brutos e classificação necessários à lista.

### 6. Fluxos e outputs

- [x] Atualizar os modos A e B com a divisão entre coleta no Apollo e
  qualificação na skill.
- [ ] Incluir instruções para exportar ou fornecer os campos necessários sem
  revelar contatos prematuramente.
- [x] Atualizar o handoff de fonte externa para permitir que o Apollo complemente
  empresas, sinais e pessoas.
- [x] Criar handoff obrigatório com prompt completo para IA de navegador quando
  uma etapa depender de software fora do alcance.
- [x] Acrescentar handoff de pesquisa para Claude com contrato factual e integração
  do retorno no Codex.
- [x] Definir o Codex como única instalação e fonte canônica da skill.
- [x] Definir o contrato mínimo da lista qualificada e manter a escolha do canal
  como decisão downstream.
- [x] Proibir abordagem, mensagem, e-mail, copy, cadência, sequência e campanha
  como outputs desta skill.
- [ ] Adicionar ao modo B a seção `Coluna customizada de AI Research` com nome,
  prompt pronto, tipo de campo, valores e regra de uso.
- [ ] Permitir múltiplas colunas apenas com dependência explícita.

### 7. Implementação e validação

- [x] Consolidar a divisão entre coleta e raciocínio no `SKILL.md`.
- [x] Atualizar `references/apollo-filtros.md` para impedir veredito pelo Apollo.
- [ ] Atualizar `references/qualificacao.md`.
- [x] Verificar e atualizar `agents/openai.yaml` para refletir coleta no Apollo e
  raciocínio na skill.
- [x] Executar o validador estrutural da skill após as mudanças.
- [ ] Testar cenários com boa e má cobertura do Apollo.
- [ ] Testar múltiplos contatos da mesma empresa para confirmar deduplicação.
- [ ] Testar quando AI Research é realmente necessário e quando um campo ou
  filtro estruturado basta.

## Critérios de conclusão da V2

- A skill nunca delega o veredito de fit ao Apollo.
- Todo AI Research responde a uma lacuna explícita que pode mudar uma decisão e
  não pôde ser coletada por outro recurso adequado.
- Pesquisa de conta acontece no máximo uma vez por domínio por rodada, salvo
  justificativa registrada.
- A saída separa fatos, inferências, incertezas e decisão.
- A skill não calcula créditos; o Apollo apresenta o consumo ao usuário.
- O Apollo não é excluído da descoberta por o mercado ser brasileiro ou por
  existir uma base de CNAE; a troca exige evidência de inadequação.
- Contatos só são revelados depois do gate de empresa e pessoa.
- Casos sem evidência suficiente não são descartados nem aprovados por intuição.
- Toda recomendação de AI Research inclui uma especificação pronta para colar no
  Apollo, não apenas uma sugestão abstrata de usar IA.
- O Apollo nunca recebe o veredito comercial como tarefa; coleta fatos para a
  skill raciocinar e decidir.
- Intenção de compra pode priorizar contas, mas não altera fit ou Tier sozinha;
  sua confiança permanece não calibrada até teste por tópico e nível.
- Toda etapa que dependa de software inacessível inclui um prompt copiável para
  uma IA de navegador, com objetivo, configuração, saída e guardrails.
- A skill existe e é mantida somente no Codex; Claude recebe apenas prompts
  autocontidos de navegação ou pesquisa.
- Resultados de Claude retornam como fatos e fontes; fit, timing, papel de compra,
  confiança e Tier são calculados no Codex.
- O output terminal é uma lista qualificada, deduplicada, evidenciada e pronta
  para handoff, com contas, pessoas, prioridade, confiança, lacunas e prontidão
  de contato.
- O canal permanece não selecionado e é decidido no workflow posterior.
- A skill não produz abordagem, mensagem, e-mail, copy, cadência, sequência ou
  campanha.

## Próximo passo

Consolidar a lógica de qualificação de empresas e pessoas, atualizar a rubrica e
testar os fluxos completos com Apollo como fonte principal e complementar.
