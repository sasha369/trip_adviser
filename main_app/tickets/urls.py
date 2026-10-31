from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExtractResultView,
    ExtractView,
    TicketsViewSet,
    TripTicketListCreateView,
)

router = DefaultRouter()
router.register("tickets", TicketsViewSet, basename="tickets")

urlpatterns = [
    path(
        "trips/{uuid:trip_id}/tickets/",
        TripTicketListCreateView.as_view(),
        name="trip-tickets",
    ),
    path("tickets/extract/", ExtractView.as_view(), name="ticket-extract"),
    path(
        "ticket/extract/{uuid:task_id}",
        ExtractResultView.as_view(),
        name="ticket-extract-result",
    ),
    path("", include(router.urls)),
]
