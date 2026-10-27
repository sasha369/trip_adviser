"""Модель путешествия и его содержания: дни, билеты, список вещей"""

import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Trip(models.Model):
    """Модель путешествия: название, даты, точки старта и назначения, путники, статус"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trips",
        verbose_name=_("user"),
    )
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    STATUS_CHOICES = [
        ("planned", "planned"),
        ("active", "active"),
        ("completed", "completed"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="planned")
    status_manual = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Trip")
        verbose_name_plural = _("Trips")

    def __str__(self) -> str:
        return str(self.title)


class Day(models.Model):
    """Модель дня - единицы плана: заголовок/описание, геолокация, набор целей"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip_id = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="days", verbose_name=_("trip")
    )
    date = models.DateField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=2000, blank=True)
    geo_location = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _("Day")
        verbose_name_plural = _("Days")

    def __str__(self) -> str:
        return str(self.title or _("Unnamed"))


class Goal(models.Model):
    """Модель цели за день: название, описание, обязательность, \\
    время/интервал, порядок, отметка выполнения"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day_id = models.ForeignKey(
        Day, on_delete=models.CASCADE, related_name="goals", verbose_name=_("goal")
    )
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    is_mandatory = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = _("Goal")
        verbose_name_plural = _("Goals")

    def __str__(self) -> str:
        return str(self.title)
