from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "listing_type",
        "category",
        "location",
        "price",
        "created_at",
    )

    list_filter = ("listing_type", "category", "location")

    search_fields = ("title", "description", "category", "location")