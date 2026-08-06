# Stack — lojadoscoilovers

## Backend
- Django + Django REST Framework
- PostgreSQL
- SMTP para e-mail (alerta de pedido) — padrão de referência em
  `famain_be/api/famainpecas/utils.py` (`core/email_utils.py` no Salonix)

## Frontend
- React
- PWA (instalável em celular/desktop)

## Deploy
- Backend + banco: Railway
- Frontend: Vercel
- Hospedagem é custo do cliente, não nosso (ver proposta)

## Fonte de dados (fornecedor)
- dtsshop.de — conector híbrido:
  - JSON limpo: dados de veículo, categorias (`getGroups`), preço/estoque
    (`GetProductsPriceAndAvailability`)
  - HTML (scraping): listagem de produtos por categoria, busca por texto
  - Detalhes técnicos completos: `/Users/pablo/Project/famaInPecas/planejamento.md`

## Por que mudou de FastAPI (V1) pra Django+DRF (V2)
V1 era proxy sem estado, sem conta de usuário — FastAPI fazia sentido (leve, sem
ORM). V2 é e-commerce real (clientes, pedidos, auth, RGPD) — Django+DRF traz isso
pronto (admin, ORM, auth) em vez de montar tudo na mão.
