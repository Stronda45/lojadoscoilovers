# 07 — Alerta por e-mail em novo pedido

Estimativa: 3h · Bloqueada por: 06

## Objetivo
Dono/funcionário sabe na hora que chegou pedido novo, pra comprar no fornecedor a
tempo (estoque não é garantido — quanto mais rápido, melhor).

## Tarefas
- [ ] Configurar envio de e-mail (SMTP — reaproveitar padrão já usado no
      `famain_be` antigo, `core/email_utils.py`, como referência de implementação).
- [ ] Disparar e-mail pro(s) e-mail(s) da equipe a cada `Order` criado, com os dados
      do pedido (produto, cliente, preço, link pro produto no dtsshop.de pra comprar).

## Aceite
- [ ] Criar um pedido de teste dispara e-mail real recebido na caixa de entrada.
