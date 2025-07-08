import os
from django.core.management.base import BaseCommand

from catalog.models import Product, ProductImage

MEDIA_ROOT = os.path.join("media", "product_images")


class Command(BaseCommand):
    help = "Синхронізація зображень між папкою з файлами та базою даних"

    def handle(self, *args, **options):
        self.add_new_images()
        self.cleanup_missing_images()
        self.delete_duplicates()

    def add_new_images(self):
        categories = [item[0] for item in Product.CATEGORY_CHOICES]

        for category in os.listdir(MEDIA_ROOT):
            category_path = os.path.join(MEDIA_ROOT, category)

            if not os.path.isdir(category_path) or category not in categories:
                continue

            for product_number in os.listdir(category_path):
                product_path = os.path.join(category_path, product_number)
                product = Product.objects.filter(product_number=product_number).first()

                if not os.path.isdir(product_path) or not product:
                    continue
                
                for image_name in os.listdir(product_path):
                    image_path = os.path.join(product_path, image_name)
                    if not os.path.exists(image_path) or os.path.isdir(image_path):
                        continue

                    message = ""
                    db_url = "\\".join([
                        "product_images", 
                        category, 
                        product_number, 
                        image_name
                        ])
                    db_url_alt = db_url.replace("\\", "/")
                    db_image = (product.images.filter(image=db_url).first() 
                                or product.images.filter(image=db_url_alt).first())
                    if not db_image:
                        db_image = ProductImage.objects.create(
                            product=product,
                            image=db_url_alt,
                            )
                        message = f'Зображення "{image_name}" для "{product}" додано'
                    
                    image_base_name, _ = os.path.splitext(image_name)
                    if image_base_name == product_number and not db_image.is_main:
                        db_image.is_main = True
                        db_image.save()
                        message = (f'Основне зображення "{image_name}" для '
                                   f'"{product}" додано')
                    
                    if message:
                        print(message)
    
    def cleanup_missing_images(self):
        for product_image in ProductImage.objects.all():
            image_path = os.path.join("media", product_image.image.path)

            if not os.path.exists(image_path):
                product_image.delete()
                print(f'Зображення "{product_image.image.path}" для продукту '
                      f'"{product_image.product}" було видалено')
                
    def delete_duplicates(self):
        product_images_dict = {}

        for product_image in ProductImage.objects.all():
            product_number = product_image.product.product_number
            image_path = product_image.image.name
            image_path_normalized = image_path.replace("\\", "/")

            if product_number not in product_images_dict:        
                product_images_dict[product_number] = set()

            product_images = product_images_dict[product_number]
            if image_path in product_images or image_path_normalized in product_images:
                product_image.delete()
                print(f'Видалено зображення-дублікат "{product_image.image.path}" '
                      f'для продукту "{product_image.product}"')
            else:
                product_images_dict[product_number].add(image_path)




