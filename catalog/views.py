from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt

from catalog.forms import ProductSearchForm, RegistrationForm
from catalog.models import Product, Clothing, Footwear, Accessory, Country, ProductImage


class ProductDetailView(generic.DetailView):
    model = Product
    
    def get_queryset(self):
        qs = super().get_queryset().select_related("country").prefetch_related("images")
        return qs


class ProductListView(generic.ListView):
    model = Product
    paginate_by = 12
    default_search_scope = "category"

    def get_search_scope(self):
        if "search_scope" in self.request.GET:
            search_scope = self.request.GET.get("search_scope")
            self.request.session["search_scope"] = search_scope
        return self.request.session.get("search_scope", self.default_search_scope)

    def get_queryset(self):
        queryset = \
            super().get_queryset().select_related("country").prefetch_related("images")
        search_input = self.request.GET.get("search_input")
        search_scope = self.get_search_scope()
        
        if search_input:
            if search_scope == "global":
                queryset = Product.objects.all()

            queryset = queryset.filter(
                Q(name__icontains=search_input) |
                Q(country__ua_name__icontains=search_input) |
                Q(country__en_name__icontains=search_input) |
                Q(description__icontains=search_input) |
                Q(product_number__icontains=search_input)
            )
        return queryset.filter(~Q(name__icontains="test"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get("search_input", "")
        search_scope = self.get_search_scope()

        context["search_form"] = ProductSearchForm(
            initial={"search_input": search_input, "search_scope": search_scope}
        )
        context["search_scope"] = search_scope
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
        if self.request.GET.get("search_scope") == "global":
            return super().get_queryset()
        
        country = get_object_or_404(Country, en_name=self.kwargs.get("name"))
        return super().get_queryset().filter(country=country)


class CustomerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()

    def get_object(self):
        return self.request.user


class CustomerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    fields = ["first_name", "last_name"]
    template_name = "catalog/customer_update.html"
    success_url = reverse_lazy("catalog:customer-detail")

    def get_object(self):
        return self.request.user
    

class RegistrationView(generic.CreateView):
    model = get_user_model()
    form_class = RegistrationForm
    template_name = "registration/registration.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("catalog:product-list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
    
    def get_success_url(self):
        return self.request.POST.get("next") or reverse_lazy("catalog:product-list")


class CustomerWishlistView(LoginRequiredMixin, ProductListView):
    template_name = "catalog/product_list.html"

    def get_queryset(self):
        return self.request.user.wishlist.all()


@login_required
def update_wishlist(request, product_number):
    customer = request.user
    product = Product.objects.get(product_number=product_number)
    action = request.GET.get("action")

    if action == "add":
        customer.wishlist.add(product)
    else:
        customer.wishlist.remove(product)
            
    return redirect(request.GET.get("next", "/"))


@xframe_options_exempt
def product_image_detail_view(request, image_pk):
    image = get_object_or_404(ProductImage, pk=image_pk)
    return render(request, "catalog/product_image_detail.html", {"image": image})
