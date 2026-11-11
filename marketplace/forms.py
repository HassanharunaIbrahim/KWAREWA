from django import forms

from .models import Listing


class ListingForm(forms.ModelForm):
    photo = forms.ImageField(required=False, help_text="Optional. JPG or PNG, up to 5 MB.")

    class Meta:
        model = Listing
        fields = [
            "title",
            "listing_type",
            "category",
            "description",
            "price",
            "location",
            "contact_phone",
            "contact_whatsapp",
        ]

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Photo must be under 5 MB.")
        return photo