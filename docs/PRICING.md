# Regra de preço (margem) — histórico e decisão atual

## Decisão atual (2026-08-12): tabela de interpolação linear

Cliente respondeu a pendência de margem com uma tabela concreta de pontos
(custo → preço de venda) e uma função de referência em JS
(`/Users/pablo/Project/famaInPecas/regra_de_preços.md`, fora deste repo — arquivo
do cliente, mesma pasta de outros documentos de negociação).

**Implementação**: `PriceTablePoint` (`core/models.py`) — cada linha é um ponto
`(cost, sale_price)`, editável via `/admin`, sem deploy pra ajustar. `apply_margin()`
reescrito pra reproduzir exatamente `calcularPVPLDC()` do cliente:

- **Abaixo do primeiro ponto**: mantém a proporção do primeiro ponto (hoje
  29/10 = 2.9×) — calculado dinamicamente a partir do primeiro ponto da tabela, não
  hardcoded, então se o cliente editar o primeiro ponto via admin, a proporção
  ajusta sozinha.
- **Entre dois pontos**: interpolação linear.
- **Acima do último ponto**: mesma lógica do "abaixo", com a proporção do último
  ponto (hoje 3999/3000 = 1.333×) — também dinâmico.
- **Arredondamento**: ao euro mais próximo, com `ROUND_HALF_UP` (não o `round()`
  padrão do Python, que arredonda pro par mais próximo/banker's rounding) — precisa
  ser `ROUND_HALF_UP` pra bater exatamente com `Math.round()` do JS original em
  casos de metade exata (ex: 5.00 × 2.9 = 14.50 → 15, não 14).

Os 17 pontos exatos da tabela do cliente foram cadastrados via data migration
(`core/migrations/0005_seed_price_table_points.py`) e cada um foi conferido
individualmente contra os exemplos que o próprio cliente deixou no arquivo — todos
batem exato.

## Histórico (removido)

Antes disso existiam `MarginRule` (regra fixa única — valor fixo somado ou
multiplicador, default +€50) e `MarginTier` (faixas de preço com regra própria por
faixa) — implementadas na task 04 da Fase 1 como estrutura flexível justamente
porque o valor/formato definitivo não estava confirmado ainda. Removidas nesta
mudança (não deixadas como código morto) — o `apply_margin(cost_price) -> Decimal`
continua sendo a interface pública usada por `core/search_views.py` e
`core/views.py`, então nada mais no código precisou mudar.
