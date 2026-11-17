from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Avg, Count, F, Q
from django.db.models.signals import post_delete
from django.dispatch import receiver

phone_validator = RegexValidator(
    regex=r"^\+?\d{10,15}$",
    message="Digits only with country code, e.g. 2348012345678.",
)


class NigerianState(models.TextChoices):
    ABIA = "abia", "Abia"
    ADAMAWA = "adamawa", "Adamawa"
    AKWA_IBOM = "akwa-ibom", "Akwa Ibom"
    ANAMBRA = "anambra", "Anambra"
    BAUCHI = "bauchi", "Bauchi"
    BAYELSA = "bayelsa", "Bayelsa"
    BENUE = "benue", "Benue"
    BORNO = "borno", "Borno"
    CROSS_RIVER = "cross-river", "Cross River"
    DELTA = "delta", "Delta"
    EBONYI = "ebonyi", "Ebonyi"
    EDO = "edo", "Edo"
    EKITI = "ekiti", "Ekiti"
    ENUGU = "enugu", "Enugu"
    FCT = "fct", "FCT (Abuja)"
    GOMBE = "gombe", "Gombe"
    IMO = "imo", "Imo"
    JIGAWA = "jigawa", "Jigawa"
    KADUNA = "kaduna", "Kaduna"
    KANO = "kano", "Kano"
    KATSINA = "katsina", "Katsina"
    KEBBI = "kebbi", "Kebbi"
    KOGI = "kogi", "Kogi"
    KWARA = "kwara", "Kwara"
    LAGOS = "lagos", "Lagos"
    NASARAWA = "nasarawa", "Nasarawa"
    NIGER = "niger", "Niger"
    OGUN = "ogun", "Ogun"
    ONDO = "ondo", "Ondo"
    OSUN = "osun", "Osun"
    OYO = "oyo", "Oyo"
    PLATEAU = "plateau", "Plateau"
    RIVERS = "rivers", "Rivers"
    SOKOTO = "sokoto", "Sokoto"
    TARABA = "taraba", "Taraba"
    YOBE = "yobe", "Yobe"
    ZAMFARA = "zamfara", "Zamfara"


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
    state = models.CharField(
        max_length=20, choices=NigerianState.choices, db_index=True
    )
    location = models.CharField(max_length=150, db_index=True)
    contact_phone = models.CharField(max_length=20, validators=[phone_validator])
    contact_whatsapp = models.CharField(
        max_length=20, blank=True, validators=[phone_validator]
    )
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


class Rating(models.Model):
    """One user's star rating (1 to 5) and comment for one seller."""

    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_given",
    )
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_received",
    )
    stars = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} star" + ("s" if i > 1 else "")) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["rater", "rated_user"],
                name="one_rating_per_user_per_seller",
            ),
            models.CheckConstraint(
                condition=~Q(rater=F("rated_user")),
                name="no_self_rating",
            ),
        ]

    def __str__(self):
        return f"{self.rater} rated {self.rated_user}: {self.stars}"


def seller_rating_summary(user):
    """Average stars (one decimal, or None) and number of ratings for a seller."""
    data = Rating.objects.filter(rated_user=user).aggregate(
        average=Avg("stars"), count=Count("id")
    )
    average = data["average"]
    return {
        "average": round(average, 1) if average else None,
        "count": data["count"],
    }


@receiver(post_delete, sender=ListingImage)
def delete_image_file(sender, instance, **kwargs):
    """Delete the photo file from disk when its database row is deleted."""
    if instance.image:
        instance.image.delete(save=False)
