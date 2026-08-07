"""Endpoints de catálogo/busca — cascata de veículo (marca->modelo->motor)
e listagem de produtos com preço (já com margem) e disponibilidade."""

from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .connectors import dtsshop
from .connectors.dtsshop import SupplierError
from .models import apply_margin


def _enrich_with_price(items: list[dict]) -> list[dict]:
    """Junta preço/disponibilidade (fornecedor) a cada item da listagem/busca
    e já aplica a margem — o frontend nunca ve o preço de custo."""
    if not items:
        return items

    product_ids = [item["product_id"] for item in items]
    try:
        price_data = dtsshop.get_price_and_availability(product_ids)
    except SupplierError:
        price_data = {}

    enriched = []
    for item in items:
        info = price_data.get(item["product_id"])
        # Fornecedor às vezes devolve `["<id> not found."]` (lista de erro) em
        # vez do dict de preço — acontece pra alguns produtos (visto em
        # rodas/wheels). Trata como indisponível em vez de quebrar a busca
        # inteira por causa de 1 produto.
        if isinstance(info, dict) and "price" in info:
            cost_price = Decimal(str(info["price"]))
            item = {
                **item,
                "price": str(apply_margin(cost_price)),
                "availability": info.get("availability"),
            }
        else:
            item = {**item, "price": None, "availability": None}
        enriched.append(item)
    return enriched


def _car_cookies(request) -> dict[str, str] | None:
    car_id = request.query_params.get("car_id")
    if not car_id:
        return None
    cookies = {"car_selector_car": car_id}
    make_id = request.query_params.get("make_id")
    model_id = request.query_params.get("model_id")
    if make_id:
        cookies["car_selector_make"] = make_id
    if model_id:
        cookies["car_selector_model"] = model_id
    return cookies


@api_view(["GET"])
@permission_classes([AllowAny])
def vehicle_makes(request):
    try:
        data = dtsshop.get_car_data()
    except SupplierError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    return Response(data.get("makes", []))


@api_view(["GET"])
@permission_classes([AllowAny])
def vehicle_models(request, make_id):
    try:
        data = dtsshop.get_models(make_id)
    except SupplierError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def vehicle_cars(request):
    make_id = request.query_params.get("make_id")
    model_id = request.query_params.get("model_id")
    if not make_id or not model_id:
        return Response(
            {"detail": "Parâmetros \"make_id\" e \"model_id\" são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        data = dtsshop.get_cars(make_id, model_id)
    except SupplierError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def vehicle_categories(request, car_id):
    try:
        data = dtsshop.get_categories(car_id)
    except SupplierError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    """`?q=<texto>` (busca livre) ou `?category_id=<id>` (listagem por
    categoria) — ambos aceitam `car_id` (+ `make_id`/`model_id`) opcional pra
    filtrar por veículo selecionado. Sem `car_id`, categorias tendem a vir
    vazias (confirmado ao vivo — dtsshop.de só mostra produtos com carro
    selecionado)."""
    q = request.query_params.get("q")
    category_id = request.query_params.get("category_id")
    car_cookies = _car_cookies(request)

    try:
        if q:
            items = dtsshop.search(q, car_cookies)
        elif category_id:
            items = dtsshop.list_products(category_id, car_cookies)
        else:
            return Response(
                {"detail": 'Informe "q" (busca por texto) ou "category_id" (+ dados do carro).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except SupplierError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response(_enrich_with_price(items))
