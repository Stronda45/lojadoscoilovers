jj20405# Investigar depois

Coisas que identificamos mas não vale parar o sprint agora pra resolver. Ler antes de
fechar cada fase, pra não esquecer.

## Pendentes

- [ ] **`search()` do conector dtsshop.de — testada ao vivo, resultado
      inconclusivo** (task 08): navegação funciona sem erro (confirma task 03),
      mas retornou "Your search returned no results" tanto pra termo genérico
      ("coilover") quanto pra um nº de peça exato de um produto que existe
      (ex: "299100180", confirmado via listagem por categoria no mesmo teste).
      O input do site diz "Search for article no. or configuration code" —
      supeita e formato exato (código completo? case-sensitive?) ainda não
      confirmado. Não bloqueia a busca principal (marca/modelo/categoria, essa
      sim testada e funcionando 100%), só a busca por texto livre.
- [ ] **Playwright lança um browser novo a cada chamada** (`list_products`/`search`).
      Funciona pra baixo volume, mas é lento (alguns segundos por chamada) e pesado
      em memória sob concorrência. Se o volume de uso crescer, revisar para reusar
      uma instância de browser (pool) em vez de `chromium.launch()` por request.
- [ ] **Postgres local quebrado** (Homebrew `postgresql@13`, lib `icu4c` faltando).
      Não bloqueia (SQLite local resolve por ora), mas resolver antes de precisar
      testar algo Postgres-específico localmente.
- [ ] **Link direto pro produto no e-mail de alerta de pedido** (task 07): não
      confirmamos o padrão de URL da página de detalhe de produto do
      dtsshop.de (só validamos endpoints de listagem/busca). E-mail hoje só
      manda o `id` do fornecedor + instrução pra buscar manualmente. Se
      confirmarmos a URL, dá pra linkar direto.
- [ ] **Contagem de categoria vs. resultados retornados** (task 08): categoria
      "Top mount" mostrava `count: 2` mas a busca filtrada por carro devolveu
      1 produto. Provavelmente o `count` da categoria é do catálogo geral, não
      filtrado pelo carro selecionado — não é erro no código (testado ao
      vivo, sem exceção), só uma discrepância de expectativa. Não afeta a
      função (mostra o que realmente está disponível pra aquele carro).
- [ ] **Fornecedor retorna "not found" pra alguns `product_id`** — visto ao
      vivo em produtos de rodas/wheels (categoria "Unlimited Base Wheels...",
      AUDI/ACURA). `GetProductsPriceAndAvailability` devolve
      `["<id> not found."]` em vez do dict de preço pra esses IDs, mesmo eles
      aparecendo normalmente na listagem. Causou um 500 (corrigido — task 08,
      agora trata como indisponível). Não investigado o motivo raiz (produto
      descontinuado no fornecedor? id de listagem ≠ id de preço pra rodas?).
## Resolvidas (mantido como histórico rápido)

- ~~Margem por faixa de preço~~ (2026-08-12) — cliente respondeu com uma tabela de
  interpolação linear (`regra_de_preços.md`, na raiz do famaInPecas), não faixas
  fixas. `MarginRule`/`MarginTier` foram **removidos** e substituídos por
  `PriceTablePoint` + `apply_margin()` reescrito (`core/models.py`). Valores exatos
  da tabela do cliente conferidos um a um contra o JS de referência dele — todos
  batem. Ver `docs/PRICING.md`.

- ~~Como pegar `product_id` numérico na listagem de produtos~~ — `ko.dataFor()` via
  Playwright (task 03).
- ~~`GetProductsPriceAndAvailability` retornando 302 "Invalid form key"~~ — precisa
  de sessão + form_key + header `X-Requested-With` (task 02).
- ~~Listagem de produtos não abre via `requests`/`curl`~~ — fingerprint de conexão,
  só navegação real de browser funciona (task 03, decisão: Playwright).
