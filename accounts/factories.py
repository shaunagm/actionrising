from factory.django import DjangoModelFactory
import factory.faker

from django.contrib.auth import models


class User(DjangoModelFactory):
    class Meta:
        model = models.User
        django_get_or_create = ('username', )

    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall('set_password', 'password')

    # profile is created in post_save signal so can't pass arguments through to RelatedFactory
