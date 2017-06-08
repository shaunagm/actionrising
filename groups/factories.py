from factory.django import DjangoModelFactory
import factory

from django.contrib.auth import models as auth_models
from groups import models as app_models
from mysite.lib.choices import PrivacyChoices

from slates.factories import ActionRisingProvider
factory.Faker.add_provider(ActionRisingProvider)

class Group(DjangoModelFactory):
    class Meta:
        model = auth_models.Group

    name = factory.Faker("name")

class GroupProfile(DjangoModelFactory):
    class Meta:
        model = app_models.GroupProfile

    group = factory.SubFactory("groups.factories.Group")
    owner = factory.SubFactory("accounts.factories.User")
    groupname = factory.Faker("group_name")
    description = "A long description!"
    summary = "A short summary"
