from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.forms import RegistrationForm


class RegistartionFormTests(TestCase):
    def setUp(self):
        self.form_data = {
            "email": "test@test.com",
            "first_name": "тест",
            "last_name": "тест",
            "password1": "password",
            "password2": "password"
        }
        self.form = RegistrationForm(data=self.form_data)
        self.user = self.form.save()

    def test_registration_form_is_valid(self):
        self.assertTrue(self.form.is_valid())        

    def test_registration_form_catches_incorrect_password(self):
        self.form_data["password2"] = "test"
        form = RegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Паролі не співпадають", form.errors["password2"])

    def test_registration_form_catches_missing_required_field(self):
        self.form_data.pop("email")
        form = RegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_registration_form_password_is_hashed(self):
        self.assertNotEqual(self.user.password, self.form_data["password1"])
        self.assertTrue(self.user.check_password(self.form_data["password1"]))

    def test_registration_form_saved_user_correctly(self):
        self.assertTrue(get_user_model().objects.exists())
        self.assertEqual(self.user.email, self.form_data["email"])
        self.assertEqual(self.user.first_name, self.form_data["first_name"])
        self.assertEqual(self.user.last_name, self.form_data["last_name"])

    def test_registartion_form_commit_attribute_works_correctly(self):
        self.user.delete()

        self.form.save(commit=False)
        self.assertFalse(get_user_model().objects.exists())

        self.form.save(commit=True)
        self.assertTrue(get_user_model().objects.exists())
