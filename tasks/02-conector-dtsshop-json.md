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

## Addendum (2026-08-07) — gap encontrado na task 08
Ao começar o frontend (task 08), achamos que a task 02/03 nunca cobriu a
cascata completa marca→modelo→motor→categoria — só marca (`get_car_data`) e
categoria a partir de um `car_id` já pronto (`get_categories`). Faltava o meio:
como chegar do modelo até o `car_id`.

Investigado ao vivo (Playwright navegando o seletor real do site,
interceptando as requisições disparadas):
- [x] `get_models(make_id)` — `getModels?year=&id=<make_id>`. GET público.
- [x] `get_cars(make_id, model_id)` — `getCars?year=&make_id=&model_id=`. GET
      público. **Achado importante**: o `id` de cada item retornado aqui É o
      `car_id` usado em tudo (categorias, cookies `car_selector_car`) —
      confirmado comparando com os cookies reais setados pelo site após
      selecionar motor.
- [x] Cascata completa testada ao vivo: AUDI (make_id=5) → A3 8P
      (model_id=4955) → 1.2 TSI (car_id=33251) → categorias reais → listagem
      de produtos reais com preço.

## Arquivo (atualizado)
`backend/core/connectors/dtsshop.py`, `backend/core/search_views.py`,
`backend/config/urls.py`
