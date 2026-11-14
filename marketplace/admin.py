from django.contrib import admin, messages

from .models import Category, ContactMessage, Listing, ListingImage, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ReportInline(admin.TabularInline):
    """Read-only report history shown inside each listing."""

    model = Report
    extra = 0
    can_delete = False
    fields = ("created_at", "reporter", "reason", "details", "status")
    readonly_fields = ("created_at", "reporter", "reason", "details", "status")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "listing_type",
        "category",
        "location",
        "status",
        "owner",
        "report_count",
        "created_at",
    )
    list_filter = ("status", "listing_type", "category")
    search_fields = ("title", "description", "location", "owner__username")
    inlines = [ListingImageInline, ReportInline]
    actions = ["approve_listings", "mark_pending", "close_listings"]

    @admin.display(description="Reports")
    def report_count(self, obj):
        return obj.reports.count()

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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("listing", "reason", "reporter", "status", "created_at")
    list_filter = ("status", "reason")
    search_fields = ("listing__title", "reporter__username", "details")
    readonly_fields = ("listing", "reporter", "reason", "details", "created_at")
    actions = ["hide_reported_listings", "mark_reviewed", "dismiss_reports"]

    @admin.action(description="Hide reported listings (back to pending) and mark reviewed")
    def hide_reported_listings(self, request, queryset):
        listing_ids = list(queryset.values_list("listing_id", flat=True))
        Listing.objects.filter(id__in=listing_ids).update(status=Listing.Status.PENDING)
        count = queryset.update(status=Report.Status.REVIEWED)
        self.message_user(request, f"{count} report(s) reviewed; listings hidden.", messages.WARNING)

    @admin.action(description="Mark selected reports as reviewed")
    def mark_reviewed(self, request, queryset):
        count = queryset.update(status=Report.Status.REVIEWED)
        self.message_user(request, f"{count} report(s) marked reviewed.", messages.SUCCESS)

    @admin.action(description="Dismiss selected reports (no problem found)")
    def dismiss_reports(self, request, queryset):
        count = queryset.update(status=Report.Status.DISMISSED)
        self.message_user(request, f"{count} report(s) dismissed.", messages.INFO)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "topic", "name", "user", "reply_contact", "status")
    list_filter = ("status", "topic")
    search_fields = ("name", "message", "user__username", "reply_contact")
    readonly_fields = ("user", "name", "reply_contact", "topic", "message", "created_at")
    actions = ["mark_answered", "mark_closed"]

    @admin.action(description="Mark selected messages as answered")
    def mark_answered(self, request, queryset):
        count = queryset.update(status=ContactMessage.Status.ANSWERED)
        self.message_user(request, f"{count} message(s) marked answered.", messages.SUCCESS)

    @admin.action(description="Close selected messages")
    def mark_closed(self, request, queryset):
        count = queryset.update(status=ContactMessage.Status.CLOSED)
        self.message_user(request, f"{count} message(s) closed.", messages.INFO)
