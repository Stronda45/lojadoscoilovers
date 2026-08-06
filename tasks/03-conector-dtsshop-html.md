# 03 — Conector dtsshop.de: HTML (listagem de produtos/busca)

Estimativa: 10h · Bloqueada por: 01 · **Status: concluída (list_products testado,
search implementado mas não testado ao vivo)**

## Objetivo
Implementar a parte do conector que precisa interpretar HTML renderizado (confirmado
ao vivo: não existe endpoint JSON pra isso).

## Achado importante — muda a abordagem original
A listagem de produtos filtrada por veículo **não é acessível via `requests`/`curl`,
nem com os cookies e headers corretos**. Investigação ao vivo confirmou:
- O filtro por carro é armazenado em cookies `car_selector_make`/`car_selector_model`/
  `car_selector_car` (não em sessão server-side, não em query params `c_make=...`
  como a URL sugere).
- Mesmo com esses cookies corretos, o servidor só devolve o HTML completo (com
  produtos) numa **navegação real de navegador** (`Sec-Fetch-Dest: document`). Um
  `fetch()` disparado de dentro da própria aba autenticada, pra exatamente a mesma
  URL, com os mesmos cookies, **não** recebe os dados — nem `curl`/`requests`
  imitando os headers de navegação manualmente. É fingerprint de conexão
  (TLS/protocolo), não algo replicável com um cliente HTTP leve.
- **Decisão**: usar **Playwright** (Chromium headless) só para `list_products` e
  `search` — as outras 3 funções do conector (`get_car_data`, `get_categories`,
  `get_price_and_availability`) continuam em `requests` puro, mais leve.
- Em vez de fazer parsing frágil de HTML/CSS, a extração usa `ko.dataFor()` do
  Knockout diretamente via `page.evaluate()` — pega o objeto JS estruturado que
  alimenta a UI (nome, imagens, `product_id` numérico, atributos), não texto
  renderizado. Mais robusto a mudanças de layout/CSS; quebra só se o site trocar de
  framework JS.

## Tarefas
- [x] `list_products(category_id, car_cookies)` — via Playwright, extrai produtos
      reais com `product_id` numérico (o mesmo ID usado por
      `get_price_and_availability`, testado ponta a ponta).
- [ ] `search(query, car_cookies)` — implementado (mesmo padrão), **não testado ao
      vivo ainda** (parei de bater no site após ~30 requisições de investigação numa
      janela curta — risco real de throttling, ver Nota abaixo). URL usada:
      `/catalogsearch/result/?q=<query>` (padrão Magento, não confirmado
      especificamente para o dtsshop.de).
- [x] Combinar com task 02: `product_id` retornado aqui é o mesmo formato aceito por
      `get_price_and_availability`.
- [x] Erro controlado se a extração falhar (host inválido testado → `SupplierError`
      limpa, sem crash). Categoria inexistente → lista vazia, sem erro (comportamento
      aceitável).

## Aceite
- [x] `list_products` retorna itens reais com nome/imagem/`product_id` — testado
      contra categoria real (Wheel Caps, VW Golf) — 63 produtos retornados.
- [ ] `search` retorna resultados reais — pendente de teste ao vivo.
- [x] Erro de host/rede não quebra a request.

## Nota operacional (relevante pra Fase 2 / uso em produção)
Durante a investigação, requisições repetidas via `requests`/`curl` num intervalo
curto pareceram disparar throttling no dtsshop.de (a home parou de emitir cookie de
sessão temporariamente; o endpoint de preço/estoque da task 02 continuou funcionando
normalmente). Não é um bloqueio permanente, mas confirma na prática o risco
operacional já documentado em `planejamento.md`/`conversa.md`: evitar polling
agressivo, manter volume de chamadas baixo e sob demanda.

## Dependência nova
`playwright` + Chromium (`playwright install chromium`) — precisa rodar esse install
em qualquer ambiente novo (dev machine, CI, Railway) além do `pip install -r
requirements.txt`. Anotar isso no `README.md`/deploy (task 10).

## Arquivo
`backend/core/connectors/dtsshop.py`
