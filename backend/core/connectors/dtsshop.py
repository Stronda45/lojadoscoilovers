"""Conector para dtsshop.de.

Endpoints confirmados ao vivo (ver /Users/pablo/Project/famaInPecas/planejamento.md):
- getAllCarData / getGroups: JSON publico, GET simples, sem sessao.
- GetProductsPriceAndAvailability: precisa de sessao Magento + form_key (CSRF) +
  header X-Requested-With, senao devolve 302 "Invalid form key".
"""

import re

import requests

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
