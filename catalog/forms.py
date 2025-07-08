from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from catalog.models import ProductImage


class ProductSearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Пошук товарів", 
            "style": "width: 500px;"
            })
    )


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Підтвердіть пароль", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Паролі не співпадають")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class ProductImageInlineForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        product = cleaned_data.get("product")

        if image and product:
            product_images = product.images.values_list("image", flat=True)
            for product_image in product_images:
                if (image.name in product_image and 
                    self.instance.image.name != product_image):
                    self.add_error(None, ValidationError(
                        f'Зображення з імʼям "{image.name}" вже існує.',
                        code="duplicate_filename"
                    ))
        return cleaned_data
