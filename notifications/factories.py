from factory.django import DjangoModelFactory
import factory.faker

from . import models


class Notification(DjangoModelFactory):
    class Meta:
        model = models.Notification

    user = factory.SubFactory("accounts.factories.User")
    event = factory.SubFactory("actions.factories.Action")


class NotificationSettings(DjangoModelFactory):
    class Meta:
        model = models.NotificationSettings

    user = factory.SubFactory("accounts.factories.User")
