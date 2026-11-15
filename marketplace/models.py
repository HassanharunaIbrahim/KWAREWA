from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?\d{10,15}$",
    message="Digits only with country code, e.g. 2348012345678.",
)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Listing(models.Model):
    class ListingType(models.TextChoices):
        SERVICE = "service", "Service"
        PRODUCT = "product", "Product"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed / sold"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )
    title = models.CharField(max_length=200)
    listing_type = models.CharField(max_length=10, choices=ListingType.choices)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="listings"
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    location = models.CharField(max_length=150, db_index=True)
    contact_phone = models.CharField(max_length=20, validators=[phone_validator])
    contact_whatsapp = models.CharField(
        max_length=20, blank=True, validators=[phone_validator]
    )
    # Switch the default to PENDING once admin moderation is ready.
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["listing_type", "status"])]

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="listings/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"



class Report(models.Model):
    class Reason(models.TextChoices):
        SCAM = "scam", "Scam or fraud"
        FAKE = "fake", "Fake or misleading listing"
        PROHIBITED = "prohibited", "Prohibited item or service"
        DUPLICATE = "duplicate", "Duplicate listing"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        REVIEWED = "reviewed", "Reviewed"
        DISMISSED = "dismissed", "Dismissed"

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="reports"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_reports",
    )
    reason = models.CharField(max_length=20, choices=Reason.choices)
    details = models.TextField(blank=True, max_length=1000)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "reporter"],
                name="one_report_per_user_per_listing",
            )
        ]

    def __str__(self):
        return f"{self.get_reason_display()} - {self.listing.title}"



class ContactMessage(models.Model):
    class Topic(models.TextChoices):
        QUESTION = "question", "Question"
        APPEAL = "appeal", "Appeal a decision about my listing"
        BUG = "bug", "Problem with the site"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NEW = "new", "New"
        ANSWERED = "answered", "Answered"
        CLOSED = "closed", "Closed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
    )
    name = models.CharField(max_length=100)
    reply_contact = models.CharField(
        max_length=150,
        help_text="Where we can reply: an email address or a WhatsApp number.",
    )
    topic = models.CharField(max_length=20, choices=Topic.choices)
    message = models.TextField(max_length=2000)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.NEW
    )
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_topic_display()} from {self.name}"

