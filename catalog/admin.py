from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from catalog.models import Product, Clothing, Footwear, Accessory, ProductImage
    

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
    show_category = True

    def display_category(self, obj):
        return f"{obj.category} - {obj.get_category_display()}"
    display_category.short_description = "Категорія"

    exclude = ["slug"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["product_number", "category"]
        return []

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields.remove("category")

        if not obj:
            fields = [f for f in fields if f != "product_number"]
            
        return fields
    
    def save_model(self, request, obj, form, change):
        if not obj.category:
            obj.category = form.cleaned_data.get("category")
        super().save_model(request, obj, form, change)

    actions = ["change_availability", "make_available", "make_unavailable"]

    def has_add_permission(self, request):
        return False

    @admin.action(description=_("Змінити наявність"))
    def change_availability(self, request, queryset):
        for item in queryset:
            item.available=not item.available
            item.save()

    @admin.action(description=_("Є в наявності"))
    def make_available(self, request, queryset):
        queryset.update(available=True)

    @admin.action(description=_("Немає в наявності"))
    def make_unavailable(self, request, queryset):
        queryset.update(available=False)


@admin.register(Clothing)
class ClothingAdmin(ProductAdmin):
    category = "1"
    show_category = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=self.category)

    def save_model(self, request, obj, form, change):
        obj.category = self.category
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True
    

@admin.register(Footwear)
class FootwearAdmin(ProductAdmin):
    category = "2"
    show_category = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=self.category)

    def save_model(self, request, obj, form, change):
        obj.category = self.category
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True
    

@admin.register(Accessory)
class AccessoryAdmin(ProductAdmin):
    category = "3"
    show_category = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=self.category)

    def save_model(self, request, obj, form, change):
        obj.category = self.category
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True


admin.site.unregister(Group)
