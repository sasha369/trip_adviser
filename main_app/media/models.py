import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from pathlib import Path

def _extension(filename):
    return Path(filename).suffix.lower()

def original_upload_to(instance, filename):
    return f"original/{instance.trip_id}/{instance.pk}{_extension(filename)}"

def thumb_upload_to(instance, filename):
    return f"thumb/{instance.trip_id}/{instance.pk}.jpg"

class Media(models.Model):
    "Хранит пути к медиа"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.CASCADE,
        related_name="mediae",
        verbose_name=_("путешествие")
    )
    day = models.ForeignKey(
        "trips.Day",
        on_delete=models.CASCADE,
        related_name="mediae",
        verbose_name=_("день"),
        blank=True,
        null=True
    )
    goal = models.ForeignKey(
        "trips.Goal",
        on_delete=models.CASCADE,
        related_name="mediae",
        verbose_name=_("цель"),
        blank=True,
        null=True
    )
    KIND_CHOICES = [(_("фото"), _("фото")), (_("видео"), _("видео"))]
    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
        default=_("фото")
    )
    original_path = models.FileField(
        verbose_name=_("оригинальный путь"),
        max_length=255,
        upload_to=original_upload_to
    )
    thumb_path = models.FileField(
        verbose_name=_("путь обложки"),
        max_length=255,
        upload_to=thumb_upload_to,
    )
    size_bytes = models.PositiveBigIntegerField(
        default=0,
        editable=False,
        verbose_name=_("размер (байт)")
    )

    # TODO