# 02 — Conector dtsshop.de: dados JSON (veículo/categoria/preço-estoque)

Estimativa: 8h · Bloqueada por: 01

Ver `/Users/pablo/Project/famaInPecas/planejamento.md` (raiz do famaInPecas) para todo
o levantamento técnico já validado ao vivo.

## Objetivo
Implementar a parte do conector que é só HTTP + JSON, sem parsing de HTML.

## Tarefas
- [ ] `get_car_data()` — extrai o JSON de veículo embutido na página inicial do
      dtsshop.de (marcas/modelos/motorizações).
- [ ] `get_categories(car_id)` — chama `getGroups?car_id=<id>&brand_filter=`.
- [ ] `get_price_and_availability(product_ids: list[str])` — POST
      `productfinder/ajax/GetProductsPriceAndAvailability`, body `idarr[]=<id>`.
- [ ] Tratar timeout/erro de rede sem derrubar o processo.

## Aceite
- [ ] Os 3 métodos retornam dado real do dtsshop.de.
- [ ] Erro de rede não quebra a request — é capturado.
