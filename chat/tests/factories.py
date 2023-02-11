import factory
from faker import Faker

from django.contrib.auth.models import User
from chat.models import Room, Message


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"username-{n}")
    password = factory.PostGenerationMethodCall("set_password", fake.password())


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    host_id = factory.LazyFunction(lambda: UserFactory.create().id)
    max_participants = fake.pyint(min_value=2, max_value=5)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    room = factory.SubFactory(RoomFactory)
    user = factory.SubFactory(UserFactory)
    text = fake.sentence()
