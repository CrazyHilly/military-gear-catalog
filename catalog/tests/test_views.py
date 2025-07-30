from django.test import TestCase
from django.urls import reverse

from catalog.models import (
    Country, 
    Product, 
    Clothing, 
    ProductImage, 
)


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
