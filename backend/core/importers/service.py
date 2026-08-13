"""Orquestra parser + upsert no banco (Fase 2, task 04). Upsert por
(supplier, external_reference) — produto que sumiu do arquivo mais recente
vira active=False, nunca é apagado."""

from ..models import ImportedProduct, ImportedProductFitment, Supplier
from .base import ParsedProduct
from .mts import parse_mts
from .security import UploadValidationError, validate_upload
from .ta_technix import parse_ta_technix_zip
from .wheels import parse_wheels_xlsx

SUPPLIER_SLUGS = {
    "mts": ("MTS", parse_mts, ".csv"),
    "ta-technix": ("TA Technix", parse_ta_technix_zip, ".zip"),
    "cheney": ("Cheney", parse_wheels_xlsx, ".xlsx"),
    "es2wheels": ("ES2WHEELS", parse_wheels_xlsx, ".xlsx"),
}

# Chaves de raw_attributes que cada parser produz — fixas no código (não
# dependem do arquivo enviado). Usado pra montar as opções de
# Supplier.selected_fields no admin (quais campos o cliente quer exibir).
SUPPLIER_FIELD_CHOICES = {
    "mts": ["housing", "type", "body_type", "drive_type", "fuel_type", "weight"],
    "ta-technix": ["ean_code", "uvp_sugerido", "liefermenge"],
    "cheney": ["brand", "model", "size", "pcd", "et", "cb", "finish", "stock"],
    "es2wheels": ["brand", "model", "size", "pcd", "et", "cb", "finish", "stock"],
}


class ImportResult:
    def __init__(self):
        self.created = 0
        self.updated = 0
        self.deactivated = 0


def import_supplier_file(supplier_slug: str, filename: str, file_bytes: bytes) -> ImportResult:
    if supplier_slug not in SUPPLIER_SLUGS:
        raise UploadValidationError(
            f"Fornecedor desconhecido: {supplier_slug!r}. Opções: {', '.join(SUPPLIER_SLUGS)}."
        )

    supplier_name, parser, expected_ext = SUPPLIER_SLUGS[supplier_slug]
    ext = validate_upload(filename, len(file_bytes), file_bytes[:16])
    if ext != expected_ext:
        raise UploadValidationError(
            f"{supplier_name} espera um arquivo {expected_ext}, recebi {ext}."
        )

    parsed: dict[str, ParsedProduct] = parser(file_bytes)

    supplier, _ = Supplier.objects.get_or_create(
        slug=supplier_slug, defaults={"name": supplier_name}
    )

    result = ImportResult()
    seen_references = set(parsed.keys())

    existing = {
        p.external_reference: p
        for p in ImportedProduct.objects.filter(supplier=supplier, external_reference__in=seen_references)
    }

    to_create = []
    to_update = []

    for reference, item in parsed.items():
        if reference in existing:
            product = existing[reference]
            product.title = item.title
            product.description = item.description
            product.cost_price = item.cost_price
            product.image_url = item.image_url
            product.category = item.category
            product.raw_attributes = item.raw_attributes
            product.active = True
            to_update.append(product)
        else:
            to_create.append(
                ImportedProduct(
                    supplier=supplier,
                    external_reference=reference,
                    title=item.title,
                    description=item.description,
                    cost_price=item.cost_price,
                    image_url=item.image_url,
                    category=item.category,
                    raw_attributes=item.raw_attributes,
                    active=True,
                )
            )

    if to_create:
        ImportedProduct.objects.bulk_create(to_create, batch_size=500)
        result.created = len(to_create)
    if to_update:
        ImportedProduct.objects.bulk_update(
            to_update,
            ["title", "description", "cost_price", "image_url", "category", "raw_attributes", "active"],
            batch_size=500,
        )
        result.updated = len(to_update)

    # Desativa só dentro das categorias presentes NESTE arquivo — a MTS manda
    # 1 arquivo por categoria (coilovers, molas, etc), então um upload de
    # "Coilover kits" não pode apagar (desativar) o que já foi importado de
    # "Adjustable Springs" só porque não está neste arquivo. Fornecedores
    # sem categoria (TA Technix, tudo em 1 arquivo só) caem no caso
    # `categories_in_file` vazio → desativa no fornecedor inteiro, que é o
    # comportamento certo pra esses (1 upload = catálogo completo).
    categories_in_file = {item.category for item in parsed.values() if item.category}
    deactivate_qs = ImportedProduct.objects.filter(supplier=supplier, active=True).exclude(
        external_reference__in=seen_references
    )
    if categories_in_file:
        deactivate_qs = deactivate_qs.filter(category__in=categories_in_file)
    result.deactivated = deactivate_qs.update(active=False)

    # Fitments: recria do zero pra cada produto tocado neste import — mais
    # simples e correto que tentar diffar (evita acumular duplicata se o
    # fornecedor reordenar linhas entre exports).
    all_products = {p.external_reference: p for p in ImportedProduct.objects.filter(
        supplier=supplier, external_reference__in=seen_references,
    )}
    ImportedProductFitment.objects.filter(product__in=all_products.values()).delete()

    fitments_to_create = []
    for reference, item in parsed.items():
        product = all_products.get(reference)
        if not product or not item.fitments:
            continue
        for fitment in item.fitments:
            fitments_to_create.append(
                ImportedProductFitment(
                    product=product,
                    make=fitment["make"],
                    model=fitment["model"],
                    variant=fitment.get("variant", ""),
                    year_range=fitment.get("year_range", ""),
                )
            )
    if fitments_to_create:
        ImportedProductFitment.objects.bulk_create(fitments_to_create, batch_size=1000)

    return result
