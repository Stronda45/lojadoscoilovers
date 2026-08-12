"""Parser do fornecedor MTS. Formato conhecido (arquivo real inspecionado,
2026-08-12) — CSV separado por ';', BOM UTF-8, uma linha por combinação
peça×veículo compatível (mesmo part_number repete várias vezes).

Campos usados: category_name, part_number, name, make, model, engine, year,
msrp, product_notes, images. O resto vira raw_attributes.
"""

import csv
import io

from .base import ParsedProduct, parse_decimal_european, sanitize_text


def parse_mts(file_bytes: bytes) -> dict[str, ParsedProduct]:
    """Devolve {external_reference: ParsedProduct}, já deduplicado (mesmo
    part_number em várias linhas vira 1 produto + N fitments)."""
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")

    products: dict[str, ParsedProduct] = {}

    for row in reader:
        reference = (row.get("part_number") or "").strip()
        if not reference:
            continue

        if reference not in products:
            image_url = ""
            images_raw = row.get("images") or ""
            if images_raw:
                image_url = images_raw.split(",")[0].strip()

            products[reference] = ParsedProduct(
                external_reference=reference,
                title=sanitize_text(row.get("name")),
                description=sanitize_text(row.get("product_notes")),
                cost_price=parse_decimal_european(row.get("msrp")),
                image_url=image_url,
                category=sanitize_text(row.get("category_name")),
                raw_attributes={
                    "housing": row.get("housing", ""),
                    "type": row.get("type", ""),
                    "body_type": row.get("body_type", ""),
                    "drive_type": row.get("drive_type", ""),
                    "fuel_type": row.get("fuel_type", ""),
                    "weight": row.get("weight", ""),
                },
            )

        make = (row.get("make") or "").strip()
        model = (row.get("model") or "").strip()
        if make and model:
            fitment = {
                "make": make,
                "model": model,
                "variant": (row.get("engine") or "").strip(),
                "year_range": (row.get("year") or "").strip(),
            }
            if fitment not in products[reference].fitments:
                products[reference].fitments.append(fitment)

    return products
