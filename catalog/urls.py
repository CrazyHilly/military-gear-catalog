from django.urls import path

from catalog.views import (
    AccessoryListView,
    ClothingListView, 
    CountryListView, 
    CountryProductsListView, 
    CustomerDetailView, 
    CustomerUpdateView, 
    CustomerWishlistView,
    FootwearListView, 
    ProductDetailView, 
    ProductListView, 
    product_image_detail_view,
    update_wishlist
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "product/<int:product_number>/update-wishlist", 
        update_wishlist, 
        name="update-wishlist"),
    path("clothing/", ClothingListView.as_view(), name="clothing-list"),
    path("footwear/", FootwearListView.as_view(), name="footwear-list"),
    path("accessories/", AccessoryListView.as_view(), name="accessory-list"),
    path("countries/", CountryListView.as_view(), name="country-list"),
    path(
        "countries/<str:name>/", 
        CountryProductsListView.as_view(), 
        name="country-products-list"
        ),
    path("customer/", CustomerDetailView.as_view(), name="customer-detail"),
    path("customer/update", CustomerUpdateView.as_view(), name="customer-update"),
    path(
        "customer/wishlist/", 
        CustomerWishlistView.as_view(), 
        name="customer-wish-list"
        ),
    path(
        "product-image/<int:image_pk>/", 
        product_image_detail_view, 
        name="product-image-detail"
        ),
]

app_name = "catalog"
