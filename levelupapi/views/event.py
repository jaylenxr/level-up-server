from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Game, Gamer, EventGamer
from rest_framework.decorators import action

class EventView(ViewSet):

    def retrieve(self, request, pk):
        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def list(self, request):
        events = Event.objects.all()
        uid = request.META['HTTP_AUTHORIZATION']
        gamer = Gamer.objects.get(uid=uid)

        for event in events:
            # Check to see if there is a row in the Event Games table that has the passed in gamer and event
            event.joined = len(EventGamer.objects.filter(
                gamer=gamer, event=event)) > 0

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Handle POST operations
        # Returns
        # Response -- JSON serialized event instance

        organizer = Gamer.objects.get(uid=request.data["userId"])
        game = Game.objects.get(pk=request.data["gameId"])
        # Note on API naming conventions:
        # We use 'userId' and 'gameId' in request payloads for client clarity,
        # but store them as 'organizer' and 'game' in the database model.
        # This separation allows for a more intuitive API while maintaining
        # proper database relationships. When serialized in responses,
        # the fields appear as 'organizer' and 'game' to reflect the model structure.

        event = Event.objects.create(
            game=game,
            description=request.data["description"],
            date=request.data["date"],
            time=request.data["time"],
            organizer=organizer,
        )
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def update(self, request, pk):
        """Handle PUT requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """
        # Updates an existing event by finding it with the primary key,
        # modifying its fields with new data from the request,
        # and saving changes to the database. Returns 204 No Content on success.

        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]

        game = Game.objects.get(pk=request.data["gameId"])
        event.game = game
        event.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

# JOIN GAME EVENT
    @action(methods=['post'], detail=True)
    # this is a decorator & is an endpoint that isn't apart of usual CRUD functions
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
        # POST to /events/{id}/signup - adds user to event attendee list

        gamer = Gamer.objects.get(uid=request.data["user_id"])
         # get Gamer by UID from request body (uses django ORM .get())-- query by uid


        event = Event.objects.get(pk=pk) #--query by pk--
        attendee = EventGamer.objects.create(
        #creates new EventGamer relationship record in join table (new row added

            gamer=gamer,
            event=event
        )
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)

#LEAVE GAME EVENT
    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to leave an event"""
        # DELETE to /events/{id}/leave - removes user from event attendee list
        gamer = Gamer.objects.get(uid=request.data["user_id"])
        event = Event.objects.get(pk=pk)
        event_gamer = EventGamer.objects.get(
               gamer=gamer,
               event=event)
        event_gamer.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date', 'time', 'organizer', 'joined')