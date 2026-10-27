from core.views import OwnedViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import TripSerializer


class TripViewSet(OwnedViewSet):
    serializer_class = TripSerializer
    queryset = Trip.objects.all()

    @action(detail=True, methods=["post"])
    def copy(self, request, pk=None):
        trip = self.get_object()
        ...
        return Response(TripSerializer(new).data, status=201)
