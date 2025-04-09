from django import forms


class ProductSearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Шукати товар"}
        )
    )
