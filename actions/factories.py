from django.utils import timezone
from factory.django import DjangoModelFactory
import factory.fuzzy
import slates.factories  # noqa # register Provider
from . import models


class Action(DjangoModelFactory):
    class Meta:
        model = models.Action

    class Params:
        due = factory.Trait(
            deadline = factory.fuzzy.FuzzyDateTime(
                start_dt=timezone.now() + timezone.timedelta(days=30),
                end_dt=timezone.now() + timezone.timedelta(days=300),
                force_second=0, force_microsecond=0))

    title = factory.Faker("title")
    creator = factory.SubFactory("accounts.factories.User")
    main_link = factory.Faker("url")
    description = factory.Faker("paragraph")


class ActionFilter(DjangoModelFactory):
    class Meta:
        model = models.ActionFilter

    creator = factory.SubFactory("accounts.factories.User")
