from factory.django import DjangoModelFactory
import factory
import slates.factories  # noqa # register Provider
from . import models


class Action(DjangoModelFactory):
    class Meta:
        model = models.Action

    title = factory.Faker("title")
    creator = factory.SubFactory("accounts.factories.User")
    main_link = factory.Faker("url")
    description = factory.Faker("paragraph")


class ActionFilter(DjangoModelFactory):
    class Meta:
        model = models.ActionFilter

    creator = factory.SubFactory("accounts.factories.User")
