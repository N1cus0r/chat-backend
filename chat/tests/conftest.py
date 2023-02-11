import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .factories import UserFactory, RoomFactory, MessageFactory


register(UserFactory)

register(RoomFactory)

register(MessageFactory)


@pytest.fixture
def client():
    return APIClient()
