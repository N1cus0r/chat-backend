import string
import random

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


'''
Generates a 6 chars code in uppercase  
'''
def generate_room_code():
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=6))
        if not Room.objects.filter(code=code).exists():
            return code


class Room(models.Model):
    host_id = models.IntegerField()
    max_participants = models.IntegerField(
        default=5, validators=[MinValueValidator(2), MaxValueValidator(5)]
    )
    code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    participants = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def validate_participants(self):
        if self.participants > self.max_participants:
            raise ValidationError("Room is full !")

    def save(self, *args, **kwargs) -> None:
        self.validate_participants()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.code


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.text
