from core.views import OwnedViewSet
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from trips.models import Trip

from . import services
from .models import Ticket
from .serializers import TicketCreateSerializer, TicketSerializer


class ExtractView(generics.CreateAPIView): ...  # TODO: когда разберемся с OCR


class ExtractResultView(generics.ListAPIView): ...


class TripTicketListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_trip(self):
        return get_object_or_404(
            Trip,
            id=self.kwargs["trip_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        return (
            Ticket.objects.filter(group__trip=self.get_trip())
            .select_related("group")
            .prefetch_related("travelers")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        data = dict(serializer.validated_data)
        for_all_travelers = data.pop("for_all_travelers", False)
        serializer.instance = services.create_ticket(
            trip=self.get_trip(), data=data, for_all_travelers=for_all_travelers
        )


class TicketsViewSet(OwnedViewSet):
    queryset = Ticket.objects.select_related("group__trip")
    serializer_class = TicketSerializer
    http_method_names = ["get", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        return self.queryset.filter(group__trip__user=self.request.user)

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        group_id = data.pop("group_id", None)
        order = data.pop("order", None)
        serializer.instance = services.update_ticket(
            ticket=serializer.instance, data=data, group_id=group_id, order=order
        )

    def perform_destroy(self, instance):
        services.delete_ticket(ticket=instance)
