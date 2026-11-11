from django.urls import path

from .views import (
    PackingItemDetailView,
    PackingTemplateDetailView,
    PackingTemplateListCreateView,
    TripItemsListCreateView,
)

urlpatterns = [path("trips/<uuid:trip_id>/packing", TripItemsListCreateView.as_view(), name="trip-packing"),
               path("packing/<uuid:pk>", PackingItemDetailView.as_view(), name="packing-detail"),
               path("packing-templates/", PackingTemplateListCreateView.as_view(), name="packing-templates"),
               path("packing-tempaltes/<uuid:pk>/", PackingTemplateDetailView.as_view(), name="packing-tempaltes-detail")]
