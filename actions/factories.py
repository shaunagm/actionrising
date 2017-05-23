import mock
from factory.django import DjangoModelFactory
import factory
import slates.factories  # noqa # register Provider

from mysite.lib.choices import PrivacyChoices
from . import models


class Action(DjangoModelFactory):
    class Meta:
        model = models.Action

    title = factory.Faker("action_title")
    creator = factory.SubFactory("accounts.factories.User")
    main_link = factory.Faker("url")
    description = factory.Faker("paragraph")


class VisibleUnfollowedAction(factory.Factory):
    class Meta:
        # trick to create random objects via factoryboy
        model = mock.Mock()

    action = factory.SubFactory(Action, privacy=PrivacyChoices.follows)
    relationship = factory.SubFactory('profiles.factories.Relationship',
        person_B=factory.SelfAttribute('..action.creator.profile'),
        B_follows_A=True)


class ActionFilter(DjangoModelFactory):
    class Meta:
        model = models.ActionFilter

    creator = factory.SubFactory("accounts.factories.User")
