from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views import generic

from catalog.forms import ProductSearchForm
from catalog.models import (
    Product, Clothing, Footwear, Accessory, Country
)


class ProductDetailView(generic.DetailView):
    model = Product


class ProductListView(generic.ListView):
    model = Product
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_input = self.request.GET.get("search_input")
        if search_input:
            queryset = queryset.filter(
                Q(name__icontains=search_input) |
                Q(country__ua_name__icontains=search_input) |
                Q(country__en_name__icontains=search_input) |
                Q(description__icontains=search_input) |
                Q(product_number__icontains=search_input)
            )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get("search_input", "")
        context["search_form"] = ProductSearchForm(
            initial={"search_input": search_input}
        )
        return context


class ClothingListView(ProductListView):
    queryset = Clothing.objects.select_related("country")
    template_name = "catalog/product_list.html"


class FootwearListView(ProductListView):
    queryset = Footwear.objects.select_related("country")
    template_name = "catalog/product_list.html"


class AccessoryListView(ProductListView):
    queryset = Accessory.objects.select_related("country")
    template_name = "catalog/product_list.html"


class CountryListView(generic.ListView):
    model = Country
    paginate_by = 20


class CountryProductsListView(ProductListView):
    template_name = "catalog/product_list.html"

    def get_queryset(self):
        country = get_object_or_404(Country, en_name=self.kwargs.get("name"))
        return super().get_queryset().filter(country=country)
