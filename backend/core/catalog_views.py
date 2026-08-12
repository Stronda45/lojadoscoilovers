"""Catálogo importado (Excel/CSV de outros fornecedores) — Fase 2, task 04.
Busca é pública (consumida pelo frontend, como /search do dtsshop.de). Upload
fica dentro do Django Admin (`core/admin.py::ImportedProductAdmin`), não
aqui — consistente com a decisão da task 02 (painel = Django Admin, sessão,
não token de API). Ver docs/EXCEL-IMPORT.md."""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ImportedProduct


@api_view(["GET"])
def catalog_search(request):
    """Catálogo importado — separado da busca do dtsshop.de (decisão já
    tomada: sem cascata de veículo compartilhada). Busca simples por texto/
    categoria; cascata de veículo própria (MTS/TA Technix têm fitment) fica
    pendente da resposta do cliente (perguntas-para-cliente.txt, 7.4)."""
    q = request.query_params.get("q", "").strip()
    category = request.query_params.get("category", "").strip()

    qs = ImportedProduct.objects.filter(active=True).select_related("supplier")
    if q:
        qs = qs.filter(title__icontains=q)
    if category:
        qs = qs.filter(category__icontains=category)

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
