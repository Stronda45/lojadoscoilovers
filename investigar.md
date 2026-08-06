# Investigar depois

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
- [ ] **Margem "1.30"**: ainda não confirmado com o cliente se é 1,30× (+30%) ou
      1,30% (+0,013×). Código já suporta os dois modos (task 04), só falta o valor
      certo.

## Resolvidas (mantido como histórico rápido)

- ~~Como pegar `product_id` numérico na listagem de produtos~~ — `ko.dataFor()` via
  Playwright (task 03).
- ~~`GetProductsPriceAndAvailability` retornando 302 "Invalid form key"~~ — precisa
  de sessão + form_key + header `X-Requested-With` (task 02).
- ~~Listagem de produtos não abre via `requests`/`curl`~~ — fingerprint de conexão,
  só navegação real de browser funciona (task 03, decisão: Playwright).
