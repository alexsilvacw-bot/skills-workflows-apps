# Agente Proposta Comercial — pacote de instruções 1.2

Preparado em 02/11/2026 a partir dos três guias fornecidos por Alex. O projeto contém instruções, contratos, controle local em SQLite e runtime da Agents API. O pacote v1.2 foi conferido (15/15 hashes). O fluxo de conteúdo está conectado ao banco e foi testado com redator e revisor nativos até a espera de aprovação textual, com zero aprovações registradas no teste. Há 98 testes locais aprovados. Fluxo PDF, importação de recursos, renderização, revisão final e entrega local estão conectados; veja `DOCUMENTO_WORKFLOW.md`. Fontes textuais/web e cálculo mensal de ROI após aprovação humana estão integrados e testados localmente; detalhes em `ROI_WORKFLOW.md`. Consulte `INTEGRACAO_AGENTES.md` para execução e canal humano, `WORKFLOW_LOCAL.md` para o núcleo e `PROGRESSO.md` para retomada.

## Arquivos para a plataforma

Cada arquivo abaixo contém regras comuns **e** instruções específicas. Use o conteúdo completo do arquivo correspondente, uma única vez, no campo de instruções do respectivo papel. Não cole apenas as fontes específicas nem concatene novamente as regras comuns.

| Nome sugerido | Arquivo completo |
|---|---|
| Propostas — Orquestrador | `instrucoes/prontas_para_plataforma/01_orquestrador.md` |
| Propostas — Redator | `instrucoes/prontas_para_plataforma/02_redator.md` |
| Propostas — Analista de ROI | `instrucoes/prontas_para_plataforma/03_analista_roi.md` |
| Propostas — Designer | `instrucoes/prontas_para_plataforma/04_designer.md` |
| Propostas — Revisor | `instrucoes/prontas_para_plataforma/05_revisor.md` |

São cinco configurações de papel. A forma de associar os especialistas ao orquestrador será definida na integração com as capacidades efetivamente disponíveis; salvar instruções não estabelece a delegação automaticamente. Modelos, ferramentas, ambiente, interface e formato de saída ainda não foram fixados por este pacote.

## Referências necessárias

`referencias/` contém cópias integrais, sem alteração do conteúdo:

| Referência | Original consultado | Identificação |
|---|---|---|
| Boas práticas B2B | `/Users/alex/Documents/Codex/2026-11-02/vamo/outputs/guia_propostas_comerciais_b2b.md` | v1.0, 02/11/2026 |
| Construção do agente | `/Users/alex/Documents/Codex/2026-11-02/quero-criar-um-agente-via-api/outputs/guia_construcao_agente_propostas_comerciais.md` | v1.0, 02/11/2026 |
| ROI | `/Users/alex/Documents/Codex/2026-11-02/cri/outputs/guia_agente_roi_propostas_comerciais.md` | Sem versão explícita; cópia identificada pelo SHA-256 no manifesto |

Boas práticas e construção devem estar acessíveis a todos os papéis. O guia de ROI é necessário ao analista e também ao orquestrador e revisor nas tarefas relacionadas; redator e designer recebem os resultados e as orientações pertinentes à sua tarefa. Os guias completos continuam sendo a referência de critérios, não somente os resumos nos prompts.

Os caminhos nas instruções são nomes relativos do pacote. Ao preparar o ambiente remoto, será necessário disponibilizar os arquivos e informar sua localização real aos agentes. Escrever um caminho local nas instruções não envia seu conteúdo à API. O pacote v1.2 já foi enviado e teve sua integridade conferida na sessão.

## Edição e montagem

Edite `instrucoes/fontes/00_regras_comuns.md` para regras compartilhadas ou o arquivo específico do papel. Depois execute, sem necessidade de chave:

```sh
python3 /Users/alex/Documents/11_IA/agente_proposta_comercial/scripts/montar_instrucoes.py
```

O script monta os cinco arquivos completos e atualiza `manifesto.json` com hashes de instruções, referências e contrato. As cópias dos guias não são atualizadas automaticamente: uma mudança de referência exige leitura, revisão de impacto e nova identificação do pacote. Não inclua chaves neste diretório.

## Integração seguinte

Na versão 1.2, todos os papéis verificam a disponibilidade de `rg` antes do uso e recorrem a `find`, `grep` ou Python quando necessário, sem repetir tentativas de comandos ausentes. A regra também distingue busca sem resultados de erro de execução. O pacote local atualizado é `pacote_sessao_v1.2.zip`; sua criação não atualiza automaticamente o agente salvo ou uma sessão já aberta na plataforma.

Na versão 1.1, o analista de ROI passa a ter responsabilidade explícita pela pesquisa web de benchmarks e informações de mercado durante a preparação do plano. O orquestrador coordena as lacunas, apresenta referências e premissas para aprovação e mantém o registro; o revisor confere fontes, comparabilidade e a sequência entre referência, adaptação, premissa aprovada e cálculo. A integração deverá disponibilizar busca e leitura web ao analista e meios de acesso às fontes ao revisor. As instruções não habilitam essas ferramentas por si só. Mudanças materiais após aprovação exigem renovar a aprovação afetada antes de recalcular.

O contrato em `contratos/delegacao_e_registros.md` especifica entradas, retornos, registros e condições que o código deverá validar. É uma proposta de organização da aplicação, não esquema oficial da API. O limite de tentativas continua configurável e sem número aprovado; acabamento visual não ganha aprovação humana obrigatória; estrutura não exige aprovação humana padrão.

Na plataforma, Alex executa as configurações no projeto **Agente Proposta Comercial**. Orquestrador, template, sessão original e sessão integrada estão identificados em `configuracao_plataforma.json`. O runtime fornece as ferramentas locais à sessão da aplicação. Aprovações são registradas pelo operador local, fora das ferramentas disponíveis ao modelo.

## Verificação desta etapa

Conferência documental: composição das instruções e hashes do manifesto. Conferência remota inicial: leitura pelo orquestrador e 15/15 hashes. Validação local: 98 testes do núcleo, gateway, runtime e ROI/fontes. Dois testes reais na API comprovaram persistência, recusa de avanço de briefing incompleto e fluxo sem ROI com redação/revisão delegadas até `aprovacao_textual`, sem aprovações. Cálculo mensal e fontes textuais/web foram integrados depois desses testes remotos e validados localmente. A produção PDF foi conectada por artefatos publicados, renderização e revisão final vinculada a versões, com validação local. O caminho principal de ROI/PDF foi depois executado na API até concluida, revisão 25, com aprovações humanas do plano e texto; produção/revisão PDF em Luna. Relatório em `verificacao_sessao/aceitacao_roi_pdf/CONCLUSAO.md`. Permanecem os demais casos de aceitação e a extração de fontes PDF/DOCX. Os casos de aceitação completos estão na seção 13 do guia de construção.
