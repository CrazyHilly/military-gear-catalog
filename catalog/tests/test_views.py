from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import (
    Accessory,
    Country, 
    Product, 
    Clothing, 
    Footwear, 
    ProductImage, 
)
from catalog.tests.category_base_test import CategoryListViewTestBase
from catalog.views import CountryListView, ProductListView


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


class ClothingListViewTest(CategoryListViewTestBase, TestCase):
    def setUp(self):
        self.model = Clothing
        self.model_name = "clothing"
        self.product_name = "одяг"
        self.secondary_model = Footwear
        self.secondary_product_name = "взуття"
        super().setUp()


class FootwearListViewTest(CategoryListViewTestBase, TestCase):
    def setUp(self):
        self.model = Footwear
        self.model_name = "footwear"
        self.product_name = "взуття"
        self.secondary_model = Clothing
        self.secondary_product_name = "одяг"
        super().setUp()


class AccessoryListViewTest(CategoryListViewTestBase, TestCase):
    def setUp(self):
        self.model = Accessory
        self.model_name = "accessory"
        self.product_name = "аксесуар"
        self.secondary_model = Footwear
        self.secondary_product_name = "взуття"
        super().setUp()


class CountryListViewTest(TestCase):
    def setUp(self):
        self.num_per_page = CountryListView.paginate_by
        self.view = "country_list"

        self.country = Country.objects.create(en_name="country", ua_name="країна")
        self.product = Clothing.objects.create(
            name="одяг",
            country=self.country,
            price_low=100,
            price_high=200,
        )
            
        self.url = reverse(f"catalog:country-list")
        self.response = self.client.get(self.url)
        self.template = f"catalog/{self.view}.html"

    def test_country_list_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_country_list_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_country_list_pagination_is_correct(self):
        self.assertFalse(self.response.context["is_paginated"])
        self.assertEqual(len(self.response.context[self.view]), 1)

        for i in range(20):
            Country.objects.create(en_name=f"test{i}", ua_name=f"тест{i}")
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context[self.view]), 20)

    def test_country_list_view_displays_all_items(self):
        for i in range(20):
            Country.objects.create(en_name=f"test{i}", ua_name=f"тест{i}")
        response = self.client.get(self.url)
        num_pages = response.context["paginator"].num_pages
        response = self.client.get(self.url + f"?page={num_pages}")
        self.assertEqual(
            len(response.context[self.view]),
            Country.objects.count() - self.num_per_page
        )


class CountryProductsListViewTest(TestCase):
    def setUp(self):
        self.num_per_page = ProductListView.paginate_by
        self.view = "product_list"

        self.country = Country.objects.create(en_name="country", ua_name="країна")
        self.product = Clothing.objects.create(
            name="одяг",
            country=self.country,
            price_low=100,
            price_high=200,
        )
        country = Country.objects.create(en_name="test", ua_name="тест")
        for _ in range(self.num_per_page + 1):
            Clothing.objects.create(
            name="одяг",
            country=country,
            price_low=1,
            price_high=2,
        )
            
        self.url = reverse(
            f"catalog:country-products-list", 
            kwargs={"name": self.country.en_name}
            )
        self.response = self.client.get(self.url)
        self.template = f"catalog/{self.view}.html"

    def test_country_product_list_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_country_product_list_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_country_product_list_pagination_is_correct(self):
        self.assertFalse(self.response.context["is_paginated"])
        self.assertEqual(len(self.response.context[self.view]), 1)

        url = reverse(f"catalog:country-products-list", kwargs={"name": "Test"})
        response = self.client.get(url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context[self.view]), self.num_per_page)

    def test_country_product_list_view_displays_all_items(self):
        url = reverse(f"catalog:country-products-list", kwargs={"name": "Test"})
        response = self.client.get(url)
        num_pages = response.context["paginator"].num_pages
        response = self.client.get(url + f"?page={num_pages}")
        self.assertEqual(len(response.context[self.view]), 1)

    def test_country_product_list_view_search_displays_correct_results(self):
        response = self.client.get(self.url + f"?search_input=одяг")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[self.view]), 1)

        url = reverse(f"catalog:country-products-list", kwargs={"name": "Test"})
        response = self.client.get(url + f"?search_input=одяг")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[self.view]), self.num_per_page)

    def test_country_product_list_view_context_is_correct(self):
        self.assertIn("search_scope", self.response.context)
        form = self.response.context["search_form"]
        self.assertEqual(form.initial.get("search_scope"), "category")

        response = self.client.get(self.url + f"?search_input=одяг")
        self.assertIn("search_form", response.context)
        form = response.context["search_form"]
        self.assertEqual(form.initial.get("search_input"), "одяг")


