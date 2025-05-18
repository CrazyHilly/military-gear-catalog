from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from slugify import slugify

from catalog.managers import CustomerManager


class Country(models.Model):
    en_name = models.CharField(max_length=60, unique=True)
    ua_name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.ua_name

    class Meta:
        ordering = ["ua_name"]


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("1", "Clothing"),
        ("2", "Footwear"),
        ("3", "Accessory"),
    ]
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    description = models.TextField(blank=True, null=True)
    price_low = models.PositiveIntegerField(
        validators=[MaxValueValidator(10000)]
    )
    price_high = models.PositiveIntegerField(
        validators=[MaxValueValidator(10000)]
    )
    available = models.BooleanField(default=True)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    product_number = models.IntegerField(unique=True)
    slug = models.SlugField(null=False)

    def __str__(self):
        return f"{self.product_number} {self.name}"

    def save(self, *args, **kwargs):
        if not self.product_number:
            last_product = Product.objects.filter(category=self.category).last()
            if last_product:
                self.product_number = last_product.product_number + 1
            else:
                self.product_number = int(self.category + "0001")
        if not self.slug:
            slug_name = f"{self.product_number}-{self.name}"
            self.slug = slugify(slug_name, separator="-", lowercase=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product-detail", args=[self.slug])

    class Meta:
        ordering = ["-available", "id"]
        
    @property
    def main_image(self):
        main_image = self.images.filter(is_main=True).first()
        return main_image if main_image else self.images.first()


class Clothing(Product):
    def save(self, *args, **kwargs):
        self.category = "1"
        super().save(*args, **kwargs)


class Footwear(Product):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = "2"


class Accessory(Product):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = "3"


def product_image_path(instance, filename):
    return (f"product_images/{instance.product.category}/"
            f"{instance.product.product_number}/{filename}")


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_image_path)
    is_main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            previous_main_image = ProductImage.objects.filter(
                product=self.product, 
                is_main=True
                )
            previous_main_image.exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Зображення: {self.product}"


class Customer(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    wishlist = models.ManyToManyField(Product, related_name="customers")

    objects = CustomerManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}, {self.first_name} {self.last_name}"
