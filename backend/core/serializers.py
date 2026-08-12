from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from .models import Customer, Order, OrderItem


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=30)
    delivery_address = serializers.CharField()
    accepts_terms = serializers.BooleanField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Já existe uma conta com este e-mail.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_accepts_terms(self, value):
        if not value:
            raise serializers.ValidationError("É preciso aceitar os termos pra criar conta.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        Customer.objects.create(
            user=user,
            phone=validated_data["phone"],
            delivery_address=validated_data["delivery_address"],
            consent_accepted_at=timezone.now(),
        )
        return user


class OrderItemInputSerializer(serializers.Serializer):
    """Item enviado pelo frontend ao confirmar o pedido. product_id/product_name
    vem do resultado da busca (task 08/09) — preço e disponibilidade NAO vem do
    cliente, sao sempre re-consultados no fornecedor na hora de criar o pedido."""

    product_id = serializers.CharField()
    product_name = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Pedido precisa ter pelo menos 1 item.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id", "supplier_product_id", "product_name", "quantity",
            "cost_price", "sale_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "created_at", "updated_at", "items"]
