# 03 — Testes automatizados (conector dtsshop.de)

Bloqueada por: - · **Status: concluída**

## Contexto
Contratado: "testes automatizados mínimos do módulo de integração com o
dtsshop.de (a parte mais frágil do sistema — reduz risco de quebra silenciosa)."
Fase 1 foi ao ar sem testes (decisão já avisada ao cliente, risco assumido por ele
— `proposta-v2-intermediario.pdf`, seção de riscos).

## Objetivo
Cobertura mínima que pega quebra silenciosa se o dtsshop.de mudar formato de
resposta, sem inflar o escopo pra suite completa (não é o contratado).

## Tarefas
- [x] `core/connectors/dtsshop.py`: mockado `requests.get`/`requests.Session` e
      `sync_playwright` — caminho feliz + `SupplierError` em falha de rede/JSON
      inválido pra `get_car_data`, `get_models`, `get_cars`, `get_categories`,
      `_session_with_form_key`, `get_price_and_availability`,
      `_extract_products_via_browser`. (`list_products`/`search` não testados
      isoladamente — são só composição de `_extract_products_via_browser` +
      `_flatten_product_groups`, ambos já cobertos direto; testar de novo seria
      duplicar.)
- [x] `core/search_views.py::_enrich_with_price` — regressão do bug real
      (fornecedor devolve lista `["<id> not found."]`) + casos de produto
      ausente/erro do fornecedor.
- [x] `_flatten_product_groups` — regressão da URL de imagem
      (`IMAGE_SIZE_PREFIX`).
- [x] `core/models.py::apply_margin` — cobertura extra (não estava no escopo
      original desta task, mas é a outra peça crítica de preço/negócio que não
      tinha teste nenhum): ponto exato da tabela, interpolação, extrapolação
      acima/abaixo, tabela vazia levanta erro em vez de vender errado.
- [x] Django `TestCase` padrão (`python manage.py test`) — sem dependência nova.

## Aceite
- [x] `python manage.py test core` — 32 testes, todos passando, nada toca rede
      de verdade (`requests`/`Session`/`sync_playwright` mockados em 100% dos
      casos).
- [x] Teste da lista `["<id> not found."]` falharia (TypeError) se o bug fosse
      reintroduzido — cobre a regressão real que aconteceu em produção.

## Arquivos
`backend/core/tests.py`
