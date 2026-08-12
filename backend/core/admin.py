from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import path

from .importers.security import UploadValidationError
from .importers.service import SUPPLIER_SLUGS, import_supplier_file
from .models import (
    Customer,
    ImportedProduct,
    ImportedProductFitment,
    Order,
    OrderItem,
    PriceTablePoint,
    Supplier,
)


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


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


class ImportedProductFitmentInline(admin.TabularInline):
    model = ImportedProductFitment
    extra = 0


class CatalogUploadForm(forms.Form):
    supplier = forms.ChoiceField(
        choices=[(slug, name) for slug, (name, _parser, _ext) in SUPPLIER_SLUGS.items()],
        label="Fornecedor",
    )
    file = forms.FileField(label="Arquivo (.csv/.xlsx/.zip conforme o fornecedor)")


@admin.register(ImportedProduct)
class ImportedProductAdmin(admin.ModelAdmin):
    list_display = ["title", "supplier", "external_reference", "cost_price", "active", "updated_at"]
    list_filter = ["supplier", "active"]
    search_fields = ["title", "external_reference"]
    inlines = [ImportedProductFitmentInline]
    readonly_fields = ["raw_attributes"]
    change_list_template = "admin/core/importedproduct/change_list.html"

    def get_urls(self):
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_view),
                name="core_importedproduct_upload",
            ),
        ]
        return custom_urls + super().get_urls()

    def upload_view(self, request):
        """Upload self-service de catálogo — só staff (sessão do admin, não
        token de API), consistente com o resto do painel (task 02). Roda
        validação de segurança + parser dedicado do fornecedor
        (core/importers/) antes de tocar o banco.

        `admin_view()` (usado no get_urls) só garante is_staff — não checa
        permissão do model pra URLs custom (achado testando: um funcionário
        sem permissão em ImportedProduct conseguia acessar a página só
        adivinhando a URL). Checagem explícita aqui fecha isso."""
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == "POST":
            form = CatalogUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded = form.cleaned_data["file"]
                try:
                    result = import_supplier_file(
                        form.cleaned_data["supplier"], uploaded.name, uploaded.read(),
                    )
                    messages.success(
                        request,
                        f"Importado: {result.created} criado(s), {result.updated} "
                        f"atualizado(s), {result.deactivated} desativado(s).",
                    )
                    return redirect("admin:core_importedproduct_changelist")
                except UploadValidationError as exc:
                    messages.error(request, str(exc))
        else:
            form = CatalogUploadForm()

        return render(
            request,
            "admin/core/catalog_upload.html",
            {"form": form, "opts": self.model._meta, "title": "Importar catálogo"},
        )
