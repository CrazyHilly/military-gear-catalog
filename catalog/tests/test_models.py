from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from slugify import slugify

from catalog.models import (
    Country, 
    Product, 
    Clothing, 
    Footwear, 
    Accessory, 
    ProductImage, 
    Customer
)


class CountryModelTest(TestCase):
    def setUp(self):
        self.country_1 = Country.objects.create(
            en_name="netherlands",
            ua_name="нідерланди",
        )
        self.country_2 = Country.objects.create(
            en_name="EU",
            ua_name="ЄС",
        )

    def test_country_is_created_correctly(self):
        self.assertTrue(Country.objects.exists())
        self.assertEqual(len(list(Country.objects.all())), 2)

    def test_country_str(self):
        self.assertEqual(str(self.country_1), self.country_1.ua_name)

    def test_country_ordering(self):
        countries = Country.objects.all()
        self.assertEqual(
            list(countries),
            sorted(countries, key=lambda country: country.ua_name)
        )

    def test_country_names_max_length(self):
        self.country_1.en_name="d" * 61
        with self.assertRaises(ValidationError):
            self.country_1.full_clean()

        self.country_2.ua_name="д" * 61
        with self.assertRaises(ValidationError):
            self.country_2.full_clean()

    def test_country_names_are_unique(self):
        ua_duplicate = Country(ua_name=self.country_1.ua_name)
        with self.assertRaises(ValidationError):
            ua_duplicate.full_clean()

        en_duplicate = Country(en_name=self.country_1.en_name)
        with self.assertRaises(ValidationError):
            en_duplicate.full_clean()

    def test_country_names_saved_with_correct_register(self):
        self.assertEqual(self.country_1.ua_name, "Нідерланди")
        self.assertEqual(self.country_1.en_name, "Netherlands")
        self.assertEqual(self.country_2.ua_name, "ЄС")
        self.assertEqual(self.country_2.en_name, "EU")


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        country_f = Country.objects.create(ua_name="Франція", en_name="France")
        country_c = Country.objects.create(ua_name="Канада", en_name="Canada")
        country_a = Country.objects.create(ua_name="Австрія", en_name="Austria")
        clothing = Clothing.objects.create(
            name="одяг",
            country=country_c,
            description="тест",
            price_low=100,
            price_high=200,
        )
        footwear = Footwear.objects.create(
            name="взуття",
            country=country_f,
            description="тест",
            price_low=1000,
            price_high=2000,
        )
        accessory = Accessory.objects.create(
            name="аксесуар",
            country=country_a,
            description="тест",
            price_low=10,
            price_high=20,
        )
        ProductImage.objects.create(
            product=clothing, 
            image="catalog\tests\test_media\test_1.jpg"
            )
        ProductImage.objects.create(
            product=footwear, 
            image="catalog\tests\test_media\test_2.jpg"
            )
        ProductImage.objects.create(
            product=accessory, 
            image="catalog\tests\test_media\test_3.jpg"
            )

    def setUp(self):
        self.clothing = Clothing.objects.get(name__icontains="одяг")
        self.footwear = Footwear.objects.get(name__icontains="взуття")
        self.accessory = Accessory.objects.get(name__icontains="аксесуар")

        self.product_clothing = Product.objects.get(name__icontains="одяг")
        self.product_footwear = Product.objects.get(name__icontains="взуття")
        self.product_accessory = Product.objects.get(name__icontains="аксесуар")
        
        self.products = (
            self.clothing, self.footwear, self.accessory,
            self.product_clothing, self.product_footwear, self.product_accessory,
            )
        self.product_child_models = (Clothing, Footwear, Accessory)

    def test_product_is_created_correctly(self):
        self.assertTrue(Product.objects.exists())
        self.assertEqual(len(list(Product.objects.all())), 3)
        
        for model in self.product_child_models:
            self.assertTrue(model.objects.exists())
            self.assertTrue(len(list(model.objects.all())), 1)

    def test_product_and_child_models_return_same_db_entries(self):
        self.assertEqual(self.clothing.pk, self.product_clothing.pk)
        self.assertEqual(self.footwear.pk, self.product_footwear.pk)
        self.assertEqual(self.accessory.pk, self.product_accessory.pk)

    def test_product_name_null_raises_error(self):
        for product in self.products:
            product.name = None
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_name_blank_raises_error(self):
        for product in self.products:
            product.name = ""
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_name_max_length(self):
        for product in self.products:
            product.name = "а" * 101
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_can_be_saved_without_country(self):
        for model in self.product_child_models:
            product = model.objects.create(name="продукт", price_low=1, price_high=2)
            self.assertTrue(product.pk)

        for product in self.products:
            product.country = None
            product.save()
            self.assertTrue(product.pk)

    def test_product_country_set_null_on_delete(self):
        for product in self.products:
            product.refresh_from_db()
            if product.country:
                product.country.delete()
            product.refresh_from_db()
            self.assertIsNone(product.country)

    def test_product_can_be_saved_without_description(self):
        for model in self.product_child_models:
            product = model.objects.create(name="продукт", price_low=1, price_high=2)
            self.assertTrue(product.pk)

        for product in self.products:
            product.description = ""
            product.save()
            self.assertEqual(product.description, "")

    def test_product_price_low_min_value(self):
        for product in self.products:
            product.price_low = 0
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_price_low_max_value(self):
        for product in self.products:
            product.price_low = 11000
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_price_high_min_value(self):
        for product in self.products:
            product.price_high = 0
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_price_high_max_value(self):
        for product in self.products:
            product.price_high = 11000
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_price_low_higher_than_high(self):
        for product in self.products:
            product.price_low = 3000
            with self.assertRaises(ValidationError):
                product.full_clean()

    def test_product_price_high_lower_than_low(self):
        for product in self.products:
            product.price_high = 3
            with self.assertRaises(ValidationError):
                product.full_clean()

    def test_product_is_available_by_default(self):
        for product in self.products:
            self.assertTrue(product.available)

    def test_product_category_should_be_within_choices(self):
        for model in self.product_child_models:
            with self.assertRaises(ValidationError):
                model.objects.create(name="а", price_low=1, price_high=10, category="5")

    def test_product_category_cannot_be_changed(self):
        for product in self.products:
            product.category = "3" if product.category != "3" else "1"
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_category_is_set_correctly(self):
        for model in self.product_child_models:
            product = model.objects.create(name="тест", price_low=1, price_high=10)
            self.assertEqual(product.category, model.CATEGORY)

    def test_product_number_is_correctly_assigned_for_new_entry(self):
        for product in self.products:
            self.assertEqual(product.product_number, int(f"{product.category}0001"))
        for model in self.product_child_models:
            product = model.objects.create(name="а", price_low=1, price_high=10)
            self.assertIsNotNone(product.product_number)
            self.assertEqual(product.product_number, int(f"{product.category}0002"))

    def test_product_number_is_unique(self):
        for _ in range(20):
            Clothing.objects.create(name="тест", price_low=1, price_high=10)
        product_numbers = list(c.product_number for c in Clothing.objects.all())
        self.assertEqual(len(product_numbers), len(set(product_numbers)))

    def test_product_number_cannot_be_set_manually(self):
        for model in self.product_child_models:
            with self.assertRaises(Product.DoesNotExist):
                model.objects.create(
                    name="тест", 
                    price_low="1", 
                    price_high="2", 
                    product_number="33333"
                    )
                
    def test_product_number_cannot_be_changed(self):
        for product in self.products:
            product.product_number = "33333"
            with self.assertRaises(ValidationError):
                product.save()

    def test_product_slug_is_correctly_assigned_for_new_entry(self):
        for model in self.product_child_models:
            product = model.objects.create(name="а", price_low=1, price_high=10)
            self.assertNotEqual(product.slug, "")
            self.assertIsNotNone(product.slug)
            slug_name = f"{product.product_number}-{product.name}"
            self.assertEqual(
                product.slug, slugify(slug_name, separator="-", lowercase=True)
                )

    def test_product_slug_cannot_be_set_manually(self):
        test_slug = "test"
        for model in self.product_child_models:
            product = model.objects.create(
                name="тест", 
                price_low="1", 
                price_high="1", 
                slug=test_slug,
                )
            self.assertNotEqual(product.slug, test_slug)

    def test_product_slug_cannot_be_changed(self):
        for product in self.products:
            product_slug = product.slug
            product.slug = "test"
            product.save()
            self.assertEqual(product.slug, product_slug)

    def test_main_image_returns_correct_image(self):
        for product in self.products[3:]:
            image = product.images.first()
            self.assertEqual(image, product.main_image)

            main_image = ProductImage.objects.create(
                product=product, 
                image="catalog\tests\test_media\test.avif",
                is_main=True
                )
            self.assertTrue(main_image.is_main)
            self.assertFalse(image.is_main)

            main_image.is_main = False
            main_image.save()

    def test_product_str(self):
        for product in self.products:
            self.assertEqual(str(product), f"{product.product_number} {product.name}")

    def test_product_ordering(self):
        self.assertEqual(Product.objects.first().pk, self.clothing.pk)
        self.assertEqual(Product.objects.last().pk, self.accessory.pk)

        self.clothing.available = False
        self.clothing.save()
        
        self.assertEqual(Product.objects.first().pk, self.footwear.pk)
        self.assertEqual(Product.objects.last().pk, self.clothing.pk)

    def test_product_class_should_not_create_instances(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(name="тест", price_low=1, price_high=2)

    def test_product_category_is_assigned_correctly(self):
        pass


class ProductImageModelTest(TestCase):
    @classmethod
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
        
    def test_product_image_is_created_correctly(self):
        self.assertTrue(ProductImage.objects.exists())
        self.assertEqual(ProductImage.objects.first().product.pk, self.product.pk)
        
    def test_product_image_is_deleted_on_product_delete(self):
        self.product.delete()
        self.assertFalse(ProductImage.objects.exists())

    def test_product_image_adds_correct_image(self):
        self.assertEqual(self.product_image.image, self.image)
        
    def test_product_image_not_is_main_by_default(self):
        self.assertFalse(self.product_image.is_main)

    def test_product_image_is_main_is_changed_correctly(self):
        self.product_image.is_main = True
        self.product_image.save()
        self.assertTrue(self.product_image.is_main)

        main_image = ProductImage.objects.create(
            product=self.product, 
            image="catalog\tests\test_media\test_3.jpg",
            is_main=True
            )
        self.product_image.refresh_from_db()
        self.assertFalse(self.product_image.is_main)
        self.assertTrue(main_image.is_main)
        self.assertEqual(self.product.main_image, main_image)

    def test_product_image_str(self):
        self.assertEqual(str(self.product_image), f"Зображення: {self.product}")


class CustomerModelTest(TestCase):
    @classmethod
    def setUp(self):
        self.customer = get_user_model().objects.create(
            first_name="test", 
            last_name="test", 
            email="test@test.com"
            )
        self.clothing = Clothing.objects.create(
            name="одяг",
            price_low=100,
            price_high=200,
        )
        self.footwear = Footwear.objects.create(
            name="взуття",
            price_low=1000,
            price_high=2000,
        )
        self.accessory = Accessory.objects.create(
            name="аксесуар",
            price_low=10,
            price_high=20,
        )
        
    def test_customer_username_is_none(self):
        self.assertIsNone(self.customer.username)

    def test_customer_email_is_unique(self):
        customer = Customer(first_name="t", last_name="t", email=self.customer.email)
        with self.assertRaises(ValidationError):
            customer.full_clean()

    def test_new_customer_wishlist_is_empty(self):
        self.assertEqual(self.customer.wishlist.all().count(), 0)

    def test_customer_wishlist_adds_items_correctly(self):
        self.customer.wishlist.add(self.clothing, self.footwear, self.accessory)
        self.customer.save()
        self.assertEqual(Customer.objects.first().wishlist.all().count(), 3)

    def test_customer_str(self):
        user = self.customer
        self.assertEqual(str(user), f"{user.email}, {user.first_name} {user.last_name}")
