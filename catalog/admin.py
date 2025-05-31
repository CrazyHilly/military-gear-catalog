from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from catalog.models import (
    Product, Clothing, Footwear, Accessory, ProductImage, Country, Customer
    )
    

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


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["ua_name", "en_name"]


class WishitemsFilter(admin.SimpleListFilter):
    title = _("списком бажань")
    parameter_name = "wishitems"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Є товари")),
            ("no", _("Немає товарів")),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(wishlist_count=Count("wishlist"))
        if self.value() == "yes":
            return queryset.filter(wishlist_count__gt=0)
        if self.value() == "no":
            return queryset.filter(wishlist_count=0)
        return queryset
    

class WishlistThroughProxy(Customer.wishlist.through):
    class Meta:
        proxy = True
        verbose_name = _("товар")
        verbose_name_plural = _("список бажань")

    def __str__(self):
        return ""
    

class WishlistInline(admin.TabularInline):
    model = WishlistThroughProxy
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    

@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = [
        "id", 
        "email", 
        "first_name", 
        "last_name", 
        "display_wishlist",
        "display_is_staff", 
        "date_joined", 
        "last_login",
        ]
    search_fields = ["id", "email", "first_name", "last_name"]
    list_filter = [
        "date_joined", 
        "last_login",
        "is_staff", 
        WishitemsFilter,
        ]
    readonly_fields = ["email", "date_joined", "last_login",]
    ordering = ("id",)
    inlines = [WishlistInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {
            "fields": (
                "is_active", "is_staff", "is_superuser", "groups", "user_permissions"
                )}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    @admin.display(boolean=True, description="Персонал")
    def display_is_staff(self, obj):
        return obj.is_staff

    def display_wishlist(self, obj):
        wishlist = obj.wishlist.all()
        if not wishlist:
            return "-"
        
        items_num = len(wishlist)
        str_products = "товар" if items_num == 1 else "товарів"
        if items_num > 9:
            short_str_wishlist = ", ".join([str(p.product_number) for p in wishlist[:7]])
            return f"{str(items_num)} {str_products}: {short_str_wishlist}, ..."
        
        str_wishlist = ", ".join([str(p.product_number) for p in wishlist])
        return f"{str(items_num)} {str_products}: {str_wishlist}"
    
    display_wishlist.short_description = "Список бажань"

    class Media:
        css = {
            "all": ("css/admin.css",)
        }

    @admin.action(description=_("Змінити статус персоналу"))
    def change_is_staff(self, request, queryset):
        for user in queryset:
            user.is_staff=not user.is_staff
            user.save()

    actions = ["change_is_staff"]
        

class WishlistStatsFilter(admin.SimpleListFilter):
    title = _("вподобаннями")
    parameter_name = "wishitems"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Є у списках бажань")),
            ("no", _("Немає у списках бажань")),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(customers_count=Count("customers"))
        if self.value() == "yes":
            return queryset.filter(customers_count__gt=0)
        if self.value() == "no":
            return queryset.filter(customers_count=0)
        return queryset
    

class ProductWishlistStats(Product):
    class Meta:
        proxy = True
        verbose_name = "Бажаний товар"
        verbose_name_plural = "Бажані товари"


@admin.register(ProductWishlistStats)
class WishlistStatsAdmin(ProductAdmin):
    list_display = [
        "product_number", 
        "name", 
        "display_product_count",
        "display_category", 
        "country", 
        "price_low", 
        "price_high", 
        "available",
        ]
    list_filter = ["available", "country", "category", WishlistStatsFilter]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_wishlist_count=Count("customers"))
    
    @admin.display(ordering="customers_count", description="Вподобань")
    def display_product_count(self, obj):
        return obj._wishlist_count
    
    def changelist_view(self, request, extra_context=None):
        if not request.GET.get("o"):
            q = request.GET.copy()
            q["o"] = "-3"
            request.GET = q
            request.META["QUERY_STRING"] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


admin.site.unregister(Group)
