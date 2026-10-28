from accounts.models import Traveler
from rest_framework import serializers

from .models import Day, Goal, Trip


class _IntervalMixin:
    """У цели либо время, либо интервал"""

    def _validate_interval(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if end and not start:
            raise serializers.ValidationError(
                {"end_time": "Интервал требует времени начала"}
            )
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "Время окончания должно быть позже начала"}
            )
        return attrs


class GoalSerializer(_IntervalMixin, serializers.ModelSerializer):
    day_id = serializers.PrimaryKeyRelatedField(
        source="day", queryset=Day.objects.none(), required=False
    )
    start_time = serializers.TimeField(format="%H:%M", required=False, allow_null=True)
    end_time = serializers.TimeField(format="%H:%M", required=False, allow_null=True)
    sort_order = serializers.IntegerField(min_value=0, required=False)

    class Meta:
        model = Goal
        fields = [
            "id",
            "day_id",
            "title",
            "description",
            "is_mandatory",
            "start_time",
            "end_time",
            "is_completed",
            "sort_order",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["day_id"].queryset = Day.objects.filter(trip__user=request.user)

    def validate(self, attrs):
        return self._validate_interval(attrs)


class GoalCreateSerializer(_IntervalMixin, serializers.ModelSerializer):
    start_time = serializers.TimeField(format="%H:%M", required=False, allow_null=True)
    end_time = serializers.TimeField(format="%H:%M", required=False, allow_null=True)
    sort_order = serializers.IntegerField(min_value=0, required=False)

    class Meta:
        model = Goal
        fields = [
            "title",
            "description",
            "is_mandatory",
            "start_time",
            "end_time",
            "sort_order",
        ]

    def validate(self, attrs):
        return self._validate_interval(attrs)


class DaySerializer(serializers.ModelSerializer):
    goals = GoalSerializer(many=True, read_only=True)

    class Meta:
        model = Day
        fields = ["id", "date", "title", "description", "geo_location", "goals"]
        read_only_fields = ["id", "date"]


class TripSerializer(serializers.ModelSerializer):
    travelers = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Traveler.objects.none()
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "title",
            "start_date",
            "end_date",
            "origin",
            "destination",
            "travelers",
            "status",
            "status_manual",
            "effective_status",
        ]
        read_only_fields = ["id", "status_manual", "effective_status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["travelers"].child_relation.queryset = Traveler.objects.filter(
                user=request.user
            )

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "Дата окончания раньше даты начала"}
            )
        if "status" in attrs:
            attrs["status_manual"] = True
        return attrs


class TripDetailSerializer(TripSerializer):
    days = DaySerializer(many=True, read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ["days"]


class CopyTripSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "Дата окончания раньше даты начала"}
            )
        return attrs
