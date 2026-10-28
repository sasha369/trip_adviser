from core.views import OwnedViewSet
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services
from .models import Day, Goal, Trip
from .serializers import (
    CopyTripSerializer,
    DaySerializer,
    GoalCreateSerializer,
    GoalSerializer,
    TripDetailSerializer,
    TripSerializer,
)


class TripViewSet(OwnedViewSet):
    """§7: /api/trips — CRUD, фильтр по статусу, copy, route-options."""

    serializer_class = TripSerializer
    queryset = Trip.objects.prefetch_related("days__goals", "travelers")

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")  # type: ignore
        if status_param in ["planned", "active", "completed"]:
            today = timezone.localdate()
            by_dates = {
                "planned": Q(start_date__gt=today),
                "active": Q(start_date__lte=today, end_date__gte=today),
                "completed": Q(end_date__lt=today),
            }[status_param]
            qs = qs.filter(
                Q(status_manual=False) & by_dates
                | Q(status_manual=True, status=status_param)
            )
        return qs

    def get_serializer_class(self):  # type: ignore
        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer

    def perform_create(self, serializer):
        serializer.instance = services.create_trip(
            self.request.user, dict(serializer.validated_data)
        )

    def perform_update(self, serializer):
        serializer.instance = services.update_trip(
            serializer.instance, dict(serializer.validated_data)
        )

    @action(detail=True, methods=["post"])
    def copy(self, request, pk=None):
        trip = self.get_object()
        payload = CopyTripSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        new_trip = services.copy_trip(trip, **payload.validated_data)
        return Response(
            TripSerializer(new_trip, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="route-options")
    def route_options(self, request, pk=None):
        return Response(services.route_options(self.get_object()))


class GoalViewSet(OwnedViewSet):
    """§7: /api/goals/{id} — чтение/правка/удаление и перенос между днями."""

    queryset = Goal.objects.select_related("day")
    serializer_class = GoalSerializer

    def get_queryset(self):
        # у Goal нет user — скоупим через день → поездку владельца
        return self.queryset.filter(day__trip__user=self.request.user)

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST")  # создание — только через день (см. §7)

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        day = data.pop("day", serializer.instance.day)
        sort_order = data.pop("sort_order", None)
        serializer.instance = services.update_goal(
            serializer.instance, data=data, day=day, sort_order=sort_order
        )


class DayGoalListCreateView(generics.ListCreateAPIView):
    """§7: /api/trips/{id}/days/{dayId}/goals."""

    permission_classes = [IsAuthenticated]  # noqa: RUF012
    pagination_class = None

    def get_day(self) -> Day:
        return get_object_or_404(
            Day,
            id=self.kwargs["day_id"],
            trip_id=self.kwargs["trip_id"],
            trip__user=self.request.user,
        )

    def get_queryset(self):
        return self.get_day().goals.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return GoalCreateSerializer
        return GoalSerializer

    def perform_create(self, serializer):
        data = dict(serializer.validated_data)
        sort_order = data.pop("sort_order", None)
        serializer.instance = services.create_goal(
            day=self.get_day(), data=data, sort_order=sort_order
        )


class DayDetailView(generics.RetrieveUpdateAPIView):
    """§7: /api/trips/{id}/days/{dayId} — заголовок/описание/геолокация."""

    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated]  # noqa: RUF012

    def get_object(self):
        return get_object_or_404(
            Day,
            id=self.kwargs["day_id"],
            trip_id=self.kwargs["trip_id"],
            trip__user=self.request.user,
        )
