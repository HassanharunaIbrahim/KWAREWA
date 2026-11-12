from django import forms

from .models import Listing, Report


class ListingForm(forms.ModelForm):
    photo = forms.ImageField(
        required=False,
        help_text="Optional. JPG or PNG, up to 5 MB.",
    )

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
        labels = {
            "listing_type": "Type",
            "contact_phone": "Phone number",
            "contact_whatsapp": "WhatsApp number",
            "price": "Price (₦)",
        }
        help_texts = {
            "contact_phone": "Digits only with country code, e.g. 2348012345678.",
            "contact_whatsapp": "Optional. Same format as the phone number.",
            "price": "Leave empty for services priced on request.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Generator repair"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Samaru, Zaria"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "2348012345678"}),
            "contact_whatsapp": forms.TextInput(attrs={"placeholder": "2348012345678"}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Photo must be under 5 MB.")
        return photo


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]
        labels = {
            "reason": "What is wrong with this listing?",
            "details": "More details (optional)",
        }
        widgets = {
            "details": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us what happened."}
            ),
        }
