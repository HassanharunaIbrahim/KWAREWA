from django import forms

from .models import (
    MAX_PHOTOS_PER_LISTING,
    ContactMessage,
    Listing,
    Rating,
    Report,
)


class ListingForm(forms.ModelForm):
    description = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    photo = forms.ImageField(
        required=False,
        help_text=(
            "Optional. JPG or PNG, up to 5 MB. "
            f"A listing can have up to {MAX_PHOTOS_PER_LISTING} photos."
        ),
    )

    class Meta:
        model = Listing
        fields = [
            "title",
            "listing_type",
            "category",
            "description",
            "price",
            "state",
            "location",
            "contact_phone",
            "contact_whatsapp",
        ]
        labels = {
            "listing_type": "Type",
            "state": "State",
            "location": "Area or town",
            "contact_phone": "Phone number",
            "contact_whatsapp": "WhatsApp number",
            "price": "Price (₦)",
        }
        help_texts = {
            "state": "The Nigerian state where the item or service is available.",
            "location": "For example: Samaru, Zaria",
            "contact_phone": "Digits only with country code, e.g. 2348012345678.",
            "contact_whatsapp": "Optional. Same format as the phone number.",
            "price": "Leave empty for services priced on request.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Generator repair"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Samaru, Zaria"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "2348012345678"}),
            "contact_whatsapp": forms.TextInput(attrs={"placeholder": "2348012345678"}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if not photo:
            return photo
        if photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Photo must be under 5 MB.")
        # When editing, stop the upload before anything is saved.
        if self.instance.pk and self.instance.images.count() >= MAX_PHOTOS_PER_LISTING:
            raise forms.ValidationError(
                f"This listing already has {MAX_PHOTOS_PER_LISTING} photos. "
                "Remove one before adding another."
            )
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


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "reply_contact", "topic", "message"]
        labels = {
            "name": "Your name",
            "reply_contact": "Email or WhatsApp number",
            "topic": "What is this about?",
            "message": "Your message",
        }
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "If this is an appeal, name the listing and explain why it should be restored.",
                }
            ),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["stars", "comment"]
        labels = {
            "stars": "Your rating",
            "comment": "Comment (optional)",
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={"rows": 4, "placeholder": "How was the work or the service?"}
            ),
        }