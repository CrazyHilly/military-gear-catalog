import debug_toolbar
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.conf import settings

from catalog.views import ProductListView, RegistrationView
from military_gear_catalog.views import contacts_view, how_to_order_view, about_us_view

urlpatterns = ([
        path("", ProductListView.as_view(), name="product-list"),
        path("admin/", admin.site.urls),
        path("", include("catalog.urls", namespace="catalog")),
        path("accounts/", include("django.contrib.auth.urls")),
        path("accounts/registration/", RegistrationView.as_view(), name="registration"),
        path("contacts/", contacts_view, name="contacts"),
        path("how-to-order/", how_to_order_view, name="how-to-order"),
        path("about-us/", about_us_view, name="about-us"),
    ]
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls)),] + \
      + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
