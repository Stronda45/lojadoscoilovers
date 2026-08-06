"""Conector para dtsshop.de.

Endpoints confirmados ao vivo (ver /Users/pablo/Project/famaInPecas/planejamento.md):
- getAllCarData / getGroups: JSON publico, GET simples, sem sessao.
- GetProductsPriceAndAvailability: precisa de sessao Magento + form_key (CSRF) +
  header X-Requested-With, senao devolve 302 "Invalid form key".
- Listagem de produtos filtrada por carro (list_products/search): SO e servida numa
  navegacao real de navegador (Sec-Fetch-Dest: document). Confirmado que fetch()/
  requests/curl com os MESMOS cookies e headers de navegacao forcados NAO funcionam
  (fingerprint de conexao, nao cookie/header) — por isso usa Playwright aqui, e so
  aqui. As outras 3 funcoes continuam em requests puro (mais leve, mais rapido).
"""

import re

import requests
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.dtsshop.de/en"
COUCH_ADAPTER = f"{BASE_URL}/fwd_php/couch_adapter/get.php"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
FORM_KEY_RE = re.compile(r'name="form_key"\s+type="hidden"\s+value="([^"]+)"')
TIMEOUT = 10


class SupplierError(Exception):
    """Erro ao consultar o dtsshop.de (rede, formato inesperado, bloqueio, etc.)."""


def _session_with_form_key() -> tuple[requests.Session, str]:
    """Abre uma sessao real (cookies) e extrai o form_key da home — necessario
    pra qualquer POST autenticado por sessao (ex: preco/estoque)."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    try:
        resp = session.get(f"{BASE_URL}/", timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise SupplierError(f"Falha ao abrir sessao no dtsshop.de: {exc}") from exc

    match = FORM_KEY_RE.search(resp.text)
    if not match:
        raise SupplierError("form_key nao encontrado na home do dtsshop.de (site mudou?)")
    return session, match.group(1)


def get_car_data() -> dict:
    """Marcas/modelos/motorizacoes. GET publico, sem sessao."""
    try:
        resp = requests.get(
            f"{COUCH_ADAPTER}/getAllCarData",
            params={"year": ""},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise SupplierError(f"Falha ao buscar dados de veiculo: {exc}") from exc
    except ValueError as exc:
        raise SupplierError(f"Resposta invalida (nao-JSON) de getAllCarData: {exc}") from exc


def get_categories(car_id: str) -> list[dict]:
    """Categorias de pecas disponiveis para um veiculo. GET publico, sem sessao."""
    try:
        resp = requests.get(
            f"{COUCH_ADAPTER}/getGroups",
            params={"car_id": car_id, "brand_filter": ""},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise SupplierError(f"Falha ao buscar categorias (car_id={car_id}): {exc}") from exc
    except ValueError as exc:
        raise SupplierError(f"Resposta invalida (nao-JSON) de getGroups: {exc}") from exc


def get_price_and_availability(product_ids: list[str]) -> dict:
    """Preco e disponibilidade em tempo real. Precisa de sessao + form_key."""
    if not product_ids:
        return {}

    session, form_key = _session_with_form_key()

    data = [("idarr[]", pid) for pid in product_ids]
    data.append(("form_key", form_key))

    try:
        resp = session.post(
            f"{BASE_URL}/productfinder/ajax/GetProductsPriceAndAvailability",
            data=data,
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{BASE_URL}/",
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise SupplierError(f"Falha ao buscar preco/estoque: {exc}") from exc

    try:
        payload = resp.json()
    except ValueError as exc:
        raise SupplierError(
            "Resposta invalida (nao-JSON) de GetProductsPriceAndAvailability "
            "— provavel form_key rejeitado ou site mudou."
        ) from exc

    # Resposta e uma lista de dicts de 1 chave cada: [{"<id>": {...}}, ...]
    result: dict = {}
    for item in payload:
        result.update(item)
    return result


# JS injetado via Playwright: extrai os dados de produto direto do view-model
# Knockout (ko.dataFor), em vez de fazer parsing fragil de HTML/CSS. Cada
# ".product-box.card" corresponde a um group_name (ex: uma variante de cor), que por
# sua vez tem uma lista "products" (o produto de fato, com "id" numerico).
_EXTRACT_PRODUCTS_JS = """
() => new Promise((resolve) => {
  require(['ko'], (ko) => {
    const boxes = document.querySelectorAll('.product-box.card');
    const groups = [];
    boxes.forEach((box) => {
      const data = ko.dataFor(box);
      if (data) groups.push(JSON.parse(JSON.stringify(data)));
    });
    resolve(groups);
  });
})
"""


def _extract_products_via_browser(url: str, car_cookies: dict[str, str] | None) -> list[dict]:
    """Abre a pagina num Chromium headless (navegacao real) e extrai os grupos de
    produto renderizados via Knockout. Levanta SupplierError em qualquer falha."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                context = browser.new_context(user_agent=USER_AGENT)
                if car_cookies:
                    context.add_cookies(
                        [
                            {
                                "name": name,
                                "value": str(value),
                                "domain": "www.dtsshop.de",
                                "path": "/",
                            }
                            for name, value in car_cookies.items()
                        ]
                    )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=TIMEOUT * 1000)
                groups = page.evaluate(_EXTRACT_PRODUCTS_JS)
            finally:
                browser.close()
    except Exception as exc:  # noqa: BLE001 — playwright levanta varios tipos distintos
        raise SupplierError(f"Falha ao renderizar/extrair produtos ({url}): {exc}") from exc

    if not isinstance(groups, list):
        raise SupplierError("Formato inesperado ao extrair produtos (site mudou?)")
    return groups


def _flatten_product_groups(groups: list[dict]) -> list[dict]:
    """Cada 'group' pode conter varios produtos (ex: variantes). Achata pra uma
    lista simples de produtos com os campos que a busca precisa."""
    items = []
    for group in groups:
        for product in group.get("products", []):
            attrs = product.get("attribute", {})
            part_no = attrs.get("att_1", {}).get("wert", "")
            image = None
            pictorama = product.get("pictorama") or []
            if pictorama:
                image = pictorama[0]["url"] + pictorama[0]["id"]
            items.append(
                {
                    "product_id": str(product.get("id")),
                    "name": group.get("group_name", ""),
                    "part_no": part_no,
                    "brand": product.get("marken_name", ""),
                    "image": image,
                }
            )
    return items


def list_products(category_id: str, car_cookies: dict[str, str] | None = None) -> list[dict]:
    """Lista produtos de uma categoria (pgs=<category_id>), opcionalmente filtrada
    por veiculo via cookies car_selector_make/model/car (ver get_car_data/
    get_categories pra obter esses IDs)."""
    url = f"{BASE_URL}/shop?pgs=%5B{category_id}%5D"
    groups = _extract_products_via_browser(url, car_cookies)
    return _flatten_product_groups(groups)


def search(query: str, car_cookies: dict[str, str] | None = None) -> list[dict]:
    """Busca por texto livre (numero de peca, codigo de configuracao, etc.)."""
    url = f"{BASE_URL}/catalogsearch/result/?q={query}"
    groups = _extract_products_via_browser(url, car_cookies)
    return _flatten_product_groups(groups)
