# Generated by Django 5.1.6 on 2025-03-09 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="customer",
            managers=[],
        ),
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(default=""),
        ),
    ]
