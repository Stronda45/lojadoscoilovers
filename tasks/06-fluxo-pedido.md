# 06 — Fluxo de pedido (backend)

Estimativa: 4h · Bloqueada por: 02, 03, 04

## Objetivo
Cliente logado escolhe uma peça encontrada na busca e confirma o pedido.

## Tarefas
- [ ] `POST /orders` — recebe `product_id` (+ dados do carro, se aplicável), busca
      preço/estoque atual via conector (task 02), aplica margem (task 04), cria
      `Order`/`OrderItem`.
- [ ] Resposta inclui aviso explícito de que a disponibilidade pode mudar até a
      confirmação da compra no fornecedor (isso também precisa aparecer no frontend —
      task 09).
- [ ] `GET /orders` — cliente vê os próprios pedidos (mesmo sem tela bonita, backend
      precisa expor isso).

## Aceite
- [ ] Pedido real criado no banco, com preço já com margem aplicada.
- [ ] Aviso de disponibilidade não garantida presente na resposta da API.
