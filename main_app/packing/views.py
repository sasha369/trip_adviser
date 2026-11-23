from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from trips.models import Trip

from .models import PackingItem, PackingTemplate
from .serializers import (
    PackingItemSerializer,
    PackingTemplateSerializer,
)


class TripItemsListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PackingItem
    pagination_class = None

    def get_trip(self) -> Trip:
        return get_object_or_404(
            Trip,
            id=self.kwargs["trip_id"],
            user=self.request.user
        )

    def get_queryset(self):
        return self.get_trip().items.all()

    def perform_create(self, serializer):
        serializer.save(trip=self.get_trip())

class PackingItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PackingItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            PackingItem,
            id=self.kwargs["pk"],
            trip__user=self.request.user
        )

class PackingTemplateListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    serializer_class = PackingTemplateSerializer

    def get_queryset(self):
        return PackingTemplate.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        ).prefetch_related("items")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PackingTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PackingTemplateSerializer

    def get_queryset(self):
        return PackingTemplate.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        ).prefetch_related("items")

    def _deny_if_system(self, instance):
        if instance.user_id is None:
            raise PermissionDenied(_("Нельзя менять системные шаблоны"))

    def perform_update(self, serializer):
        self._deny_if_system(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._deny_if_system(instance)
        instance.delete()