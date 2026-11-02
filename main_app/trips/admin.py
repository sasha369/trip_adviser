from django.contrib import admin

from .models import Day, Goal, Trip


class DayAdmin(admin.ModelAdmin):
    fields = ["trip", "date", "title", "description", "geo_location"]


class GoalAdmin(admin.ModelAdmin):
    fields = [
        "day",
        "title",
        "description",
        "is_mandatory",
        "start_time",
        "end_time",
        "is_completed",
    ]


class TripAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "title",
        "start_date",
        "end_date",
        "origin",
        "destination",
        "travelers",
        "status",
    ]


admin.site.register(Day, DayAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(Trip, TripAdmin)