class RegistrationViewPublicTest(TestCase):
    def setUp(self):
        self.url = reverse(f"customer-registration")
        self.response = self.client.get(self.url)
        self.template = f"registration/registration.html"
        self.post_data = {
            "first_name": "test_name", 
            "last_name": "test_last_name",
            "email": "test@test.com",
            "password1": "password",
            "password2": "password"
            }

    def test_registration_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_registration_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_registration_view_contains_all_fields(self):
        form = self.response.context.get("form")
        self.assertIn("first_name", form.fields)
        self.assertIn("last_name", form.fields)
        self.assertIn("email", form.fields)
        self.assertIn("password1", form.fields)
        self.assertIn("password2", form.fields)

    def test_registration_view_context_is_correct(self):
        next_url = reverse("catalog:country-list")
        url_with_next = reverse("customer-registration") + f"?next={next_url}"
        
        response_get = self.client.get(url_with_next)
        self.assertEqual(response_get.status_code, 200)
        self.assertIn("next", response_get.context)
        self.assertEqual(response_get.context["next"], next_url)

    def test_registration_view_gets_user_logged_in_on_success(self):
        response_post = self.client.post(self.url, self.post_data)
        user = response_post.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(self.post_data["first_name"], user.first_name)
        self.assertEqual(self.post_data["last_name"], user.last_name)
        self.assertEqual(self.post_data["email"], user.email)
        self.assertTrue(user.password)

    def test_registration_view_redirects_to_index_page(self):
        response_post = self.client.post(self.url, self.post_data)
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, reverse(f"catalog:product-list"))

    def test_registration_view_redirects_to_next_page(self):
        next_url = reverse(f"catalog:country-list")
        self.assertEqual(self.response.status_code, 200)

        self.post_data["next"] = next_url
        response_post = self.client.post(self.url, self.post_data)
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, next_url)


class RegistrationViewPrivateTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="TestUser@test.com",
            password="password",
        )
        self.client.force_login(self.user)
        self.url = reverse(f"customer-registration")
        self.response = self.client.get(self.url)

    def test_authenticated_user_is_redirected_from_registration_view(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse(f"catalog:product-list"))


class CustomerDetailViewPublicTest(TestCase):
    def test_customer_detail_view_is_private(self):
        url = reverse(f"catalog:customer-detail")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)


class CustomerDetailViewPrivateTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="TestUser@test.com",
            password="password",
        )
        self.client.force_login(self.user)
        self.url = reverse(f"catalog:customer-detail")
        self.response = self.client.get(self.url)
        self.template = f"catalog/customer_detail.html"
        
    def test_customer_detail_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_customer_detail_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)


class CustomerUpdateViewPublicTest(TestCase):
    def test_customer_update_view_is_private(self):
        url = reverse(f"catalog:customer-update")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)


class CustomerUpdateViewPrivateTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="TestUser@test.com",
            password="password",
        )
        self.client.force_login(self.user)
        self.url = reverse(f"catalog:customer-update")
        self.response = self.client.get(self.url)
        self.template = f"catalog/customer_update.html"
        
    def test_customer_update_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_customer_update_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_customer_update_view_contains_all_fields(self):
        form = self.response.context.get("form")
        self.assertIn("first_name", form.fields)
        self.assertIn("last_name", form.fields)

    def test_customer_update_view_redirect_is_correct(self):
        post_data = {"first_name": "test", "last_name": "test"}
        response_post = self.client.post(self.url, post_data)
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, reverse(f"catalog:customer-detail"))


class CustomerWishlistViewPublicTest(TestCase):
    def test_customer_wishlist_view_is_private(self):
        url = reverse(f"catalog:customer-wishlist")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)


class CustomerWishlistViewPrivateTest(TestCase):
    def setUp(self):
        self.view = "product_list"
        self.num_per_page = ProductListView.paginate_by
        self.user = get_user_model().objects.create_user(
            email="TestUser@test.com",
            password="password",
        )

        for _ in range(self.num_per_page + 1):
            item = Clothing.objects.create(
                name="одяг",
                price_low=100,
                price_high=200,
            )
            item.customers.add(self.user)

        Footwear.objects.create(
            name="взуття",
            price_low=100,
            price_high=200,
        )

        self.client.force_login(self.user)
        self.url = reverse(f"catalog:customer-wishlist")
        self.response = self.client.get(self.url)
        self.template = f"catalog/product_list.html"

    def test_customer_wishlist_view_is_accessible(self):
        self.assertEqual(self.response.status_code, 200)

    def test_customer_wishlist_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, self.template)

    def test_customer_wishlist_view_pagination_is_correct(self):
        self.assertTrue(self.response.context["is_paginated"])
        self.assertEqual(len(self.response.context[self.view]), self.num_per_page)

    def test_customer_wishlist_view_displays_all_items(self):
        num_pages = self.response.context["paginator"].num_pages
        response = self.client.get(self.url + f"?page={num_pages}")
        self.assertEqual(len(response.context[self.view]), 1)
