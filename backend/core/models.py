from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    """Dados de entrega do cliente final. Nome e e-mail ficam no User (evita
    duplicação) — aqui só o que o User nao tem."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    phone = models.CharField(max_length=30)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class MarginRule(models.Model):
    """Regra de precificacao padrao (fallback). Singleton editavel via /admin —
    trocar o modo ou o valor NAO exige deploy, so mudar aqui.

    Cliente pediu faixas de preco com taxa diferente por faixa (ver
    `MarginTier`), entao esta regra so e usada quando nenhuma faixa cadastrada
    bate com o preco (ou nenhuma faixa existe ainda). Default fica em
    fixed_amount=50 (o que ja foi orcado). Ver investigar.md.
    """

    FIXED_AMOUNT = "fixed_amount"
    MULTIPLIER = "multiplier"
    MODE_CHOICES = [
        (FIXED_AMOUNT, "Valor fixo somado (ex: +50 EUR)"),
        (MULTIPLIER, "Multiplicador (ex: 1.30 = +30%)"),
    ]

    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=FIXED_AMOUNT)
    value = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("50"))
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_mode_display()} ({self.value})"

    def apply(self, cost_price: Decimal) -> Decimal:
        if self.mode == self.MULTIPLIER:
            return (cost_price * self.value).quantize(Decimal("0.01"))
        return (cost_price + self.value).quantize(Decimal("0.01"))

    @classmethod
    def active(cls) -> "MarginRule":
        """Sempre existe exatamente 1 registro (singleton). Cria com o default na
        primeira chamada se ainda nao existir."""
        rule, _ = cls.objects.get_or_create(pk=1)
        return rule

    class Meta:
        verbose_name = "Regra de margem"
        verbose_name_plural = "Regra de margem"


class MarginTier(models.Model):
    """Faixa de preco com regra propria (pedido do cliente: taxa diferente por
    faixa, ex: <100 EUR vs 100-500 EUR). Percentuais/valores ainda nao
    confirmados pelo cliente — cadastro fica vazio ate ele mandar os numeros
    (ver investigar.md). Enquanto nao houver faixas, `apply_margin` cai pra
    `MarginRule` (regra fixa unica)."""

    FIXED_AMOUNT = MarginRule.FIXED_AMOUNT
    MULTIPLIER = MarginRule.MULTIPLIER
    MODE_CHOICES = MarginRule.MODE_CHOICES

    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    max_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Vazio = sem limite superior",
    )
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=FIXED_AMOUNT)
    value = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("50"))

    class Meta:
        ordering = ["min_price"]
        verbose_name = "Faixa de margem"
        verbose_name_plural = "Faixas de margem"

    def __str__(self):
        upper = str(self.max_price) if self.max_price is not None else "sem limite"
        return f"{self.min_price} - {upper}: {self.get_mode_display()} ({self.value})"

    def matches(self, cost_price: Decimal) -> bool:
        if cost_price < self.min_price:
            return False
        if self.max_price is not None and cost_price >= self.max_price:
            return False
        return True

    def apply(self, cost_price: Decimal) -> Decimal:
        if self.mode == self.MULTIPLIER:
            return (cost_price * self.value).quantize(Decimal("0.01"))
        return (cost_price + self.value).quantize(Decimal("0.01"))


def apply_margin(cost_price: Decimal) -> Decimal:
    """Preco de venda a partir do preco de custo. Usa a primeira `MarginTier`
    cuja faixa bate com o preco; se nenhuma faixa existir/bater, cai pra
    `MarginRule` (regra fixa unica)."""
    for tier in MarginTier.objects.all():
        if tier.matches(cost_price):
            return tier.apply(cost_price)
    return MarginRule.active().apply(cost_price)


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ORDERED_WITH_SUPPLIER = "ordered_with_supplier"
    STATUS_DELIVERED = "delivered"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_ORDERED_WITH_SUPPLIER, "Comprado no fornecedor"),
        (STATUS_DELIVERED, "Entregue"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.pk} — {self.customer}"


class OrderItem(models.Model):
    """Um item de pedido. Guarda o preco de custo E o preco de venda aplicado no
    momento do pedido (nao recalcula depois, mesmo se a margem mudar)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    supplier_product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
