import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Traveler(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="travelers",
        verbose_name=_("user"),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("Traveler")
        verbose_name_plural = _("Travelers")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
