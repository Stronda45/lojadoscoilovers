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
