from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from slugify import slugify

from catalog.managers import CustomerManager


class Country(models.Model):
    en_name = models.CharField(
        max_length=60, 
        unique=True, 
        verbose_name="назва англійською"
        )
    ua_name = models.CharField(max_length=60, unique=True, verbose_name="країна")

    def __str__(self):
        return self.ua_name

    class Meta:
        ordering = ["ua_name"]
        verbose_name = "країна"
        verbose_name_plural = "країни"


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("1", "Одяг"),
        ("2", "Взуття"),
        ("3", "Аксесуари"),
    ]
    name = models.CharField(max_length=100, verbose_name="назва")
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="країна", 
    )
    description = models.TextField(blank=True, null=True, verbose_name="опис")
    price_low = models.PositiveIntegerField(
        validators=[MaxValueValidator(10000)], 
        verbose_name="ціна від"
    )
    price_high = models.PositiveIntegerField(
        validators=[MaxValueValidator(10000)], 
        verbose_name="ціна до"
    )
    available = models.BooleanField(default=True, verbose_name="в наявності")
    category = models.CharField(
        max_length=2, 
        choices=CATEGORY_CHOICES, 
        verbose_name="категорія",
        )
    product_number = models.IntegerField(
        unique=True, 
        verbose_name="код товару", 
        editable=False
        )
    slug = models.SlugField(null=False, blank=False, unique=True)

    @property
    def main_image(self):
        main_image = self.images.filter(is_main=True).first()
        return main_image if main_image else self.images.first()

    def __str__(self):
        return f"{self.product_number} {self.name}"
    
    class Meta:
        ordering = ["-available", "id"]
        verbose_name = "товар"
        verbose_name_plural = "товари"
    
    def clean(self):
        if not self.price_high or not self.price_low:
            return
        
        if self.price_low > self.price_high:
            raise ValidationError("Мінімальна ціна має бути нижчою від максимальної.")

    def save(self, *args, **kwargs):
        if self.__class__ == Product and not self.pk:
            raise ValidationError("Об'єкти можна створювати тільки через "\
                                  "моделі-нащадки: Clothing, Footwear, Accessory")
        
        if not self.product_number:
            product_objects = Product.objects.filter(category=self.category)
            last_product = product_objects.order_by("product_number").last()
            if last_product:
                self.product_number = last_product.product_number + 1
            else:
                self.product_number = int(self.category + "0001")

        else:
            db_product = Product.objects.get(pk=self.pk)
            if db_product.product_number != self.product_number:
                raise ValidationError("Код товару змінювати заборонено!")
            if db_product.category and db_product.category != self.category:
                raise ValidationError("Категорію товару змінювати заборонено!")

        slug_name = f"{self.product_number}-{self.name}"
        if not self.slug or self.slug != slug_name:
            self.slug = slugify(slug_name, separator="-", lowercase=True)

        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product-detail", args=[self.slug])


class Clothing(Product):
    def save(self, *args, **kwargs):
        category = "1"
        if self.category and self.category != category:
            raise ValidationError("Категорію товару змінювати заборонено!")
            
        self.category = category
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "одяг"
        verbose_name_plural = "одяг"


class Footwear(Product):
    def save(self, *args, **kwargs):
        category = "2"
        if self.category and self.category != category:
            raise ValidationError("Категорію товару змінювати заборонено!")
            
        self.category = category
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "взуття"
        verbose_name_plural = "взуття"


class Accessory(Product):
    def save(self, *args, **kwargs):
        category = "3"
        if self.category and self.category != category:
            raise ValidationError("Категорію товару змінювати заборонено!")
            
        self.category = category
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "аксесуар"
        verbose_name_plural = "аксесуари"


def product_image_path(instance, filename):
    return (f"product_images/{instance.product.category}/"
            f"{instance.product.product_number}/{filename}")


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name="images", 
        verbose_name="товар"
        )
    image = models.ImageField(upload_to=product_image_path, verbose_name="зображення")
    is_main = models.BooleanField(default=False, verbose_name="основне зображення")

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
    
    class Meta:
        verbose_name = "зображення"
        verbose_name_plural = "зображення"


class Customer(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    wishlist = models.ManyToManyField(Product, related_name="customers")

    objects = CustomerManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}, {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "клієнт"
        verbose_name_plural = "клієнти"
