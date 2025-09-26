# utils.py or forms.py
from django_countries import countries

# Middle East + USA (add/remove as needed)
SHIP_TO = [
    "AE", "SA", "QA", "KW", "OM", "BH", "JO", "LB", "EG", "US"
]

SHIP_TO_COUNTRIES = [(code, dict(countries)[code]) for code in SHIP_TO]


from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "sku", "short_description", "description",
            "price", "image_url", "gallery_csv",
            "is_active", "free_delivery", "is_bundle"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]"}),
            "sku": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]"}),
            "short_description": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]"}),
            "description": forms.Textarea(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]"}),
            "image_url": forms.URLInput(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]"}),
            "gallery_csv": forms.Textarea(attrs={"class": "w-full px-3 py-2 rounded-xl border border-[#E1E1E1]", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "rounded border-[#E1E1E1]"}),
            "free_delivery": forms.CheckboxInput(attrs={"class": "rounded border-[#E1E1E1]"}),
            "is_bundle": forms.CheckboxInput(attrs={"class": "rounded border-[#E1E1E1]"}),
        }
