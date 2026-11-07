from django.contrib import admin

from .models import User, Traveler


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    fields = ["username", "email"]


@admin.register(Traveler)
class AdminTraveler(admin.ModelAdmin):
    fields = ["user", "first_name", "last_name", "birth_date"]
