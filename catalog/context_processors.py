from django.core.cache import cache
from django.db.models import Count

from .models import Country


def countries_context(request):
    fields_to_display = ("id", "ua_name", "en_name", "product_count")
    cached_data = cache.get("countries_with_products")
    if cached_data is None:
        cached_data = list(Country.objects.annotate(
            product_count=Count("products")
        ).filter(product_count__gt=0).values(*fields_to_display))
        cache.set("countries_with_products", cached_data, 600)
    return {"countries_with_products": cached_data}
