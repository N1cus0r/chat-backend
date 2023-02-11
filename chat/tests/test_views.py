import pytest

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import fake
from chat.models import Room, generate_room_code


@pytest.mark.django_db
def test_create_user_view(client):
    form_data = {"username": fake.word(), "password": fake.password()}

    response = client.post(path=reverse("chat:create-user"), data=form_data)

    assert response.status_code == 201

    assert User.objects.count() == 1


@pytest.mark.django_db
def test_get_room_details_view(user_factory, room_factory, client):
    user = user_factory.create()
    room = room_factory.create()
    room_code = room.code

    client.force_authenticate(user)
    response = client.get(
        path=reverse("chat:get-room-details"), data={"code": room_code}
    )

    assert response.status_code == 200

    assert response.data.get("id") == room.id


@pytest.mark.django_db
def test_create_room_view(user_factory, client):
    user = user_factory.create()
    tokens = RefreshToken.for_user(user)
    form_data = {"max_participants": fake.pyint(min_value=2, max_value=5)}

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")
    create_room_response = client.post(path=reverse("chat:create-room"), data=form_data)

    assert create_room_response.status_code == 201

    assert Room.objects.count() == 1

    assert create_room_response.data.get("host_id") == user.id

    create_new_room_response = client.post(path=reverse("chat:create-room"), data=form_data)
    
    assert create_new_room_response.status_code == 201

    assert Room.objects.count() == 1

    assert create_new_room_response.data.get("host_id") == user.id
    

@pytest.mark.django_db
def test_join_room_view(user_factory, room_factory, client):
    user_1 = user_factory.create()
    user_2 = user_factory.create()
    user_3 = user_factory.create()
    room = room_factory.create(max_participants=2)

    client.force_authenticate(user_1)
    first_room_join_response = client.put(
        path=reverse("chat:join-room"), data={"code": room.code}
    )

    client.force_authenticate(user_2)
    second_room_join_response = client.put(
        path=reverse("chat:join-room"), data={"code": room.code}
    )

    client.force_authenticate(user_3)
    third_room_join_response = client.put(
        path=reverse("chat:join-room"), data={"code": room.code}
    )

    assert first_room_join_response.status_code == 200

    assert second_room_join_response.status_code == 200

    assert third_room_join_response.status_code == 403


@pytest.mark.django_db
def test_leave_room_view(user_factory, room_factory, client):
    room_host = user_factory.create()
    room_participant = user_factory.create()
    room = room_factory.create(host_id=room_host.id, participants=2)

    participant_tokens = RefreshToken.for_user(room_participant)
    host_tokens = RefreshToken.for_user(room_host)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {participant_tokens.access_token}")
    participant_leave_response = client.put(
        path=reverse("chat:leave-room"), data={"code": room.code}
    )

    assert participant_leave_response.status_code == 200

    assert Room.objects.count() == 1

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {host_tokens.access_token}")
    host_leave_response = client.put(
        path=reverse("chat:leave-room"), data={"code": room.code}
    )

    assert host_leave_response.status_code == 200

    assert Room.objects.count() == 0


@pytest.mark.django_db
def test_get_room_messages_view(user_factory, room_factory, message_factory, client):
    user = user_factory.create()
    room = room_factory.create()
    message_factory.create_batch(size=12, room=room, user=user)

    client.force_authenticate(user)
    response = client.get(path=reverse("chat:get-messages"), data={"roomId": room.id})

    assert response.status_code == 200

    assert len(response.data) == 10


@pytest.mark.django_db
def test_is_room_active_view(room_factory, client):
    room = room_factory.create()

    active_room_response = client.get(
        path=reverse("chat:is-room-active"), data={"code": room.code}
    )
    inactive_room_response = client.get(
        path=reverse("chat:is-room-active"), data={"code": generate_room_code()}
    )

    assert active_room_response.status_code == 200

    assert inactive_room_response.status_code == 404
