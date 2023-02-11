import pytest

from django.contrib.auth.models import User
from chat.models import Room, Message


@pytest.mark.django_db
def test_create_user_model(user_factory):
    new_user = user_factory.create()

    assert User.objects.count() == 1

    assert User.objects.last().id == new_user.id


@pytest.mark.django_db
def test_create_room_model(user_factory, room_factory):
    new_room = room_factory.create()

    assert Room.objects.count() == 1

    assert Room.objects.last().id == new_room.id

    assert new_room.host_id == User.objects.last().id

    assert str(new_room) == new_room.code


@pytest.mark.django_db
def test_create_message_model(message_factory):
    new_message = message_factory.create()

    assert Message.objects.count() == 1

    assert new_message.user == User.objects.last()

    assert new_message.room == Room.objects.last()

    assert str(new_message) == new_message.text
