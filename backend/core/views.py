from decimal import Decimal

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .connectors.dtsshop import SupplierError, get_price_and_availability
from .models import Order, OrderItem, apply_margin
from .serializers import OrderCreateSerializer, OrderSerializer, RegisterSerializer

DISPONIBILIDADE_AVISO = (
    "Preço e disponibilidade conferidos no fornecedor no momento do pedido, mas "
    "podem mudar até a confirmação da compra."
)


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


register.cls.throttle_scope = 'register'


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def login(request):
    email = request.data.get('email', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response(
            {'detail': 'E-mail ou senha inválidos.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})


login.cls.throttle_scope = 'login'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Invalida o token atual — unica forma de 'derrubar' uma sessao, ja que
    token DRF nao expira sozinho (achado da revisao de seguranca)."""
    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders(request):
    if request.method == 'GET':
        qs = Order.objects.filter(customer=request.user.customer).order_by('-created_at')
        return Response(OrderSerializer(qs, many=True).data)

    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    items_input = serializer.validated_data['items']

    product_ids = [item['product_id'] for item in items_input]
    try:
        price_data = get_price_and_availability(product_ids)
    except SupplierError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    missing = [pid for pid in product_ids if pid not in price_data]
    if missing:
        return Response(
            {'detail': f'Produto(s) não encontrado(s) no fornecedor: {", ".join(missing)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        order = Order.objects.create(customer=request.user.customer)
        for item in items_input:
            info = price_data[item['product_id']]
            cost_price = Decimal(str(info['price']))
            OrderItem.objects.create(
                order=order,
                supplier_product_id=item['product_id'],
                product_name=item['product_name'],
                quantity=item['quantity'],
                cost_price=cost_price,
                sale_price=apply_margin(cost_price),
            )

    return Response(
        {**OrderSerializer(order).data, 'aviso': DISPONIBILIDADE_AVISO},
        status=status.HTTP_201_CREATED,
    )
