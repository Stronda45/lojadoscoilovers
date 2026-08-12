# 04 — Models: Customer, Order, regra de margem

Estimativa: 5h · Bloqueada por: 01 · **Status: concluída**

## Objetivo
Estrutura de dados do negócio (cliente final + pedido) e a regra de preço de venda.

## Tarefas
- [x] Model `Customer` — `phone`, `delivery_address`, ligado a `User` via
      `OneToOneField`. **Decisão**: nome e e-mail não duplicados aqui — usa
      `user.get_full_name()`/`user.email` direto, evita dado desincronizado.
- [x] Model `Order` (status: pendente/comprado no fornecedor/entregue) e `OrderItem`
      (produto, preço de custo E preço de venda aplicado — guardado no momento do
      pedido, não recalcula depois se a margem mudar).
- [x] **Regra de margem configurável** — `MarginRule` (singleton, editável via
      `/admin`, sem precisar de deploy pra trocar): suporta `fixed_amount` e
      `multiplier`. Default: `fixed_amount = 50`.
- [x] Migrations criadas e aplicadas (`core/migrations/0001_initial.py`).

## Aceite
- [x] Dado um preço de custo, `apply_margin()` devolve o preço certo nos dois modos
      — testado manualmente: `9.70` + fixo 50 = `59.70`; `9.70` × 1.30 = `12.61`.
- [x] Trocar o modo de margem é só editar o registro `MarginRule` (via `/admin` ou
      shell) — nenhuma mudança de código nem deploy.

## Extra
- Superuser local criado (`admin`/`admin123`, só dev) pra validação visual no
  `/admin` — pedido do usuário numa conversa anterior.
- `/admin` responde 302 → `/admin/login/?next=/admin/` sem sessão (comportamento
  normal do Django, confirmado).
- `default_auto_field` do app `core` estava faltando (Django gerou warning
  `W042`) — corrigido em `core/apps.py` antes de gerar a migration, pra não deixar
  isso pra trás.

## Arquivos
`backend/core/models.py`, `backend/core/admin.py`, `backend/core/apps.py`,
`backend/core/migrations/0001_initial.py`

## Addendum (2026-08-07)
Cliente recusou o multiplicador fixo (1.30×), quer taxa variável por faixa de
preço (ex: abaixo de 100 EUR uma taxa, entre 100-500 outra). Ainda não mandou
os valores.

- [x] Model `MarginTier` — faixa (`min_price`/`max_price`) + `mode`/`value`
      (mesma estrutura fixed_amount/multiplier da `MarginRule`). Editável via
      `/admin`, sem deploy.
- [x] `apply_margin()` agora percorre as `MarginTier` cadastradas e usa a
      primeira que bate com o preço; se nenhuma existir/bater, cai pra
      `MarginRule` (mantém o default de 50 EUR já orçado).
- [x] Migration `0002_margintier.py` criada e aplicada.
- Cadastro de faixas fica vazio até o cliente confirmar os percentuais — ver
  `investigar.md`.

## Addendum (2026-08-12) — substituição completa por tabela de preços
Cliente respondeu com uma tabela concreta de interpolação linear (custo→venda),
não faixas percentuais. `MarginRule` e `MarginTier` **removidos** (não mantidos
como fallback morto) e substituídos por `PriceTablePoint`. Detalhe completo em
`docs/PRICING.md`. `apply_margin()` continua com a mesma assinatura — nada em
`search_views.py`/`views.py` precisou mudar.

- [x] Migration `0004` (remove `MarginRule`/`MarginTier`, cria `PriceTablePoint`)
      e `0005` (data migration, popula os 17 pontos exatos do cliente).
- [x] Todos os pontos conferidos individualmente contra os exemplos do arquivo do
      cliente — batem exato, incluindo arredondamento (`ROUND_HALF_UP`, pra bater
      com `Math.round()` do JS original).
