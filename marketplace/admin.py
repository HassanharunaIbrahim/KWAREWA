from django.contrib import admin

from .models import Category, Listing, ListingImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "listing_type", "category", "location", "status", "owner", "created_at")
    list_filter = ("listing_type", "status", "category")
    search_fields = ("title", "description", "location")
    list_editable = ("status",)
    inlines = [ListingImageInline]