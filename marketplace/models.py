from django.db import models

# Create your models here.

from django.db import models


class Listing(models.Model):
    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="listings",
    )
    LISTING_TYPES = [
        ("service", "Service"),
        ("product", "Product"),
    ]

    title = models.CharField(max_length=200)
    listing_type = models.CharField(
        max_length=10,
        choices=LISTING_TYPES,
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    contact_phone = models.CharField(max_length=20)
    contact_whatsapp = models.CharField(
        max_length=20,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title