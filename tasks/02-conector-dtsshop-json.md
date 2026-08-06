# 02 — Conector dtsshop.de: dados JSON (veículo/categoria/preço-estoque)

Estimativa: 8h · Bloqueada por: 01 · **Status: concluída**

Ver `/Users/pablo/Project/famaInPecas/planejamento.md` (raiz do famaInPecas) para todo
o levantamento técnico já validado ao vivo.

## Objetivo
Implementar a parte do conector que é só HTTP + JSON, sem parsing de HTML.

## Tarefas
- [x] `get_car_data()` — GET público `getAllCarData?year=`, sem sessão.
- [x] `get_categories(car_id)` — GET público `getGroups?car_id=<id>&brand_filter=`.
- [x] `get_price_and_availability(product_ids: list[str])` — POST
      `productfinder/ajax/GetProductsPriceAndAvailability`, body `idarr[]=<id>`.
- [x] Tratar timeout/erro de rede sem derrubar o processo.

## Achado importante durante a implementação
`get_price_and_availability` **não é um GET público simples** como os outros dois —
precisa de sessão Magento (cookie `PHPSESSID`) + `form_key` (CSRF, extraído do HTML da
home) + header `X-Requested-With: XMLHttpRequest`. Sem isso, o dtsshop.de devolve
`302` com "Invalid form key" em vez de erro claro. Implementado em
`_session_with_form_key()` no `core/connectors/dtsshop.py`.

## Aceite
- [x] Os 3 métodos retornam dado real do dtsshop.de (testado manualmente contra o
      site ao vivo — 167 marcas, categorias reais, preço/estoque real de 2 produtos).
- [x] Erro de rede não quebra a request — testado com host inexistente,
      `SupplierError` capturada corretamente.

## Arquivo
`backend/core/connectors/dtsshop.py`
