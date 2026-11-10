# Handoff para Claude: navegador e pesquisa

Usar Claude somente como agente externo da skill canônica do Codex. Não instalar,
copiar nem sincronizar a skill no Claude. Entregar um prompt autocontido para uma
tarefa de navegação ou pesquisa e trazer o resultado de volta ao Codex.

## Conteúdo

- Quando usar Claude
- Contrato comum
- Template de navegação
- Exemplo de navegação: Receita via BigQuery
- Template de pesquisa
- Integração do retorno no Codex

## Quando usar Claude

### Navegação

- executar consulta no Google Cloud/BigQuery ou em base cadastral;
- configurar busca, lista, filtro, enriquecimento ou coluna no Apollo;
- operar portal autenticado, diretório, CRM ou ferramenta comercial;
- exportar dados necessários para a skill qualificar;
- realizar qualquer etapa de interface que a skill não consiga executar.

### Pesquisa

- acessar fontes ou páginas que o Codex não consegue alcançar adequadamente;
- navegar por interfaces autenticadas ou conteúdo dependente de interação;
- executar coleta extensa e bem delimitada em múltiplas fontes;
- fazer uma segunda apuração independente quando ela aumentar materialmente a
  confiança de uma decisão relevante;
- pesquisar um lote de empresas com o mesmo contrato factual.

Não criar handoff apenas por preferência de modelo. Se o Codex puder concluir a
tarefa com evidência suficiente, continuar no Codex. Se houver mais de uma etapa,
mostrar a ordem de dependência.

## Contrato comum

O prompt deve conter:

1. papel de Claude como executor externo;
2. objetivo e resultado comercial da etapa;
3. software e URL inicial, se conhecida;
4. contexto mínimo do ICP e da busca;
5. entradas fornecidas pelo usuário;
6. sequência operacional clara;
7. consulta, filtros, valores ou configuração prontos;
8. validações durante a execução;
9. formato exato da saída ou exportação;
10. critério de sucesso;
11. ações que exigem confirmação do usuário.

Não pedir a Claude que redesenhe a estratégia, calcule fit, escolha Tier ou
qualifique leads. Ele opera a interface ou pesquisa, coleta fatos e devolve
evidências para o Codex raciocinar.

## Template de navegação

```text
Você é Claude operando como agente de navegador na interface do usuário. Você
recebeu uma tarefa delimitada pelo Codex; não altere a estratégia comercial.

OBJETIVO
[Resultado operacional específico que precisa ser concluído.]

CONTEXTO
- Empresa representada: [nome e oferta relevante]
- ICP/segmento: [definição curta]
- Decisão posterior: [como os dados serão usados pela skill]

SOFTWARE
- Ferramenta: [nome]
- URL inicial: [URL, se conhecida]
- Conta/projeto/dataset: [identificador, se fornecido]

ENTRADAS
[Lista de arquivos, domínios, códigos, filtros, datas, regiões e demais valores.]

TAREFA
1. Abra a ferramenta e confirme que está na conta/projeto corretos.
2. [Passo operacional específico.]
3. [Aplicar consulta, filtros ou configuração fornecida abaixo.]
4. Valide uma amostra antes de executar ou exportar o conjunto completo.
5. Entregue o resultado no formato solicitado.

CONSULTA OU CONFIGURAÇÃO
"""
[SQL pronto, filtros exatos, definição da coluna ou configuração.]
"""

VALIDAÇÕES
- Não altere o objetivo, o ICP ou os critérios.
- Confirme identidade, projeto, dataset, período e geografia quando aplicável.
- Registre avisos, campos ausentes, erros e limitações de cobertura.
- Não trate ausência de resultado como prova de inexistência.

SAÍDA ESPERADA
- Formato: [CSV | planilha | texto | lista | configuração salva]
- Campos: [nomes e ordem]
- Destino: [download, tela, pasta ou retorno no chat]
- Inclua: total encontrado, total exportado e limitações observadas.

CRITÉRIO DE SUCESSO
[Condição objetiva que indica conclusão.]

GUARDRAILS
- Pode navegar, preencher campos, executar consultas somente leitura e preparar
  configurações dentro do objetivo acima.
- Pare e peça confirmação antes de compra, consumo explicitamente confirmado na
  interface, exclusão, sobrescrita, publicação, envio externo, alteração de
  permissões ou qualquer ação irreversível.
- Nunca solicite que o usuário revele senha, token ou segredo no chat. Use a
  sessão autenticada existente; se houver bloqueio de acesso, informe-o.
- Se a interface divergir destas instruções, não improvise uma ação material:
  descreva a diferença e peça orientação.

RELATÓRIO FINAL
Informe o que foi executado, onde o resultado ficou disponível, totais, avisos e
qualquer etapa que ainda dependa do usuário.
```

