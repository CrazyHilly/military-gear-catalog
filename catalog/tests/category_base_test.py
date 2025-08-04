from django.urls import reverse

from catalog.models import ProductImage
from catalog.views import ProductListView


class CategoryListViewTestBase:
    model = None
    model_name = None
    product_name = None
    secondary_model = None
    secondary_product_name = None

    def setUp(self):
        self.num_per_page = ProductListView.paginate_by
        self.view = f"{self.model_name}_list"

        self.product = self.model.objects.create(
            name=self.product_name,
            price_low=100,
            price_high=200,
        )
        self.image = "catalog\tests\test_media\test_1.jpg"
        self.product_image = ProductImage.objects.create(
            product=self.product, 
            image=self.image
            )
        for _ in range(self.num_per_page):
            self.secondary_model.objects.create(
            name=self.secondary_product_name,
            price_low=1,
            price_high=2,
        )
            
        self.url = reverse(f"catalog:{self.model_name}-list")
        self.response = self.client.get(self.url)
        self.template = f"catalog/product_list.html"

    def test_category_list_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_category_list_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_category_list_pagination_is_correct(self):
        self.assertFalse(self.response.context["is_paginated"])
        self.assertEqual(len(self.response.context[self.view]), 1)

        for _ in range(self.num_per_page):
            self.model.objects.create(
            name=self.product_name,
            price_low=1,
            price_high=2,
        )
        response = self.client.get(self.url)
        self.assertEqual(len(response.context[self.view]), 12)

    def test_category_list_view_displays_all_items(self):
        num_pages = self.response.context["paginator"].num_pages
        response = self.client.get(self.url + f"?page={num_pages}")
        self.assertEqual(len(response.context[self.view]), 1)

        for _ in range(self.num_per_page - 1):
            self.model.objects.create(
            name=self.product_name,
            price_low=1,
            price_high=2,
        )
        response = self.client.get(self.url + f"?page={num_pages}")
        self.assertEqual(len(response.context[self.view]), 12)

    def test_category_list_view_search_displays_correct_results(self):
        response = self.client.get(self.url + f"?search_input={self.product_name}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[self.view]), 1)
        
        response = self.client.get(
            self.url + f"?search_input={self.secondary_product_name}"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[self.view]), 0)

    def test_category_list_view_context_is_correct(self):
        self.assertIn("search_scope", self.response.context)
        form = self.response.context["search_form"]
        self.assertEqual(form.initial.get("search_scope"), "category")

        response = self.client.get(self.url + f"?search_input={self.product_name}")
        self.assertIn("search_form", response.context)
        form = response.context["search_form"]
        self.assertEqual(form.initial.get("search_input"), self.product_name)