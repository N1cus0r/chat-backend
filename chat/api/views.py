import jwt

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from config.settings import SECRET_KEY
from ..models import Room, Message
from .serializers import (
    RoomSerializer,
    CreateRoomSerializer,
    MyTokenObtainSerializer,
    UserSerializer,
    MessageSerializer,
)


'''
This view overrides Simple JWT TokenObtainPairView 
serializer_class attribute to return user id and username
in the access token
'''
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer

'''
This view accepts POST requests and cerates
a User model instance 
'''
class CreateUser(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data provided !"})
'''
This view accepts GET requests of an authenticated user
and return the data of the Room model with given code
'''

class GetRoomDetails(APIView):
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        code = request.query_params.get("code")
        if code is not None:
            room_query = Room.objects.filter(code=code)
            if room_query.exists():
                room = room_query[0]
                data = self.serializer_class(room).data
                return Response(data, status=status.HTTP_200_OK)
            return Response(
                {"error": "Room not found, invalid room code"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"error": "Room code was not provided in url"},
            status=status.HTTP_404_NOT_FOUND,
        )

'''
This view accepts POST requests of an authenticated user
and creates a Room model instance
'''

class CreateRoom(APIView):
    serializer_class = CreateRoomSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            access_token = request.auth.token
            token_data = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            host_id = token_data["user_id"]
            max_participants = serializer.validated_data.get("max_participants")
            room_query = Room.objects.filter(host_id=host_id)
            if room_query.exists():
                room = room_query[0]
                room.host_id = host_id
                room.max_participants = max_participants
                room.participants = 0
                room.save(update_fields=["host_id", "max_participants"])
                return Response(
                    RoomSerializer(room).data, status=status.HTTP_201_CREATED
                )

            room = Room(host_id=host_id, max_participants=max_participants)
            room.save()
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

'''
This view accepts PUT requests of an authenticated user
and increments the participants field of a Room instance 
with the provided code if a room is not full
'''

class JoinRoom(APIView):
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        code = request.data.get("code")
        if code is not None:
            room_query = Room.objects.filter(code=code)
            if room_query.exists():
                room = room_query[0]
                if room.participants < room.max_participants:
                    room.participants += 1
                    room.save(update_fields=["participants"])
                    serializer = self.serializer_class(room)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(
                    {"error": "Room is full"}, status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {"error": "Room not found, invalid room code"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"error": "Room code was not provided in the body"},
            status=status.HTTP_404_NOT_FOUND,
        )

'''
This view accepts PUT requests of an authenticated user
and increments the participants field of a Room instance 
with the given code and destroys the room if the user
leaving the room is the host
'''

class LeaveRoom(APIView):
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        code = request.data.get("code")
        if code is not None:
            room_query = Room.objects.filter(code=code)
            if room_query.exists():
                room = room_query[0]
                access_token = request.auth.token
                token_data = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
                host_id = token_data["user_id"]
                if room.host_id == host_id:
                    room.delete()
                else:
                    room.participants -= 1
                    room.save(update_fields=["participants"])
                return Response({}, status=status.HTTP_200_OK)
            return Response(
                {"error": "Room not found, invalid room code"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"error": "Room code was not provided in the body"},
            status=status.HTTP_404_NOT_FOUND,
        )

'''
This view accepts GET requests of an authenticated user
and return last 10 messages sent in the room with the
provided id 
'''
class GetRoomMessages(APIView):
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        room_id = request.query_params.get("roomId")
        if room_id is not None:
            messages = Message.objects.filter(room_id=room_id).order_by("-time_sent")[
                :10
            ]
            serializer = self.serializer_class(messages, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Room code was not provided in url"},
            status=status.HTTP_404_NOT_FOUND,
        )

'''
This view accepts GET requests and return a 200 
status response if a room with provided code
exists else a 404 response 
'''
class IsRoomActive(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if code is not None:
            room_query = Room.objects.filter(code=code)
            if room_query.exists():
                return Response({}, status=status.HTTP_200_OK)
            return Response(
                {"error": "Room not found, invalid room code"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"error": "Room code was not provided in url"},
            status=status.HTTP_404_NOT_FOUND,
        )
