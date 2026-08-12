# 03 — Testes automatizados (conector dtsshop.de)

Bloqueada por: -

## Contexto
Contratado: "testes automatizados mínimos do módulo de integração com o
dtsshop.de (a parte mais frágil do sistema — reduz risco de quebra silenciosa)."
Fase 1 foi ao ar sem testes (decisão já avisada ao cliente, risco assumido por ele
— `proposta-v2-intermediario.pdf`, seção de riscos).

## Objetivo
Cobertura mínima que pega quebra silenciosa se o dtsshop.de mudar formato de
resposta, sem inflar o escopo pra suite completa (não é o contratado).

## Tarefas
- [ ] `core/connectors/dtsshop.py`: mockar `requests.get`/`requests.post` e
      `playwright.sync_api.sync_playwright` (`unittest.mock.patch`) — testar, pra
      cada função pública (`get_car_data`, `get_models`, `get_cars`,
      `get_categories`, `get_price_and_availability`, `list_products`, `search`):
      parsing do caso feliz + `SupplierError` em falha de rede/JSON inválido.
- [ ] `core/search_views.py::_enrich_with_price` — teste de regressão específico
      pro bug já corrigido em produção (fornecedor devolve lista
      `["<id> not found."]` em vez de dict de preço).
- [ ] `_flatten_product_groups` — teste da URL de imagem (`IMAGE_SIZE_PREFIX`,
      bug já corrigido de imagem quebrada).
- [ ] Django `TestCase` padrão (`python manage.py test`) — sem dependência nova
      (pytest-django não é necessário pro escopo "mínimo").

## Aceite
- [ ] `python manage.py test` roda sem tocar a rede de verdade (tudo mockado).
- [ ] Teste falha de propósito se alguém reintroduzir o bug do `_enrich_with_price`
      (assert específico pro formato de erro do fornecedor).

## Arquivos
`backend/core/tests.py` (ou quebrar em `backend/core/tests/` se ficar grande —
decidir na hora conforme volume).
