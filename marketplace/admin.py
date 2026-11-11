from django.contrib import admin, messages

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
    list_filter = ("status", "listing_type", "category")
    search_fields = ("title", "description", "location", "owner__username")
    inlines = [ListingImageInline]
    actions = ["approve_listings", "mark_pending", "close_listings"]

    @admin.action(description="Approve selected listings")
    def approve_listings(self, request, queryset):
        count = queryset.update(status=Listing.Status.ACTIVE)
        self.message_user(request, f"{count} listing(s) approved.", messages.SUCCESS)

    @admin.action(description="Send selected listings back to pending")
    def mark_pending(self, request, queryset):
        count = queryset.update(status=Listing.Status.PENDING)
        self.message_user(request, f"{count} listing(s) set to pending.", messages.WARNING)

    @admin.action(description="Close selected listings")
    def close_listings(self, request, queryset):
        count = queryset.update(status=Listing.Status.CLOSED)
        self.message_user(request, f"{count} listing(s) closed.", messages.INFO)