# 04 — Import de Excel/CSV de outros fornecedores

**Status: bloqueada.** Bloqueada por: respostas do cliente (seção 7 de
`/Users/pablo/Project/famaInPecas/perguntas-para-cliente.txt`) + alinhamento de
escopo/preço (não estava no PDF original da Fase 2).

## Contexto
Cliente tem 4 fornecedores em planilhas (MTS, TA Technix, Cheney, ES2WHEELS),
arquivos reais já recebidos (`csvs.rar`) e inspecionados. São muito mais complexos
do que "planilha de preço simples" — MTS e TA Technix têm compatibilidade de
veículo completa (uma linha por peça×motorização, igual ao dtsshop.de); as rodas
(Cheney/ES2WHEELS) não têm preço nenhum no arquivo. Desenho técnico completo em
`docs/EXCEL-IMPORT.md` — **não repetir aqui, ler lá antes de começar**.

## Objetivo
Catálogo de produtos desses 4 fornecedores navegável/buscável na plataforma,
atualizável recorrentemente sem duplicar produto.

## Tarefas (resumo — detalhe em `docs/EXCEL-IMPORT.md`)
- [ ] Models `Supplier`, `ImportedProduct`, `ImportedProductFitment`.
- [ ] Parser dedicado por fornecedor (4 funções, não mapeamento genérico — formatos
      já conhecidos): MTS (CSV, streaming por causa dos 206MB), TA Technix (CSV),
      Cheney/ES2WHEELS (XLSX via `openpyxl`).
- [ ] Management command `import_supplier <nome> <arquivo>` — roda o parser certo,
      faz upsert por `(supplier, external_reference)`, marca sumidos como
      `active=False` em vez de apagar.
- [ ] Endpoint de busca separado (`/catalogo` ou nome a definir) — com ou sem
      cascata de veículo, depende da resposta à pergunta 7.4.
- [ ] Tela no frontend pra esse catálogo (reusa padrão visual de
      `pages/SearchPage.jsx`, mas fluxo próprio).

## Aceite
- [ ] `import_supplier mts caminho/arquivo.csv` roda sem estourar memória (arquivo
      de 206MB) e não duplica produto ao rodar 2x.
- [ ] Produto que some do arquivo novo fica `active=False`, não é apagado.
- [ ] Busca no catálogo importado devolve produto real com preço já com margem
      aplicada (onde há preço — rodas ficam pendentes, ver pergunta 7.3).

## Antes de começar
1. Resolver as 6 perguntas da seção 7 em `perguntas-para-cliente.txt`.
2. Confirmar com o cliente se isso está coberto pelos €1.200 da Fase 2 ou é
   orçado à parte — não estava no PDF assinado.

## Arquivos (quando destravar)
`backend/core/models.py` (novos models), `backend/core/management/commands/
import_supplier.py` (novo), parsers em `backend/core/importers/` (novo),
`docs/EXCEL-IMPORT.md`.
