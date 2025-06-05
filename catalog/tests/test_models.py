from django.core.exceptions import ValidationError
from django.test import TestCase

from catalog.models import Country


class CountryModelTest(TestCase):
    def setUp(self):
        self.country_1 = Country.objects.create(
            en_name="belgium",
            ua_name="бельгія",
        )
        self.country_2 = Country.objects.create(
            en_name="netherlands",
            ua_name="нідерланди",
        )

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
