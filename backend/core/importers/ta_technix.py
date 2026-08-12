"""Parser do fornecedor TA Technix. Formato conhecido (arquivo real
inspecionado, 2026-08-12) — vem num zip com 2 arquivos: um CSV de cabeçalho
separado ("CSV Kopfzeile...") e o CSV de dados de verdade, ambos separados
por ';', aspas em todo campo, decimal europeu ("1.399,00"), "#Z" como quebra
de linha dentro da descrição.

Preço de custo default: "Netto EK in EUR" (não "UVP in EUR", que é o preço
de venda que o fornecedor sugere) — mesmo padrão do resto do sistema
(margem sempre em cima do custo). Pendente confirmação do cliente
(perguntas-para-cliente.txt, 7.2) — se ele preferir usar o UVP direto, é só
trocar a coluna lida aqui.
"""

import csv
import io
import re

from .base import ParsedProduct, parse_decimal_european, sanitize_text
from .security import safe_read_zip_member

# "Hersteller" nao e sempre uma marca limpa — visto ao vivo nos dados reais:
# "passend für Audi / Seat / VW" (varias marcas juntas, prefixo em alemao
# "adequado para"), ou lixo tipo "Universell"/"1 Set" (peca universal, sem
# marca especifica — nao e erro de parsing, e o proprio dado do fornecedor).
_HERSTELLER_PREFIX_RE = re.compile(r"^passend\s+f[üu]r\s*", re.IGNORECASE)
_HERSTELLER_JUNK_VALUES = {
    "universell", "nicht belegt", "1 set", "1 stück", "1 stk", "1 swt", "",
}


def _parse_makes(raw: str) -> list[str]:
    """'Hersteller' pode ter varias marcas separadas por '/', com o prefixo
    'passend für' (alemao pra 'adequado para'). Devolve lista de marcas
    limpas — vazia se for peca universal/sem marca (nao e erro)."""
    raw = raw.strip()
    if raw.lower() in _HERSTELLER_JUNK_VALUES:
        return []
    without_prefix = _HERSTELLER_PREFIX_RE.sub("", raw).strip()
    if without_prefix.lower() in _HERSTELLER_JUNK_VALUES:
        return []
    return [make.strip() for make in without_prefix.split("/") if make.strip()]


HEADER = [
    "Artikelnummer", "EAN-Code", "Hersteller", "Modell", "Typ", "Baujahr",
    "Bezeichnung", "description", "UVP in EUR", "Netto EK in EUR", "Zulassung",
    "Leistung in KW", "KW modifiziert", "Leistung in PS", "PS modifiziert",
    "NM", "NM modifiziert", "Leistungsteigerung in %", "Hubraum", "Achse",
    "VA Last", "HA Last", "Tieferlegung", "Ausführung", "Endrohr",
    "Vergleichsnummer", "OEM Vergleichsnummer", "Wälzlager", "Material",
    "Hinweise", "Liefermenge", "KType Teilenummer", "Bildlink",
]


def parse_ta_technix_zip(zip_bytes: bytes) -> dict[str, ParsedProduct]:
    """Recebe o .zip como o fornecedor manda (não pede pra descompactar
    antes) — extração feita em memória, sem tocar o disco. O zip tem 2 CSVs
    (um de cabeçalho, pequeno, e o de dados de verdade) — pega o de dados
    pelo nome ("Preisliste" = lista de preços, estável entre exports; o
    resto do nome do arquivo muda a cada exportação nova do fornecedor)."""
    csv_bytes = safe_read_zip_member(zip_bytes, "Preisliste")
    return parse_ta_technix_csv(csv_bytes)


def parse_ta_technix_csv(file_bytes: bytes) -> dict[str, ParsedProduct]:
    text = file_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text), delimiter=";", quotechar='"')

    products: dict[str, ParsedProduct] = {}

    for row in reader:
        if len(row) < len(HEADER):
            continue
        values = dict(zip(HEADER, row))

        reference = values["Artikelnummer"].strip()
        if not reference:
            continue

        title_en = values.get("description", "").strip()
        title_de = values.get("Bezeichnung", "").strip()
        title = (title_en or title_de).split("#Z")[0]  # primeira linha, sem o resto do bloco

        description = (title_en or title_de).replace("#Z", "\n")

        products[reference] = ParsedProduct(
            external_reference=reference,
            title=sanitize_text(title),
            description=sanitize_text(description),
            cost_price=parse_decimal_european(values.get("Netto EK in EUR")),
            image_url=values.get("Bildlink", "").strip(),
            category="",
            raw_attributes={
                "ean_code": values.get("EAN-Code", ""),
                "uvp_sugerido": values.get("UVP in EUR", ""),
                "liefermenge": values.get("Liefermenge", ""),
            },
            fitments=[
                {
                    "make": make,
                    "model": values["Modell"].strip(),
                    "variant": values.get("Typ", "").strip(),
                    "year_range": values.get("Baujahr", "").strip(),
                }
                for make in _parse_makes(values.get("Hersteller", ""))
            ],
        )

    return products
