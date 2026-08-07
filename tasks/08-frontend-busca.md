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

## Bugs encontrados no teste manual do usuário (corrigidos)
- Categoria de rodas (AUDI/ACURA, "Unlimited Base Wheels...") causava 500: o
  fornecedor devolve `["<id> not found."]` (lista de erro) em vez do dict de
  preço pra alguns `product_id` — `_enrich_with_price` assumia sempre dict e
  quebrava. Corrigido pra tratar como indisponível (`price: null`, frontend
  já mostra "preço indisponível"). Ver `investigar.md`.
- Imagens não apareciam: a URL montada (`pictorama.url + pictorama.id`)
  devolvia 403 do S3. Comparando com o `<img src>` real do site, faltava um
  prefixo de tamanho (`248/`) que não vem no JSON do Knockout — é hardcoded
  no template do site pro thumbnail. Corrigido em
  `connectors/dtsshop.py::_flatten_product_groups` (constante
  `IMAGE_SIZE_PREFIX`).

## Logo + banner + limpar pesquisa (pedido do usuário, 2026-08-07)
Mesmo motivo da UI acima — faltando 2 dias pra entrega. Adicionado:
- Logo placeholder (SVG inline, mola de suspensão estilizada) no header.
- Banner/hero na página de busca (SVG inline, sem foto de banco de imagens —
  evita risco de licença, mantém o bundle autocontido).
- Botão "Limpar pesquisa" (aparece só quando algum filtro está ativo,
  reseta marca/modelo/motorização/categoria de uma vez).
Continua sem imagem de marca real do cliente — placeholder até ele mandar
algo (ou aprovar o SVG genérico como está).

## Paginação (pedido do usuário, 2026-08-07)
Client-side (12 por página) — **decisão**: backend já traz todos os
resultados numa chamada só (a listagem do dtsshop.de não pagina, extrai
tudo da página carregada via Playwright); paginar no backend exigiria
rebuscar no fornecedor a cada página (mais lento, mais chamadas ao site
real). Paginar só a exibição é imediato e sem risco. Reseta pra página 1
a cada nova busca (`categoryId` muda).

## UI (pedido do usuário, 2026-08-07)
Continua "sem design" por decisão de escopo, mas o usuário pediu um
acabamento melhor que HTML cru — vai ser a primeira coisa que o cliente
mostra pro cliente final dele, faltando ~2-3 dias pra entrega. Adicionado:
header com nome do produto, grid de cards (imagem, nome, marca/nº peça,
preço em destaque, badge colorido de disponibilidade usando a cor que o
próprio fornecedor já manda). Sem biblioteca de UI — CSS handcrafted em
`index.css` (ver `docs/FRONTEND.md`).

## Arquivos
`frontend/` (scaffold Vite + React), `frontend/src/App.jsx`,
`frontend/src/api.js`, `frontend/src/index.css`,
`backend/core/search_views.py` (ver task 02)
