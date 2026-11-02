from django import forms
from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title",
            "listing_type",
            "description",
            "price",
            "category",
            "location",
            "contact_phone",
            "contact_whatsapp",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 4}
            ),
        }