from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from catalog.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "product_number", 
        "name", 
        "display_category", 
        "country", 
        "price_low", 
        "price_high", 
        "description", 
        "available"
        ]
    search_fields = [
        "name", 
        "country__ua_name", 
        "country__en_name", 
        "description", 
        "product_number", 
        "category"
        ]
    list_filter = ["available", "country__ua_name", "category"]
    inlines = [ProductImageInline]

    def display_category(self, obj):
        return f"{obj.category} - {obj.get_category_display()}"
    
    display_category.short_description = "Категорія"

    exclude = ["slug"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["product_number"]
        return []

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not obj:
            fields = [f for f in fields if f != "product_number"]
        return fields

    actions = ["change_availability"]

    @admin.action(description=_("Змінити наявність"))
    def change_availability(self, request, queryset):
        for item in queryset:
            item.available=not item.available
            item.save()


admin.site.unregister(Group)
