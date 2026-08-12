# 02 — Painel admin (dono + funcionário)

Bloqueada por: -

## Contexto
Contratado: "painel para você e seu funcionário acompanharem os pedidos e
marcarem como 'comprado no fornecedor' / 'entregue'." Cliente confirmou
(`questionario.txt`, 4.2) que vai operar com mais 1 funcionário.

**Decisão**: usar o Django Admin já existente (`core/admin.py`), configurado com
permissões, em vez de construir uma tela React nova do zero. A proposta já vende
isso — "autenticação e área administrativa madura prontas de fábrica" é citado como
parte da stack técnica. O orçamento de "design de verdade" é pro que o cliente final
vê (loja), não pro painel interno.

## Objetivo
Dono vê e gerencia tudo; funcionário vê/atualiza só o que precisa pra cumprir
pedido, sem acesso a configuração de margem nem à lista solta de todos os clientes
fora do contexto de um pedido.

## Tarefas
- [ ] Grupo Django "Funcionário" — permissões: view/change em `Order`/`OrderItem`,
      view em `Customer` (precisa ver endereço/telefone pra cumprir o pedido — ver
      decisão já tomada com o usuário sobre isso). **Sem** acesso a `MarginRule`/
      `MarginTier`/`User` (auth) geral.
- [ ] Django admin actions no `OrderAdmin` — marcar seleção como "comprado no
      fornecedor" ou "entregue" direto da listagem, sem abrir cada pedido.
- [ ] Criar o usuário do funcionário (`is_staff=True`, sem `is_superuser`, no grupo
      "Funcionário") quando o cliente confirmar quem é/e-mail dele.

## Aceite
- [ ] Login do dono (superuser) continua vendo tudo, sem mudança.
- [ ] Login de teste no grupo "Funcionário": vê `Order`, `OrderItem`, `Customer`;
      não vê `MarginRule`/`MarginTier` no menu do admin.
- [ ] Marcar um pedido como "entregue" via admin action funciona sem abrir o
      registro.

## Arquivos
`backend/core/admin.py`, migration/data migration pro grupo (ou criado via
`/admin` mesmo, sem código).
