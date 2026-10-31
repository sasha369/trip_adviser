from accounts.models import Traveler
from rest_framework import serializers

from .models import Ticket, TicketGroup


class _UserScopeMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if not (request and request.user.is_authenticated):
            return
        if "travelers" in self.fields:
            self.fields["travelers"].child_relation.queryset = Traveler.objects.filter(
                user=request.user
            )
        if "group" in self.fields:
            self.fields["group"].queryset = TicketGroup.objects.filter(
                trip__user=request.user
            )


class _TicketFormMixin:
    def validate(self, attrs):
        depart = attrs.get("departure_at", getattr(self.instance, "departure_at", None))
        arrive = attrs.get("arrival_at", getattr(self.instance, "arrival_at", None))
        if depart and arrive and depart >= arrive:
            raise serializers.ValidationError(
                {"departure_at": "Дата вылета должна быть раньше даты прилета"}
            )
        return attrs


class TicketSerializer(_UserScopeMixin, _TicketFormMixin, serializers.ModelSerializer):
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
            "status",
            "ticket_file_link",
        ]
        read_only_fields = ["id"]


class TicketCreateSerializer(
    _UserScopeMixin, _TicketFormMixin, serializers.ModelSerializer
):
    travelers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Traveler.objects.none(), required=False
    )
    direction = serializers.ChoiceField(
        choices=TicketGroup.DIRECTION_CHOICES,
        required=False,
        write_only=True,
    )
    for_all_travelers = serializers.BooleanField(required=False, write_only=True)
    order = serializers.IntegerField(read_only=True)

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
            "for_all_travelers",
            "status",
            "ticket_file_link",
        ]
        read_only_fields = ["id"]
