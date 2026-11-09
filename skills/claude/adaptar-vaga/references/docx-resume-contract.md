# Contrato Word do currículo

## Ferramentas obrigatórias

Usar a skill `documents` para toda criação ou alteração de DOCX. Carregar as dependências do workspace e usar o runtime retornado. Não depender de Python, Node ou pacotes globais do sistema.

Ler na skill `documents`.

1. `tasks/create_edit.md`.
2. `tasks/verify_render.md`.
3. `references/design_presets.md`.

Usar `python-docx` ou a biblioteca de documentos fornecida pelo runtime do workspace. Manter scripts de construção em diretório temporário ou no diretório da candidatura, nunca dentro da skill gerenciada.

## Sistema visual

Usar `compact_reference_guide` como preset-base com o override nomeado `resume_ats`.

Aplicar exatamente.

1. Página US Letter em retrato.
2. Margens de 0,75 polegada.
3. Fonte Arial.
4. Corpo com 10,5 pt, alinhamento à esquerda, 0 pt antes, 3 pt depois e espaçamento 1,05.
5. Nome com 18 pt, negrito, preto, 0 pt antes e 2 pt depois.
6. Título funcional com 11 pt, negrito, preto, 0 pt antes e 4 pt depois.
7. Contato com 9 pt, preto, 0 pt antes e 7 pt depois.
8. Títulos de seção com 11 pt, negrito, preto, 8 pt antes e 3 pt depois.
9. Bullets com 0,18 polegada de alinhamento do marcador, 0,38 polegada de recuo do texto, 0,20 polegada de recuo suspenso, 2 pt depois e espaçamento 1,05.
10. Cabeçalho e rodapé vazios. Não colocar informação essencial fora do corpo.
11. Uma coluna. Não usar tabelas, caixas de texto, ícones, imagens, gráficos ou barras de habilidade.
12. Usar negrito com moderação para empresa, cargo ou resultado. Não usar sublinhado decorativo.
13. Usar somente preto. Cinza escuro pode aparecer no contato quando a renderização preservar contraste.

Usar estilos Word reais para corpo e títulos. Usar definições reais de lista para bullets. Não criar bullets com caracteres manuais.

Manter duas páginas como objetivo operacional. Não reduzir o corpo abaixo de 10 pt para forçar o limite. Quando ultrapassar, reduzir conteúdo por relevância antes de reduzir espaçamento.

## Conteúdo e ATS

Manter o texto pesquisável. Não inserir informação essencial em cabeçalho, rodapé ou elemento visual. Usar seções convencionais no idioma da vaga. Manter datas e nomes consistentes.

## Renderização e inspeção

Depois de cada alteração material.

1. Renderizar o DOCX com `render_docx.py` da skill `documents` para um diretório temporário.
2. No macOS, iniciar o render com `TMPDIR=/private/tmp` quando necessário.
3. Abrir todas as páginas PNG em 100 por cento.
4. Verificar clipping, sobreposição, fonte substituída, espaços irregulares, bullets desalinhados, linhas órfãs, seções partidas e páginas excessivamente vazias.
5. Corrigir o DOCX e renderizar novamente.
6. Não entregar até a última renderização passar.

Não entregar PNGs ou PDFs de QA. Criar PDF somente quando Alex pedir ou quando o processo exigir.

## Registro de QA

Criar `qa-word.json` na raiz da candidatura.

Usar esta estrutura.

```json
{
  "status": "passed",
  "verified_resume": {
    "path": "Alex_Floriano_Cargo_Empresa_PTBR.docx",
    "pages_rendered": 2,
    "all_pages_inspected": true,
    "visual_issues": []
  }
}
```

Não definir `passed` quando qualquer página não tiver sido inspecionada ou quando houver problema visual aberto.
