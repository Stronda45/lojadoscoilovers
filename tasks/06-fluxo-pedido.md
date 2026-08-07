# 06 — Fluxo de pedido (backend)

Estimativa: 4h · Bloqueada por: 02, 03, 04 · **Status: concluída**

## Objetivo
Cliente logado escolhe uma peça encontrada na busca e confirma o pedido.

## Tarefas
- [x] `POST /orders` — recebe `items: [{product_id, product_name, quantity}]`,
      busca preço/estoque atual via conector (task 02), aplica margem (task 04/
      `MarginTier`+`MarginRule`), cria `Order`/`OrderItem`. **Decisão**: aceita
      lista de itens (não só 1 produto) — o model já suporta pedido com vários
      itens, não custava nada a mais.
- [x] Resposta inclui aviso explícito de que a disponibilidade pode mudar até a
      confirmação da compra no fornecedor (também precisa aparecer no frontend —
      task 09).
- [x] `GET /orders` — cliente vê os próprios pedidos. Mesma rota (`/orders`),
      método diferencia (`GET` lista, `POST` cria).

## Aceite
- [x] Pedido real criado no banco, com preço já com margem aplicada — testado
      (custo 9.70 + margem fixa 50 = venda 59.70).
- [x] Aviso de disponibilidade não garantida presente na resposta da API.
- [x] Produto inexistente no fornecedor → 400, nenhum pedido parcial criado
      (tudo em `transaction.atomic()`).

## Decisões
- Preço/nome enviados pelo cliente NUNCA são usados pra definir o preço —
  sempre re-consultados no fornecedor na hora do pedido (evita preço
  manipulado vindo do frontend).
- `product_name` ainda vem do frontend (o endpoint de preço/estoque do
  fornecedor não devolve nome) — risco baixo, é só texto de exibição.

## Não testado ao vivo
Testado com resposta do conector mockada (sem chamar o dtsshop.de de novo) —
a parte de rede (`get_price_and_availability`) já foi validada ao vivo na
task 02, então isso cobre só a lógica nova (task 06: serializer, margem,
transação, resposta). Ver `investigar.md`.

## Arquivos
`backend/core/views.py`, `backend/core/serializers.py`,
`backend/config/urls.py`