## Exemplo de navegação: Receita via BigQuery

Para consulta cadastral, preencher o template com:

- projeto e região corretos;
- dataset/tabelas confirmados na interface, sem inventar nomes;
- SQL somente leitura preparado pela skill;
- campos de empresa necessários para a rodada;
- preview/amostra para validar esquema e resultados;
- exportação sem contatos pessoais desnecessários;
- retorno dos campos brutos para qualificação na skill.

Se o esquema real for diferente do esperado, instruir a IA a inspecionar metadados
e relatar as diferenças antes de adaptar a query. Não autorizar criação de recurso,
mudança de permissão ou consulta materialmente diferente sem confirmação.

## Template de pesquisa

```text
Você é Claude atuando como pesquisador externo para uma estratégia de prospecção
coordenada pelo Codex. Sua função é coletar e documentar evidências; não qualificar
leads nem emitir o veredito comercial final.

OBJETIVO DA PESQUISA
[Pergunta factual e delimitada.]

CONTEXTO NECESSÁRIO
- Empresa representada: [nome e oferta relevante]
- Objeto pesquisado: [empresa, pessoa, mercado, evento ou tecnologia]
- Identidade: [nome, domínio, localização e outros identificadores]
- Janela temporal: [quando aplicável]
- Decisão posterior no Codex: [qual decisão os fatos informarão]

ESCOPO
- Fontes prioritárias: [site oficial, registros públicos, imprensa, diretórios etc.]
- Fontes permitidas: [lista]
- Fontes proibidas ou fora do escopo: [lista]
- Limite de objetos/páginas/tempo: [limite operacional]

PERGUNTAS FACTUAIS
1. [Pergunta observável.]
2. [Pergunta observável.]
3. [Pergunta observável.]

REGRAS DE EVIDÊNCIA
- Confirme a identidade antes de usar uma fonte.
- Ligue cada afirmação importante à URL, título da fonte e data.
- Prefira fonte primária; use fonte secundária para complementar ou confirmar.
- Separe fato observado de inferência.
- Não preencha lacunas por plausibilidade.
- Distinga: encontrado, não encontrado nas fontes consultadas, indisponível,
  ambíguo e conflitante.
- Para achados negativos, informe quais fontes foram verificadas.

FORMATO DE SAÍDA
Para cada objeto:
- identity_status:
- facts:
  - claim:
  - evidence_excerpt:
  - source_title:
  - source_url:
  - source_date:
- conflicts:
- missing_or_blocked:
- sources_checked:
- coverage_assessment:

CRITÉRIO DE SUCESSO
[Cobertura e evidência mínimas para encerrar.]

LIMITES
- Não classifique como Qualified, Disqualified, High Value ou Tier.
- Não identifique decision maker apenas pelo título.
- Não envie mensagens, altere sistemas ou revele contatos.
- Se a pesquisa exigir sair do escopo, pare e explique o que falta.

RELATÓRIO FINAL
Entregue os fatos estruturados, fontes, conflitos, lacunas e limitações. O Codex
fará a interpretação e a decisão comercial.
```

## Integração do retorno no Codex

Ao receber o resultado de Claude:

1. validar identidade e rastreabilidade;
2. separar fatos de inferências produzidas por Claude;
3. tratar ausência conforme a cobertura declarada;
4. confrontar conflitos com os critérios da rodada;
5. calcular fit, timing, papel de compra, confiança e Tier no Codex;
6. pedir complemento direcionado somente se uma lacuna puder mudar a decisão.

## Princípio transferível

A skill decide o que precisa ser feito e prepara a configuração. Claude navega ou
pesquisa e coleta o resultado. O Codex mantém a fonte canônica da skill,
integra as evidências e faz a qualificação.
