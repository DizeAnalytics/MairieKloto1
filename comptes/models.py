from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_INFO = "info"
    TYPE_DOCUMENT = "document"
    TYPE_RENDEZVOUS = "rendezvous"
    TYPE_CHOICES = [
        (TYPE_INFO, "Information"),
        (TYPE_DOCUMENT, "Document non conforme"),
        (TYPE_RENDEZVOUS, "Rendez-vous"),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO)
    rendezvous_datetime = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="notifications_sent",
        on_delete=models.SET_NULL,
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
