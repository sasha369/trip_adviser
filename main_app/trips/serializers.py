from rest_framework import serializers
from .models import Trip, Day, Goal


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ["id", "title", "start_date", "end_date"]

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "Дата окончания раньше даты начала"}
            )
        return attrs


"""class GoalSerializer(serializers.ModelSerializer):
    day_id = """
