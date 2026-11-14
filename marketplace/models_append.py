

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
