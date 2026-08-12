"""Utilitários compartilhados pelos parsers de fornecedor."""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

# CSV injection: celula comecando com um desses vira formula se alguem abrir
# o dado depois num Excel/planilha (ex: relatorio exportado pro cliente).
_FORMULA_PREFIXES = ("=", "+", "-", "@")


def sanitize_text(value: str | None) -> str:
    """Neutraliza CSV injection prefixando com aspas simples — mesma tecnica
    usada por exportadores (Google Sheets, etc). Nao afeta a leitura normal
    do valor como texto."""
    if not value:
        return value or ""
    value = value.strip()
    if value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def parse_decimal_european(raw: str | None) -> Decimal | None:
    """Formato "1.399,00" ou "707,25" ou "699" (ponto = milhar opcional,
    virgula = decimal — usado tanto pela TA Technix quanto pela MTS,
    confirmado nos arquivos reais: "699" sem casas decimais, "707,25" com)."""
    if not raw or not raw.strip():
        return None
    cleaned = raw.strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


@dataclass
class ParsedProduct:
    """Um produto extraído de uma linha (ou grupo de linhas) do arquivo do
    fornecedor — formato comum antes de virar `ImportedProduct` no banco."""

    external_reference: str
    title: str
    description: str = ""
    cost_price: Decimal | None = None
    image_url: str = ""
    category: str = ""
    raw_attributes: dict = field(default_factory=dict)
    fitments: list[dict] = field(default_factory=list)
    # cada fitment: {"make":..., "model":..., "variant":..., "year_range":...}
