from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from ..models import Room, Message

'''
Custom Token serializer class that provides 
user id and username in the token 
'''
class MyTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_id"] = user.id
        token["user_username"] = user.username

        return token

'''
Simple User model serializer
'''
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            password=make_password(validated_data["password"]),
        )

        return user

'''
Simple Room model serializer
'''
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "host_id", "code", "max_participants", "participants")

'''
Create Room serializer
'''
class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("max_participants",)

'''
Simple Message model serializer
'''
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
