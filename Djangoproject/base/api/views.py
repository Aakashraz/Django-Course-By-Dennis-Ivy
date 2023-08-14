from rest_framework.decorators import api_view
from rest_framework.response import Response

from base.models import Room
from .serializers import RoomSerializer


@api_view(['GET'])
def getRoutes(request):
    routes=[
        'GET api/',
        'GET api/rooms',
        'GET api/rooms/:id',
    ]
    return Response(routes) #Response cannot return the python objects

@api_view(['GET'])
def getRooms(request):
    rooms= Room.objects.all()
    serializer= RoomSerializer(rooms, many=True) #many= True refers to many Room objects
    return Response(serializer.data)    
# request.POST  Only handles form data.  Only works for 'POST' method.
# request.data  Handles arbitrary data.  Works for 'POST', 'PUT' and 'PATCH' methods.

@api_view(['GET'])
def getOneRoomOnly(request,pk):
    room= Room.objects.get(id=pk)
    serializer= RoomSerializer(room, many=False) #many= True refers to many Room objects
    return Response(serializer.data) 