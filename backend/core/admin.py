from django.contrib import admin

from .models import Customer, MarginRule, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "created_at"]
    search_fields = ["user__username", "user__email", "phone"]


@admin.register(MarginRule)
class MarginRuleAdmin(admin.ModelAdmin):
    list_display = ["mode", "value", "updated_at"]

    def has_add_permission(self, request):
        # Singleton — nao deixa criar um segundo registro.
        return not MarginRule.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["cost_price", "sale_price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline]
