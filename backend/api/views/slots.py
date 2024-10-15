from rest_framework import viewsets

from api.filters.slots import SlotFilter
from api.serializers.slots import SlotSerializer
from slots.models import Slot


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    filterset_class = SlotFilter
