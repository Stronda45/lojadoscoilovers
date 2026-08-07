# 09 — Frontend: login/cadastro/pedido (sem design)

Estimativa: 5h · Bloqueada por: 05, 06 · **Status: concluída**

## Objetivo
Cliente final consegue criar conta, logar e confirmar um pedido, tudo sem estilo.

## Tarefas
- [x] Tela de cadastro (nome, e-mail, senha, endereço, telefone) — `/cadastro`.
- [x] Tela de login — `/login`.
- [x] Botão "Pedir" no resultado da busca (task 08) → confirma pedido.
      Sem login → mostra link pra entrar em vez de tentar pedir.
- [x] Aviso visível: "disponibilidade sujeita a confirmação" antes de pedir
      (banner acima dos resultados) e depois de pedir (mensagem de sucesso
      repete o aviso que a API devolve — task 06).
- [x] Lista simples dos próprios pedidos — `/pedidos`.

## Aceite
- [x] Fluxo completo funciona: cadastra → loga → busca → pede → aparece na
      lista de pedidos — testado ao vivo (Playwright dirigindo o frontend
      real contra o backend real, dados reais do dtsshop.de). Sem erro de
      console em nenhuma etapa.

## Decisões
- **`react-router-dom`** adicionado (já previsto em `docs/FRONTEND.md`) —
  4 rotas (`/`, `/login`, `/cadastro`, `/pedidos`) justificam a lib.
- **Auth em Context + localStorage** (`src/auth.jsx`) — token DRF guardado
  no browser, sem lib de state management (escopo pequeno não justifica).
- **"Pedir" cria pedido de 1 item na hora** (sem carrinho) — mais simples,
  suficiente pro fluxo pedido no aceite. Carrinho/múltiplos itens por
  pedido de uma vez fica pra quando o cliente pedir.

## Arquivos
`frontend/src/auth.jsx`, `frontend/src/api.js` (endpoints de auth/pedido),
`frontend/src/App.jsx` (rotas + nav), `frontend/src/pages/*.jsx`,
`frontend/src/index.css`
