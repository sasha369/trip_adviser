from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

# TODO: создать все вьюхи

router = DefaultRouter()
router.register("trips", TripViewSet, basename="trips")
router.register("goals", GoalViewSet, basename="goals")

urlpatterns = router.urls
