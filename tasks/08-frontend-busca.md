# 08 — Frontend: busca e resultados (sem design)

Estimativa: 5h (+ ~2h não orçadas, ver addendum) · Bloqueada por: 02, 03 · **Status: concluída**

## Objetivo
Tela funcional (sem estilo) pra buscar peça e ver preço/estoque.

## Tarefas
- [x] Filtros em cascata: marca → modelo → **motorização** → categoria.
      **Desvio da task original**: o site não tem um seletor de "ano"
      separado — o ano fica embutido no nome do modelo (ex: "A3 (8P) 8P1
      05/2003-12/2013") e a motorização é o 3º nível real da cascata do site
      (confirmado navegando o seletor ao vivo — ver addendum da task 02).
- [x] Lista de resultados com nome, imagem, preço (já com margem), estoque
      (texto de disponibilidade do fornecedor).
- [x] Estados de carregamento ("carregando...") e "sem resultado" em cada
      nível da cascata e nos resultados finais.

## Aceite
- [x] Busca real contra o backend retorna resultados na tela, sem quebrar —
      testado ao vivo (Playwright dirigindo o Chromium contra o frontend
      React de verdade): AUDI → A3 (8P) → 1.2 TSI → Suspensions/Top mount →
      1 produto real na tela (nome, marca, preço com margem, prazo de envio).
      Sem erro de console.

## Addendum — pré-requisito descoberto (backend)
Ao começar esta task, achamos que faltava a cascata marca→modelo→motor no
backend (task 02/03 só tinham marca e categoria-a-partir-de-car_id prontos).
Resolvido e documentado em `tasks/02-conector-dtsshop-json.md` (addendum
2026-08-07) — `get_models`/`get_cars` no conector + `core/search_views.py`
expondo `/vehicles/*` e `/search`. Não estava no orçamento original da task
08 (~2h extras).

## Bug encontrado no teste manual do usuário (corrigido)
Categoria de rodas (AUDI/ACURA, "Unlimited Base Wheels...") causava 500: o
fornecedor devolve `["<id> not found."]` (lista de erro) em vez do dict de
preço pra alguns `product_id` — `_enrich_with_price` assumia sempre dict e
quebrava. Corrigido pra tratar como indisponível (`price: null`, frontend já
mostra "preço indisponível"). Ver `investigar.md`.

## Arquivos
`frontend/` (scaffold Vite + React), `frontend/src/App.jsx`,
`frontend/src/api.js`, `frontend/src/index.css`,
`backend/core/search_views.py` (ver task 02)
