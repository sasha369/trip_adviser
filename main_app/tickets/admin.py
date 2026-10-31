from django.contrib import admin

from .models import Ticket, TicketGroup


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    fields = [
        "group",
        "transport_type",
        "departure_at",
        "arrival_at",
        "origin_point",
        "destination_point",
        "route_number",
        "seat",
        "status",
        "ticket_file_link",
        "travelers",
        "order",
    ]


@admin.register(TicketGroup)
class TicketGroupAdmin(admin.ModelAdmin):
    fields = ["trip", "direction"]
