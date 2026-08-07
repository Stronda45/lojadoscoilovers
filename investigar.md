jj20405# Investigar depois

Coisas que identificamos mas não vale parar o sprint agora pra resolver. Ler antes de
fechar cada fase, pra não esquecer.

## Pendentes

- [ ] **`search()` do conector dtsshop.de não testada ao vivo** (task 03). Testar
      quando o site "esfriar" das investigações anteriores.
- [ ] **Playwright lança um browser novo a cada chamada** (`list_products`/`search`).
      Funciona pra baixo volume, mas é lento (alguns segundos por chamada) e pesado
      em memória sob concorrência. Se o volume de uso crescer, revisar para reusar
      uma instância de browser (pool) em vez de `chromium.launch()` por request.
- [ ] **Postgres local quebrado** (Homebrew `postgresql@13`, lib `icu4c` faltando).
      Não bloqueia (SQLite local resolve por ora), mas resolver antes de precisar
      testar algo Postgres-específico localmente.
- [ ] **Margem por faixa de preço**: cliente recusou o 1.30× fixo, quer taxa
      variável por faixa (ex: <100 EUR vs 100-500 EUR), mas ainda não mandou os
      valores/percentuais de cada faixa. Estrutura já pronta (`MarginTier`,
      task 04) — só falta ele confirmar os números e cadastrar via `/admin`.

## Resolvidas (mantido como histórico rápido)

- ~~Como pegar `product_id` numérico na listagem de produtos~~ — `ko.dataFor()` via
  Playwright (task 03).
- ~~`GetProductsPriceAndAvailability` retornando 302 "Invalid form key"~~ — precisa
  de sessão + form_key + header `X-Requested-With` (task 02).
- ~~Listagem de produtos não abre via `requests`/`curl`~~ — fingerprint de conexão,
  só navegação real de browser funciona (task 03, decisão: Playwright).
