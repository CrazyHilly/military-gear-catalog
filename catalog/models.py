from django.db import models


class Country(models.Model):
    en_name = models.CharField(max_length=60, unique=True)
    ua_name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.ua_name

    class Meta:
        ordering = ["ua_name"]
