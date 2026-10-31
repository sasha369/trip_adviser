from accounts.models import Traveler
from rest_framework import serializers

from .models import Ticket, TicketGroup


class TicketGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketGroup
        fields = ["id", "trip", "direction"]


class TicketSerializer(serializers.ModelSerializer):
    travelers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Traveler.objects.none(), required=False
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "group",
            "transport_type",
            "departure_at",
            "arrival_at",
            "origin_point",
            "destination_point",
            "route_number",
            "seat",
            "travelers",
            "order",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["travelers"].child_relation.queryset = Traveler.objects.filter(
                user=request.user
            )

    def validate(self, attrs):
        depart = attrs.get("departure_at", getattr(self.instance, "departure_at", None))
        arrive = attrs.get("arrival_at", getattr(self.instance, "arrival_at", None))
        if depart and arrive and depart >= arrive:
            raise serializers.ValidationError(
                {"departure_at": "Дата вылета должна быть раньше даты прилета"}
            )
        return attrs
