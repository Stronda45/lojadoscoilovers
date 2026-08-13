# 04 — Import de Excel/CSV de outros fornecedores

**Status: parcialmente adiantada.** A parte que não depende do cliente está
implementada e testada (ver abaixo). Falta: seleção de campos visíveis
(`Supplier.selected_fields`, sem UI ainda), busca no frontend, decisão de
cascata de veículo (pergunta 7.4), preço das rodas (7.3), e alinhamento de
escopo/preço com o cliente (não estava no PDF original da Fase 2).

## Contexto
Cliente tem 4 fornecedores em planilhas (MTS, TA Technix, Cheney, ES2WHEELS),
arquivos reais já recebidos (`csvs.rar`) e inspecionados. São muito mais complexos
do que "planilha de preço simples" — MTS e TA Technix têm compatibilidade de
veículo completa (uma linha por peça×motorização, igual ao dtsshop.de); as rodas
(Cheney/ES2WHEELS) não têm preço nenhum no arquivo. Desenho técnico completo em
`docs/EXCEL-IMPORT.md` — **não repetir aqui, ler lá antes de mexer**.

## Tarefas
- [x] Models `Supplier` (com `selected_fields`, ainda sem UI pra editar),
      `ImportedProduct`, `ImportedProductFitment` — migration `0007`.
- [x] Parser dedicado por fornecedor (`backend/core/importers/`): `mts.py`,
      `ta_technix.py`, `wheels.py` (Cheney/ES2WHEELS, mesmo formato). Testados
      contra os arquivos reais do cliente (não só amostras).
- [x] Upload **dentro do Django Admin** (`ImportedProductAdmin.upload_view`,
      sessão — não token de API). **Desvio da task original**: pensamos em
      endpoint DRF separado, mas isso não bate com a decisão da task 02
      (painel = Django Admin) — funcionário/dono usam sessão, não token.
      Corrigido antes de ir pra produção.
- [x] Upsert por `(supplier, external_reference)` — cria/atualiza. Desativação
      (`active=False`, nunca apaga) **escopada por categoria presente no
      arquivo**, não pelo fornecedor inteiro — achado real testando: a MTS
      manda 1 arquivo por categoria, sem esse escopo o 2º upload apagava
      (desativava) o 1º.
- [x] Checklist de segurança (`core/importers/security.py`): extensão +
      assinatura real do conteúdo, limite de tamanho, zip bomb (tamanho
      descomprimido), zero escrita em disco ao ler dentro de zip (elimina
      path traversal por construção, não por sanitização), CSV injection.
- [ ] UI pra escolher quais campos (`raw_attributes`) ficam visíveis
      (`Supplier.selected_fields` já existe no model, falta a tela).
- [x] Busca dupla (texto/categoria **e** veículo) — cliente confirmou que
      quer os dois (pergunta 7.4). `GET /catalog/makes`,
      `GET /catalog/makes/<make>/models`, `GET /catalog/variants`,
      `GET /catalog/search` (todos os filtros combináveis). Testado contra
      dados reais importados (MTS) + 7 testes automatizados.
- [ ] Tela no frontend pra esse catálogo — não iniciada.
- [ ] Documentação não-técnica pro cliente (passo a passo de upload) — não
      iniciada, entregável obrigatório antes de considerar concluído.

## Achados testando contra os arquivos reais (não só amostras)
- **MTS usa vírgula decimal** ("707,25", "699"), não ponto — bug real no
  primeiro parser (`parse_decimal_dot`), corrigido pra usar o mesmo parser
  europeu da TA Technix (`parse_decimal_european`).
- **TA Technix "Hersteller" não é uma marca limpa**: vem como "passend für
  Audi / Seat / VW" (várias marcas, prefixo alemão "adequado para") ou lixo
  tipo "Universell"/"1 Set" (peça universal, sem marca). Parser separa em
  várias `ImportedProductFitment` ou nenhuma (peça universal) — não é erro,
  é o dado real do fornecedor.
- **Rodas sem referência única**: não tem coluna de SKU — referência
  construída a partir de modelo+medida+furação+offset+acabamento (única
  combinação que identifica a variante real).
- **Desativação por fornecedor inteiro estava errada** — corrigido pra
  escopar por categoria (ver Tarefas acima).
- **Upload como API token não bate com o painel** — corrigido pra sessão do
  Django Admin, e um gap de permissão foi encontrado e fechado no processo:
  `admin_view()` sozinho só garante `is_staff`, não permissão de model pra
  URLs custom — um funcionário sem permissão em `ImportedProduct` conseguia
  acessar a página de upload só adivinhando a URL. Checagem explícita de
  `has_add_permission` adicionada.

## Aceite (do que já foi feito)
- [x] Testado contra os 4 arquivos reais do cliente (não amostras): MTS
      (adjustable-springs, camber-plates), TA Technix (via zip, como o
      fornecedor manda), ES2WHEELS — todos importam corretamente.
- [x] Rodar o mesmo arquivo 2x não duplica produto (idempotente, testado).
- [x] Produto que some do arquivo mais novo vira `active=False`, sem apagar.
- [x] Importar categoria B da MTS não desativa produtos já importados da
      categoria A (regressão do bug encontrado).
- [x] Upload de arquivo malicioso (extensão trocada, conteúdo binário como
      .csv, .xlsx sem assinatura zip, zip bomb) rejeitado com mensagem clara.
- [x] Funcionário sem permissão em `ImportedProduct` → 403 ao tentar acessar
      a página de upload direto pela URL; dono → 200.
- [x] 31 testes automatizados novos (`core/tests_importers.py`), suite total
      da Fase 2 em 63 testes, todos passando.

## Antes de finalizar (itens que ainda dependem do cliente)
1. Resolver as 6 perguntas da seção 7 em `perguntas-para-cliente.txt`.
2. Confirmar com o cliente se isso está coberto pelos €1.200 da Fase 2 ou é
   orçado à parte — não estava no PDF assinado.

## Arquivos
`backend/core/models.py` (Supplier/ImportedProduct/ImportedProductFitment),
`backend/core/importers/` (base.py, security.py, mts.py, ta_technix.py,
wheels.py, service.py), `backend/core/admin.py` (upload integrado),
`backend/core/templates/admin/core/` (templates do upload),
`backend/core/catalog_views.py` (busca pública),
`backend/core/tests_importers.py`, `backend/core/migrations/0007_*.py`,
`docs/EXCEL-IMPORT.md`.
