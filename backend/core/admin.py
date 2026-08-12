from django.contrib import admin

from .models import Customer, Order, OrderItem, PriceTablePoint


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "created_at"]
    search_fields = ["user__username", "user__email", "phone"]


@admin.register(PriceTablePoint)
class PriceTablePointAdmin(admin.ModelAdmin):
    list_display = ["cost", "sale_price"]
    ordering = ["cost"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["cost_price", "sale_price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline]
    actions = ["mark_ordered_with_supplier", "mark_delivered"]

    @admin.action(description="Marcar como 'comprado no fornecedor'")
    def mark_ordered_with_supplier(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_ORDERED_WITH_SUPPLIER)
        self.message_user(request, f"{updated} pedido(s) marcado(s) como comprado no fornecedor.")

    @admin.action(description="Marcar como 'entregue'")
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_DELIVERED)
        self.message_user(request, f"{updated} pedido(s) marcado(s) como entregue.")
