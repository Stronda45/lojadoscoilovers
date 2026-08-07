# Frontend — decisões

## Stack
- **React + Vite** (não Next.js/CRA). Fase 1 é SPA simples consumindo REST —
  não precisa de SSR/rotas de servidor do Next. Vite é mais rápido pra
  scaffold/dev e é o padrão atual pra SPA React sem framework full-stack.
- **Sem bibliotecas extras** além de `react-router-dom` (adicionada na task
  09, como já previsto aqui — múltiplas telas precisavam de rotas). Sem
  axios, sem react-query/swr — `fetch` nativo + um hook pequeno (`useAsync`)
  cobrem o que a Fase 1 precisa.
  - `npm audit` acusa 2 "high" em `react-router` (CSRF bypass em "RSC
    Mode") — não se aplica aqui: app é SPA client-side puro
    (`BrowserRouter`), sem React Server Components. Decisão: manter a
    versão instalada, não fazer downgrade forçado.
- **Sem CSS framework/design system** — Fase 1 é "sem design" por decisão de
  escopo (ver `tasks/00-overview.md`). CSS em `index.css` é só o mínimo pra
  não ficar ilegível.

## Comunicação com o backend
- `VITE_API_BASE_URL` (env, default `http://127.0.0.1:8000`) — nunca
  hardcoded, pra funcionar em dev/produção sem mudar código.
- Backend precisa ter a origin do frontend em `CORS_ALLOWED_ORIGINS`
  (`backend/.env`) — dev usa `http://localhost:5173` (porta padrão do Vite).

## Cascata de veículo (marca → modelo → motorização → categoria)
Implementada como 4 `<select>` em cascata, cada um dependente do anterior
(reseta os de baixo quando um de cima muda). Motorização é o 3º nível real
da cascata do dtsshop.de — não existe seletor de "ano" separado no site (o
ano vem embutido no nome do modelo). Ver `tasks/08-frontend-busca.md` e o
addendum em `tasks/02-conector-dtsshop-json.md` pra como os IDs foram
descobertos.

## Testado com
Playwright dirigindo Chromium contra o dev server real (não só revisão de
código) — fluxo completo AUDI → A3 (8P) → motor → categoria → resultado
real na tela, sem erro de console. Ver notas da task 08.
