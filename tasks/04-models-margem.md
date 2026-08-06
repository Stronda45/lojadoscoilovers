# 04 — Models: Customer, Order, regra de margem

Estimativa: 5h · Bloqueada por: 01

## Objetivo
Estrutura de dados do negócio (cliente final + pedido) e a regra de preço de venda.

## Tarefas
- [ ] Model `Customer` (nome, e-mail, endereço de entrega, telefone) — ligado a
      `User` do Django.
- [ ] Model `Order` / `OrderItem` (produto, preço aplicado, status, cliente, criado em).
- [ ] **Regra de margem configurável** — não travar em fixo nem em percentual:
      suportar os dois modos (`fixed_amount` ou `multiplier`), com um valor default,
      até o cliente confirmar o que quis dizer com "1.30".
      - Default provisório: `fixed_amount = 50` (o que já foi orçado/proposto).
      - Trocar para `multiplier = 1.30` é só mudar a config, sem alterar código, assim
        que ele confirmar.
- [ ] Migrations.

## Aceite
- [ ] Dado um preço de custo, a função de margem devolve o preço de venda certo nos
      dois modos (testar manualmente os dois).
- [ ] Trocar o modo de margem não exige deploy de código novo, só config.
