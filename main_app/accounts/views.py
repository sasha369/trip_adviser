from core.views import OwnedViewSet
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import User

# class AccountRegisterView(generics.CreateAPIView):
