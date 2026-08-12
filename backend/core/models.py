from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    """Dados de entrega do cliente final. Nome e e-mail ficam no User (evita
    duplicação) — aqui só o que o User nao tem."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    phone = models.CharField(max_length=30)
    delivery_address = models.TextField()
    consent_accepted_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Quando o cliente aceitou os termos no cadastro (RGPD).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class PriceTablePoint(models.Model):
    """Ponto (custo, preco de venda) da tabela de precos do cliente
    (`regra_de_precos.md`, formula dele — interpolacao linear entre pontos).
    Substituiu o sistema anterior de margem fixa/multiplicador (MarginRule/
    MarginTier) — o cliente respondeu com uma tabela concreta em vez de
    percentuais por faixa. Editavel via /admin, sem deploy pra ajustar."""

    cost = models.DecimalField(max_digits=10, decimal_places=2, unique=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["cost"]
        verbose_name = "Ponto da tabela de preços"
        verbose_name_plural = "Tabela de preços"

    def __str__(self):
        return f"custo {self.cost} → venda {self.sale_price}"


def apply_margin(cost_price: Decimal) -> Decimal:
    """Preco de venda a partir do preco de custo — interpolacao linear sobre a
    tabela de pontos do cliente (`PriceTablePoint`), mesma logica do
    `calcularPVPLDC` em `regra_de_precos.md`:

    - Abaixo do primeiro ponto: mantem a proporcao do primeiro ponto.
    - Entre dois pontos: interpolacao linear.
    - Acima do ultimo ponto: mantem a proporcao do ultimo ponto.

    Arredonda ao euro mais proximo (Math.round do JS original = arredonda
    ,5 pra cima, por isso ROUND_HALF_UP em vez do round() padrao do Python,
    que arredonda pro par mais proximo).
    """
    points = list(PriceTablePoint.objects.all())
    if not points:
        raise ValueError(
            "Tabela de preços vazia — cadastre pelo menos 1 ponto em "
            "PriceTablePoint antes de calcular preço de venda."
        )

    def round_to_euro(value: Decimal) -> Decimal:
        return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    if cost_price < points[0].cost:
        ratio = points[0].sale_price / points[0].cost
        return round_to_euro(cost_price * ratio)

    if cost_price > points[-1].cost:
        ratio = points[-1].sale_price / points[-1].cost
        return round_to_euro(cost_price * ratio)

    for lower, upper in zip(points, points[1:]):
        if lower.cost <= cost_price <= upper.cost:
            if upper.cost == lower.cost:
                return round_to_euro(lower.sale_price)
            fraction = (cost_price - lower.cost) / (upper.cost - lower.cost)
            sale_price = lower.sale_price + fraction * (upper.sale_price - lower.sale_price)
            return round_to_euro(sale_price)

    # Custo bate exatamente no unico ponto existente (tabela com 1 item so).
    return round_to_euro(points[0].sale_price)


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


class Supplier(models.Model):
    """Fornecedor de catálogo importado via Excel/CSV (Fase 2, task 04 — ver
    docs/EXCEL-IMPORT.md). Diferente do dtsshop.de: não é consultado ao vivo,
    o catálogo fica no banco, atualizado por upload."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    selected_fields = models.JSONField(
        default=list, blank=True,
        help_text="Nomes dos campos de raw_attributes que o cliente escolheu "
                   "exibir/usar pra esse fornecedor.",
    )

    class Meta:
        verbose_name = "Fornecedor (catálogo importado)"
        verbose_name_plural = "Fornecedores (catálogo importado)"

    def __str__(self):
        return self.name


class ImportedProduct(models.Model):
    """Produto de um catálogo importado (Excel/CSV). Deduplicado por
    (supplier, external_reference) — upload recorrente atualiza em vez de
    duplicar; produto que sumiu do arquivo mais recente fica active=False,
    nunca é apagado (mantém histórico/pedidos já feitos íntegros)."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")
    external_reference = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(blank=True, max_length=500)
    category = models.CharField(max_length=255, blank=True)
    raw_attributes = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "external_reference"], name="unique_product_per_supplier",
            )
        ]
        indexes = [models.Index(fields=["supplier", "active"])]

    def __str__(self):
        return f"[{self.supplier.name}] {self.title} ({self.external_reference})"

    @property
    def sale_price(self) -> Decimal | None:
        if self.cost_price is None:
            return None
        return apply_margin(self.cost_price)


class ImportedProductFitment(models.Model):
    """Compatibilidade de veículo de um produto importado (só existe pra
    fornecedores que têm fitment — MTS, TA Technix; vazio pra rodas). Uma
    linha por combinação marca/modelo/motor compatível."""

    product = models.ForeignKey(ImportedProduct, on_delete=models.CASCADE, related_name="fitments")
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=150)
    variant = models.CharField(max_length=150, blank=True)
    year_range = models.CharField(max_length=50, blank=True)

    class Meta:
        indexes = [models.Index(fields=["make", "model"])]

    def __str__(self):
        return f"{self.make} {self.model} {self.variant}".strip()
