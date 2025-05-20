from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import EventGamer


class EventGamerView(ViewSet):

    def retrieve(self, request, pk):

        event_gamer = EventGamer.objects.get(pk=pk)
        serializer = EventGamerSerializer(event_gamer)
        return Response(serializer.data)

    def list(self, request):

        event_gamers = EventGamer.objects.all()
        serializer = EventGamerSerializer(event_gamers, many=True)
        return Response(serializer.data)

class EventGamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGamer
        fields = ('id', 'label')