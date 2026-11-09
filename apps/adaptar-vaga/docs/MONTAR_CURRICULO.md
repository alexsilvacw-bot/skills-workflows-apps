# Montagem do currículo

O script `montar_curriculo.py` recebe o JSON reescrito aprovado e gera um DOCX novo usando `TEMPLATE_CV.docx`. Não chama API, não faz matching, não traduz e não decide a redação. O conteúdo final de cada experiência e cargo deve chegar no idioma do currículo. A base vigente é `base/curriculo_base.json`.

Execute com o Python que contém lxml, disponível no runtime do Codex:

```bash
/Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 "/Users/alex/Documents/Adaptar Vaga/scripts/montar_curriculo.py" \
  --entrada "/Users/alex/Documents/Adaptar Vaga/candidaturas/empresa_cargo/dados-reescritos.json" \
  --saida "/Users/alex/Documents/Adaptar Vaga/candidaturas/empresa_cargo/alex-floriano-curriculo.docx"
```

A aprovação deve estar registrada como `aprovado_por_usuario: true`, ou ser informada com `--aprovado` depois da revisão humana. Para substituir um DOCX existente, use `--sobrescrever`. O template nunca pode ser sobrescrito. Existem também `--config`, `--base` e `--template` para selecionar entradas explicitamente.

## Contrato do JSON reescrito

Este exemplo é ilustrativo. Substitua os IDs pelos IDs reais da base e inclua todos os vínculos obrigatórios. Os textos deste exemplo não constituem currículo aprovado.

```json
{
  "aprovado_por_usuario": true,
  "idioma_cv": "en",
  "cargo_alvo": "Business Manager",
  "resumo_profissional": "Texto final do resumo aprovado em inglês.",
  "competencias": ["Lista de 10 competências extraídas da vaga"],
  "ferramentas": ["Lista de 5 a 10 ferramentas extraídas da vaga"],
  "vinculos": [
    {
      "empresa_id": "EMP_ID_REAL_DA_BASE",
      "cargo": "Sales and Marketing Manager",
      "experiencias": [
        {
          "id": "EXP_ID_REAL_DA_BASE",
          "texto": "Texto final da experiência aprovado em inglês."
        }
      ]
    },
    {
      "empresa_id": "EMP_OUTRO_ID_REAL_DA_BASE",
      "cargo": "Marketing Manager",
      "experiencias": []
    }
  ]
}
```

Cada `empresa_id` deve aparecer uma vez. O nome da empresa é recuperado da base; o cargo é o texto final aprovado, já traduzido. Cada experiência aponta para um ID pertencente à empresa, enquanto `texto` guarda sua versão final aprovada. A lista de experiências mantém a ordem de seleção recebida. Não envie propostas ainda sem aprovação nessa lista. Hipóteses aprovadas sem ID devem primeiro receber uma referência persistente na base; o montador não cria fatos ou IDs.

Todos os vínculos da base devem estar presentes, exceto Skywalker e Consultoria, que são opcionais. Um vínculo com `experiencias: []` vai para Experiências anteriores. Eavision permanece em primeiro lugar na seção profissional, mesmo sem bullets. Empresas não são duplicadas entre seções.

As datas confirmadas da base prevalecem. Para vínculos ainda sem datas na base, pode-se fornecer `periodo` com `entrada: "YYYY-MM"`, `saida: "YYYY-MM"` ou `null` e `atual: true/false`, após revisão humana. Datas desconhecidas são omitidas e informadas como pendência no terminal. Datas de entrada posteriores à saída são informadas como pendência, sem alterar os valores aprovados.

## Regras executadas

- Ordem das seções lida da configuração. IA após resumo e competências por último.
- Eavision primeiro. Restantes atuais por entrada decrescente, depois encerrados por saída decrescente. Datas desconhecidas depois das conhecidas na mesma categoria.
- Nome, contatos, IA, formação e idiomas copiados de `dados_fixos` da configuração em português ou inglês. Outros idiomas precisam de cadastro explícito antes do uso.
- Descrições institucionais copiadas da configuração somente quando há experiências detalhadas. Não há criação ou adaptação de descrições.
- Competências e ferramentas copiadas da entrada, sem pontuação. A quantidade fora da configuração gera uma pendência, sem corte automático.
- Travessões e dois-pontos normalizados na cópia de saída. Base e JSON de entrada permanecem intactos.
- Estilos, margens, numeração, cabeçalhos e rodapés preservados do template. Títulos ficam junto ao conteúdo seguinte e cada bloco de empresa fica junto ao primeiro bullet; os demais bullets podem passar para outra página.
- IDs inválidos, vínculos duplicados, textos ausentes ou estrutura ilegível geram erro técnico no terminal. O script não inventa ou troca conteúdo para resolver esses erros.
- Excesso de experiências é sinalizado sem remover conteúdo aprovado. Admissão por nota, deduplicação semântica e limites da seleção devem ser resolvidos no matching antes desta etapa.

O DOCX solicitado é gravado. Com `--pdf`, é gerado também um PDF com o mesmo nome e pasta. Não são gerados JSONs de auditoria ou cópias de dados operacionais. Os intermediários da conversão são temporários e removidos automaticamente.

## Exportação para PDF

Acrescente `--pdf` ao comando de montagem. Exemplo de saída `alex-floriano-curriculo.docx` gera também `alex-floriano-curriculo.pdf`. A conversão usa o LibreOffice do runtime Codex e pypdf para conferir texto extraível em todas as páginas, sem API e sem consumo de tokens. O DOCX não é alterado pela conversão.

Se o PDF já existir, é necessário escolher outro nome ou informar `--sobrescrever`. Se a conversão falhar ou ultrapassar 45 segundos, o DOCX fica preservado e o terminal informa a falha com código de saída 2. A verificação de texto não comprova importação em ATS ou fidelidade visual integral; faça a conferência abaixo.

## Conferência visual

A verificação estrutural não detecta toda falha de paginação. Após montar, renderize e inspecione todas as páginas. O renderer do Codex pode ser usado para revisão local:

```bash
/Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 "/Users/alex/.codex/plugins/cache/openai-primary-runtime/documents/26.915.20218/skills/documents/render_docx.py" \
  "/Users/alex/Documents/Adaptar Vaga/candidaturas/empresa_cargo/alex-floriano-curriculo.docx" \
  --output_dir "/private/tmp/revisao-curriculo"
```

Os campos de paginação do rodapé são atualizados ao abrir no Word, conforme o template. O montador não muda os valores em cache. Esta montagem não comprova aceitação ou leitura em uma plataforma ATS real.
