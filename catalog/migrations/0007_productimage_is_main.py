# Generated by Django 5.1.5 on 2025-04-29 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_productimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="productimage",
            name="is_main",
            field=models.BooleanField(default=False),
        ),
    ]
