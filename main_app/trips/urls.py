from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DayDetailView, DayGoalListCreateView, GoalViewSet, TripViewSet

router = DefaultRouter()
router.register("trips", TripViewSet, basename="trips")
router.register("goals", GoalViewSet, basename="goals")

urlpatterns = [
    path(
        "trips/<uuid:trip_id>/days/<uuid:day_id>/goals/",
        DayGoalListCreateView.as_view(),
        name="day-goals",
    ),
    path(
        "trips/<uuid:trip_id>/days/<uuid:day_id>/",
        DayDetailView.as_view(),
        name="day-detail",
    ),
    path("", include(router.urls)),
]
