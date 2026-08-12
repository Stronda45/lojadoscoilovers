# 02 — Painel admin (dono + funcionário)

Bloqueada por: - · **Status: concluída** (falta só criar o usuário real do
funcionário quando o cliente confirmar quem é/e-mail)

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
- [x] Grupo Django "Funcionário" — permissões: view em `Customer`, view+change em
      `Order`, view em `OrderItem`. **Sem** acesso a `PriceTablePoint`/`User`
      (auth) geral. Criado via data migration (`0006_funcionario_group.py`), não
      manualmente pelo admin — reproduzível em qualquer ambiente (dev, produção)
      sem passo manual.
- [x] Django admin actions no `OrderAdmin` — "Marcar como 'comprado no
      fornecedor'"/"Marcar como 'entregue'", direto da listagem, em lote.
- [ ] Criar o usuário do funcionário (`is_staff=True`, sem `is_superuser`, no grupo
      "Funcionário") — **pendente**, aguardando o cliente confirmar quem é/e-mail
      (`questionario.txt`, 4.2, só diz "mais um funcionário", sem nome).

## Achado técnico (corrigido)
Primeira versão da migration criava o grupo mas **sem nenhuma permissão** —
`Permission` do Django só é criada pelo sinal `post_migrate`, que dispara depois
de *todas* as migrations rodarem, não durante. Numa instalação nova (0001 a 0006
na mesma chamada de `migrate`), as permissões de `Customer`/`Order`/`OrderItem`
ainda não existiam quando a migration tentou usá-las. Corrigido chamando
`django.contrib.auth.management.create_permissions()` explicitamente dentro da
própria migration antes de atribuir as permissões ao grupo.

## Aceite
- [x] Login do dono (superuser) continua vendo tudo, sem mudança — testado.
- [x] Login de teste no grupo "Funcionário" (via `Client` do Django, sessão HTTP
      real): vê "Order" no índice do admin, **não** vê "Price"/"Users".
- [x] Marcar pedido como "comprado no fornecedor" via action (POST real) funciona
      sem abrir o registro — status mudou de `pending` pra
      `ordered_with_supplier`, confirmado no banco.
- [x] Acesso direto a `/admin/core/pricetablepoint/` pelo funcionário → 403
      (`PermissionDenied`); pelo dono → 200.

## Arquivos
`backend/core/admin.py`, migration/data migration pro grupo (ou criado via
`/admin` mesmo, sem código).
