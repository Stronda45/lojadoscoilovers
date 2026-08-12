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

**Decisão 2026-08-12**: upload é **self-service pelo cliente** (não comando rodado
por nós), com o arquivo master da MTS (206MB) tratado como exceção cara (ver
`docs/EXCEL-IMPORT.md`) — caminho padrão usa os recortes por categoria da MTS.

## Objetivo
Catálogo de produtos desses 4 fornecedores navegável/buscável na plataforma, com
upload feito pelo próprio cliente sempre que precisar, sem duplicar produto.

## Tarefas (resumo — detalhe em `docs/EXCEL-IMPORT.md`)
- [ ] Models `Supplier` (com `selected_fields`), `ImportedProduct`,
      `ImportedProductFitment`.
- [ ] Parser dedicado por fornecedor (4 funções, não mapeamento genérico — formatos
      já conhecidos): MTS (CSV, streaming), TA Technix (CSV), Cheney/ES2WHEELS
      (XLSX via `openpyxl`).
- [ ] Endpoint de upload no admin (self-service) — recebe arquivo, identifica
      fornecedor, roda o parser certo, faz upsert por
      `(supplier, external_reference)`, marca sumidos como `active=False` em vez
      de apagar.
- [ ] **Checklist de segurança do upload** (validação de tipo/conteúdo real, limite
      de tamanho, proteção contra zip bomb e path traversal na descompactação,
      escape de CSV injection, só `.csv`/`.xlsx`) — ver `docs/EXCEL-IMPORT.md`,
      seção "Segurança do upload". Não é opcional.
- [ ] UI simples no admin pra escolher quais campos (`raw_attributes`) de cada
      fornecedor ficam visíveis/são usados (`Supplier.selected_fields`).
- [ ] Endpoint de busca separado (`/catalogo` ou nome a definir) — com ou sem
      cascata de veículo, depende da resposta à pergunta 7.4.
- [ ] Tela no frontend pra esse catálogo (reusa padrão visual de
      `pages/SearchPage.jsx`, mas fluxo próprio).
- [ ] **Documentação não-técnica pro cliente** (passo a passo de upload + por que
      usar os arquivos por categoria da MTS, não o master) — entregável desta
      task, não opcional.

## Aceite
- [ ] Cliente sobe um arquivo por categoria da MTS pelo admin e o catálogo atualiza
      sem intervenção nossa.
- [ ] Upload de arquivo malicioso (extensão trocada, zip bomba, path traversal)
      é rejeitado com mensagem clara, não quebra o servidor.
- [ ] Rodar o mesmo arquivo 2x não duplica produto; produto que sumiu vira
      `active=False`.
- [ ] Busca no catálogo importado devolve produto real com preço já com margem
      aplicada (onde há preço — rodas ficam pendentes, ver pergunta 7.3).
- [ ] Documentação de upload testada com alguém não-técnico (ou pelo menos redigida
      nesse nível) antes de considerar concluído.

## Antes de começar
1. Resolver as 6 perguntas da seção 7 em `perguntas-para-cliente.txt` (inclui
   confirmar se ele topa o custo extra caso queira processar o master da MTS).
2. Confirmar com o cliente se isso está coberto pelos €1.200 da Fase 2 ou é
   orçado à parte — não estava no PDF assinado.

## Arquivos (quando destravar)
`backend/core/models.py` (novos models), `backend/core/importers/` (parsers,
novo), endpoint de upload em `backend/core/` (nome a definir), documentação de
upload (novo arquivo, possivelmente `docs/GUIA-UPLOAD-CLIENTE.md` ou anexo direto
no admin), `docs/EXCEL-IMPORT.md`.
