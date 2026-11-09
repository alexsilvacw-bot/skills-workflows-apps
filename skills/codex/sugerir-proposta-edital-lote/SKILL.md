---
name: sugerir-proposta-edital-lote
description: Consulta o histórico de leilões da Receita Federal para dar referências de proposta e arrematação de um lote. Use para pedidos como “Sugerir proposta edital X lote Y”, “verificar a base para este lote” ou consulta por categoria, UF, mínimo e avaliação.
---

# Sugerir proposta — edital + lote

Entender o pedido como consulta de referências históricas de lotes semelhantes. Usar os cálculos da ferramenta local; o nome da skill não transforma a referência em modelo preditivo ou autorização para enviar propostas.

## Fonte e ferramenta

Projeto: `/Users/alex/Documents/Leilão receita` (o “ã” do caminho está decomposto em Unicode).

- Guia: `consulta_historica/LEIA_PRIMEIRO.md`.
- Banco de consulta: `consulta_historica/historico.sqlite`.
- Consulta: `consulta_historica/consultar.py`.
- Regras: `consulta_historica/regras.json`.

Ler o guia e as regras quando aplicar a skill. Conferir o universo atual pelos metadados do banco/saída da consulta, sem fixar contagens no prompt. A versão preparada tem 76 editais; a antiga reserva foi liberada para uso descritivo. Arquivos e critérios anteriores de previsão são registros históricos, não o fluxo atual.

A pasta está no iCloud Drive/Documentos, mantida baixada no Mac. PDFs originais ficam no projeto, com download removido. Não baixar o acervo inteiro para uma consulta; abrir somente os documentos necessários ao lote. Se os caminhos não estiverem acessíveis, informar a falta de acesso; não preencher a resposta com medianas lembradas.

## Identificar o lote e consultar

- Aceitar edital + lote, link oficial ou os quatro campos: categoria, UF de localização dos bens, mínimo e avaliação. Usar a descrição para distinguir famílias como veículos rodoviários e veículos para desmontagem. Não presumir equivalência de kits, quantidades, condição ou perfil PF/PJ.
- Se vier edital + lote, primeiro procurar a chave completa em `historico.sqlite` em modo somente leitura e ler descrição/cadastro no banco original ou documento específico quando necessário. O edital usa unidade/número/ano; o número do lote sozinho não identifica o registro. Normalizar apenas quando a identificação for inequívoca.
- Se o lote não estiver na base, consultar a página/documentação oficial vigente da Receita para obter os quatro campos e a descrição. Para mínimos, avaliação, estado e retificações, citar a fonte efetivamente consultada e usar a versão aplicável. A unidade promotora não substitui a localização física dos bens.
- Se faltar um campo essencial ou houver categoria/UF ambígua, pedir apenas essa informação. Não estimar avaliação, mínimo ou estado para conseguir uma resposta.
- Executar o script com os quatro campos. Exemplo de sintaxe, com valores ilustrativos:

```sh
python3 '/Users/alex/Documents/Leilão receita/consulta_historica/consultar.py' --categoria 'veículos rodoviários' --estado PR --minimo '10000' --avaliacao '30000' --json
```

A ferramenta consulta em modo somente leitura. Usar `--listar-categorias` quando precisar resolver a taxonomia. As regras de filtros e ampliação pertencem a `regras.json`; não relaxá-las silenciosamente para obter mais casos. Se o usuário pedir um recorte diferente, identificá-lo como tal.

## Responder

Confirmar a identificação e os valores do lote e entregar uma tabela com os quatro indicadores:

1. Menor proposta inicial classificada / avaliação.
2. Menor proposta inicial classificada / mínimo.
3. Arrematação / avaliação.
4. Arrematação / mínimo.

Para cada um, trazer mediana e P10–P90 históricos, equivalentes em reais e quantidade de lotes/editais usados. Informar período, recorte efetivo e qualquer ampliação de UF ou faixa de valores. Amostra reduzida ou ausência de comparáveis deve permanecer explícita. Quando a composição/restrição do histórico mudar materialmente a comparação, explicar essa diferença de forma breve.

Manter as referências pela avaliação e pelo mínimo separadas; não fazer média delas para inventar um valor único. O equivalente em reais aplica a razão histórica ao denominador informado. Não tratar P10–P90 como probabilidade futura garantida, menor classificada como limiar contrafactual, nem ausência de venda como preço zero.

Se o lote consultado já tiver resultado histórico, apresentar esse fato separadamente. A consulta padrão pode incluir o próprio lote: verificar as chaves dos comparáveis e declarar sua presença, em vez de apresentar a comparação como independente. Se for necessária comparação excluindo o próprio lote, calcular esse recorte explicitamente e identificá-lo, sem alterar a base.

Não iniciar treino, coleta recorrente, atualização da base, migração ou submissão de propostas por causa desta skill. Para pedido de consulta, concluir com os dados e a interpretação necessária; evitar alertas genéricos. Se o usuário solicitar salvar, usar uma pasta nova de resultados para preservar consultas anteriores.
