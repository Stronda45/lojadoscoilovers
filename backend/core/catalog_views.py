"""Catálogo importado (Excel/CSV de outros fornecedores) — Fase 2, task 04.
Busca é pública (consumida pelo frontend, como /search do dtsshop.de). Upload
fica dentro do Django Admin (`core/admin.py::ImportedProductAdmin`), não
aqui — consistente com a decisão da task 02 (painel = Django Admin, sessão,
não token de API). Ver docs/EXCEL-IMPORT.md.

Busca dupla (texto + veículo) — cliente confirmou que quer os dois
(perguntas-para-cliente.txt, 7.4). Cascata de veículo própria, sourced do
`ImportedProductFitment` (dado já no banco, sem chamada externa) — só
MTS/TA Technix têm fitment; rodas (Cheney/ES2WHEELS) não aparecem nesses
endpoints, só na busca por texto/categoria."""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ImportedProduct, ImportedProductFitment


def _fitment_qs():
    return ImportedProductFitment.objects.filter(product__active=True)


@api_view(["GET"])
def catalog_makes(request):
    makes = _fitment_qs().order_by("make").values_list("make", flat=True).distinct()
    return Response(list(makes))


@api_view(["GET"])
def catalog_models(request, make):
    models = (
        _fitment_qs().filter(make=make).order_by("model").values_list("model", flat=True).distinct()
    )
    return Response(list(models))


@api_view(["GET"])
def catalog_variants(request):
    make = request.query_params.get("make", "")
    model = request.query_params.get("model", "")
    if not make or not model:
        return Response(
            {"detail": 'Parâmetros "make" e "model" são obrigatórios.'}, status=400
        )
    variants = (
        _fitment_qs()
        .filter(make=make, model=model)
        .exclude(variant="")
        .order_by("variant")
        .values_list("variant", flat=True)
        .distinct()
    )
    return Response(list(variants))


@api_view(["GET"])
def catalog_search(request):
    """`?q=<texto>` e/ou `?category=<categoria>` (busca livre) combináveis com
    `?make=&model=&variant=` (busca por veículo, só produtos com fitment —
    MTS/TA Technix)."""
    q = request.query_params.get("q", "").strip()
    category = request.query_params.get("category", "").strip()
    make = request.query_params.get("make", "").strip()
    model = request.query_params.get("model", "").strip()
    variant = request.query_params.get("variant", "").strip()

    qs = ImportedProduct.objects.filter(active=True).select_related("supplier")
    if q:
        qs = qs.filter(title__icontains=q)
    if category:
        qs = qs.filter(category__icontains=category)
    if make:
        qs = qs.filter(fitments__make=make)
    if model:
        qs = qs.filter(fitments__model=model)
    if variant:
        qs = qs.filter(fitments__variant=variant)
    if make or model or variant:
        qs = qs.distinct()

    qs = qs[:100]

    return Response(
        [
            {
                "id": p.id,
                "supplier": p.supplier.name,
                "external_reference": p.external_reference,
                "title": p.title,
                "description": p.description,
                "price": str(p.sale_price) if p.sale_price is not None else None,
                "image_url": p.image_url,
                "category": p.category,
            }
            for p in qs
        ]
    )
