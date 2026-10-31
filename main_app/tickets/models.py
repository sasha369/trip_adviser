import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TicketGroup(models.Model):
    """Упорядоченный набор билетов одного направления (туда / обратно / промежуточные); предмет проверки стыковок (минимум 30 минут между прибытием и отправлением)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(
        "trips.Trip",
        verbose_name=_("trip"),
        on_delete=models.CASCADE,
        related_name="ticket_groups",
    )
    DIRECTION_CHOICES = [
        ("outbound", "outbound"),
        ("return", "return"),
        ("layover", "layover"),
    ]
    direction = models.CharField(
        _("direction"), max_length=20, choices=DIRECTION_CHOICES, default="outbound"
    )

    class Meta:
        verbose_name = _("TicketGroup")
        verbose_name_plural = _("TicketGroups")

    def __str__(self):
        return f"{self.trip} - {self.direction}"


class Ticket(models.Model):
    """Сегмент проезда/перелёта: тип транспорта, даты-времена с часовыми поясами, пункты отправления/прибытия, номер рейса/поезда, место/вагон, статус покупки, ссылка на электронный билет, привязка к путнику(ам)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        TicketGroup,
        verbose_name=_("ticket group"),
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    TRANSPORT_CHOICES = [
        ("plane", "plane"),
        ("bus", "bus"),
        ("train", "train"),
        ("car", "car"),
    ]
    transport_type = models.CharField(
        _("transport type"), max_length=10, choices=TRANSPORT_CHOICES, default="train"
    )
    departure_at = models.DateTimeField(
        _("departure time"), auto_now=False, auto_now_add=False
    )
    arrival_at = models.DateTimeField(
        _("arrival time"), auto_now=False, auto_now_add=False
    )
    origin_point = models.CharField(_("origin"), max_length=200)
    destination_point = models.CharField(_("destination"), max_length=200)
    route_number = models.CharField(_("route number"), max_length=20)
    seat = models.CharField(_("seat"), max_length=20)
    STATUS_CHOICES = [
        ("required", "required"),
        ("booked", "booked"),
        ("purchased", "purchased"),
    ]
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="required"
    )
    ticket_file_link = models.URLField(
        _("ticket file link"), max_length=200, blank=True, null=True
    )
    travelers = (
        models.ManyToManyField(
            "accounts.Traveler",
            verbose_name=_("traveler"),
            blank=True,
            related_name="tickets",
        ),
    )
    order = models.PositiveIntegerField(_("order"), default=0, db_index=True)

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return f"{self.group} - {self.route_number}"
