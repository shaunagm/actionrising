from factory.django import DjangoModelFactory
import factory
from . import models


class Commitment(DjangoModelFactory):
    class Meta:
        model = models.Commitment

    profile = factory.SubFactory("profiles.factories.Profile")
    action = factory.SubFactory("actions.factories.Action")
