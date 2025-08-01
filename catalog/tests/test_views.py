from django.test import TestCase
from django.urls import reverse

from catalog.models import (
    Country, 
    Product, 
    Clothing, 
    Footwear, 
    ProductImage, 
)
from catalog.views import ProductListView


class ProductDetailViewTest(TestCase):            
    def setUp(self):
        self.country = Country.objects.create(ua_name="Франція", en_name="France")
        self.product = Clothing.objects.create(
            name="одяг",
            country=self.country,
            description="тест",
            price_low=100,
            price_high=200,
        )
        self.image = "catalog\tests\test_media\test_1.jpg"
        self.product_image = ProductImage.objects.create(
            product=self.product, 
            image=self.image
            )
        self.url = reverse(
            f"catalog:product-detail", 
            kwargs={"slug": Product.objects.first().slug}
            )
        self.response = self.client.get(self.url)
        self.template = f"catalog/product_detail.html"

    def test_product_detail_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_product_detail_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)


class ProductListViewTest(TestCase):
    def setUp(self):
        self.num_per_page = ProductListView.paginate_by
        self.view = "product_list"

        self.product = Clothing.objects.create(
            name="одяг",
            price_low=100,
            price_high=200,
        )
        self.image = "catalog\tests\test_media\test_1.jpg"
        self.product_image = ProductImage.objects.create(
            product=self.product, 
            image=self.image
            )
        for _ in range(self.num_per_page):
            Footwear.objects.create(
            name="тест",
            price_low=1,
            price_high=2,
        )
            
        self.url = reverse(f"catalog:product-list")
        self.response = self.client.get(self.url)
        self.template = f"catalog/{self.view}.html"

    def test_product_list_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_product_list_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_product_list_pagination_is_correct(self):
        self.assertTrue(self.response.context["is_paginated"])
        self.assertEqual(len(self.response.context[self.view]), self.num_per_page)

    def test_product_list_view_displays_all_items(self):
        num_pages = self.response.context["paginator"].num_pages
        response = self.client.get(self.url + f"?page={num_pages}")
        self.assertEqual(
            len(response.context[self.view]),
            Product.objects.count() - self.num_per_page
        )

    def test_product_list_view_search_displays_correct_results(self):
        response = self.client.get(self.url + f"?search_input=одяг")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[self.view]), 1)
        
        response = self.client.get(self.url + f"?search_input=тест")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[self.view]), 12)

    def test_product_list_view_context_is_correct(self):
        self.assertIn("search_scope", self.response.context)
        form = self.response.context["search_form"]
        self.assertEqual(form.initial.get("search_scope"), "category")

        response = self.client.get(self.url + f"?search_input=одяг")
        self.assertIn("search_form", response.context)
        form = response.context["search_form"]
        self.assertEqual(form.initial.get("search_input"), "одяг")
