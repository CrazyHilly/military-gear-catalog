from django import template
from django.urls import reverse
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, 0)

    return updated.urlencode()


@register.simple_tag(takes_context=True)
def update_wishlist_url(context, product, action=None):
    product_number = product.product_number
    base_url = reverse(
        "catalog:update-wishlist", 
        kwargs={"product_number": product_number}
        )
    next_path = context["request"].get_full_path() + f"#{product.product_number}"

    query_params = {"next": next_path}
    if action:
        query_params["action"] = action

    return f"{base_url}?{urlencode(query_params)}"
