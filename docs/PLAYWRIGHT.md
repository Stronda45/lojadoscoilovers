# Playwright — por que existe, onde é usado, o que muda no deploy

## Por que existe

O conector do dtsshop.de (`backend/core/connectors/dtsshop.py`) tem 4 funções. 3 delas
(`get_car_data`, `get_categories`, `get_price_and_availability`) são chamadas HTTP
simples via `requests` — leves, rápidas, sem navegador.

A 4ª, listagem de produtos (`list_products` e `search`), **precisa de Playwright**
(Chromium headless real). Motivo, confirmado por investigação ao vivo (ver task 03):

- O filtro por veículo é armazenado em cookies (`car_selector_make/model/car`).
- Mesmo com esses cookies certos, o dtsshop.de só devolve a página completa (com os
  produtos) numa **navegação real de navegador** (`Sec-Fetch-Dest: document`).
- Testamos `fetch()` de dentro da própria aba autenticada, e `curl`/`requests`
  imitando headers de navegação manualmente — nenhum funciona. É fingerprint de
  conexão (TLS/protocolo), não é cookie nem header que dá pra copiar.
- Um navegador real (Playwright) é a única forma comprovada de conseguir esse dado.

## Onde é usado

Só em `_extract_products_via_browser()`, chamada por `list_products()` e `search()`
em `backend/core/connectors/dtsshop.py`. As outras 3 funções do conector **não**
dependem de Playwright.

## Como funciona (resumo técnico)

1. Abre um Chromium headless.
2. Injeta os cookies de veículo (`car_selector_make/model/car`) no contexto do
   navegador.
3. Navega (`page.goto`) até a URL da categoria ou busca — navegação real, não
   `fetch()`.
4. Executa JS na página (`page.evaluate`) que usa `ko.dataFor()` (API do Knockout,
   framework JS do site) pra ler o objeto de dados já carregado por trás de cada
   card de produto — **não** faz parsing de HTML/CSS. Mais robusto: só quebra se o
   site trocar de framework JS inteiro, não se mudar o design/CSS.
5. Fecha o navegador, devolve os dados extraídos como JSON.

## Impacto no deploy (Railway) — ver task 10 para o checklist completo

- **Build**: precisa de `Dockerfile` próprio baseado na imagem oficial
  `mcr.microsoft.com/playwright/python:v1.62.0-noble` (o build automático padrão do
  Railway não instala as dependências de sistema do Chromium).
- **Código**: em produção (container Railway, roda como root), o Chromium precisa da
  flag `--no-sandbox` — não necessário localmente no Mac.
- **Custo**: imagem maior (~1-2GB vs ~150MB) e mais RAM/CPU por request de busca
  (abre um navegador de verdade a cada chamada). Provável que o custo mensal no
  Railway fique mais alto que um backend Django comum — sem número exato ainda,
  acompanhar a fatura nos primeiros dias.
- **Latência**: busca de produtos (via Playwright) é alguns segundos mais lenta que
  preço/estoque (via `requests`). Esperado, não é bug.

## Setup local

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

Ou `make install` (já inclui esse passo — ver `Makefile`).

## Limitação conhecida / melhoria futura

Cada chamada de `list_products`/`search` abre e fecha um Chromium novo
(`chromium.launch()` por request). Funciona para baixo volume, mas é lento e pesado
sob concorrência. Se o volume de uso crescer, revisar para reusar uma instância de
browser (pool) em vez de lançar um novo a cada chamada. Registrado em
`investigar.md` (raiz do `lojadoscoilovers`).
