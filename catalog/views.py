from django.views import generic

from catalog.models import Product


class ProductDetailView(generic.DetailView):
    model = Product
